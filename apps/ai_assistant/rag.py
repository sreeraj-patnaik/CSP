"""
CSP AI Assistant — robust context-stuffed LangChain + Ollama pipeline.

Strategy: at every query, build a complete snapshot of all live project data
(visits, villages, team, survey stats, site settings) and stuff it into the
system prompt so the LLM always has the full picture without relying on
vector-store retrieval or a pre-built index.

The FAISS knowledge base (build_knowledge_base / "Rebuild KB" staff button) is
kept as a secondary index for potential future use; it is NOT used in the
primary answer path.
"""
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from django.conf import settings
from django.db.models import Count, Q

try:
    from langchain_ollama import OllamaEmbeddings, ChatOllama
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """\
You are the official AI research assistant for the Community Service Project (CSP) on
"Safe Usage of Internet and Cybercrime Awareness in Rural Areas."

You have been given a complete, live snapshot of all project data below.
Use ONLY this data to answer questions. Do not invent or hallucinate statistics.

When answering:
- Be factual, precise, and comprehensive.
- Cite which visit, village, or data source you are drawing from.
- For numeric comparisons, mention exact counts and percentages.
- For team questions, include name, role, and designation.
- For visit questions, include date, villages, team, objectives, activities, and outcomes.
- If asked for recommendations, ground them in the survey findings.
- If the data does not contain an answer, say so clearly rather than guessing.

═══════════════════════════════════════════════════════════════════════════════
COMPLETE PROJECT DATA SNAPSHOT (live from database — current as of this query)
═══════════════════════════════════════════════════════════════════════════════

{context}

═══════════════════════════════════════════════════════════════════════════════
"""


# ── Context builder ───────────────────────────────────────────────────────────

