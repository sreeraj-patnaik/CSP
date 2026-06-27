from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count, Avg
from .models import SurveyResponse
from .serializers import SurveyResponseSerializer


class SurveyResponseListAPIView(ListAPIView):
    queryset = SurveyResponse.objects.select_related("village").all()
    serializer_class = SurveyResponseSerializer
    permission_classes = [AllowAny]


class SurveyStatsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = SurveyResponse.objects.all()
        total = qs.count()
        internet_users = qs.filter(uses_internet=True).count()
        return Response({
            "total": total,
            "internet_users": internet_users,
            "internet_pct": round((internet_users / total * 100) if total else 0, 1),
            "by_village": list(
                qs.values("village__name").annotate(count=Count("id")).order_by("-count")
            ),
        })
