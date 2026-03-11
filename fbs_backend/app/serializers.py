from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    AirlineTax, AirportFee, Booking, BookingDetail, BookingTax, CheckInDetail,
    PassengerInfo, Students, PassengerTypeTaxRate, Route, Airline, SeatClass,
    Aircraft, Airport, AddOnType, Flight, Schedule, Seat, TaxType, TrackLog,
    SeatRequirement, Payment, Country, SeatClassFeature,
    InsuranceProvider, InsuranceBenefit, InsuranceCoverageType, TravelInsurancePlan,
    PlanCoverage, MealCategory, MealOption, AssistanceService, BaggageOption,
    PricingConfiguration, FareBundle, FareBundleFeature
)
from fbs_instructor.models import Instructor

# ==========================================
# USER SERIALIZER
# ==========================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


# ==========================================
# STUDENT SERIALIZER
# ==========================================
class StudentsSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Students
        fields = [
            'id', 
            'student_number', 
            'first_name', 
            'last_name', 
            'mi', 
            'full_name',
            'email', 
            'phone_number', 
            'gender', 
            'date_enrolled'
        ]
        read_only_fields = ['date_enrolled']

    def get_full_name(self, obj):
        if obj.mi:
            return f"{obj.first_name} {obj.mi}. {obj.last_name}"
        return f"{obj.first_name} {obj.last_name}"


# ==========================================
# INSTRUCTOR SERIALIZER
# ==========================================
class InstructorsSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Instructor
        fields = [
            'id', 
            'instructor_id', 
            'first_name', 
            'last_name', 
            'middle_initial', 
            'full_name',
            'email', 
            'phone'
        ]

    def get_full_name(self, obj):
        parts = [obj.first_name, f"{obj.middle_initial}." if obj.middle_initial else None, obj.last_name]
        return " ".join([p for p in parts if p])

# ==========================================
# MANAGE FLIGHT
# ==========================================
class RouteSerializer(serializers.ModelSerializer):
    origin_info = serializers.StringRelatedField(source='origin_airport', read_only=True)
    destination_info = serializers.StringRelatedField(source='destination_airport', read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'origin_airport', 'destination_airport', 'origin_info', 'destination_info', 'base_price']

class FlightSerializer(serializers.ModelSerializer):
    airline_display = serializers.ReadOnlyField(source='airline.name')
    aircraft_display = serializers.ReadOnlyField(source='aircraft.model')
    route_display = serializers.ReadOnlyField(source='route.__str__')

    class Meta:
        model = Flight
        fields = ['id', 'flight_number', 'airline', 'airline_display', 
                  'aircraft', 'aircraft_display', 'route', 'route_display', 'total_stops']

class ScheduleSerializer(serializers.ModelSerializer):
    flight_number = serializers.ReadOnlyField(source='flight.flight_number')
    duration_display = serializers.ReadOnlyField(source='duration')
    aircraft_name = serializers.ReadOnlyField(source='flight.aircraft.model')
    aircraft_capacity = serializers.ReadOnlyField(source='flight.aircraft.capacity')
    flight_detail = FlightSerializer(source='flight', read_only=True)
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all(), required=True)
    status = serializers.ReadOnlyField(source='automatic_status')
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Schedule
        fields = ['id', 'flight', 'flight_number', 'flight_detail', 'aircraft_name', 'aircraft_capacity',
                  'departure_time', 'arrival_time', 'price', 'status', 'status_display', 'duration_display']

class SeatRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatRequirement
        fields = '__all__'

class SeatSerializer(serializers.ModelSerializer):
    class_name = serializers.ReadOnlyField(source='seat_class.name')
    final_price = serializers.ReadOnlyField()
    seat_code = serializers.ReadOnlyField()
    is_booked = serializers.SerializerMethodField()
    is_locked = serializers.ReadOnlyField()
    
    class Meta:
        model = Seat
        fields = '__all__'

    def get_is_booked(self, obj):
        return BookingDetail.objects.filter(seat=obj, status__in=['pending', 'confirmed', 'checkin']).exists()

# ==========================================
# ASSETS
# ==========================================
class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = ['id', 'name', 'code', 'logo']

class SeatClassSerializer(serializers.ModelSerializer):
    airline_name = serializers.ReadOnlyField(source='airline.name')
    class Meta:
        model = SeatClass
        fields = ['id', 'name', 'price_multiplier', 'airline', 'airline_name', 'description', 'is_active', 'color']

class AircraftSerializer(serializers.ModelSerializer):
    airline_name = serializers.ReadOnlyField(source='airline.name')
    class Meta:
        model = Aircraft
        fields = ['id', 'model', 'capacity', 'airline', 'airline_name', 'layout_config']