def build_complete_context() -> str:
    """
    Build a comprehensive text representation of all project data from the live
    database. Called fresh on every query so answers are always up to date.
    """
    from apps.core.models import SiteSettings
    from apps.team.models import TeamMember
    from apps.villages.models import Village, VillageObservation
    from apps.visits.models import FieldVisit, VisitMedia
    from apps.surveys.models import SurveyResponse

    parts: list[str] = []

    # ── 1. Project overview ───────────────────────────────────────────────────
    try:
        s = SiteSettings.get()
        parts.append(
            f"PROJECT OVERVIEW\n"
            f"Name: {s.project_name}\n"
            f"Topic: {s.project_topic}\n"
            f"Mentor: {s.mentor_name}\n"
            f"College: {s.college_name or 'N/A'}\n"
            f"Academic Year: {s.academic_year}\n"
        )
    except Exception:
        parts.append("PROJECT OVERVIEW: (settings unavailable)\n")

    # ── 2. Team members ───────────────────────────────────────────────────────
    members = TeamMember.objects.filter(is_active=True).order_by("order", "name")
    if members.exists():
        lines = ["TEAM MEMBERS"]
        for m in members:
            line = f"  • {m.name} — {m.get_role_display()}"
            if m.designation:
                line += f", {m.designation}"
            if m.roll_number:
                line += f" (Roll: {m.roll_number})"
            if m.email:
                line += f" | {m.email}"
            if m.bio:
                line += f"\n    Bio: {m.bio}"
            lines.append(line)
        parts.append("\n".join(lines))

    # ── 3. Villages ───────────────────────────────────────────────────────────
    villages = Village.objects.filter(is_active=True).order_by("order", "name")
    for v in villages:
        qs = SurveyResponse.objects.filter(village=v)
        total = qs.count()
        internet = qs.filter(uses_internet=True).count()
        fraud_yes = qs.filter(faced_fraud="yes").count()
        otp_aware = qs.filter(knows_otp_rule="yes").count()
        otp_partial = qs.filter(knows_otp_rule="partial").count()
        otp_no = qs.filter(knows_otp_rule="no").count()

        def pct(num, den):
            return f"{round(num / den * 100, 1)}%" if den else "N/A"

        age_counts = {}
        for row in qs.values("age_group").annotate(n=Count("id")):
            age_counts[row["age_group"]] = row["n"]

        occ_counts = {}
        for row in qs.values("occupation").annotate(n=Count("id")):
            occ_counts[row["occupation"]] = row["n"]

        devices: list[str] = []
        purposes: list[str] = []
        for r in qs:
            devices.extend(r.devices or [])
            purposes.extend(r.internet_purposes or [])
        unique_devices = sorted(set(devices))
        unique_purposes = sorted(set(purposes))

        obs_qs = VillageObservation.objects.filter(village=v).order_by("order")
        obs_lines = [
            f"    [{o.category or 'general'}] {o.title}: {o.content}"
            for o in obs_qs
        ]

        visit_names = ", ".join(
            v.visits.filter(is_published=True)
            .values_list("title", flat=True)
        ) or "none"

        block = (
            f"VILLAGE: {v.name}\n"
            f"  District: {v.district or 'N/A'} | State: {v.state or 'N/A'}\n"
            f"  Population: {v.population or 'N/A'} | Households: {v.households or 'N/A'}"
            f" | Area: {v.area_sqkm or 'N/A'} sq.km\n"
            f"  Primary Occupation: {v.primary_occupation or 'N/A'}\n"
            f"  Description: {v.description or 'N/A'}\n"
            f"  Internet Infrastructure: {v.internet_infrastructure or 'N/A'}\n"
            f"  Challenges: {v.challenges or 'N/A'}\n"
            f"  Community Response: {v.community_response or 'N/A'}\n"
            f"  Visits conducted: {visit_names}\n"
            f"  Survey data ({total} responses):\n"
            f"    Internet users: {internet} ({pct(internet, total)})\n"
            f"    Faced cyber fraud: {fraud_yes} ({pct(fraud_yes, total)})\n"
            f"    Knows OTP rule: {otp_aware} yes, {otp_partial} partial, {otp_no} no\n"
            f"    Age breakdown: {json.dumps(age_counts)}\n"
            f"    Occupation breakdown: {json.dumps(occ_counts)}\n"
            f"    Devices used: {', '.join(unique_devices) or 'N/A'}\n"
            f"    Internet purposes: {', '.join(unique_purposes) or 'N/A'}\n"
        )
        if obs_lines:
            block += "  Observations:\n" + "\n".join(obs_lines) + "\n"
        parts.append(block)

    # ── 4. Field visits ───────────────────────────────────────────────────────
    visits = (
        FieldVisit.objects.filter(is_published=True)
        .prefetch_related("villages", "team_members")
        .order_by("day_number")
    )
    for visit in visits:
        village_names = ", ".join(visit.villages.values_list("name", flat=True)) or "N/A"
        team_lines = "\n".join(
            f"    • {m.name} ({m.get_role_display()}"
            + (f", {m.designation}" if m.designation else "") + ")"
            for m in visit.team_members.all()
        ) or "    • (none recorded)"

        objs = "\n".join(f"    • {o}" for o in (visit.objectives or [])) or "    (none)"
        acts = "\n".join(f"    {i+1}. {a}" for i, a in enumerate(visit.activities or [])) or "    (none)"

        # Survey stats for this visit
        vsr = SurveyResponse.objects.filter(visit=visit)
        vsrtotal = vsr.count()
        vsrinternet = vsr.filter(uses_internet=True).count()
        vsrfraud = vsr.filter(faced_fraud="yes").count()

        # Media count
        photo_count = VisitMedia.objects.filter(visit=visit, media_type="photo").count()
        try:
            from apps.gallery.models import Photo
            photo_count += Photo.objects.filter(visit=visit).count()
        except Exception:
            pass

        block = (
            f"FIELD VISIT — Day {visit.day_number}: {visit.title}\n"
            f"  Date: {visit.date.strftime('%B %d, %Y')}\n"
            f"  Villages: {village_names}\n"
            f"  Attendance (participants): {visit.attendance}\n"
            f"  Surveys collected: {visit.surveys_collected}\n"
            f"  Photos: {photo_count}\n"
            f"  Team present:\n{team_lines}\n"
            f"  Objectives:\n{objs}\n"
            f"  Activities:\n{acts}\n"
            f"  Observations: {visit.observations or '(none)'}\n"
            f"  Challenges/Problems: {visit.problems_faced or '(none)'}\n"
            f"  Solutions: {visit.solutions or '(none)'}\n"
            f"  Lessons learned: {visit.lessons_learned or '(none)'}\n"
            f"  Impact: {visit.impact or '(none)'}\n"
            f"  Summary: {visit.summary}\n"
        )
        if vsrtotal:
            block += (
                f"  Survey results from this visit ({vsrtotal} responses):\n"
                f"    Internet users: {vsrinternet} | Fraud cases: {vsrfraud}\n"
            )
        parts.append(block)

    # ── 5. Overall survey statistics ──────────────────────────────────────────
    all_r = SurveyResponse.objects.all()
    total_r = all_r.count()
    if total_r:
        internet_r = all_r.filter(uses_internet=True).count()
        fraud_yes_r = all_r.filter(faced_fraud="yes").count()
        fraud_no_r = all_r.filter(faced_fraud="no").count()
        fraud_ns_r = all_r.filter(faced_fraud="not_sure").count()
        otp_yes_r = all_r.filter(knows_otp_rule="yes").count()
        otp_part_r = all_r.filter(knows_otp_rule="partial").count()
        otp_no_r = all_r.filter(knows_otp_rule="no").count()

        age_agg = {
            row["age_group"]: row["n"]
            for row in all_r.values("age_group").annotate(n=Count("id"))
        }
        occ_agg = {
            row["occupation"]: row["n"]
            for row in all_r.values("occupation").annotate(n=Count("id"))
        }
        edu_agg = {
            row["education"]: row["n"]
            for row in all_r.values("education").annotate(n=Count("id"))
        }

        # Collect fraud descriptions
        fraud_descs = list(
            all_r.exclude(fraud_description="")
            .values_list("fraud_description", "village__name")
        )

        stats_block = (
            f"OVERALL SURVEY STATISTICS ({total_r} total responses across all villages)\n"
            f"  Internet usage: {internet_r} ({round(internet_r/total_r*100,1)}%)\n"
            f"  Faced cyber fraud:\n"
            f"    Yes: {fraud_yes_r} ({round(fraud_yes_r/total_r*100,1)}%)\n"
            f"    No: {fraud_no_r} ({round(fraud_no_r/total_r*100,1)}%)\n"
            f"    Not sure: {fraud_ns_r} ({round(fraud_ns_r/total_r*100,1)}%)\n"
            f"  OTP rule awareness:\n"
            f"    Fully aware: {otp_yes_r} ({round(otp_yes_r/total_r*100,1)}%)\n"
            f"    Partially aware: {otp_part_r} ({round(otp_part_r/total_r*100,1)}%)\n"
            f"    Not aware: {otp_no_r} ({round(otp_no_r/total_r*100,1)}%)\n"
            f"  Age breakdown: {json.dumps(age_agg)}\n"
            f"  Occupation breakdown: {json.dumps(occ_agg)}\n"
            f"  Education breakdown: {json.dumps(edu_agg)}\n"
        )
        if fraud_descs:
            stats_block += "  Reported fraud cases:\n"
            for desc, vname in fraud_descs:
                stats_block += f"    [{vname}] {desc}\n"
        parts.append(stats_block)

    # ── 6. Analytics insights (if available) ─────────────────────────────────
    try:
        from apps.analytics import insights as ins
        auto = ins.generate_auto_insights()
        if auto:
            lines = ["AUTOMATED INSIGHTS"]
            for item in auto:
                lines.append(f"  • {item['title']}: {item['text']}")
            parts.append("\n".join(lines))

        comparison = ins.village_comparison()
        if comparison:
            lines = ["VILLAGE COMPARISON"]
            for item in comparison:
                lines.append(
                    f"  • {item['village']}: {item['total']} responses, "
                    f"{item['internet_users']} internet users "
                    f"({item['internet_pct']}%), "
                    f"avg awareness {item['avg_awareness']}/5"
                )
            parts.append("\n".join(lines))
    except Exception:
        pass

    return "\n\n".join(parts)


