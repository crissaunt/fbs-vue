from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count, Sum, Avg
from ..models import PassengerInfo, Booking, BookingDetail, Schedule

class DashboardViewSet(viewsets.ViewSet):
    """
    API endpoint for dashboard statistics
    """
    permission_classes = [AllowAny]
    
    def list(self, request):
        """Default list action - returns available dashboard endpoints"""
        return Response({
            'endpoints': [
                'stats',
                'revenue_breakdown',
                'ticket_sales',
                'recent_bookings',
                'alerts',
                'passenger_composition',
                'popular_routes',
                'active_flights_map',
                'flight_operations_stats',
                'aircraft_utilization',
                'revenue_by_route'
            ]
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        try:
            today = timezone.now().date()
            yesterday = today - timedelta(days=1)
            last_month = today - timedelta(days=30)
            
            passengers_today = PassengerInfo.objects.filter(bookingdetail__booking_date__date=today).distinct().count()
            passengers_yesterday = PassengerInfo.objects.filter(bookingdetail__booking_date__date=yesterday).distinct().count()
            
            passenger_growth = 0
            if passengers_yesterday > 0:
                passenger_growth = round(((passengers_today - passengers_yesterday) / passengers_yesterday) * 100, 1)
            
            total_revenue = Booking.objects.filter(status='Completed').aggregate(total=Sum('total_amount'))['total'] or 0
            last_month_revenue = Booking.objects.filter(status='Completed', created_at__gte=last_month).aggregate(total=Sum('total_amount'))['total'] or 0
            
            previous_month_start = last_month - timedelta(days=30)
            previous_month_revenue = Booking.objects.filter(status='Completed', created_at__gte=previous_month_start, created_at__lt=last_month).aggregate(total=Sum('total_amount'))['total'] or 0
            
            revenue_growth = 0
            if previous_month_revenue and previous_month_revenue > 0:
                revenue_growth = round(((last_month_revenue - previous_month_revenue) / previous_month_revenue) * 100, 1)
            
            total_bookings = Booking.objects.count()
            pending_bookings = Booking.objects.filter(status='Pending').count()
            
            now = timezone.now()
            active_flights = Schedule.objects.filter(departure_time__lte=now, arrival_time__gte=now).count()
            scheduled_flights = Schedule.objects.filter(departure_time__date=today).count()
            
            return Response({
                'passengersToday': passengers_today,
                'passengerGrowth': passenger_growth,
                'totalRevenue': float(total_revenue) if total_revenue else 0.0,
                'revenueGrowth': revenue_growth,
                'totalBookings': total_bookings,
                'pendingBookings': pending_bookings,
                'activeFlights': active_flights,
                'scheduledFlights': scheduled_flights
            })
        except Exception as e:
            return Response({
                'passengersToday': 0, 'passengerGrowth': 0, 'totalRevenue': 0.0,
                'revenueGrowth': 0, 'totalBookings': 0, 'pendingBookings': 0,
                'activeFlights': 0, 'scheduledFlights': 0, 'error': str(e)
            }, status=200)

    @action(detail=False, methods=['get'])
    def revenue_breakdown(self, request):
        try:
            completed_bookings = Booking.objects.filter(status='Completed')
            total = completed_bookings.aggregate(sum=Sum('total_amount'))['sum'] or 0
            tickets = completed_bookings.aggregate(sum=Sum('base_fare_total'))['sum'] or 0
            addons = completed_bookings.aggregate(sum=Sum('insurance_total'))['sum'] or 0
            taxes = completed_bookings.aggregate(sum=Sum('tax_total'))['sum'] or 0
            
            return Response({
                'total': float(total),
                'breakdown': {'tickets': float(tickets), 'addons': float(addons), 'taxes': float(taxes)}
            })
        except Exception as e:
            return Response({'total': 0.0, 'breakdown': {'tickets': 0.0, 'addons': 0.0, 'taxes': 0.0}}, status=200)

    @action(detail=False, methods=['get'])
    def ticket_sales(self, request):
        try:
            days = int(request.query_params.get('days', 7))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days-1)
            sales_data = []
            labels = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                count = BookingDetail.objects.filter(booking_date__date=date).count()
                sales_data.append(count)
                labels.append(date.strftime('%a') if days <= 7 else date.strftime('%d %b'))
            return Response({'labels': labels, 'data': sales_data})
        except Exception as e:
            return Response({'labels': [], 'data': []}, status=200)

    @action(detail=False, methods=['get'])
    def recent_bookings(self, request):
        try:
            limit = int(request.query_params.get('limit', 5))
            bookings = Booking.objects.select_related('user').order_by('-created_at')[:limit]
            data = []
            for b in bookings:
                data.append({
                    'id': b.id, 'passenger': b.user.get_full_name() if b.user else 'Guest',
                    'date': b.created_at.isoformat() if b.created_at else None,
                    'amount': float(b.total_amount) if b.total_amount else 0.0,
                    'status': b.status or 'Unknown'
                })
            return Response(data)
        except Exception as e:
            return Response([], status=200)

    @action(detail=False, methods=['get'])
    def popular_routes(self, request):
        try:
            routes = Schedule.objects.values('flight__route__origin_airport__code', 'flight__route__destination_airport__code').annotate(
                bookings_count=Count('bookingdetail', filter=Q(bookingdetail__status__in=['confirmed', 'checkin', 'boarding', 'completed']))
            ).order_by('-bookings_count')[:5]
            labels = [f"{r['flight__route__origin_airport__code']} → {r['flight__route__destination_airport__code']}" for r in routes]
            data = [r['bookings_count'] for r in routes]
            return Response({'labels': labels, 'data': data})
        except Exception as e:
            return Response({'labels': [], 'data': []}, status=200)
    
    # ... Other actions can be moved here similarly if needed
