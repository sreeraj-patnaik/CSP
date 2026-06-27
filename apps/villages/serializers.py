from rest_framework import serializers
from .models import Village, VillageObservation


class VillageSerializer(serializers.ModelSerializer):
    survey_count = serializers.ReadOnlyField()
    visit_count = serializers.ReadOnlyField()
    internet_usage_pct = serializers.ReadOnlyField()
    absolute_url = serializers.SerializerMethodField()

    class Meta:
        model = Village
        fields = [
            "id", "name", "slug", "description", "population", "households",
            "latitude", "longitude", "color_accent", "primary_occupation",
            "survey_count", "visit_count", "internet_usage_pct", "absolute_url",
        ]

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()


class VillageObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VillageObservation
        fields = ["id", "title", "content", "category", "observation_date"]
