from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Route, Flight, Schedule, Seat, SeatRequirement, SeatClass
from ..serializers import RouteSerializer, FlightSerializer, ScheduleSerializer, SeatSerializer, SeatRequirementSerializer

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [AllowAny]

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [AllowAny]

class SeatRequirementViewSet(viewsets.ModelViewSet):
    queryset = SeatRequirement.objects.all()
    serializer_class = SeatRequirementSerializer
    permission_classes = [AllowAny]

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        now = timezone.now()
        today = now.date()
        
        active = Schedule.objects.filter(
            departure_time__lte=now,
            arrival_time__gte=now
        ).count()
        
        scheduled_today = Schedule.objects.filter(
            departure_time__date=today
        ).count()
        
        upcoming = Schedule.objects.filter(
            departure_time__gte=now,
            departure_time__date=today
        ).count()
        
        return Response({
            'active': active,
            'scheduled': scheduled_today,
            'upcoming': upcoming
        })

    @action(detail=True, methods=['post'], url_path='generate-seats')
    def generate_seats(self, request, pk=None):
        """Generate seats for this schedule based on layout config"""
        schedule = self.get_object()
        
        config_data = request.data.get('layout_config', {})
        seat_classes_config = config_data.get('seat_classes', [])
        
        if not seat_classes_config:
            return Response(
                {'error': 'layout_config.seat_classes is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            with transaction.atomic():
                existing_seats = Seat.objects.filter(schedule=schedule)
                existing_map = {f"{s.row}-{s.column}": s for s in existing_seats}
                
                created_count = 0
                updated_count = 0
                processed_seat_ids = []
                
                for sc_config in seat_classes_config:
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
                            col_num = c + 1
                            col_label = chr(64 + col_num) # 1=A, 2=B, etc.
                            
                            seat_key = f"{row_num}-{col_label}"
                            
                            is_window = (col_num == 1 or col_num == columns)
                            is_aisle = False
                            
                            if columns == 6:
                                is_aisle = (col_num == 3 or col_num == 4)
                            elif columns == 4:
                                is_aisle = (col_num == 2 or col_num == 3)
                                
                            seat_data = {
                                'schedule': schedule,
                                'seat_class': seat_class,
                                'seat_number': f"{row_num}{col_label}",
                                'row': row_num,
                                'column': col_label,
                                'is_window': is_window,
                                'is_aisle': is_aisle,
                                'is_available': True
                            }
                            
                            if seat_key in existing_map:
                                seat = existing_map[seat_key]
                                processed_seat_ids.append(seat.id)
                                if seat.seat_class_id != class_id:
                                    seat.seat_class = seat_class
                                    seat.save()
                                    updated_count += 1
                            else:
                                seat = Seat.objects.create(**seat_data)
                                created_count += 1
                                processed_seat_ids.append(seat.id)

                seats_to_delete = Seat.objects.filter(schedule=schedule).exclude(id__in=processed_seat_ids)
                deleted_count = seats_to_delete.count()
                seats_to_delete.delete()

                return Response({
                    'success': True,
                    'message': f'Generated {created_count} new seats, updated {updated_count} seats, deleted {deleted_count} obsolete seats',
                    'created': created_count,
                    'updated': updated_count,
                    'deleted': deleted_count
                })
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['schedule', 'seat_class']

    @action(detail=False, methods=['post'], url_path='bulk-reset')
    def bulk_reset(self, request):
        schedule_id = request.data.get('schedule_id')
        if not schedule_id:
            return Response({"error": "Schedule ID is required"}, status=400)
        
        updated_count = Seat.objects.filter(schedule_id=schedule_id).update(is_available=True)
        
        return Response({
            "message": f"Successfully reset {updated_count} seats to available.",
            "count": updated_count
        })

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        seats_data = request.data.get('seats', [])
        if not seats_data:
            return Response({"error": "No seats provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        created_seats = []
        errors = []
        
        for index, seat_data in enumerate(seats_data):
            try:
                serializer = self.get_serializer(data=seat_data)
                if serializer.is_valid():
                    serializer.save()
                    created_seats.append(serializer.data)
                else:
                    errors.append({'index': index, 'error': serializer.errors})
            except Exception as e:
                errors.append({'index': index, 'error': str(e)})
        
        return Response({
            'success': True,
            'created_count': len(created_seats),
            'errors': errors
        }, status=status.HTTP_201_CREATED if created_seats else status.HTTP_400_BAD_REQUEST)
