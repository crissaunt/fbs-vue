from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from ..models import (
    Country, SeatClassFeature, InsuranceProvider, InsuranceBenefit,
    InsuranceCoverageType, TravelInsurancePlan, PlanCoverage,
    MealCategory, MealOption, AssistanceService, BaggageOption, PricingConfiguration
)
from ..serializers import (
    CountrySerializer, SeatClassFeatureSerializer,
    InsuranceProviderSerializer, InsuranceBenefitSerializer, InsuranceCoverageTypeSerializer,
    TravelInsurancePlanSerializer, PlanCoverageSerializer,
    MealCategorySerializer, MealOptionSerializer, AssistanceServiceSerializer,
    BaggageOptionSerializer, PricingConfigurationSerializer
)

# ==========================================
# COUNTRY
# ==========================================
class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all().order_by('name')
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]
    pagination_class = None


# ==========================================
# SEAT CLASS FEATURE
# ==========================================
class SeatClassFeatureViewSet(viewsets.ModelViewSet):
    serializer_class = SeatClassFeatureSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = SeatClassFeature.objects.all().select_related('seat_class').order_by('seat_class', 'display_order')
        sc = self.request.query_params.get('seat_class')
        if sc:
            qs = qs.filter(seat_class_id=sc)
        return qs


# ==========================================
# INSURANCE
# ==========================================
class InsuranceProviderViewSet(viewsets.ModelViewSet):
    queryset = InsuranceProvider.objects.all().order_by('name')
    serializer_class = InsuranceProviderSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class InsuranceBenefitViewSet(viewsets.ModelViewSet):
    queryset = InsuranceBenefit.objects.all().order_by('display_order', 'name')
    serializer_class = InsuranceBenefitSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class InsuranceCoverageTypeViewSet(viewsets.ModelViewSet):
    queryset = InsuranceCoverageType.objects.all().order_by('display_order', 'name')
    serializer_class = InsuranceCoverageTypeSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class TravelInsurancePlanViewSet(viewsets.ModelViewSet):
    queryset = TravelInsurancePlan.objects.all().select_related('provider').order_by('display_order')
    serializer_class = TravelInsurancePlanSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class PlanCoverageViewSet(viewsets.ModelViewSet):
    serializer_class = PlanCoverageSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = PlanCoverage.objects.all().select_related('insurance_plan', 'coverage_type')
        plan = self.request.query_params.get('insurance_plan')
        if plan:
            qs = qs.filter(insurance_plan_id=plan)
        return qs


# ==========================================
# MEALS
# ==========================================
class MealCategoryViewSet(viewsets.ModelViewSet):
    queryset = MealCategory.objects.all().order_by('display_order', 'name')
    serializer_class = MealCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None

class MealOptionViewSet(viewsets.ModelViewSet):
    serializer_class = MealOptionSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = MealOption.objects.all().select_related('airline').order_by('display_order')
        airline = self.request.query_params.get('airline')
        if airline:
            qs = qs.filter(airline_id=airline)
        return qs


# ==========================================
# ASSISTANCE
# ==========================================
class AssistanceServiceViewSet(viewsets.ModelViewSet):
    serializer_class = AssistanceServiceSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = AssistanceService.objects.all().select_related('airline').order_by('display_order')
        airline = self.request.query_params.get('airline')
        if airline:
            qs = qs.filter(airline_id=airline)
        return qs


# ==========================================
# BAGGAGE
# ==========================================
class BaggageOptionViewSet(viewsets.ModelViewSet):
    serializer_class = BaggageOptionSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = BaggageOption.objects.all().select_related('airline').order_by('display_order')
        airline = self.request.query_params.get('airline')
        if airline:
            qs = qs.filter(airline_id=airline)
        return qs


# ==========================================
# PRICING CONFIGURATION
# ==========================================
class PricingConfigurationViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = PricingConfigurationSerializer
    pagination_class = None

    def get_queryset(self):
        return PricingConfiguration.objects.all()

    def update(self, request, *args, **kwargs):
        # Always update the singleton
        config = PricingConfiguration.load()
        serializer = self.get_serializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