class AirportSerializer(serializers.ModelSerializer):
    country_name = serializers.ReadOnlyField(source='country.name')
    airport_type_display = serializers.CharField(source='get_airport_type_display', read_only=True)
    class Meta:
        model = Airport
        fields = ['id', 'name', 'code', 'city', 'country', 'country_name', 'location', 'airport_type', 'airport_type_display']

class AddOnTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOnType
        fields = ['id', 'name', 'description']

# ==========================================
# BOOKING MANAGEMENT
# ==========================================
class BookingDetailSerializer(serializers.ModelSerializer):
    passenger_name = serializers.ReadOnlyField(source='passenger.get_full_name')
    flight_number = serializers.ReadOnlyField(source='schedule.flight.flight_number')
    
    class Meta:
        model = BookingDetail
        fields = ['id', 'booking', 'passenger', 'passenger_name', 'schedule', 'flight_number', 'status']

class PassengerInfoSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='get_full_name')
    class Meta:
        model = PassengerInfo
        fields = ['id', 'first_name', 'last_name', 'full_name', 'passenger_type']

# ==========================================
# CHECK-IN SERIALIZERS
# ==========================================
class PassengerCheckInSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = PassengerInfo
        fields = ['id', 'first_name', 'last_name', 'full_name', 'passport_number']
    def get_full_name(self, obj):
        return obj.get_full_name()

class BookingDetailCheckInSerializer(serializers.ModelSerializer):
    passenger = PassengerCheckInSerializer()
    class Meta:
        model = BookingDetail
        fields = ['id', 'passenger', 'seat']

class CheckInDetailSerializer(serializers.ModelSerializer):
    passenger_name = serializers.ReadOnlyField()
    flight_number = serializers.ReadOnlyField()
    route = serializers.ReadOnlyField()
    departure_time = serializers.ReadOnlyField()
    seat_number = serializers.ReadOnlyField()
    status = serializers.CharField()
    
    class Meta:
        model = CheckInDetail
        fields = [
            'id', 'booking_detail', 'check_in_time', 'boarding_pass', 
            'status', 'passenger_name', 'flight_number', 'route', 
            'departure_time', 'seat_number', 'baggage_count', 'baggage_weight',
            'pwd_id_number', 'senior_id_number', 'passport_expiry'
        ]
        read_only_fields = ['boarding_pass', 'check_in_time']

    def create(self, validated_data):
        if 'status' not in validated_data:
            validated_data['status'] = 'checked-in'
        instance = super().create(validated_data)
        if not instance.boarding_pass:
            instance.generate_boarding_pass()
        return instance

class CheckInListSerializer(serializers.ModelSerializer):
    passenger_name = serializers.ReadOnlyField()
    flight_number = serializers.ReadOnlyField()
    route = serializers.ReadOnlyField()
    departure_time = serializers.ReadOnlyField()
    seat_number = serializers.ReadOnlyField()
    status = serializers.CharField()
    
    class Meta:
        model = CheckInDetail
        fields = [
            'id', 'status', 'check_in_time', 'passenger_name', 
            'flight_number', 'route', 'departure_time', 'seat_number',
            'boarding_pass', 'baggage_count', 'baggage_weight',
            'pwd_id_number', 'senior_id_number', 'passport_expiry'
        ]

# ==========================================
# OTHERS
# ==========================================
class TrackLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackLog
        fields = ['id', 'user', 'action', 'timestamp']

class TaxTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxType
        fields = '__all__'

class AirportFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirportFee
        fields = '__all__'

class AirlineTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirlineTax
        fields = '__all__'

class PassengerTypeTaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassengerTypeTaxRate
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Booking
        fields = ['id', 'user', 'user_name', 'trip_type', 'status', 'created_at', 'total_amount']

class BookingTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingTax
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class SeatClassFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatClassFeature
        fields = '__all__'

class InsuranceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceProvider
        fields = '__all__'

class InsuranceBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceBenefit
        fields = '__all__'

class InsuranceCoverageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCoverageType
        fields = '__all__'

class TravelInsurancePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelInsurancePlan
        fields = '__all__'

class PlanCoverageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanCoverage
        fields = '__all__'

class MealCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MealCategory
        fields = '__all__'

class MealOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealOption
        fields = '__all__'

class AssistanceServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistanceService
        fields = '__all__'

class BaggageOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaggageOption
        fields = '__all__'

class PricingConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingConfiguration
        fields = '__all__'
