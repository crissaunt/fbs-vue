from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.db.models import Q
from ..models import Students
from ..serializers import StudentsSerializer

class StudentsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing student information.
    """
    queryset = Students.objects.all().order_by('id')
    serializer_class = StudentsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        gender = self.request.query_params.get('gender')
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(student_number__icontains=search) |
                Q(email__icontains=search)
            )
            
        if gender:
            queryset = queryset.filter(gender=gender)
            
        return queryset
