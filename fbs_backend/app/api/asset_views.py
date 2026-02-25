from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import (
    Airline, Airport, Aircraft, SeatClass, AddOnType, 
    TaxType, AirportFee, AirlineTax, PassengerTypeTaxRate
)
from ..serializers import (
    AirlineSerializer, AirportSerializer, AircraftSerializer, 
    SeatClassSerializer, AddOnTypeSerializer, TaxTypeSerializer, 
    AirportFeeSerializer, AirlineTaxSerializer, PassengerTypeTaxRateSerializer
)

class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [AllowAny]

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [AllowAny]

class AircraftViewSet(viewsets.ModelViewSet):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'], url_path='save-layout')
    def save_layout(self, request, pk=None):
        aircraft = self.get_object()
        config_data = request.data.get('layout_config', {})
        seat_classes = config_data.get('seat_classes', [])
        
        if not seat_classes:
            return Response({'error': 'layout_config.seat_classes is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        total_seats = sum(c.get('rows', 0) * c.get('columns', 0) for c in seat_classes)
        if total_seats > aircraft.capacity:
            return Response({'error': f'Layout has {total_seats} seats but capacity is {aircraft.capacity}'}, status=status.HTTP_400_BAD_REQUEST)
        
        aircraft.save_layout({'seat_classes': seat_classes, 'total_seats': total_seats})
        return Response({'success': True, 'message': 'Layout saved', 'layout_config': aircraft.layout_config})

    @action(detail=True, methods=['get'], url_path='layout')
    def get_layout(self, request, pk=None):
        aircraft = self.get_object()
        return Response({'aircraft_id': aircraft.id, 'layout': aircraft.get_layout_config()})

class SeatClassViewSet(viewsets.ModelViewSet):
    queryset = SeatClass.objects.all()
    serializer_class = SeatClassSerializer
    permission_classes = [AllowAny]

class AddOnTypeViewSet(viewsets.ModelViewSet):
    queryset = AddOnType.objects.all()
    serializer_class = AddOnTypeSerializer
    permission_classes = [AllowAny]

class TaxTypeViewSet(viewsets.ModelViewSet):
    queryset = TaxType.objects.all()
    serializer_class = TaxTypeSerializer
    permission_classes = [AllowAny]

class AirportFeeViewSet(viewsets.ModelViewSet):
    queryset = AirportFee.objects.all()
    serializer_class = AirportFeeSerializer
    permission_classes = [AllowAny]

class AirlineTaxViewSet(viewsets.ModelViewSet):
    queryset = AirlineTax.objects.all()
    serializer_class = AirlineTaxSerializer
    permission_classes = [AllowAny]

class PassengerTypeTaxRateViewSet(viewsets.ModelViewSet):
    queryset = PassengerTypeTaxRate.objects.all()
    serializer_class = PassengerTypeTaxRateSerializer
    permission_classes = [AllowAny]
