from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from app.models import Schedule, BookingDetail
from decimal import Decimal

@api_view(['GET'])
@permission_classes([AllowAny])
def get_dcs_flights(request):
    """Get upcoming flights for the DCS Dashboard"""
    # Show flights from 1 hour ago through the future (to handle flights currently in boarding)
    schedules = Schedule.objects.filter(
        departure_time__gte=timezone.now() - timezone.timedelta(hours=1)
    ).select_related('flight__route__origin_airport', 'flight__route__destination_airport').order_by('departure_time')[:20]
    
    data = []
    for sched in schedules:
        airline = sched.flight.airline if sched.flight else None
        data.append({
            'id': sched.id,
            'flight_number': sched.flight.flight_number if sched.flight else 'N/A',
            'airline_name': airline.name if airline else 'Unknown',
            'airline_logo': airline.logo.url if airline and airline.logo else None,
            'airline_code': airline.code if airline else 'N/A',
            'origin': sched.flight.route.origin_airport.code if sched.flight and sched.flight.route else 'N/A',
            'destination': sched.flight.route.destination_airport.code if sched.flight and sched.flight.route else 'N/A',
            'departure_time': sched.departure_time,
            'arrival_time': sched.arrival_time,
            'gate': getattr(sched, 'gate', 'TBA'),
            'status': sched.status,
            'booked_count': BookingDetail.objects.filter(schedule=sched).count(),
            'total_seats': sched.seats.count() or 1, # Avoid div by zero
        })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_dcs_manifest(request, schedule_id):
    """Get passenger manifest for a specific flight"""
    try:
        schedule = Schedule.objects.get(id=schedule_id)
    except Schedule.DoesNotExist:
        return Response({'error': 'Flight not found'}, status=status.HTTP_404_NOT_FOUND)
        
    details = BookingDetail.objects.filter(
        schedule=schedule
    ).select_related('passenger', 'seat', 'booking')
    
    manifest = []
    for d in details:
        # Calculate allowed baggage weight
        allowed_weight = 0
        baggage_name = "None"
        
        # Check addons for baggage
        for addon in d.addons.all():
            if addon.is_baggage and addon.baggage_option:
                allowed_weight = addon.baggage_option.weight_kg
                baggage_name = addon.baggage_option.name
        
        manifest.append({
            'booking_detail_id': d.id,
            'pnr': d.booking.pnr,
            'passenger_name': d.passenger.get_full_name() if d.passenger else 'Unknown',
            'passenger_type': d.passenger.passenger_type if d.passenger else 'Unknown',
            'seat': d.seat.seat_number if d.seat else 'Unassigned',
            'status': d.status,
            'allowed_baggage_weight': allowed_weight,
            'baggage_allowance_name': baggage_name,
        })
        
    return Response({
        'flight': {
            'flight_number': schedule.flight.flight_number if schedule.flight else 'N/A',
            'origin': schedule.flight.route.origin_airport.code if schedule.flight and schedule.flight.route else 'N/A',
            'destination': schedule.flight.route.destination_airport.code if schedule.flight and schedule.flight.route else 'N/A',
            'departure_time': schedule.departure_time,
            'gate': getattr(schedule, 'gate', 'TBA'),
        },
        'manifest': manifest
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def process_dcs_checkin(request):
    """
    Process agent check-in for one or more passengers.
    Supports baggage pooling by accepting a list of passengers and a total weight.
    """
    passenger_data = request.data.get('passengers', [])
    
    # Legacy support (if only one ID is sent)
    if not passenger_data:
        passenger_id = request.data.get('booking_detail_id')
        if passenger_id:
            passenger_data = [{'booking_detail_id': passenger_id, 'actual_weight': request.data.get('actual_baggage_weight', 0)}]

    if not passenger_data:
        return Response({'error': 'No passengers provided'}, status=status.HTTP_400_BAD_REQUEST)

    results = []
    checkin_details = []
    
    for entry in passenger_data:
        try:
            detail_id = entry.get('booking_detail_id')
            weight = float(entry.get('actual_weight', 0))
            
            detail = BookingDetail.objects.get(id=detail_id)
            detail.status = 'checkin'
            # In a real system, you'd store the actual weight per bag here
            detail.save()

            checkin_details.append(detail)
            results.append({'id': detail_id, 'status': 'checkin'})
        except BookingDetail.DoesNotExist:
            continue
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- BUNDLED EMAIL LOGIC ---
    if checkin_details:
        try:
            from flightapp.services.email_service import EmailService
            if len(checkin_details) > 1:
                # Bundled for group
                EmailService.send_group_checkin_confirmation(checkin_details)
            else:
                # Individual for single
                EmailService.send_checkin_confirmation(checkin_details[0])
        except Exception as email_err:
            print(f"Failed to send check-in email(s): {email_err}")

    return Response({
        'success': True,
        'message': f'Checked in {len(results)} passenger(s)',
        'results': results
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_dcs_pnr_details(request, pnr, schedule_id):
    """Get all passengers on a specific PNR for a specific flight"""
    details = BookingDetail.objects.filter(
        booking__pnr__iexact=pnr,
        schedule_id=schedule_id
    ).select_related('passenger', 'seat', 'booking', 'schedule')

    if not details.exists():
        return Response({'error': 'No passengers found for this PNR on this flight'}, status=status.HTTP_404_NOT_FOUND)

    passengers = []
    for d in details:
        allowed_weight = 0
        baggage_name = "None"
        for addon in d.addons.all():
            if addon.is_baggage and addon.baggage_option:
                allowed_weight = addon.baggage_option.weight_kg
                baggage_name = addon.baggage_option.name

        passengers.append({
            'booking_detail_id': d.id,
            'pnr': d.booking.pnr,
            'passenger_name': d.passenger.get_full_name() if d.passenger else 'Unknown',
            'passenger_type': d.passenger.passenger_type if d.passenger else 'Unknown',
            'seat': d.seat.seat_number if d.seat else 'Unassigned',
            'status': d.status,
            'allowed_baggage_weight': allowed_weight,
            'baggage_allowance_name': baggage_name,
        })

    # Get schedule info from the first record
    s = details.first().schedule
    
    return Response({
        'pnr': pnr,
        'schedule': {
            'id': s.id,
            'flight_number': s.flight.flight_number if s.flight else 'N/A',
            'origin': s.flight.route.origin_airport.code if s.flight and s.flight.route else 'N/A',
            'destination': s.flight.route.destination_airport.code if s.flight and s.flight.route else 'N/A',
        },
        'passengers': passengers
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_dcs_passenger_details(request, booking_detail_id):
    """Get detailed info for a single passenger by booking detail ID"""
    try:
        d = BookingDetail.objects.select_related('passenger', 'seat', 'booking', 'schedule').get(id=booking_detail_id)
        
        # Calculate allowed baggage weight
        allowed_weight = 0
        baggage_name = "None"
        for addon in d.addons.all():
            if addon.is_baggage and addon.baggage_option:
                allowed_weight = addon.baggage_option.weight_kg
                baggage_name = addon.baggage_option.name
        
        return Response({
            'booking_detail_id': d.id,
            'pnr': d.booking.pnr,
            'passenger_name': d.passenger.get_full_name() if d.passenger else 'Unknown',
            'passenger_type': d.passenger.passenger_type if d.passenger else 'Unknown',
            'seat': d.seat.seat_number if d.seat else 'Unassigned',
            'status': d.status,
            'allowed_baggage_weight': allowed_weight,
            'baggage_allowance_name': baggage_name,
            'schedule': {
                'id': d.schedule.id,
                'flight_number': d.schedule.flight.flight_number if d.schedule.flight else 'N/A',
                'origin': d.schedule.flight.route.origin_airport.code if d.schedule.flight and d.schedule.flight.route else 'N/A',
                'destination': d.schedule.flight.route.destination_airport.code if d.schedule.flight and d.schedule.flight.route else 'N/A',
            }
        })
    except BookingDetail.DoesNotExist:
        return Response({'error': 'Passenger not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def scan_qr_lookup(request):
    """
    Simulate scanning a passenger's itinerary/boarding-pass QR code.
    The itinerary QR contains the PNR (e.g. "YWSQEU").
    The boarding-pass QR contains "{booking_detail_id}{flight}{origin}{dest}{seat}".
    We try to match either format against the given schedule.
    """
    qr_value = (request.data.get('qr_value') or '').strip()
    schedule_id = request.data.get('schedule_id')

    if not qr_value or not schedule_id:
        return Response({'error': 'Missing qr_value or schedule_id'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        schedule = Schedule.objects.get(id=schedule_id)
    except Schedule.DoesNotExist:
        return Response({'error': 'Flight not found'}, status=status.HTTP_404_NOT_FOUND)

    # Strategy 1: QR value is a PNR (6-char alphanumeric from itinerary)
    details = BookingDetail.objects.filter(
        schedule=schedule,
        booking__pnr__iexact=qr_value
    ).select_related('passenger', 'seat', 'booking')

    # Strategy 2: QR value starts with a booking_detail_id (from boarding pass QR)
    if not details.exists():
        # Try extracting just the leading numeric ID
        import re
        match = re.match(r'^(\d+)', qr_value)
        if match:
            detail_id = int(match.group(1))
            details = BookingDetail.objects.filter(
                id=detail_id,
                schedule=schedule
            ).select_related('passenger', 'seat', 'booking')

    if not details.exists():
        return Response({'error': f'No passenger found for QR code "{qr_value}" on this flight'},
                        status=status.HTTP_404_NOT_FOUND)

    results = []
    for d in details:
        allowed_weight = 0
        baggage_name = "None"
        for addon in d.addons.all():
            if addon.is_baggage and addon.baggage_option:
                allowed_weight = addon.baggage_option.weight_kg
                baggage_name = addon.baggage_option.name

        results.append({
            'booking_detail_id': d.id,
            'pnr': d.booking.pnr,
            'passenger_name': d.passenger.get_full_name() if d.passenger else 'Unknown',
            'passenger_type': d.passenger.passenger_type if d.passenger else 'Unknown',
            'seat': d.seat.seat_number if d.seat else 'Unassigned',
            'status': d.status,
            'allowed_baggage_weight': allowed_weight,
            'baggage_allowance_name': baggage_name,
        })

    return Response({
        'success': True,
        'passengers': results,
        'message': f'Found {len(results)} passenger(s) for PNR {qr_value}'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def download_boarding_pass_view(request, booking_detail_id):
    """Generate and return a boarding pass PDF for a specific passenger"""
    from flightapp.services.pdf_service import BoardingPassPDFService
    response = BoardingPassPDFService.download_boarding_pass(booking_detail_id)
    if response:
        return response
    return Response({'error': 'Passenger check-in record not found'}, status=status.HTTP_404_NOT_FOUND)

