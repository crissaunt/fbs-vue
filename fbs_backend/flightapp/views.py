# flightapp/views.py
from rest_framework import viewsets, generics, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q, F, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import transaction

from app.models import (
    Airport, Route, Flight, Schedule, Seat, Country,
    SeatClass, PassengerInfo, Airline,  # Make sure Airline is imported
    MealOption, BaggageOption, AssistanceService  # Import these too
)

from .serializers import *

class AirlineFilterMixin:
    """Mixin to handle common airline filtering logic by ID or Code"""
    def get_queryset(self):
        # Call parent's get_queryset if it exists
        queryset = super().get_queryset() if hasattr(super(), 'get_queryset') else self.queryset
        airline_param = self.request.query_params.get('airline')
        
        if airline_param:
            if airline_param.isdigit():
                # If it's a number, filter by the numeric ID
                return queryset.filter(airline_id=airline_param)
            else:
                # If it's letters (like '5J'), filter by the airline's code field
                # CORRECTED: Use 'airline__code' not 'airline__airline_code'
                return queryset.filter(airline__code=airline_param)
        
        return queryset

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only viewset that provides 'list' and 'retrieve' actions.
    """
    permission_classes = [permissions.AllowAny]
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class AirportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only viewset for Airports.
    """
    permission_classes = [permissions.AllowAny]
    queryset = Airport.objects.all().select_related('country')
    serializer_class = AirportSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'city', 'code', 'country__name']

class ScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.none()
    permission_classes = [permissions.AllowAny]    
    
    def get_queryset(self):
        # select_related joins the tables so we don't hit the DB 100 times
        queryset = Schedule.objects.filter(status='Open').select_related(
            'flight__airline', 
            'flight__route__origin_airport', 
            'flight__route__destination_airport'
        )
        
        origin = self.request.query_params.get('origin')
        destination = self.request.query_params.get('destination')
        date = self.request.query_params.get('departure')

        if origin:
            queryset = queryset.filter(flight__route__origin_airport__code=origin)
        if destination:
            queryset = queryset.filter(flight__route__destination_airport__code=destination)
        if date:
            try:
                # Ensures that even if a full ISO string is sent, we only filter by date
                clean_date = date.split('T')[0] 
                queryset = queryset.filter(departure_time__date=clean_date)
            except Exception:
                pass

        return queryset

class SeatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows seats to be viewed based on a schedule.
    """
    serializer_class = SeatSerializer
    queryset = Seat.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Seat.objects.all().select_related('seat_class')
        schedule_id = self.request.query_params.get('schedule')
        
        if schedule_id:
            queryset = queryset.filter(schedule_id=schedule_id)
        
        # We order by seat_number to help the frontend 
        # render rows correctly (e.g., 1A, 1B, 1C...)
        return queryset.order_by('seat_number')

class MealOptionViewSet(AirlineFilterMixin, viewsets.ReadOnlyModelViewSet):
    # REMOVE any model field definitions here - ViewSets don't have model fields
    queryset = MealOption.objects.all()
    serializer_class = MealOptionSerializer
    permission_classes = [permissions.AllowAny]

class AssistanceServiceViewSet(AirlineFilterMixin, viewsets.ReadOnlyModelViewSet):
    queryset = AssistanceService.objects.all()
    serializer_class = AssistanceServiceSerializer
    permission_classes = [permissions.AllowAny]

class BaggageOptionViewSet(AirlineFilterMixin, viewsets.ReadOnlyModelViewSet):
    queryset = BaggageOption.objects.all()
    serializer_class = BaggageOptionSerializer
    permission_classes = [permissions.AllowAny]