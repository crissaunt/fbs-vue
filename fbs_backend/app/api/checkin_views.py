import csv
from django.http import HttpResponse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from ..models import CheckInDetail, BookingDetail
from ..serializers import CheckInDetailSerializer, CheckInListSerializer

class CheckInDetailViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing check-in details.
    """
    queryset = CheckInDetail.objects.select_related(
        'booking_detail',
        'booking_detail__passenger',
        'booking_detail__schedule',
        'booking_detail__schedule__flight',
    ).all()
    
    serializer_class = CheckInDetailSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'flight_number', 'check_in_counter']
    search_fields = [
        'booking_detail__passenger__first_name',
        'booking_detail__passenger__last_name',
        'boarding_pass',
        'booking_detail__schedule__flight__flight_number',
    ]
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
        total_checkins = self.get_queryset().count()
        today = timezone.now().date()
        todays_checkins = self.get_queryset().filter(check_in_time__date=today).count()
        
        status_stats = self.get_queryset().values('status').annotate(count=Count('id'))
        
        return Response({
            'total_checkins': total_checkins,
            'todays_checkins': todays_checkins,
            'status_stats': {stat['status']: stat['count'] for stat in status_stats},
        })
    
    @action(detail=True, methods=['post'])
    def print_boarding_pass(self, request, pk=None):
        checkin = self.get_object()
        if not checkin.boarding_pass:
            checkin.boarding_pass = f"BP-{checkin.id}-{timezone.now().strftime('%Y%m%d%H%M')}"
            checkin.save()
        
        return Response({
            'message': 'Boarding pass ready for printing',
            'boarding_pass': checkin.boarding_pass,
            'passenger_name': checkin.passenger_name,
            'flight_number': checkin.flight_number,
        })
    
    @action(detail=False, methods=['post'])
    def bulk_checkin(self, request):
        booking_detail_ids = request.data.get('booking_detail_ids', [])
        check_in_counter = request.data.get('check_in_counter')
        
        created_checkins = []
        for bd_id in booking_detail_ids:
            try:
                booking_detail = BookingDetail.objects.get(id=bd_id)
                checkin = CheckInDetail.objects.create(
                    booking_detail=booking_detail,
                    check_in_counter=check_in_counter,
                    status='checked-in'
                )
                created_checkins.append(checkin.id)
            except Exception:
                continue
                
        return Response({'success': len(created_checkins), 'created_checkins': created_checkins})
    
    @action(detail=False, methods=['get'])
    def pending_bookings(self, request):
        pending = BookingDetail.objects.filter(
            status='confirmed',
            checkins__isnull=True
        ).select_related('passenger', 'schedule__flight')
        
        data = [{
            'id': b.id,
            'passenger_name': b.passenger.get_full_name() if b.passenger else 'Guest',
            'flight_number': b.schedule.flight.flight_number if b.schedule and b.schedule.flight else 'N/A',
        } for b in pending]
        
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        checkin = self.get_object()
        new_status = request.data.get('status')
        if new_status:
            checkin.status = new_status
            checkin.save()
            return Response({'status': 'updated'})
        return Response({'error': 'status required'}, status=400)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="checkins.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Passenger', 'Flight', 'Status'])
        for c in self.get_queryset():
            writer.writerow([c.id, c.passenger_name, c.flight_number, c.status])
        return response
