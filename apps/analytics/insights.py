"""
Pandas-powered analytics engine.  All methods return plain dicts/lists
that are JSON-serialisable so views can pass them straight to ECharts.
"""
import pandas as pd
from django.db.models import Count, Avg
from apps.surveys.models import SurveyResponse
from apps.villages.models import Village


def _get_df(village_slug=None):
    qs = SurveyResponse.objects.select_related("village").values(
        "id", "village__name", "age_group", "education", "occupation",
        "uses_internet", "devices", "connection_type", "hours_per_day",
        "internet_purposes", "cyber_awareness_rating", "knows_otp_rule",
        "faced_fraud", "created_at",
    )
    if village_slug and village_slug != "all":
        qs = qs.filter(village__slug=village_slug)
    df = pd.DataFrame(list(qs))
    if df.empty:
        return df
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["date"] = df["created_at"].dt.date
    df["awareness_score"] = df["cyber_awareness_rating"].map({
        "very_low": 1, "low": 2, "moderate": 3, "high": 4, "very_high": 5
    }).fillna(0)
    return df


def village_comparison(village_slug=None):
    df = _get_df()
    if df.empty:
        return []
    grp = df.groupby("village__name").agg(
        total=("id", "count"),
        internet_users=("uses_internet", "sum"),
        avg_awareness=("awareness_score", "mean"),
    ).reset_index()
    grp["internet_pct"] = (grp["internet_users"] / grp["total"] * 100).round(1)
    grp["avg_awareness"] = grp["avg_awareness"].round(2)
    return grp.rename(columns={"village__name": "village"}).to_dict(orient="records")


def age_vs_internet():
    df = _get_df()
    if df.empty:
        return {}
    AGE_ORDER = ["below_18", "18_25", "26_35", "36_45", "46_60", "above_60"]
    AGE_LABELS = {
        "below_18": "Below 18", "18_25": "18–25", "26_35": "26–35",
        "36_45": "36–45", "46_60": "46–60", "above_60": "Above 60"
    }
    ct = pd.crosstab(df["age_group"], df["uses_internet"])
    ct = ct.reindex([a for a in AGE_ORDER if a in ct.index])
    result = {
        "categories": [AGE_LABELS.get(a, a) for a in ct.index],
        "internet_yes": ct.get(True, pd.Series([0]*len(ct))).tolist(),
        "internet_no": ct.get(False, pd.Series([0]*len(ct))).tolist(),
    }
    return result


def education_vs_awareness():
    df = _get_df()
    if df.empty:
        return {}
    EDU_ORDER = ["none", "primary", "upper_primary", "secondary", "intermediate", "graduate", "postgraduate"]
    EDU_LABELS = {
        "none": "None", "primary": "Primary", "upper_primary": "Upper Primary",
        "secondary": "Secondary", "intermediate": "Intermediate",
        "graduate": "Graduate", "postgraduate": "Postgraduate+"
    }
    ct = pd.crosstab(df["education"], df["awareness_score"])
    ct = ct.reindex([e for e in EDU_ORDER if e in ct.index])
    avg = df.groupby("education")["awareness_score"].mean().reindex(
        [e for e in EDU_ORDER if e in ct.index]
    ).round(2)
    return {
        "categories": [EDU_LABELS.get(e, e) for e in ct.index],
        "avg_awareness": avg.tolist(),
    }


def occupation_vs_awareness():
    df = _get_df()
    if df.empty:
        return {}
    OCC_LABELS = {
        "student": "Student", "farmer": "Farmer", "daily_wage": "Daily Wage",
        "private_employee": "Private Emp.", "government_employee": "Govt. Emp.",
        "self_employed": "Self-Employed", "homemaker": "Homemaker",
        "unemployed": "Unemployed", "other": "Other"
    }
    grp = df.groupby("occupation").agg(
        count=("id", "count"),
        avg_awareness=("awareness_score", "mean"),
        internet_pct=("uses_internet", "mean"),
    ).reset_index()
    grp["avg_awareness"] = grp["avg_awareness"].round(2)
    grp["internet_pct"] = (grp["internet_pct"] * 100).round(1)
    grp["label"] = grp["occupation"].map(OCC_LABELS).fillna(grp["occupation"])
    return grp.to_dict(orient="records")


