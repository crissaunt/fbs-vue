from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, Avg
from ..models import CheckInDetail, BookingDetail
from ..serializers import CheckInDetailSerializer, CheckInListSerializer

class CheckInDetailViewSet(viewsets.ModelViewSet):
    queryset = CheckInDetail.objects.all()
    serializer_class = CheckInDetailSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'flight_number', 'check_in_counter']
    search_fields = [
        'booking_detail__passenger__first_name',
        'booking_detail__passenger__last_name',
        'boarding_pass',
        'booking_detail__schedule__flight__flight_number',
    ]
    ordering_fields = ['check_in_time', 'departure_time', 'created_at']
    ordering = ['-check_in_time']
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CheckInListSerializer
        return CheckInDetailSerializer
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        today_checkins = self.get_queryset().filter(check_in_time__date=today)
        serializer = self.get_serializer(today_checkins, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = self.get_queryset().count()
        return Response({'total_checkins': total})
