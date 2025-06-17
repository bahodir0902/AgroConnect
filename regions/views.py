from rest_framework.views import APIView
from regions.serializers import RegionSerializer
from rest_framework.permissions import AllowAny
from regions.models import Region
from rest_framework.response import Response

class RegionAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        regions = Region.objects.all()
        serializer = RegionSerializer(regions, many=True)
        return Response(serializer.data)