def device_distribution():
    df = _get_df()
    if df.empty:
        return []
    internet_df = df[df["uses_internet"] == True]
    DEVICE_LABELS = {
        "smartphone": "Smartphone", "basic_phone": "Basic Phone",
        "tablet": "Tablet", "laptop": "Laptop", "desktop": "Desktop"
    }
    counts = {}
    for devices in internet_df["devices"]:
        for d in (devices or []):
            counts[d] = counts.get(d, 0) + 1
    return [{"name": DEVICE_LABELS.get(k, k), "value": v}
            for k, v in sorted(counts.items(), key=lambda x: -x[1])]


def internet_purposes_distribution():
    df = _get_df()
    if df.empty:
        return []
    internet_df = df[df["uses_internet"] == True]
    PURPOSE_LABELS = {
        "education": "Education", "work": "Work/Business",
        "communication": "Communication", "social_media": "Social Media",
        "entertainment": "Entertainment", "shopping": "Shopping",
        "banking": "Banking", "government": "Govt. Services"
    }
    counts = {}
    for purposes in internet_df["internet_purposes"]:
        for p in (purposes or []):
            counts[p] = counts.get(p, 0) + 1
    return [{"name": PURPOSE_LABELS.get(k, k), "value": v}
            for k, v in sorted(counts.items(), key=lambda x: -x[1])]


def fraud_experience_by_village():
    df = _get_df()
    if df.empty:
        return {}
    ct = pd.crosstab(df["village__name"], df["faced_fraud"])
    return {
        "villages": ct.index.tolist(),
        "yes": ct.get("yes", pd.Series([0]*len(ct))).tolist(),
        "no": ct.get("no", pd.Series([0]*len(ct))).tolist(),
        "not_sure": ct.get("not_sure", pd.Series([0]*len(ct))).tolist(),
    }


def otp_awareness_distribution():
    df = _get_df()
    if df.empty:
        return []
    OTP_LABELS = {
        "yes": "Yes, I know this",
        "partial": "Heard but not sure",
        "no": "No, I do not know"
    }
    counts = df["knows_otp_rule"].value_counts()
    return [{"name": OTP_LABELS.get(k, k), "value": int(v)}
            for k, v in counts.items()]


def daily_submission_trend():
    df = _get_df()
    if df.empty:
        return {}
    trend = df.groupby("date").size().reset_index(name="count")
    return {
        "dates": [str(d) for d in trend["date"]],
        "counts": trend["count"].tolist(),
    }


def awareness_heatmap():
    """Village × Age Group awareness heatmap data."""
    df = _get_df()
    if df.empty:
        return {}
    AGE_ORDER = ["below_18", "18_25", "26_35", "36_45", "46_60", "above_60"]
    AGE_LABELS = {
        "below_18": "Below 18", "18_25": "18–25", "26_35": "26–35",
        "36_45": "36–45", "46_60": "46–60", "above_60": "Above 60"
    }
    pivot = df.pivot_table(
        index="village__name", columns="age_group",
        values="awareness_score", aggfunc="mean"
    ).reindex(columns=[a for a in AGE_ORDER if a in df["age_group"].unique()])
    data_points = []
    for vi, village in enumerate(pivot.index):
        for ai, age in enumerate(pivot.columns):
            val = pivot.loc[village, age]
            if not pd.isna(val):
                data_points.append([vi, ai, round(float(val), 2)])
    return {
        "villages": pivot.index.tolist(),
        "age_groups": [AGE_LABELS.get(a, a) for a in pivot.columns],
        "data": data_points,
    }


def connection_type_distribution():
    df = _get_df()
    if df.empty:
        return []
    internet_df = df[df["uses_internet"] == True]
    CON_LABELS = {
        "mobile_data": "Mobile Data", "broadband": "Home Broadband",
        "public_wifi": "Public Wi-Fi", "other": "Other"
    }
    counts = internet_df["connection_type"].value_counts()
    return [{"name": CON_LABELS.get(k, k), "value": int(v)} for k, v in counts.items()]


def hours_per_day_distribution():
    df = _get_df()
    if df.empty:
        return []
    internet_df = df[df["uses_internet"] == True]
    HRS_LABELS = {
        "less_1": "< 1 hr", "1_2": "1–2 hrs",
        "2_4": "2–4 hrs", "4_6": "4–6 hrs", "more_6": "> 6 hrs"
    }
    counts = internet_df["hours_per_day"].value_counts()
    return [{"name": HRS_LABELS.get(k, k), "value": int(v)} for k, v in counts.items()]


