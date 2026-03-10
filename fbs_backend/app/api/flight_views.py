from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Route, Flight, Schedule, Seat, SeatRequirement, SeatClass
from ..serializers import (
    RouteSerializer, FlightSerializer, ScheduleSerializer, 
    SeatSerializer, SeatRequirementSerializer
)

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class SeatRequirementViewSet(viewsets.ModelViewSet):
    queryset = SeatRequirement.objects.all()
    serializer_class = SeatRequirementSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all().select_related(
        'flight', 'flight__airline', 'flight__aircraft', 
        'flight__route', 'flight__route__origin_airport', 
        'flight__route__destination_airport'
    ).order_by('-departure_time')
    serializer_class = ScheduleSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    @action(detail=False, methods=['get'])
    def stats(self, request):
        now = timezone.now()
        today = now.date()
        active = Schedule.objects.filter(departure_time__lte=now, arrival_time__gte=now).count()
        scheduled_today = Schedule.objects.filter(departure_time__date=today).count()
        return Response({'active': active, 'scheduled': scheduled_today})

    @action(detail=True, methods=['post'], url_path='generate-seats')
    def generate_seats(self, request, pk=None):
        schedule = self.get_object()
        config_data = request.data.get('layout_config', {})
        seat_classes = config_data.get('seat_classes', [])
        
        if not seat_classes:
            return Response({'error': 'layout_config.seat_classes is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            with transaction.atomic():
                existing_seats = Seat.objects.filter(schedule=schedule)
                existing_map = {f"{s.row}-{s.column}": s for s in existing_seats}
                processed_seat_ids = []
                
                for sc_config in seat_classes:
                    class_id = sc_config.get('class_id')
                    rows = sc_config.get('rows', 0)
                    columns = sc_config.get('columns', 0)
                    start_row = sc_config.get('start_row', 1)
                    
                    try:
                        seat_class = SeatClass.objects.get(id=class_id)
                    except SeatClass.DoesNotExist:
                        continue
                        
                    for r in range(rows):
                        row_num = start_row + r
                        for c in range(columns):
                            col_label = chr(64 + c + 1)
                            seat_key = f"{row_num}-{col_label}"
                            
                            seat_data = {
                                'schedule': schedule,
                                'seat_class': seat_class,
                                'seat_number': f"{row_num}{col_label}",
                                'row': row_num,
                                'column': col_label,
                                'is_available': True
                            }
                            
                            if seat_key in existing_map:
                                seat = existing_map[seat_key]
                                seat.seat_class = seat_class
                                seat.save()
                                processed_seat_ids.append(seat.id)
                            else:
                                seat = Seat.objects.create(**seat_data)
                                processed_seat_ids.append(seat.id)
                
                Seat.objects.filter(schedule=schedule).exclude(id__in=processed_seat_ids).delete()
                return Response({'success': True, 'message': 'Seats generated successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['schedule', 'seat_class']

    @action(detail=True, methods=['post'], url_path='lock')
    def lock_seat(self, request, pk=None):
        """Temporarily lock a seat for a session to prevent double booking"""
        seat = self.get_object()
        session_id = request.data.get('session_id')
        duration_minutes = int(request.data.get('duration', 10))

        if not session_id:
            return Response({'error': 'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Refresh and lock the row for update
            seat = Seat.objects.select_for_update().get(id=seat.id)
            
            # 1. Check if permanently booked
            is_permanently_booked = BookingDetail.objects.filter(
                seat=seat,
                status__in=['pending', 'confirmed', 'checkin', 'boarding', 'completed']
            ).exists()
            
            if is_permanently_booked:
                return Response({'error': 'Seat is already booked'}, status=status.HTTP_409_CONFLICT)
            
            # 2. Check if locked by SOMEONE ELSE
            if seat.is_locked and seat.locked_by_session != session_id:
                return Response({'error': 'Seat is currently locked by another user'}, status=status.HTTP_423_LOCKED)
            
            # 3. Apply/Extend the lock
            seat.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
            seat.locked_by_session = session_id
            seat.save()
            
            return Response({
                'success': True, 
                'seat_number': seat.seat_number,
                'locked_until': seat.locked_until
            })

    @action(detail=False, methods=['post'], url_path='bulk-reset')
    def bulk_reset(self, request):
        schedule_id = request.data.get('schedule_id')
        if not schedule_id:
            return Response({"error": "Schedule ID is required"}, status=400)
        updated_count = Seat.objects.filter(schedule_id=schedule_id).update(is_available=True)
        return Response({"message": f"Successfully reset {updated_count} seats.", "count": updated_count})

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        seats_data = request.data.get('seats', [])
        if not isinstance(seats_data, list):
            return Response({"error": "Seats must be a list"}, status=status.HTTP_400_BAD_REQUEST)
        
        created_count = 0
        for seat_data in seats_data:
            serializer = self.get_serializer(data=seat_data)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
        return Response({'success': True, 'created_count': created_count})
