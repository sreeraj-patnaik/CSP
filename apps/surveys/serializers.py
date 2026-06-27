from rest_framework import serializers
from .models import SurveyResponse


class SurveyResponseSerializer(serializers.ModelSerializer):
    village_name = serializers.CharField(source="village.name", read_only=True)
    age_group_label = serializers.CharField(source="get_age_group_display", read_only=True)
    education_label = serializers.CharField(source="get_education_display", read_only=True)

    class Meta:
        model = SurveyResponse
        fields = [
            "id", "village_name", "age_group", "age_group_label",
            "education", "education_label", "occupation", "uses_internet",
            "devices", "connection_type", "hours_per_day", "internet_purposes",
            "cyber_awareness_rating", "knows_otp_rule", "faced_fraud",
            "created_at",
        ]
