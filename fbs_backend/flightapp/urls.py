from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'airports', AirportViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'seats', SeatViewSet)
router.register(r'meal-options', MealOptionViewSet)
router.register(r'assistance-services', AssistanceServiceViewSet)
router.register(r'baggage-options', BaggageOptionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]