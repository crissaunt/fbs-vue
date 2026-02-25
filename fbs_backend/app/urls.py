from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api.admin_auth_views import AdminLoginView
from .api.asset_views import (
    AirlineTaxViewSet, AirlineViewSet, AirportViewSet, 
    AircraftViewSet, SeatClassViewSet, AddOnTypeViewSet,
    TaxTypeViewSet, AirportFeeViewSet, PassengerTypeTaxRateViewSet
)
from .api.booking_views import (
    BookingDetailViewSet, BookingTaxViewSet, BookingViewSet, PaymentViewSet
)
from .api.checkin_views import CheckInDetailViewSet
from .api.dashboard_views import DashboardViewSet
from .api.passenger_views import PassengerInfoViewSet
from .api.flight_views import (
    RouteViewSet, FlightViewSet, ScheduleViewSet, 
    SeatViewSet, SeatRequirementViewSet
)
from .api.student_views import StudentsViewSet
from .api.instructor_views import InstructorsViewSet
from .api.extra_services_views import (
    CountryViewSet, SeatClassFeatureViewSet, InsuranceProviderViewSet,
    InsuranceBenefitViewSet, InsuranceCoverageTypeViewSet, TravelInsurancePlanViewSet,
    PlanCoverageViewSet, MealCategoryViewSet, MealOptionViewSet,
    AssistanceServiceViewSet, BaggageOptionViewSet, PricingConfigurationViewSet
)

# Create a router and register our viewsets
router = DefaultRouter()

# DASHBOARD
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

# USERS
router.register(r'students', StudentsViewSet, basename='student')
router.register(r'instructors', InstructorsViewSet, basename='instructor')

# MANAGE FLIGHT
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'flights', FlightViewSet, basename='flight')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'seats', SeatViewSet, basename='seat')
router.register(r'seat-requirements', SeatRequirementViewSet, basename='seatrequirement')

# ASSETS
router.register(r'airlines', AirlineViewSet, basename='airline')
router.register(r'airports', AirportViewSet, basename='airport')
router.register(r'aircraft', AircraftViewSet, basename='aircraft')
router.register(r'seat-classes', SeatClassViewSet, basename='seatclass')
router.register(r'add-ons', AddOnTypeViewSet, basename='addon')

# BOOKING & PASSENGER
router.register(r'booking-details', BookingDetailViewSet, basename='bookingdetail')
router.register(r'passengers', PassengerInfoViewSet, basename='passenger')
router.register(r'checkins', CheckInDetailViewSet, basename='checkin')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')

# TAX & FEES
router.register(r'airport-fees', AirportFeeViewSet, basename='airportfee')
router.register(r'tax-types', TaxTypeViewSet, basename='taxtype')
router.register(r'airline-taxes', AirlineTaxViewSet, basename='airlinetax')
router.register(r'passenger-tax-rates', PassengerTypeTaxRateViewSet, basename='passengertaxrate')
router.register(r'booking-taxes', BookingTaxViewSet, basename='bookingtax')

# EXTRA SERVICES & CONFIG
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'seat-class-features', SeatClassFeatureViewSet, basename='seatclassfeature')
router.register(r'insurance-providers', InsuranceProviderViewSet, basename='insuranceprovider')
router.register(r'insurance-benefits', InsuranceBenefitViewSet, basename='insurancebenefit')
router.register(r'insurance-coverage-types', InsuranceCoverageTypeViewSet, basename='insurancecoveragetype')
router.register(r'insurance-plans', TravelInsurancePlanViewSet, basename='insuranceplan')
router.register(r'plan-coverages', PlanCoverageViewSet, basename='plancoverage')
router.register(r'meal-categories', MealCategoryViewSet, basename='mealcategory')
router.register(r'meal-options', MealOptionViewSet, basename='mealoption')
router.register(r'assistance-services', AssistanceServiceViewSet, basename='assistanceservice')
router.register(r'baggage-options', BaggageOptionViewSet, basename='baggageoption')
router.register(r'pricing-config', PricingConfigurationViewSet, basename='pricingconfig')

urlpatterns = [
    # Manual path for login
    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),
    
    # Include all the router-generated CRUD URLs
    path('', include(router.urls)),
]