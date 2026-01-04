# flightapp/serializers.py
from rest_framework import serializers
from django.db.models import Q
from datetime import datetime, timedelta
from app.models import (
    Country, Airline, SeatClass, Aircraft, Airport,
    Route, Flight, Schedule, Seat, PassengerInfo,
    Booking, BookingDetail, AddOnType, AddOn,
    InsuranceProvider, InsuranceCoverageType, InsuranceBenefit,
    TravelInsurancePlan, PlanCoverage, BookingInsuranceRecord,
    TaxType, AirlineTax, AirportFee, PassengerTypeTaxRate, MealCategory,
    MealOption, AssistanceService, BaggageOption,

)



class CountrySerializer(serializers.ModelSerializer):
    """Serializer to handle Country details inside Airport responses."""
    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'currency']

class AirportSerializer(serializers.ModelSerializer):
    # Nested country details (read-only)
    country_details = CountrySerializer(source='country', read_only=True)
    
    # Adding the properties from your model as fields
    is_international = serializers.ReadOnlyField()
    is_domestic = serializers.ReadOnlyField()
    is_philippine_airport = serializers.ReadOnlyField()
    
    # Display the human-readable version of the choice field
    airport_type_display = serializers.CharField(
        source='get_airport_type_display', 
        read_only=True
    )

    class Meta:
        model = Airport
        fields = [
            'id', 
            'name', 
            'code', 
            'city', 
            'location', 
            'airport_type', 
            'airport_type_display',
            'country',         # Used for POST/PUT (expects the ID)
            'country_details', # Used for GET (provides the object)
            'is_international',
            'is_domestic',
            'is_philippine_airport'
        ]
        # We keep 'country' writeable for creation, but 'country_details' for display
        extra_kwargs = {
            'country': {'write_only': True}
        }


class ScheduleSerializer(serializers.ModelSerializer):
    # These "source" fields reach through the Foreign Keys
    airline_name = serializers.ReadOnlyField(source='flight.airline.name')
    airline_code = serializers.ReadOnlyField(source='flight.airline.code')
    flight_number = serializers.ReadOnlyField(source='flight.flight_number')
    
    # Route info
    origin = serializers.ReadOnlyField(source='flight.route.origin_airport.code')
    origin_city = serializers.ReadOnlyField(source='flight.route.origin_airport.city')
    destination = serializers.ReadOnlyField(source='flight.route.destination_airport.code')
    destination_city = serializers.ReadOnlyField(source='flight.route.destination_airport.city')
    
    # Helper method for duration (calls the model method)
    flight_duration = serializers.ReadOnlyField(source='duration')

    class Meta:
        model = Schedule
        fields = [
            'id', 'flight_number', 'airline_name', 'airline_code',
            'origin', 'origin_city', 'destination', 'destination_city',
            'departure_time', 'arrival_time', 'price', 'status', 
            'flight_duration'
        ] 


class SeatClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatClass
        fields = ['id', 'name', 'price_multiplier', 'description']

class SeatSerializer(serializers.ModelSerializer):
    # Include the calculated price and features from the model @properties
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    seat_class_name = serializers.CharField(source='seat_class.name', read_only=True)
    class Meta:
        model = Seat
        fields = [
            'id', 'seat_number', 'row', 'column', 'is_available', 
            'price_adjustment', 'final_price', 'seat_class', 
            'seat_class_name', 'is_window', 'is_aisle', 'has_extra_legroom'
        ]


class MealOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealOption
        fields = [
            'id', 'name', 'description', 'meal_type', 'price', 
            'is_included', 'dietary_info', 'image_url', 'is_free'
        ]

class AssistanceServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistanceService
        fields = [
            'id', 'name', 'service_type', 'level', 'description', 
            'price', 'is_included', 'advance_notice_text', 'is_free'
        ]

class BaggageOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaggageOption
        fields = [
            'id', 'name', 'weight_kg', 'formatted_weight', 
            'price', 'is_included', 'is_free'
        ]