def generate_auto_insights():
    """Generate human-readable observation strings automatically."""
    df = _get_df()
    if df.empty:
        return []
    insights = []
    total = len(df)

    # Most common occupation
    top_occ = df["occupation"].mode().iloc[0] if not df["occupation"].empty else None
    if top_occ:
        pct = round(len(df[df["occupation"] == top_occ]) / total * 100, 1)
        OCC_LABELS = {
            "student": "Students", "farmer": "Farmers", "daily_wage": "Daily wage workers",
            "private_employee": "Private employees", "government_employee": "Government employees",
            "self_employed": "Self-employed individuals", "homemaker": "Homemakers",
            "unemployed": "Unemployed individuals"
        }
        insights.append({
            "type": "occupation",
            "icon": "👤",
            "title": "Most Common Occupation",
            "text": f"{OCC_LABELS.get(top_occ, top_occ)} form the largest group at {pct}% of respondents.",
            "severity": "info",
        })

    # Village with highest awareness
    grp = df.groupby("village__name")["awareness_score"].mean()
    if not grp.empty:
        best = grp.idxmax()
        best_score = round(grp.max(), 2)
        worst = grp.idxmin()
        worst_score = round(grp.min(), 2)
        insights.append({
            "type": "village_awareness",
            "icon": "🏆",
            "title": "Highest Cyber Awareness",
            "text": f"{best} has the highest average cyber awareness score of {best_score}/5.",
            "severity": "success",
        })
        insights.append({
            "type": "village_concern",
            "icon": "⚠️",
            "title": "Attention Needed",
            "text": f"{worst} has the lowest average awareness score of {worst_score}/5 and may need targeted interventions.",
            "severity": "warning",
        })

    # Smartphone dominance
    all_devices = [d for devs in df["devices"] for d in (devs or [])]
    if all_devices:
        smartphone_pct = round(all_devices.count("smartphone") / len(all_devices) * 100, 1)
        insights.append({
            "type": "device",
            "icon": "📱",
            "title": "Primary Internet Device",
            "text": f"Smartphones account for {smartphone_pct}% of all internet access devices, making mobile-first outreach essential.",
            "severity": "info",
        })

    # Vulnerable groups
    fraud_df = df[df["faced_fraud"] == "yes"]
    if len(fraud_df) > 0:
        top_fraud_occ = fraud_df["occupation"].mode().iloc[0] if not fraud_df.empty else None
        if top_fraud_occ:
            OCC_LABELS = {"farmer": "Farmers", "daily_wage": "Daily wage workers", "homemaker": "Homemakers"}
            insights.append({
                "type": "vulnerable",
                "icon": "🔴",
                "title": "Vulnerable Group Identified",
                "text": f"{OCC_LABELS.get(top_fraud_occ, top_fraud_occ.title())} report the highest frequency of online fraud encounters. Targeted awareness sessions recommended.",
                "severity": "danger",
            })

    # OTP awareness gap
    otp_no = len(df[df["knows_otp_rule"] == "no"])
    otp_no_pct = round(otp_no / total * 100, 1)
    if otp_no_pct > 20:
        insights.append({
            "type": "otp",
            "icon": "🔑",
            "title": "OTP Awareness Gap",
            "text": f"{otp_no_pct}% of respondents are unaware of OTP sharing risks — a critical cybersecurity vulnerability in this community.",
            "severity": "danger",
        })

    # Internet non-users
    non_internet = len(df[df["uses_internet"] == False])
    non_internet_pct = round(non_internet / total * 100, 1)
    if non_internet_pct > 0:
        insights.append({
            "type": "digital_divide",
            "icon": "🌐",
            "title": "Digital Divide",
            "text": f"{non_internet_pct}% of surveyed residents do not use the Internet at all, highlighting a significant digital inclusion gap.",
            "severity": "warning",
        })

    # Education-awareness correlation
    edu_aware = df.groupby("education")["awareness_score"].mean()
    if "graduate" in edu_aware and "none" in edu_aware:
        gap = round(edu_aware["graduate"] - edu_aware["none"], 2)
        insights.append({
            "type": "education_correlation",
            "icon": "📚",
            "title": "Education–Awareness Correlation",
            "text": f"Graduates score {gap} points higher in cyber awareness than those with no formal education, confirming education's role in digital literacy.",
            "severity": "info",
        })

    return insights
