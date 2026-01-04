from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeView

router = DefaultRouter()

urlpatterns = [
    path('me/', MeView.as_view()),

]