from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.db.models import Q
from ..models import Students
from ..serializers import StudentsSerializer

from django.http import HttpResponse
import csv
from rest_framework.decorators import action

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

    @action(detail=False, methods=['get'])
    def export(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['username', 'student_number', 'first_name', 'mi', 'last_name', 'email', 'phone', 'course', 'year_level', 'gender'])
        
        students = self.get_queryset()
        for s in students:
            writer.writerow([
                s.user.username if s.user else '',
                s.student_number,
                s.first_name,
                s.mi or '',
                s.last_name,
                s.email,
                s.phone_number,
                s.course,
                s.year_level,
                s.gender
            ])
            
        return response
