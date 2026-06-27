import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .rag import answer_question, build_knowledge_base


@ensure_csrf_cookie
def chat_page(request):
    return render(request, "ai/chat.html")


@require_POST
def chat_api(request):
    try:
        body = json.loads(request.body)
        question = body.get("question", "").strip()
        history = body.get("history", [])
        if not question:
            return JsonResponse({"error": "Empty question"}, status=400)
        result = answer_question(question, conversation_history=history)
        return JsonResponse({
            "answer": result["answer"],
            "sources": result.get("sources", []),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_POST
def rebuild_knowledge_base(request):
    result = build_knowledge_base()
    if "error" in result:
        return JsonResponse(result, status=500)
    return JsonResponse(result)


SUGGESTED_QUESTIONS = [
    "How many people from each village use smartphones?",
    "Which village has the highest cyber fraud rate?",
    "What percentage of respondents are fully aware of OTP rules?",
    "Summarize Day 1 field visit — objectives, activities, and outcomes.",
    "What are the most common internet purposes among farmers?",
    "Compare internet usage across all villages.",
    "Which age group is most vulnerable to cyber fraud?",
    "List all team members and their roles.",
    "What challenges did the team face during field visits and how were they solved?",
    "What are the key recommendations from our survey findings?",
]


def suggested_questions(request):
    return JsonResponse({"questions": SUGGESTED_QUESTIONS})
