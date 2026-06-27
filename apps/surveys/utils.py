"""Survey import/export utilities using pandas."""
import io
import pandas as pd
from django.http import HttpResponse
from .models import SurveyResponse
from apps.villages.models import Village


# ── Export ────────────────────────────────────────────────────────────────────

def queryset_to_dataframe(qs=None):
    if qs is None:
        qs = SurveyResponse.objects.select_related("village", "visit").all()
    rows = []
    for r in qs:
        rows.append({
            "ID": r.pk,
            "Submission Date": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "Village": r.village.name if r.village else "",
            "Age Group": r.get_age_group_display(),
            "Education": r.get_education_display(),
            "Occupation": r.occupation_display,
            "Uses Internet": "Yes" if r.uses_internet else "No",
            "Devices": ", ".join(r.devices_display),
            "Connection Type": r.get_connection_type_display() if r.connection_type else "",
            "Hours Per Day": r.get_hours_per_day_display() if r.hours_per_day else "",
            "Internet Purposes": ", ".join(r.purposes_display),
            "Cyber Awareness": r.get_cyber_awareness_rating_display() if r.cyber_awareness_rating else "",
            "Knows OTP Rule": r.get_knows_otp_rule_display() if r.knows_otp_rule else "",
            "Faced Fraud": r.get_faced_fraud_display() if r.faced_fraud else "",
            "Fraud Description": r.fraud_description,
            "Visit Day": r.visit.day_number if r.visit else "",
        })
    return pd.DataFrame(rows)


def export_excel(qs=None):
    df = queryset_to_dataframe(qs)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Survey Responses")
        ws = writer.sheets["Survey Responses"]
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 60)
    buffer.seek(0)
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="survey_responses.xlsx"'
    return response


