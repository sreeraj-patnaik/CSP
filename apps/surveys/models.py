from django.db import models
from django.urls import reverse
from apps.core.models import TimeStampedModel
from apps.villages.models import Village


class SurveyResponse(TimeStampedModel):
    # ── Section 1: Demographics ───────────────────────────────────────────────
    AGE_CHOICES = [
        ("below_18", "Below 18 years"),
        ("18_25", "18–25 years"),
        ("26_35", "26–35 years"),
        ("36_45", "36–45 years"),
        ("46_60", "46–60 years"),
        ("above_60", "Above 60 years"),
    ]
    EDUCATION_CHOICES = [
        ("none", "No formal education"),
        ("primary", "Primary (1–5)"),
        ("upper_primary", "Upper Primary (6–8)"),
        ("secondary", "Secondary (9–10)"),
        ("intermediate", "Intermediate / +2"),
        ("graduate", "Graduate"),
        ("postgraduate", "Postgraduate and above"),
    ]
    OCCUPATION_CHOICES = [
        ("student", "Student"),
        ("farmer", "Farmer"),
        ("daily_wage", "Daily wage worker"),
        ("private_employee", "Private employee"),
        ("government_employee", "Government employee"),
        ("self_employed", "Self-employed / Business"),
        ("homemaker", "Homemaker"),
        ("unemployed", "Unemployed"),
        ("other", "Other"),
    ]

    village = models.ForeignKey(
        Village, on_delete=models.SET_NULL, null=True,
        related_name="survey_responses"
    )
    age_group = models.CharField(max_length=20, choices=AGE_CHOICES)
    education = models.CharField(max_length=30, choices=EDUCATION_CHOICES)
    occupation = models.CharField(max_length=30, choices=OCCUPATION_CHOICES)
    occupation_other = models.CharField(max_length=200, blank=True)

    # ── Q5: Internet Usage (branching trigger) ────────────────────────────────
    uses_internet = models.BooleanField(default=False)

    # ── Section 2: Internet Usage (conditional) ───────────────────────────────
    DEVICE_CHOICES = [
        ("smartphone", "Smartphone"),
        ("basic_phone", "Basic phone (with internet)"),
        ("tablet", "Tablet"),
        ("laptop", "Laptop"),
        ("desktop", "Desktop computer"),
    ]
    CONNECTION_CHOICES = [
        ("mobile_data", "Mobile data"),
        ("broadband", "Home broadband / Wi-Fi"),
        ("public_wifi", "Public Wi-Fi"),
        ("other", "Other"),
    ]
    HOURS_CHOICES = [
        ("less_1", "Less than 1 hour"),
        ("1_2", "1–2 hours"),
        ("2_4", "2–4 hours"),
        ("4_6", "4–6 hours"),
        ("more_6", "More than 6 hours"),
    ]
    PURPOSE_CHOICES = [
        ("education", "Education / Online Classes"),
        ("work", "Work / Business"),
        ("communication", "Communication (WhatsApp, Calls, Email)"),
        ("social_media", "Social Media"),
        ("entertainment", "Entertainment"),
        ("shopping", "Online Shopping"),
        ("banking", "Online Banking / Bill Payments"),
        ("government", "Government Services"),
    ]
    AWARENESS_CHOICES = [
        ("very_low", "Very Low"),
        ("low", "Low"),
        ("moderate", "Moderate"),
        ("high", "High"),
        ("very_high", "Very High"),
    ]
    OTP_CHOICES = [
        ("yes", "Yes, I know this."),
        ("partial", "I have heard about it but I am not fully sure."),
        ("no", "No, I do not know this."),
    ]
    FRAUD_CHOICES = [
        ("yes", "Yes"),
        ("no", "No"),
        ("not_sure", "Not Sure"),
    ]

    devices = models.JSONField(default=list, blank=True)
    device_other = models.CharField(max_length=200, blank=True)
    connection_type = models.CharField(max_length=20, choices=CONNECTION_CHOICES, blank=True)
    connection_other = models.CharField(max_length=200, blank=True)
    hours_per_day = models.CharField(max_length=10, choices=HOURS_CHOICES, blank=True)
    internet_purposes = models.JSONField(default=list, blank=True)
    purpose_other = models.CharField(max_length=200, blank=True)
    cyber_awareness_rating = models.CharField(max_length=10, choices=AWARENESS_CHOICES, blank=True)
    knows_otp_rule = models.CharField(max_length=10, choices=OTP_CHOICES, blank=True)
    faced_fraud = models.CharField(max_length=10, choices=FRAUD_CHOICES, blank=True)
    fraud_description = models.TextField(blank=True)

    # ── Metadata ──────────────────────────────────────────────────────────────
    visit = models.ForeignKey(
        "visits.FieldVisit", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="survey_responses"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_imported = models.BooleanField(default=False)
    import_source = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Survey Response"
        verbose_name_plural = "Survey Responses"

    def __str__(self):
        return f"Response #{self.pk} – {self.village} – {self.get_age_group_display()}"

    @property
    def age_group_display(self):
        return dict(self.AGE_CHOICES).get(self.age_group, self.age_group)

    @property
    def education_display(self):
        return dict(self.EDUCATION_CHOICES).get(self.education, self.education)

    @property
    def occupation_display(self):
        label = dict(self.OCCUPATION_CHOICES).get(self.occupation, self.occupation)
        if self.occupation == "other" and self.occupation_other:
            return self.occupation_other
        return label

    @property
    def devices_display(self):
        mapping = dict(self.DEVICE_CHOICES)
        return [mapping.get(d, d) for d in (self.devices or [])]

    @property
    def purposes_display(self):
        mapping = dict(self.PURPOSE_CHOICES)
        return [mapping.get(p, p) for p in (self.internet_purposes or [])]

    @property
    def awareness_score(self):
        """Numeric 1–5 for the cyber_awareness_rating."""
        scores = {
            "very_low": 1, "low": 2, "moderate": 3, "high": 4, "very_high": 5
        }
        return scores.get(self.cyber_awareness_rating, 0)