# ── Chat model helper ─────────────────────────────────────────────────────────

def _get_chat_model():
    """Return a ChatOllama instance configured from settings."""
    return ChatOllama(
        model=getattr(settings, "OLLAMA_MODEL", "mistral:latest"),
        base_url=getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.1,
        num_ctx=8192,
    )


# ── Primary answer function ───────────────────────────────────────────────────

def answer_question(question: str, conversation_history: list = None) -> dict:
    """
    Answer a question using a complete live context stuffed into the system prompt.

    Returns {"answer": str, "sources": list, "status": str}.
    """
    if not LANGCHAIN_AVAILABLE:
        return {
            "answer": (
                "The AI assistant requires LangChain and Ollama. "
                "Please install requirements and ensure Ollama is running."
            ),
            "sources": [],
            "status": "error",
        }

    try:
        context = build_complete_context()
        system_content = SYSTEM_PROMPT_TEMPLATE.format(context=context)

        messages = [SystemMessage(content=system_content)]

        for turn in (conversation_history or [])[-8:]:
            role = turn.get("role", "")
            content = turn.get("content", "")
            if not content:
                continue
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role in ("ai", "assistant"):
                messages.append(AIMessage(content=content))

        messages.append(HumanMessage(content=question))

        llm = _get_chat_model()
        response = llm.invoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)

        return {
            "answer": answer,
            "sources": _infer_sources(question, context),
            "status": "success",
        }

    except Exception as exc:
        import traceback
        return {
            "answer": (
                f"Sorry, I could not answer your question: {exc}\n\n"
                "Please make sure Ollama is running and the model is available."
            ),
            "sources": [],
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "status": "error",
        }


