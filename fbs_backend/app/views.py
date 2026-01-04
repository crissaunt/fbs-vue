from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer

class MeView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users can access

    def get(self, request):
        serializer = UserSerializer(request.user)  # Serialize the logged-in user
        return Response(serializer.data)           # Return JSON
          