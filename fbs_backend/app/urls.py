from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminLoginView,
    AirlineTaxViewSet, 
    AirlineViewSet, 
    AirportViewSet, 
    AircraftViewSet,
    BookingDetailViewSet,
    BookingTaxViewSet,
    BookingViewSet,
    CheckInDetailViewSet,
    DashboardViewSet,
    PassengerInfoViewSet,
    PassengerTypeTaxRateViewSet, 
    SeatClassViewSet, 
    AddOnTypeViewSet,
    RouteViewSet,
    FlightViewSet,
    ScheduleViewSet,
    SeatViewSet,
    SeatRequirementViewSet,
    AirportFeeViewSet,
    TaxTypeViewSet,
    StudentsViewSet,
    InstructorsViewSet,
    PaymentViewSet,
    # --- New ---
    CountryViewSet,
    SeatClassFeatureViewSet,
    InsuranceProviderViewSet,
    InsuranceBenefitViewSet,
    InsuranceCoverageTypeViewSet,
    TravelInsurancePlanViewSet,
    PlanCoverageViewSet,
    MealCategoryViewSet,
    MealOptionViewSet,
    AssistanceServiceViewSet,
    BaggageOptionViewSet,
    PricingConfigurationViewSet,
)

# Create a router and register our viewsets
router = DefaultRouter()

# ... (rest of the router registrations)
router.register(r'seat-requirements', SeatRequirementViewSet, basename='seatrequirement')
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
# ==========================================
# ASSETS
# ==========================================
router.register(r'airlines', AirlineViewSet, basename='airline')
router.register(r'airports', AirportViewSet, basename='airport')
router.register(r'aircraft', AircraftViewSet, basename='aircraft')
router.register(r'seat-classes', SeatClassViewSet, basename='seatclass')
router.register(r'add-ons', AddOnTypeViewSet, basename='addon')

# ==========================================
# BOOKING
# ==========================================
router.register(r'booking-details', BookingDetailViewSet, basename='bookingdetail')

# ==========================================
# PASSENGER
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
router.register(r'booking-taxes', BookingTaxViewSet, basename='bookingtax')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')

# ==========================================
# NEWLY ADDED
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