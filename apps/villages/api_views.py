from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Village
from .serializers import VillageSerializer


class VillageListAPIView(ListAPIView):
    queryset = Village.objects.filter(is_active=True)
    serializer_class = VillageSerializer
    permission_classes = [AllowAny]


class VillageDetailAPIView(RetrieveAPIView):
    queryset = Village.objects.filter(is_active=True)
    serializer_class = VillageSerializer
    lookup_field = "slug"
    permission_classes = [AllowAny]


class VillageMapAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        villages = Village.objects.filter(is_active=True, latitude__isnull=False)
        data = VillageSerializer(villages, many=True).data
        return Response(data)