def export_csv(qs=None):
    df = queryset_to_dataframe(qs)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    response = HttpResponse(buffer.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="survey_responses.csv"'
    return response


# ── Reverse lookup maps ───────────────────────────────────────────────────────

AGE_REVERSE = {v: k for k, v in dict(SurveyResponse.AGE_CHOICES).items()}
EDU_REVERSE = {v: k for k, v in dict(SurveyResponse.EDUCATION_CHOICES).items()}
OCC_REVERSE = {v: k for k, v in dict(SurveyResponse.OCCUPATION_CHOICES).items()}
CON_REVERSE = {v: k for k, v in dict(SurveyResponse.CONNECTION_CHOICES).items()}
HRS_REVERSE = {v: k for k, v in dict(SurveyResponse.HOURS_CHOICES).items()}
AWR_REVERSE = {v: k for k, v in dict(SurveyResponse.AWARENESS_CHOICES).items()}
OTP_REVERSE = {v: k for k, v in dict(SurveyResponse.OTP_CHOICES).items()}
FRD_REVERSE = {v: k for k, v in dict(SurveyResponse.FRAUD_CHOICES).items()}
DEV_REVERSE = {v: k for k, v in dict(SurveyResponse.DEVICE_CHOICES).items()}
PUR_REVERSE = {v: k for k, v in dict(SurveyResponse.PURPOSE_CHOICES).items()}

# Ordered list for substring-safe matching (longest first to avoid partial hits)
KNOWN_PURPOSES = sorted(PUR_REVERSE.items(), key=lambda x: -len(x[0]))
KNOWN_DEVICES  = sorted(DEV_REVERSE.items(),  key=lambda x: -len(x[0]))


def _cell(row, col):
    """Return a clean string from a DataFrame row cell, '' if NaN/None."""
    val = row.get(col, "")
    if val is None:
        return ""
    s = str(val).strip()
    return "" if s in ("nan", "NaN", "None", "<NA>") else s


# ── Import ────────────────────────────────────────────────────────────────────

# Exact Google Forms export column headers
COL_TIMESTAMP   = "Timestamp"
COL_VILLAGE     = "Village"
COL_AGE         = "Age Group"
COL_EDUCATION   = "Education"
COL_OCCUPATION  = "Occupation"
COL_INTERNET    = "Do you use the Internet?"
COL_DEVICES     = "Which device(s) do you usually use to access the Internet?"
COL_DEV_OTHER   = "Other device (if any)"
COL_CONNECTION  = "What type of internet connection do you mainly use?"
COL_HOURS       = "On average, how many hours per day do you use the Internet?"
COL_PURPOSES    = "What are your main purposes for using the Internet?"
COL_PUR_OTHER   = "Other purpose (if any)"
COL_AWARENESS   = "How would you rate your awareness about cyber safety?"
COL_OTP         = ("Do you know that you should never share your OTP (One Time Password) "
                   "with anyone, even if they claim to be from a bank or government office?")
COL_FRAUD       = ("Have you ever faced any online fraud or suspicious activity such as "
                   "fake calls, phishing messages, account hacking, OTP fraud, or money loss?")
COL_FRAUD_DESC  = "If yes, briefly describe what happened."


def _match_multi(raw, known_pairs):
    """Match a comma-separated cell against known (label→key) pairs via substring."""
    results = []
    for label, key in known_pairs:
        if label in raw:
            results.append(key)
    return results


def import_excel(file_obj, visit=None, source_name="Google Forms Export"):
    """
    Import survey responses from a Google Forms Excel/CSV export.

    Accepts both .xlsx (Excel) and .csv formats.
    Returns {"created": int, "errors": list, "total_rows": int}.
    """
    try:
        df = pd.read_excel(file_obj)
    except Exception:
        file_obj.seek(0)
        df = pd.read_csv(file_obj)

    created = 0
    errors = []
    villages_cache = {v.name.lower(): v for v in Village.objects.all()}

    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-indexed + header row
        try:
            # ── Village ──────────────────────────────────────────────────────
            village_name = _cell(row, COL_VILLAGE)
            village = villages_cache.get(village_name.lower())
            if not village:
                errors.append(
                    f"Row {row_num}: Village '{village_name}' not found. "
                    f"Known: {', '.join(sorted(villages_cache.keys()))}"
                )
                continue

            # ── Timestamp (optional — backdate created_at if present) ────────
            timestamp = None
            ts_raw = _cell(row, COL_TIMESTAMP)
            if ts_raw:
                try:
                    timestamp = pd.to_datetime(ts_raw, dayfirst=False)
                except Exception:
                    pass

            # ── Demographics ─────────────────────────────────────────────────
            age_group  = AGE_REVERSE.get(_cell(row, COL_AGE), "")
            education  = EDU_REVERSE.get(_cell(row, COL_EDUCATION), "")
            occ_raw    = _cell(row, COL_OCCUPATION)
            occupation = OCC_REVERSE.get(occ_raw, "other")
            occupation_other = occ_raw if occupation == "other" else ""

            # ── Internet usage ────────────────────────────────────────────────
            uses_internet = _cell(row, COL_INTERNET).lower() in ("yes", "true", "1")

            # ── Devices (substring-safe) ─────────────────────────────────────
            devices_raw = _cell(row, COL_DEVICES)
            devices     = _match_multi(devices_raw, KNOWN_DEVICES)
            device_other = _cell(row, COL_DEV_OTHER)

            # ── Connection type ───────────────────────────────────────────────
            connection_type = CON_REVERSE.get(_cell(row, COL_CONNECTION), "")

            # ── Hours ─────────────────────────────────────────────────────────
            hours_per_day = HRS_REVERSE.get(_cell(row, COL_HOURS), "")

            # ── Purposes (substring-safe) ─────────────────────────────────────
            purposes_raw     = _cell(row, COL_PURPOSES)
            internet_purposes = _match_multi(purposes_raw, KNOWN_PURPOSES)
            purpose_other    = _cell(row, COL_PUR_OTHER)

            # ── Awareness / OTP / Fraud ───────────────────────────────────────
            cyber_awareness_rating = AWR_REVERSE.get(_cell(row, COL_AWARENESS), "")
            knows_otp_rule         = OTP_REVERSE.get(_cell(row, COL_OTP), "")
            faced_fraud            = FRD_REVERSE.get(_cell(row, COL_FRAUD), "")
            fraud_description      = _cell(row, COL_FRAUD_DESC)

            obj = SurveyResponse(
                village=village,
                age_group=age_group,
                education=education,
                occupation=occupation,
                occupation_other=occupation_other,
                uses_internet=uses_internet,
                devices=devices,
                device_other=device_other,
                connection_type=connection_type,
                hours_per_day=hours_per_day,
                internet_purposes=internet_purposes,
                purpose_other=purpose_other,
                cyber_awareness_rating=cyber_awareness_rating,
                knows_otp_rule=knows_otp_rule,
                faced_fraud=faced_fraud,
                fraud_description=fraud_description,
                is_imported=True,
                import_source=source_name,
                visit=visit,
            )
            obj.save()

            # Backdate timestamp (update bypasses auto_now_add)
            if timestamp is not None:
                try:
                    SurveyResponse.objects.filter(pk=obj.pk).update(created_at=timestamp)
                except Exception:
                    pass

            created += 1

        except Exception as exc:
            errors.append(f"Row {row_num}: {exc}")

    return {"created": created, "errors": errors, "total_rows": len(df)}
