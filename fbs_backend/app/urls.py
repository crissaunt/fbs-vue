from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Modular view imports
from .api.admin_auth_views import AdminLoginView
from .api.student_views import StudentsViewSet
from .api.instructor_views import InstructorsViewSet
from .api.booking_views import (
    BookingViewSet, BookingDetailViewSet, BookingTaxViewSet, PaymentViewSet
)
from .api.flight_views import (
    RouteViewSet, FlightViewSet, ScheduleViewSet, 
    SeatViewSet, SeatRequirementViewSet
)
from .api.asset_views import (
    AirlineViewSet, AirportViewSet, AircraftViewSet, 
    SeatClassViewSet, AddOnTypeViewSet, TaxTypeViewSet, 
    AirportFeeViewSet, AirlineTaxViewSet, PassengerTypeTaxRateViewSet
)
from .api.dashboard_views import DashboardViewSet
from .api.checkin_views import CheckInDetailViewSet
from .api.passenger_views import PassengerInfoViewSet
from .api.extra_services_views import (
    CountryViewSet, SeatClassFeatureViewSet, InsuranceProviderViewSet,
    InsuranceBenefitViewSet, InsuranceCoverageTypeViewSet,
    TravelInsurancePlanViewSet, PlanCoverageViewSet,
    MealCategoryViewSet, MealOptionViewSet, AssistanceServiceViewSet,
    BaggageOptionViewSet, PricingConfigurationViewSet
)

# Create a router and register our viewsets
router = DefaultRouter()

# ==========================================
# USERS & ROLES
# ==========================================
router.register(r'students', StudentsViewSet, basename='student')
router.register(r'instructors', InstructorsViewSet, basename='instructor')

# ==========================================
# DASHBOARD
# ==========================================
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

# ==========================================
# MANAGE FLIGHT
# ==========================================
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'flights', FlightViewSet, basename='flight')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'seats', SeatViewSet, basename='seat')
router.register(r'seat-requirements', SeatRequirementViewSet, basename='seatrequirement')

# ==========================================
# ASSETS
# ==========================================
router.register(r'airlines', AirlineViewSet, basename='airline')
router.register(r'airports', AirportViewSet, basename='airport')
router.register(r'aircraft', AircraftViewSet, basename='aircraft')
router.register(r'seat-classes', SeatClassViewSet, basename='seatclass')
router.register(r'add-ons', AddOnTypeViewSet, basename='addon')

# ==========================================
# BOOKING & PAYMENTS
# ==========================================
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'booking-details', BookingDetailViewSet, basename='bookingdetail')
router.register(r'booking-taxes', BookingTaxViewSet, basename='bookingtax')
router.register(r'payments', PaymentViewSet, basename='payment')

# ==========================================
# PASSENGER & CHECK-IN
# ==========================================
router.register(r'passengers', PassengerInfoViewSet, basename='passenger')
router.register(r'checkins', CheckInDetailViewSet, basename='checkin')

# ==========================================
# MANAGE TAX
# ==========================================
router.register(r'airport-fees', AirportFeeViewSet, basename='airportfee')
router.register(r'tax-types', TaxTypeViewSet, basename='taxtype')
router.register(r'airline-taxes', AirlineTaxViewSet, basename='airlinetax')
router.register(r'passenger-tax-rates', PassengerTypeTaxRateViewSet, basename='passengertaxrate')

# ==========================================
# NEWLY ADDED (Extra Services)
# ==========================================
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