def _infer_sources(question: str, context: str) -> list[str]:
    """Return plausible source labels based on keywords in the question."""
    q = question.lower()
    sources = []
    if any(w in q for w in ("visit", "day", "field", "activity", "activities")):
        sources.append("field-visits")
    if any(w in q for w in ("village", "maharajupeta", "jonnada", "akulapeta")):
        sources.append("villages")
    if any(w in q for w in ("survey", "internet", "fraud", "otp", "awareness", "cyber")):
        sources.append("survey-data")
    if any(w in q for w in ("team", "member", "mentor", "student", "who")):
        sources.append("team")
    if any(w in q for w in ("compare", "comparison", "insight", "trend", "analytic")):
        sources.append("analytics")
    return sources or ["project-data"]


# ── FAISS knowledge base (staff Rebuild KB feature) ──────────────────────────

def build_knowledge_base() -> dict:
    """
    Index all project data into a FAISS vector store.
    Used by the staff "Rebuild KB" button. Not required for answering questions.
    """
    if not LANGCHAIN_AVAILABLE:
        return {"error": "LangChain not installed"}

    try:
        context_text = build_complete_context()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = splitter.create_documents(
            [context_text],
            metadatas=[{"source": "csp-project-full"}],
        )

        embeddings = OllamaEmbeddings(
            model=getattr(settings, "OLLAMA_EMBED_MODEL", "nomic-embed-text:latest"),
            base_url=getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434"),
        )

        vectorstore = FAISS.from_documents(chunks, embeddings)
        index_dir = str(getattr(settings, "CHROMA_PERSIST_DIR", "data/chroma"))
        Path(index_dir).mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(index_dir)

        return {
            "indexed": len(chunks),
            "documents": 1,
            "sources": ["csp-project-full"],
            "context_length": len(context_text),
        }

    except Exception as exc:
        return {"error": str(exc)}
