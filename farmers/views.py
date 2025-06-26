from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import User
from django.contrib.auth.models import Group
from farmers.serializers import FarmerSerializer


class FarmerAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        groups = Group.objects.get_or_create(name='Farmers')[0]
        print(groups)
        farmers = User.objects.filter(groups=groups)
        serializer = FarmerSerializer(farmers, many=True)
        return Response(serializer.data)
