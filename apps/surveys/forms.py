from django import forms
from .models import SurveyResponse
from apps.villages.models import Village
from apps.visits.models import FieldVisit


class SurveyResponseForm(forms.ModelForm):
    visit = forms.ModelChoiceField(
        queryset=FieldVisit.objects.filter(is_published=True).order_by("day_number"),
        required=False,
    )
    village = forms.ModelChoiceField(
        queryset=Village.objects.filter(is_active=True),
        widget=forms.RadioSelect,
        empty_label=None,
    )
    devices = forms.MultipleChoiceField(
        choices=SurveyResponse.DEVICE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    internet_purposes = forms.MultipleChoiceField(
        choices=SurveyResponse.PURPOSE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = SurveyResponse
        fields = [
            "visit", "village", "age_group", "education", "occupation", "occupation_other",
            "uses_internet",
            "devices", "device_other", "connection_type", "connection_other",
            "hours_per_day", "internet_purposes", "purpose_other",
            "cyber_awareness_rating", "knows_otp_rule", "faced_fraud", "fraud_description",
        ]
        widgets = {
            "age_group": forms.Select(attrs={"class": "form-select"}),
            "education": forms.Select(attrs={"class": "form-select"}),
            "occupation": forms.RadioSelect,
            "uses_internet": forms.RadioSelect(choices=[(True, "Yes"), (False, "No")]),
            "connection_type": forms.RadioSelect,
            "hours_per_day": forms.RadioSelect,
            "cyber_awareness_rating": forms.RadioSelect,
            "knows_otp_rule": forms.RadioSelect,
            "faced_fraud": forms.RadioSelect,
            "fraud_description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        cleaned = super().clean()
        uses_internet = cleaned.get("uses_internet")
        if uses_internet:
            if not cleaned.get("devices"):
                self.add_error("devices", "Please select at least one device.")
            if not cleaned.get("connection_type"):
                self.add_error("connection_type", "Please select your connection type.")
            if not cleaned.get("hours_per_day"):
                self.add_error("hours_per_day", "Please select your daily usage hours.")
            if not cleaned.get("cyber_awareness_rating"):
                self.add_error("cyber_awareness_rating", "Please rate your cyber awareness.")
            if not cleaned.get("knows_otp_rule"):
                self.add_error("knows_otp_rule", "Please answer the OTP question.")
            if not cleaned.get("faced_fraud"):
                self.add_error("faced_fraud", "Please answer the fraud question.")
        return cleaned
