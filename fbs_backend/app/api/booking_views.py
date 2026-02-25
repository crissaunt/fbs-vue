from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
import random
from ..models import Booking, BookingDetail, BookingTax, Payment
from ..serializers import BookingSerializer, BookingDetailSerializer, BookingTaxSerializer, PaymentSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]

class BookingDetailViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing booking details (for check-ins).
    """
    queryset = BookingDetail.objects.all()
    serializer_class = BookingDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'passenger', 
            'schedule', 
            'schedule__flight',
            'schedule__flight__route',
            'seat'
        )
        
        flight_number = self.request.query_params.get('flight')
        if flight_number:
            queryset = queryset.filter(schedule__flight__flight_number=flight_number)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        date_filter = self.request.query_params.get('date')
        if date_filter:
            queryset = queryset.filter(schedule__departure_time__date=date_filter)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(passenger__first_name__icontains=search) |
                Q(passenger__last_name__icontains=search) |
                Q(schedule__flight__flight_number__icontains=search)
            )
        
        return queryset.order_by('id')

    @action(detail=False, methods=['get'])
    def today_checkins(self, request):
        today = timezone.now().date()
        checkins = self.get_queryset().filter(
            schedule__departure_time__date=today,
            status__in=['checkin', 'boarding']
        )
        
        serializer = self.get_serializer(checkins, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        booking_detail = self.get_object()
        
        if booking_detail.status in ['checkin', 'boarding', 'completed']:
            return Response(
                {'error': 'Passenger already checked in or boarded.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking_detail.status = 'checkin'
        booking_detail.save()
        
        boarding_pass = f"{booking_detail.schedule.flight.flight_number}-{booking_detail.id}-{random.randint(1000, 9999)}"
        
        return Response({
            'success': True,
            'message': 'Passenger checked in successfully.',
            'boarding_pass': boarding_pass,
            'seat': booking_detail.seat.seat_number if booking_detail.seat else None
        })

    @action(detail=True, methods=['post'])
    def update_baggage(self, request, pk=None):
        booking_detail = self.get_object()
        
        baggage_count = request.data.get('baggage_count', 0)
        baggage_weight = request.data.get('baggage_weight', 0.0)
        
        return Response({
            'success': True,
            'message': 'Baggage information updated.',
            'baggage_count': baggage_count,
            'baggage_weight': baggage_weight
        })

class BookingTaxViewSet(viewsets.ModelViewSet):
    queryset = BookingTax.objects.all()
    serializer_class = BookingTaxSerializer
    permission_classes = [AllowAny]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().order_by('-payment_date')
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]
