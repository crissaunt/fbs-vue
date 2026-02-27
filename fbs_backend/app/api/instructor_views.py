from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.db.models import Q
from fbs_instructor.models import Instructor
from ..serializers import InstructorsSerializer

class InstructorsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing instructor information.
    """
    queryset = Instructor.objects.all().order_by('id')
    serializer_class = InstructorsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(instructor_id__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset
