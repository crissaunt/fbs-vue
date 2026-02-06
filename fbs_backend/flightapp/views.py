# flightapp/views.py
from django.http import JsonResponse
import requests
from rest_framework import viewsets, generics, status, filters, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q, F, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import transaction
from decimal import Decimal
from django.contrib.auth.models import User
from .services.email_service import EmailService
from .services.pdf_service import BoardingPassPDFService
from django.http import HttpResponse

from app.models import (
    Airport, Route, Flight, Schedule, Seat, Country,
    SeatClass, PassengerInfo, Airline, Booking, BookingDetail,
    MealOption, BaggageOption, AssistanceService, AddOn, AddOnType,
    TaxType, PassengerTypeTaxRate, BookingTax, TravelInsurancePlan, 
    BookingInsuranceRecord, Aircraft, BookingContact, SeatClass, SeatClassFeature
)
import json
from .serializers import *
from .services.paymongo_service import paymongo_service

class AirlineFilterMixin:
    """Mixin to handle common airline filtering logic by ID or Code"""
    def get_queryset(self):
        # Call parent's get_queryset if it exists
        queryset = super().get_queryset() if hasattr(super(), 'get_queryset') else self.queryset
        airline_param = self.request.query_params.get('airline')
        
        if airline_param:
            if airline_param.isdigit():
                # If it's a number, filter by the numeric ID
                return queryset.filter(airline_id=airline_param)
            else:
                # If it's letters (like '5J'), filter by the airline's code field
                return queryset.filter(airline__code=airline_param)
        
        return queryset

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only viewset that provides 'list' and 'retrieve' actions.
    """
    permission_classes = [permissions.AllowAny]
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class AirportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only viewset for Airports.
    """
    permission_classes = [permissions.AllowAny]
    queryset = Airport.objects.all().select_related('country')
    serializer_class = AirportSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'city', 'code', 'country__name']

class ScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScheduleSerializer
    queryset = Schedule.objects.none()
    permission_classes = [permissions.AllowAny]    
    
    def get_queryset(self):
        # select_related joins the tables so we don't hit the DB 100 times
        queryset = Schedule.objects.filter(status='Open').select_related(
            'flight__airline', 
            'flight__route__origin_airport', 
            'flight__route__destination_airport'
        )
        
        origin = self.request.query_params.get('origin')
        destination = self.request.query_params.get('destination')
        date = self.request.query_params.get('departure')

        if origin:
            queryset = queryset.filter(flight__route__origin_airport__code=origin)
        if destination:
            queryset = queryset.filter(flight__route__destination_airport__code=destination)
        if date:
            try:
                # Ensures that even if a full ISO string is sent, we only filter by date
                clean_date = date.split('T')[0] 
                queryset = queryset.filter(departure_time__date=clean_date)
            except Exception:
                pass

        return queryset

# In views.py - Update the SeatViewSet class
class SeatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows seats to be viewed based on a schedule.
    """
    serializer_class = SeatSerializer
    queryset = Seat.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Seat.objects.all().select_related(
            'seat_class', 
            'schedule', 
            'schedule__flight',
            'schedule__flight__route'
        )
        schedule_id = self.request.query_params.get('schedule')
        
        if schedule_id:
            queryset = queryset.filter(schedule_id=schedule_id)
        
        return queryset.order_by('row', 'column')

    def list(self, request, *args, **kwargs):
        # Override to add schedule price info
        response = super().list(request, *args, **kwargs)
        
        schedule_id = request.query_params.get('schedule')
        if schedule_id:
            try:
                schedule = Schedule.objects.get(id=schedule_id)
                # Add schedule price to response
                response.data = {
                    'success': True,
                    'schedule_id': int(schedule_id),
                    'schedule_price': float(schedule.price) if schedule.price else 0.00,
                    'seats': response.data,
                    'total_seats': len(response.data),
                    'available_seats': Seat.objects.filter(schedule_id=schedule_id, is_available=True).count()
                }
            except Schedule.DoesNotExist:
                response.data = {
                    'success': False,
                    'error': 'Schedule not found',
                    'seats': [],
                    'schedule_price': 0.00,
                    'total_seats': 0,
                    'available_seats': 0
                }
        else:
            response.data = {
                'success': True,
                'schedule_price': 0.00,
                'seats': response.data,
                'total_seats': len(response.data),
                'available_seats': 0
            }
        
        return response

class MealOptionViewSet(AirlineFilterMixin, viewsets.ReadOnlyModelViewSet):
    queryset = MealOption.objects.all()
    serializer_class = MealOptionSerializer
    permission_classes = [permissions.AllowAny]

class AssistanceServiceViewSet(AirlineFilterMixin, viewsets.ReadOnlyModelViewSet):
    queryset = AssistanceService.objects.all()
    serializer_class = AssistanceServiceSerializer
    permission_classes = [permissions.AllowAny]

class BaggageOptionViewSet(AirlineFilterMixin, viewsets.ReadOnlyModelViewSet):
    queryset = BaggageOption.objects.all()
    serializer_class = BaggageOptionSerializer
    permission_classes = [permissions.AllowAny]



@api_view(['POST'])
@permission_classes([AllowAny])
def create_payment_intent(request):
    """
    Create payment intent with PayMongo for a booking
    """
    try:
        amount = request.data.get('amount')
        booking_id = request.data.get('booking_id')
        
        if not amount:
            return Response({
                'success': False,
                'error': 'Amount is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare FLAT metadata (PayMongo does not allow nested objects or Decimals)
        metadata = {}
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                metadata = {
                    "booking_id": str(booking.id),  # Flat string
                    "booking_ref": f"CSUCC{booking.id:08d}", # Flat string
                    "trip_type": str(booking.trip_type) # Flat string
                }
            except Booking.DoesNotExist:
                metadata = {"booking_id": str(booking_id)}
        
        result = paymongo_service.create_payment_intent(
            amount=amount,
            description=f"Flight Booking {booking_id}",
            metadata=metadata  
        )
        
        if result['success']:
            return Response({
                'success': True,
                'client_key': result['client_key'],
                'intent_id': result['intent_id'],
                'amount': result['amount'],
                'status': result['status'],
                'message': 'Payment intent created successfully'
            })
        else:
            # result['error'] contains the PayMongo error details
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to create payment intent')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_payment_source(request):
    """
    Create payment source for specific payment methods (GCash, GrabPay, etc.)
    """
    try:
        amount = request.data.get('amount')
        payment_type = request.data.get('type', 'gcash')
        booking_id = request.data.get('booking_id')
        
        if not amount:
            return Response({
                'success': False,
                'error': 'Amount is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create payment source
        result = paymongo_service.create_payment_source(
            amount=amount,
            type=payment_type
        )
        
        if result['success']:
            return Response({
                'success': True,
                'source_id': result['source_id'],
                'checkout_url': result['checkout_url'],
                'amount': result['data']['attributes']['amount'],
                'status': result['status'],
                'message': f'{payment_type.capitalize()} payment source created'
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to create payment source')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_and_process_payment(request):
    """
    Verify and process a payment using PayMongo payment intent ID
    """
    try:
        data = request.data
        booking_id = data.get('booking_id')
        payment_intent_id = data.get('payment_intent_id')
        
        print(f"\n=== VERIFY AND PROCESS PAYMENT ===")
        print(f"Booking ID: {booking_id}")
        print(f"Payment Intent ID: {payment_intent_id}")
        
        if not booking_id or not payment_intent_id:
            return Response({
                'success': False,
                'error': 'Booking ID and Payment Intent ID are required'
            }, status=400)
        
        # Get the booking
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Booking {booking_id} not found'
            }, status=404)
        
        # Check if payment already exists for this booking
        existing_payment = Payment.objects.filter(
            booking=booking,
            status='Completed'
        ).first()
        
        if existing_payment:
            print(f"✅ Payment already exists: {existing_payment.id}")
            return Response({
                'success': True,
                'payment_id': existing_payment.id,
                'booking_reference': f"CSUCC{booking.id:08d}",
                'booking_status': booking.status,
                'message': 'Payment already processed'
            })
        
        # Verify the payment with PayMongo
        from .services.paymongo_service import paymongo_service
        
        print(f"🔍 Verifying payment intent with PayMongo...")
        
        # Get payment intent details
        intent_url = f"{paymongo_service.api_url}/payment_intents/{payment_intent_id}"
        response = requests.get(intent_url, headers=paymongo_service.headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get payment intent: {response.status_code}")
            print(f"Response: {response.text}")
            return Response({
                'success': False,
                'error': f'Failed to verify payment: {response.text}'
            }, status=400)
        
        intent_data = response.json()['data']
        intent_attributes = intent_data['attributes']
        
        print(f"Payment Intent Status: {intent_attributes['status']}")
        print(f"Amount: {intent_attributes['amount'] / 100} PHP")
        
        if intent_attributes['status'] != 'succeeded':
            print(f"❌ Payment intent not succeeded. Status: {intent_attributes['status']}")
            return Response({
                'success': False,
                'error': f'Payment is not successful. Status: {intent_attributes["status"]}',
                'payment_status': intent_attributes['status']
            })
        
        # Get the payment ID from the payment intent
        payments = intent_attributes.get('payments', [])
        if not payments:
            print(f"❌ No payments found in payment intent")
            return Response({
                'success': False,
                'error': 'No payment found in payment intent'
            })
        
        payment_data = payments[0]
        payment_id = payment_data['id']
        payment_attrs = payment_data['attributes']
        
        print(f"✅ Found payment: {payment_id}")
        print(f"Payment Status: {payment_attrs['status']}")
        
        # Process the payment
        return process_payment_from_paymongo(payment_id, payment_attrs, booking)
        
    except Exception as e:
        print(f"❌ Error in verify_and_process_payment: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)


def process_payment_from_paymongo(payment_id, payment_attrs, booking):
    """Process payment from PayMongo data"""
    from django.db import transaction
    from decimal import Decimal
    
    try:
        with transaction.atomic():
            # Convert amount from centavos to PHP
            amount = Decimal(str(payment_attrs['amount'] / 100))
            
            # Get payment method
            payment_method = "Unknown"
            source = payment_attrs.get('source', {})
            if source.get('type') == 'gcash':
                payment_method = 'GCash'
            elif source.get('type') == 'card':
                payment_method = 'Credit Card'
            elif source.get('type') == 'grab_pay':
                payment_method = 'Grab Pay'
            else:
                payment_method = source.get('type', 'Unknown').capitalize()
            
            print(f"💾 Creating payment record...")
            print(f"   Amount: {amount} PHP")
            print(f"   Method: {payment_method}")
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                method=payment_method,
                transaction_id=payment_id,
                status='Completed',
                payment_date=timezone.now()
            )
            
            print(f"✅ Payment saved: {payment.id}")
            
            # Update booking status
            booking.status = 'Confirmed'
            booking.save()
            print(f"✅ Booking status updated to: {booking.status}")
            
            # Update all booking details status
            updated_details = booking.details.all().update(status='confirmed')
            print(f"✅ Updated {updated_details} booking details")
            
            # Mark seats as unavailable
            seat_count = 0
            for detail in booking.details.all():
                if detail.seat:
                    detail.seat.is_available = False
                    detail.seat.save()
                    seat_count += 1
            print(f"✅ Marked {seat_count} seats as unavailable")
            
            # 🎉 SEND BOOKING CONFIRMATION EMAIL
            print(f"📧 Sending booking confirmation email...")
            email_sent = EmailService.send_booking_confirmation(booking, payment)
            
            if email_sent:
                print(f"✅ Booking confirmation email sent successfully!")
            else:
                print(f"⚠️ Failed to send booking confirmation email")
            
            print(f"🎉 Payment processing COMPLETED!")
            
            return Response({
                'success': True,
                'message': 'Payment processed successfully',
                'payment_id': payment.id,
                'booking_id': booking.id,
                'booking_reference': f"CSUCC{booking.id:08d}",
                'booking_status': 'confirmed',
                'amount': float(amount),
                'method': payment_method,
                'email_sent': email_sent
            })
            
    except Exception as e:
        print(f"❌ Error in payment processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_payment(request):
    """
    Verify payment intent status
    """
    try:
        intent_id = request.data.get('intent_id')
        
        if not intent_id:
            return Response({
                'success': False,
                'error': 'Payment intent ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Retrieve payment intent
        result = paymongo_service.retrieve_payment_intent(intent_id)
        
        if result['success']:
            return Response({
                'success': True,
                'status': result['status'],
                'amount': result['amount'],
                'data': result['data'],
                'message': f'Payment status: {result["status"]}'
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to retrieve payment intent')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_checkout_session(request):
    """
    Generate a PayMongo Checkout URL for method selection
    """
    try:
        amount = request.data.get('amount')
        booking_id = request.data.get('booking_id')
        
        if not amount or not booking_id:
            return Response({
                'success': False,
                'error': 'Amount and booking_id are required'
            }, status=400)

        # Get additional customer info
        customer_email = request.data.get('customer_email')
        customer_name = request.data.get('customer_name')
        customer_phone = request.data.get('customer_phone')
        
        print(f"DEBUG: Creating checkout session for booking {booking_id}, amount {amount}")
        
        result = paymongo_service.create_checkout_session(
            amount=float(amount),
            booking_id=int(booking_id),
            customer_email=customer_email,
            customer_name=customer_name,
            customer_phone=customer_phone
        )
        
        print(f"DEBUG: PayMongo result: {result}")
        
        if result['success']:
            return Response({
                'success': True,
                'checkout_url': result['checkout_url'],
                'session_id': result.get('session_id')
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to create checkout session')
            }, status=400)
    except Exception as e:
        print(f"ERROR in create_checkout_session: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def attach_payment_method(request):
    """
    Attach payment method to payment intent
    """
    try:
        intent_id = request.data.get('intent_id')
        payment_method_id = request.data.get('payment_method_id')
        
        if not intent_id or not payment_method_id:
            return Response({
                'success': False,
                'error': 'Intent ID and Payment Method ID are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Attach payment method
        result = paymongo_service.attach_payment_method(intent_id, payment_method_id)
        
        if result['success']:
            return Response({
                'success': True,
                'status': result['status'],
                'data': result['data'],
                'message': 'Payment method attached successfully'
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to attach payment method')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request):
    """
    API endpoint to create a booking with pending status
    """
    try:
        print(f"🔍 DEBUG: Raw request data: {request.data}")
        
        # Validate request data using serializer
        serializer = CreateBookingSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"DEBUG: Serializer errors: {serializer.errors}")
            return Response({
                'success': False,
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Start transaction
        with transaction.atomic():
            # 1. Create or get user
            user = _get_or_create_user(data)
            
            # 2. Create main booking WITH total amount from frontend
            trip_type = data.get('trip_type', 'one_way')
            total_amount = data.get('total_amount', Decimal('0.00'))
            
            print(f"DEBUG: Creating booking with total amount: {total_amount}")
            
            # Create booking WITH the total_amount field
            booking = Booking.objects.create(
                user=user,
                trip_type=trip_type,
                status='Pending',
                base_fare_total=Decimal('0.00'),
                insurance_total=Decimal('0.00'),
                tax_total=Decimal('0.00'),
                total_amount=total_amount  # Use the field from your model
            )
            
            print(f"DEBUG: Booking created with ID: {booking.id}, Total: {booking.total_amount}")
            
            contact_info = data.get('contact_info', {})
            booking_contact = _create_booking_contact(booking, contact_info)
            
            # 3. Create passengers
            passengers = _create_passengers(data.get('passengers', []))
            print(f"DEBUG: Created {len(passengers)} passengers")
            
            # 4. Create booking details for each passenger
            booking_details = []
            
            # For each passenger, create TWO booking details for round trips
            for i, passenger in enumerate(passengers):
                print(f"DEBUG: Creating booking details for passenger {i+1}: {passenger.first_name} {passenger.last_name}")
                
                # Get the passenger data from request to get the key
                passenger_data = data.get('passengers', [])[i] if i < len(data.get('passengers', [])) else None
                
                # Create DEPART flight booking detail
                depart_detail = _create_booking_detail(
                    booking, passenger, data, passenger_data, is_return=False
                )
                if depart_detail:
                    booking_details.append(depart_detail)
                    print(f"DEBUG: Depart booking detail created: {depart_detail.id}")
                
                # Create RETURN flight booking detail for round trips
                if trip_type == 'round_trip':
                    return_detail = _create_booking_detail(
                        booking, passenger, data, passenger_data, is_return=True
                    )
                    if return_detail:
                        booking_details.append(return_detail)
                        print(f"DEBUG: Return booking detail created: {return_detail.id}")
            
            if not booking_details:
                raise Exception("No booking details created")
            
            # 5. Calculate and apply taxes
            print(f"DEBUG: Applying taxes for {len(booking_details)} booking details")
            _apply_taxes(booking, booking_details)
            
            # 6. Save booking totals
            print(f"DEBUG: Updating booking totals")
            _update_booking_totals(booking)
            
            print(f"DEBUG: Booking creation successful!")
            
            # Return the correct total amount
            return Response({
                'success': True,
                'booking_id': booking.id,
                'booking_reference': f"CSUCC{booking.id:08d}",
                'status': 'pending',
                'total_amount': float(total_amount),  # Use the total amount from frontend
                'payment_info': {
                    'needs_payment': True,
                    'amount': float(total_amount),  # Use the total amount from frontend
                    'currency': 'PHP',
                    'description': f'Flight Booking {booking.id}'
                },
                'message': 'Booking created successfully with pending payment status'
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        import traceback
        print("=== ERROR TRACEBACK ===")
        traceback.print_exc()
        print("======================")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'PUT'])
@permission_classes([AllowAny])
def update_booking(request, booking_id):
    """
    API endpoint to update an existing booking
    """
    try:
        print(f"🔍 DEBUG: Updating booking ID: {booking_id}")
        print(f"DEBUG: Request data: {request.data}")
        
        # First, check if booking exists
        try:
            booking = Booking.objects.get(id=booking_id)
            print(f"DEBUG: Found booking {booking_id}, current status: {booking.status}")
        except Booking.DoesNotExist:
            print(f"DEBUG: Booking {booking_id} not found")
            return Response({
                'success': False,
                'error': f'Booking {booking_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Don't update if booking is already confirmed/cancelled
        if booking.status in ['Confirmed', 'Cancelled']:
            print(f"DEBUG: Booking {booking_id} is already {booking.status}, cannot update")
            return Response({
                'success': False,
                'error': f'Cannot update booking with status: {booking.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate the update data
        serializer = CreateBookingSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            print(f"DEBUG: Serializer errors: {serializer.errors}")
            return Response({
                'success': False,
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        print(f"DEBUG: Validated data: {data}")
        
        # Start transaction for the update
        with transaction.atomic():
            # Update booking contact info if provided
            if 'contact_info' in data:
                contact_info = data['contact_info']
                print(f"DEBUG: Updating contact info: {contact_info}")
                
                # Create or update booking contact
                try:
                    booking_contact = BookingContact.objects.get(booking=booking)
                    booking_contact.first_name = contact_info.get('firstName', booking_contact.first_name)
                    booking_contact.last_name = contact_info.get('lastName', booking_contact.last_name)
                    booking_contact.email = contact_info.get('email', booking_contact.email)
                    booking_contact.phone = contact_info.get('phone', booking_contact.phone)
                    booking_contact.title = contact_info.get('title', booking_contact.title)
                    booking_contact.middle_name = contact_info.get('middleName', booking_contact.middle_name)
                    booking_contact.save()
                    print(f"DEBUG: Updated booking contact")
                except BookingContact.DoesNotExist:
                    # Create new contact
                    booking_contact = BookingContact.objects.create(
                        booking=booking,
                        first_name=contact_info.get('firstName', ''),
                        last_name=contact_info.get('lastName', ''),
                        email=contact_info.get('email', ''),
                        phone=contact_info.get('phone', ''),
                        title=contact_info.get('title', 'MR'),
                        middle_name=contact_info.get('middleName', '')
                    )
                    print(f"DEBUG: Created new booking contact")
            
            # Update passengers if provided
            if 'passengers' in data:
                passengers_data = data['passengers']
                print(f"DEBUG: Updating {len(passengers_data)} passengers")
                
                # For simplicity, we'll delete existing passengers and create new ones
                # First, delete existing booking details
                deleted_details_count, _ = BookingDetail.objects.filter(booking=booking).delete()
                print(f"DEBUG: Deleted {deleted_details_count} old booking details")
                
                # Delete existing passengers linked to this booking
                passenger_ids = BookingDetail.objects.filter(booking=booking).values_list('passenger_id', flat=True)
                PassengerInfo.objects.filter(id__in=passenger_ids).delete()
                print(f"DEBUG: Deleted old passengers")
                
                # Create new passengers
                new_passengers = _create_passengers(passengers_data)
                print(f"DEBUG: Created {len(new_passengers)} new passengers")
                
                # Create new booking details
                booking_details = []
                
                for i, passenger in enumerate(new_passengers):
                    print(f"DEBUG: Creating booking details for passenger {i+1}")
                    
                    # Get passenger data
                    passenger_data = passengers_data[i] if i < len(passengers_data) else {}
                    
                    # Create DEPART flight booking detail
                    depart_detail = _create_booking_detail(
                        booking, passenger, data, passenger_data, is_return=False
                    )
                    if depart_detail:
                        booking_details.append(depart_detail)
                        print(f"DEBUG: Created depart booking detail: {depart_detail.id}")
                    
                    # Create RETURN flight booking detail for round trips
                    if booking.trip_type == 'round_trip':
                        return_detail = _create_booking_detail(
                            booking, passenger, data, passenger_data, is_return=True
                        )
                        if return_detail:
                            booking_details.append(return_detail)
                            print(f"DEBUG: Created return booking detail: {return_detail.id}")
                
                print(f"DEBUG: Created {len(booking_details)} new booking details")
            
            # Update flight selections if provided
            if 'selectedOutbound' in data:
                # Update would require more complex logic to change schedules
                # For now, we'll log it but not change the actual schedule
                print(f"DEBUG: Update requested for outbound flight: {data['selectedOutbound']}")
                print(f"NOTE: Flight schedule changes not implemented in update")
            
            if 'selectedReturn' in data and booking.trip_type == 'round_trip':
                print(f"DEBUG: Update requested for return flight: {data['selectedReturn']}")
                print(f"NOTE: Flight schedule changes not implemented in update")
            
            # Update add-ons if provided
            if 'addons' in data or 'return_addons' in data:
                print(f"DEBUG: Update requested for add-ons")
                print(f"NOTE: Add-on updates would require more complex logic")
            
            # Update total amount if provided
            if 'total_amount' in data:
                new_total = data['total_amount']
                booking.total_amount = new_total
                print(f"DEBUG: Updated total amount to: {new_total}")
            
            # Save booking
            booking.save()
            
            # Recalculate taxes
            if booking_details:
                print(f"DEBUG: Recalculating taxes for {len(booking_details)} booking details")
                _apply_taxes(booking, booking_details)
                _update_booking_totals(booking)
            
            print(f"DEBUG: Booking update successful!")
            
            return Response({
                'success': True,
                'booking_id': booking.id,
                'booking_reference': f"CSUCC{booking.id:08d}",
                'status': booking.status,
                'total_amount': float(booking.total_amount),
                'message': 'Booking updated successfully'
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        import traceback
        print("=== ERROR TRACEBACK ===")
        traceback.print_exc()
        print("======================")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

def _create_booking_contact(booking, contact_info):
    """Create contact record for booking"""    
    try:
        contact = BookingContact.objects.create(
            booking=booking,
            first_name=contact_info.get('firstName', ''),
            last_name=contact_info.get('lastName', ''),
            email=contact_info.get('email', ''),
            phone=contact_info.get('phone', ''),
            title=contact_info.get('title', 'MR'),
            middle_name=contact_info.get('middleName', '')
        )
        print(f"✅ Booking contact created: {contact.id}")
        return contact
    except Exception as e:
        print(f"❌ Error creating booking contact: {str(e)}")
        return None

def _get_or_create_user(data):
    """
    Get or create a user for the booking
    """
    contact_info = data.get('contact_info', {})
    email = contact_info.get('email', 'guest@example.com')
    
    if not email:
        print("❌ ERROR: No email provided in contact info")
        email = 'guest@example.com'
    
    print(f"DEBUG: Creating user with email: {email}")
    print(f"DEBUG: Contact info for user: {contact_info}")
    
    # Create a unique username based on email and timestamp
    username_base = email.split('@')[0] if '@' in email else 'guest'
    username = f"{username_base}_{int(timezone.now().timestamp())}"
    
    # Clean the username (remove special characters)
    import re
    username = re.sub(r'[^a-zA-Z0-9_]', '', username)
    
    # Get or create the user
    try:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': contact_info.get('firstName', ''),
                'last_name': contact_info.get('lastName', ''),
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Created new user: {user.id} - {user.email}")
            print(f"   First name: {user.first_name}")
            print(f"   Last name: {user.last_name}")
        else:
            print(f"✅ Found existing user: {user.id} - {user.email}")
            
        return user
        
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")
        # Fallback to a default guest user
        fallback_user, _ = User.objects.get_or_create(
            username=f'guest_{int(timezone.now().timestamp())}',
            defaults={
                'email': 'guest@example.com',
                'first_name': 'Guest',
                'last_name': 'User',
                'is_active': True
            }
        )
        return fallback_user

def _create_booking(data, user):
    """Create main booking record"""
    trip_type = data.get('trip_type', 'one_way')
    is_round_trip = trip_type == 'round_trip'
    
    # Calculate total amount from frontend data
    total_amount = Decimal(str(data.get('total_amount', 0)))
    print(f"DEBUG: Creating booking with total amount from frontend: {total_amount}")
    
    # Create and save the booking immediately
    booking = Booking.objects.create(
        user=user,
        trip_type=trip_type,
        status='Pending',
        base_fare_total=Decimal('0.00'),
        insurance_total=Decimal('0.00'),
        tax_total=Decimal('0.00'),
        total_amount=total_amount  # Store the total amount from frontend
    )
    
    print(f"DEBUG: Booking created. ID: {booking.id}, Total: {total_amount}")
    
    return booking

def _create_passengers(passengers_data):
    """Create passenger records"""
    passengers = []
    print(f"DEBUG: Creating {len(passengers_data)} passengers")
    
    for i, pax_data in enumerate(passengers_data):
        try:
            print(f"  Passenger {i+1} full data: {pax_data}")
            
            # Use the validated data from serializer
            # The serializer has already normalized the field names
            first_name = pax_data.get('first_name', '')
            last_name = pax_data.get('last_name', '')
            middle_name = pax_data.get('middle_name', '')
            title = pax_data.get('title', 'MR')
            date_of_birth = pax_data.get('date_of_birth', '')
            nationality = pax_data.get('nationality', 'Philippines')
            passport_number = pax_data.get('passport_number', '')
            passenger_type = pax_data.get('type', 'Adult')
            
            print(f"    First Name: {first_name}")
            print(f"    Last Name: {last_name}")
            print(f"    Middle Name: {middle_name}")
            print(f"    Type: {passenger_type}")
            print(f"    Date of Birth: {date_of_birth}")
            
            # Parse date of birth
            dob_parsed = None
            if date_of_birth:
                try:
                    # Remove timezone if present
                    clean_dob = str(date_of_birth).split('T')[0]
                    dob_parsed = datetime.strptime(clean_dob, '%Y-%m-%d').date()
                    print(f"    Date of birth parsed: {dob_parsed}")
                except Exception as e:
                    print(f"    ERROR parsing date of birth: {e}")
                    # Try alternative format
                    try:
                        dob_parsed = datetime.strptime(str(date_of_birth), '%Y-%m-%d').date()
                        print(f"    Date of birth parsed (alternative): {dob_parsed}")
                    except:
                        print(f"    Could not parse date, using None")
                        dob_parsed = None
            
            print(f"    Creating PassengerInfo...")
            
            # Create passenger with validated data
            passenger = PassengerInfo.objects.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                title=title,
                date_of_birth=dob_parsed,
                nationality=nationality,
                passport_number=passport_number,
                passenger_type=passenger_type
            )
            
            print(f"    Passenger created with ID: {passenger.id}")
            print(f"    Passenger full name: {passenger.get_full_name()}")
            passengers.append(passenger)
            
        except Exception as e:
            print(f"    ERROR creating passenger: {e}")
            import traceback
            traceback.print_exc()
            # Don't continue, raise the error
            raise Exception(f"Failed to create passenger {i+1}: {str(e)}")
    
    print(f"DEBUG: Created {len(passengers)} passengers successfully")
    return passengers

def _create_booking_detail(booking, passenger, data, passenger_data=None, is_return=False):
    """Create booking detail for each passenger - UPDATED for round trips"""
    try:
        print(f"DEBUG: In _create_booking_detail - is_return: {is_return}")
        
        # Determine which flight to use
        if is_return:
            selected_flight = data.get('selectedReturn', {})
            flight_label = "Return"
        else:
            selected_flight = data.get('selectedOutbound', {})
            flight_label = "Depart"
        
        print(f"  {flight_label} flight data: {selected_flight}")
        
        # Get schedule ID
        schedule_id = selected_flight.get('schedule_id') or selected_flight.get('id')
        
        if not schedule_id:
            print(f"  ERROR: No schedule ID found for {flight_label.lower()} flight")
            return None
        
        print(f"  {flight_label} Schedule ID: {schedule_id}")
        
        # Get schedule
        try:
            schedule = Schedule.objects.select_related(
                'flight__airline',
                'flight__route',
                'flight__aircraft'
            ).get(id=schedule_id)
            print(f"  {flight_label} schedule found: {schedule.id} - {schedule.flight.flight_number}")
            print(f"  {flight_label} schedule price: {schedule.price}")
        except Schedule.DoesNotExist:
            print(f"  ERROR: {flight_label} schedule with ID {schedule_id} not found")
            return None
        
        # Get seat if selected (seats usually apply to all flights, not segmented)
        seat = None
        seat_class = None
        addons_data = data.get('addons', {})
        
        # Use the passenger key from passenger_data
        passenger_key = None
        if passenger_data and passenger_data.get('key'):
            passenger_key = passenger_data.get('key')
        else:
            passenger_key = f"{passenger.first_name}_{passenger.last_name}"
        
        print(f"  Passenger key for addons: {passenger_key}")
        
        # Find seat for this passenger (seats are not segmented)
        if passenger_key in addons_data.get('seats', {}):
            seat_data = addons_data['seats'][passenger_key]
            print(f"  Seat data for this passenger: {seat_data}")
            
            try:
                if isinstance(seat_data, int):
                    seat = Seat.objects.select_related('seat_class').get(id=seat_data)
                elif isinstance(seat_data, dict) and seat_data.get('id'):
                    seat = Seat.objects.select_related('seat_class').get(id=seat_data['id'])
                
                if seat:
                    # Only mark seat as unavailable for the FIRST booking detail (depart flight)
                    if not is_return:  # Only mark seat unavailable once
                        seat.is_available = False
                        seat.save()
                    seat_class = seat.seat_class
                    print(f"  Seat assigned: {seat.seat_number}")
                    
            except Seat.DoesNotExist:
                print(f"  WARNING: Seat not found")
        
        # If no seat selected, get default seat class
        if not seat_class:
            fare_type = selected_flight.get('class_type', 'Economy')
            seat_class = SeatClass.objects.filter(
                airline=schedule.flight.airline,
                name__icontains=fare_type
            ).first()
        
        # Calculate base price
        base_price = Decimal(str(selected_flight.get('price', 0)))
        print(f"  {flight_label} base price: {base_price}")
        
        # Create booking detail
        print(f"  Creating BookingDetail for {flight_label.lower()} flight...")
        try:
            booking_detail = BookingDetail.objects.create(
                booking=booking,
                passenger=passenger,
                schedule=schedule,
                seat=seat if not is_return else None,  # Only assign seat to depart flight
                seat_class=seat_class,
                price=base_price,
                passenger_type=passenger.passenger_type,
                status='pending'
            )
            print(f"  {flight_label} BookingDetail created with ID: {booking_detail.id}")
        except Exception as e:
            print(f"  ERROR creating {flight_label} BookingDetail: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        
        # Add add-ons - pass is_return flag
        print(f"  Adding {flight_label.lower()} flight addons...")
        _add_addons_to_booking_detail(booking_detail, addons_data, passenger_data or {}, is_return)
        
        return booking_detail
        
    except Exception as e:
        print(f"ERROR in _create_booking_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# In flightapp/views.py, update the _add_addons_to_booking_detail function:
def _add_addons_to_booking_detail(booking_detail, addons_data, passenger_data, is_return=False):
    """Add selected add-ons to booking detail with segment support"""
    addons_to_link = []
    
    # Get airline from schedule
    airline = booking_detail.schedule.flight.airline if booking_detail.schedule else None
    
    # Get passenger key from passenger data
    passenger_key = passenger_data.get('key', f"{booking_detail.passenger.first_name}_{booking_detail.passenger.last_name}")
    
    print(f"DEBUG: Looking for addons for passenger key: {passenger_key}")
    print(f"DEBUG: Is return flight: {is_return}")
    
    # Determine which addons to use (depart or return)
    addon_source = addons_data
    if is_return and 'return_addons' in addons_data:
        addon_source = addons_data.get('return_addons', {})
    
    # Baggage add-on
    baggage_data = addon_source.get('baggage', {}).get(passenger_key)
    if baggage_data:
        if isinstance(baggage_data, dict) and baggage_data.get('id'):
            try:
                baggage_option = BaggageOption.objects.get(id=baggage_data['id'])
                # Create add-on for baggage
                addon, created = AddOn.objects.get_or_create(
                    baggage_option=baggage_option,
                    defaults={
                        'name': f"Extra Baggage {baggage_option.formatted_weight}",
                        'price': baggage_option.price,
                        'airline': airline,
                        'segment': 'return' if is_return else 'depart'  # NEW: Add segment
                    }
                )
                addons_to_link.append(addon)
                print(f"DEBUG: Added baggage addon ({'return' if is_return else 'depart'}): {baggage_option.name}")
            except BaggageOption.DoesNotExist:
                print(f"DEBUG: Baggage option with ID {baggage_data['id']} not found")
        elif isinstance(baggage_data, int):
            try:
                baggage_option = BaggageOption.objects.get(id=baggage_data)
                addon, created = AddOn.objects.get_or_create(
                    baggage_option=baggage_option,
                    defaults={
                        'name': f"Extra Baggage {baggage_option.formatted_weight}",
                        'price': baggage_option.price,
                        'airline': airline,
                        'segment': 'return' if is_return else 'depart'
                    }
                )
                addons_to_link.append(addon)
                print(f"DEBUG: Added baggage addon ({'return' if is_return else 'depart'}): {baggage_option.name}")
            except BaggageOption.DoesNotExist:
                print(f"DEBUG: Baggage option with ID {baggage_data} not found")
    
    # Meal add-on
    meal_data = addon_source.get('meals', {}).get(passenger_key)
    if meal_data:
        if isinstance(meal_data, dict) and meal_data.get('id'):
            try:
                meal_option = MealOption.objects.get(id=meal_data['id'])
                addon, created = AddOn.objects.get_or_create(
                    meal_option=meal_option,
                    defaults={
                        'name': f"Meal: {meal_option.name}",
                        'price': meal_option.price,
                        'airline': airline,
                        'segment': 'return' if is_return else 'depart'
                    }
                )
                addons_to_link.append(addon)
                print(f"DEBUG: Added meal addon ({'return' if is_return else 'depart'}): {meal_option.name}")
            except MealOption.DoesNotExist:
                print(f"DEBUG: Meal option with ID {meal_data['id']} not found")
        elif isinstance(meal_data, int):
            try:
                meal_option = MealOption.objects.get(id=meal_data)
                addon, created = AddOn.objects.get_or_create(
                    meal_option=meal_option,
                    defaults={
                        'name': f"Meal: {meal_option.name}",
                        'price': meal_option.price,
                        'airline': airline,
                        'segment': 'return' if is_return else 'depart'
                    }
                )
                addons_to_link.append(addon)
                print(f"DEBUG: Added meal addon ({'return' if is_return else 'depart'}): {meal_option.name}")
            except MealOption.DoesNotExist:
                print(f"DEBUG: Meal option with ID {meal_data} not found")
    
    # Assistance service
    service_id = addon_source.get('wheelchair', {}).get(passenger_key)
    if service_id:
        try:
            assistance_service = AssistanceService.objects.get(id=service_id)
            addon, created = AddOn.objects.get_or_create(
                assistance_service=assistance_service,
                defaults={
                    'name': f"Assistance: {assistance_service.name}",
                    'price': assistance_service.price,
                    'airline': airline,
                    'included': assistance_service.is_included,
                    'segment': 'return' if is_return else 'depart'
                }
            )
            addons_to_link.append(addon)
            print(f"DEBUG: Added assistance addon ({'return' if is_return else 'depart'}): {assistance_service.name}")
        except AssistanceService.DoesNotExist:
            print(f"DEBUG: Assistance service with ID {service_id} not found")
    
    # Link addons to booking detail
    if addons_to_link:
        booking_detail.addons.add(*addons_to_link)
        print(f"DEBUG: Linked {len(addons_to_link)} addons to booking detail {booking_detail.id} for {'return' if is_return else 'depart'} flight")

def _apply_taxes(booking, booking_details):
    """Calculate and apply taxes to booking"""
    for detail in booking_details:
        if not detail.schedule:
            continue
            
        # Get applicable taxes based on route and passenger type
        route = detail.schedule.flight.route
        passenger_type = detail.passenger_type.lower() if detail.passenger_type else 'adult'
        
        # Find applicable taxes
        applicable_taxes = TaxType.objects.filter(
            is_active=True,
            applies_domestic=route.is_domestic,
            applies_international=route.is_international
        )
        
        for tax in applicable_taxes:
            try:
                # Check if passenger type is applicable
                if tax.adult_only and passenger_type != 'adult':
                    continue
                    
                # Check passenger type rate
                try:
                    rate = PassengerTypeTaxRate.objects.get(
                        tax_type=tax,
                        passenger_type=passenger_type
                    )
                    amount = rate.amount
                except PassengerTypeTaxRate.DoesNotExist:
                    amount = tax.base_amount
                
                # Apply per passenger or per booking
                if tax.per_passenger:
                    # Create booking tax record
                    BookingTax.objects.create(
                        booking=booking,
                        tax_type=tax,
                        amount=amount,
                        passenger_type=passenger_type
                    )
                    
                    # Add to booking detail tax amount
                    detail.tax_amount += amount
                    detail.save()
                
            except Exception as e:
                print(f"Error applying tax {tax.name}: {e}")
                continue

def _update_booking_totals(booking):
    """Update booking totals after all details are created and verify against stored total"""
    try:
        print(f"DEBUG: In _update_booking_totals for booking {booking.id}")
        
        # Wait a moment to ensure all details are saved
        import time
        time.sleep(0.1)  # Small delay
        
        # Refresh booking from database
        booking.refresh_from_db()
        
        # Recalculate totals - use direct query instead of reverse relationship
        from django.db.models import Sum
        
        # Calculate base fare total
        base_fare_total = BookingDetail.objects.filter(
            booking=booking
        ).aggregate(total=Sum('price'))['total'] or Decimal('0.00')
        
        print(f"  Base fare total: {base_fare_total}")
        
        # Calculate insurance total (if you have insurance logic)
        insurance_total = Decimal('0.00')
        # Add your insurance calculation here
        
        # Calculate tax total
        tax_total = BookingTax.objects.filter(
            booking=booking
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        print(f"  Tax total: {tax_total}")
        
        # Calculate the total from components
        calculated_total = base_fare_total + insurance_total + tax_total
        
        # Verify the stored total matches the calculated total
        stored_total = booking.total_amount
        print(f"  Stored total: {stored_total}")
        print(f"  Calculated total: {calculated_total}")
        
        # If there's a discrepancy, log it but use the stored total (from frontend)
        if calculated_total != stored_total:
            print(f"  ⚠️ WARNING: Total mismatch! Stored: {stored_total}, Calculated: {calculated_total}")
            print(f"  ⚠️ Using stored total from frontend: {stored_total}")
        
        # Update booking with calculated totals
        booking.base_fare_total = base_fare_total
        booking.insurance_total = insurance_total
        booking.tax_total = tax_total
        booking.save()
        
        print(f"  Booking totals updated successfully")
        
    except Exception as e:
        print(f"ERROR in _update_booking_totals: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


@api_view(['POST'])
@permission_classes([AllowAny])
def process_payment(request):
    """
    Process payment callback from PayMongo
    """
    try:
        # Get payment intent ID from PayMongo webhook or callback
        intent_id = request.data.get('payment_intent_id') or request.data.get('intent_id')
        booking_id = request.data.get('booking_id')
        
        if not intent_id or not booking_id:
            return Response({
                'success': False,
                'error': 'Payment intent ID and booking ID are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get booking
        try:
            booking = Booking.objects.select_related('user').get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Booking not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify payment with PayMongo
        payment_result = paymongo_service.retrieve_payment_intent(intent_id)
        
        if not payment_result['success']:
            return Response({
                'success': False,
                'error': f'Payment verification failed: {payment_result.get("error")}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment_data = payment_result['data']
        payment_status = payment_data['attributes']['status']
        
        # Check payment method used
        payment_method = "Unknown"
        if payment_data['attributes'].get('payment_method'):
            pm_type = payment_data['attributes']['payment_method']['attributes']['type']
            if pm_type == 'card':
                payment_method = 'Credit Card'
            elif pm_type == 'gcash':
                payment_method = 'GCash'
            elif pm_type == 'grab_pay':
                payment_method = 'Grab Pay'
            else:
                payment_method = pm_type.capitalize()
        
        # Process payment based on status
        with transaction.atomic():
            if payment_status == 'succeeded':
                # Create payment record
                amount = payment_data['attributes']['amount'] / 100  # Convert from centavos
                
                payment = Payment.objects.create(
                    booking=booking,
                    amount=Decimal(str(amount)),
                    method=payment_method,
                    transaction_id=intent_id,
                    status='Completed',
                    payment_date=timezone.now()
                )
                
                # Update booking status
                booking.status = 'Confirmed'
                booking.save()
                
                # Update all booking details status
                booking.details.all().update(status='confirmed')
                
                # Mark seats as unavailable
                for detail in booking.details.all():
                    if detail.seat:
                        detail.seat.is_available = False
                        detail.seat.save()
                
                return Response({
                    'success': True,
                    'payment_id': payment.id,
                    'booking_status': 'confirmed',
                    'booking_reference': f"CSUCC{booking.id:08d}",
                    'message': 'Payment processed successfully'
                }, status=status.HTTP_200_OK)
            
            elif payment_status in ['awaiting_next_action', 'awaiting_payment_method']:
                # Payment is still being processed
                return Response({
                    'success': True,
                    'booking_status': 'pending',
                    'payment_status': payment_status,
                    'message': 'Payment is being processed'
                }, status=status.HTTP_200_OK)
            
            else:
                # Payment failed
                return Response({
                    'success': False,
                    'error': f'Payment failed with status: {payment_status}',
                    'payment_status': payment_status
                }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AllowAny])
def get_booking_details(request, booking_id):
    """
    Get booking details by ID
    """
    try:
        booking = Booking.objects.select_related('user').get(id=booking_id)
        
        # Serialize booking data
        from .serializers import BookingSerializer
        
        return Response({
            'success': True,
            'booking': BookingSerializer(booking).data
        })
        
    except Booking.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Booking not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

# Optional: Add a booking viewset for admin/management
class BookingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view bookings (admin only)
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.none()
    basename = 'booking'
    
    def get_queryset(self):
        user = self.request.user
        
        # If user is staff, show all bookings
        if user.is_staff:
            return Booking.objects.all().select_related('user')
        
        # Otherwise, only show user's own bookings
        return Booking.objects.filter(user=user).select_related('user')
    
# flightapp/views.py
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_session_payment(request):
    """
    Verify payment using session ID
    """
    try:
        session_id = request.data.get('session_id')
        booking_id = request.data.get('booking_id')
        
        if not session_id or not booking_id:
            return Response({
                'success': False,
                'error': 'Session ID and Booking ID are required'
            }, status=400)
        
        # Retrieve checkout session from PayMongo
        from .services.paymongo_service import paymongo_service
        
        session_url = f"{paymongo_service.api_url}/checkout_sessions/{session_id}"
        session_response = requests.get(session_url, headers=paymongo_service.headers)
        
        if session_response.status_code != 200:
            return Response({
                'success': False,
                'error': 'Invalid session ID'
            }, status=400)
        
        session_data = session_response.json()['data']
        session_attributes = session_data['attributes']
        
        # Check if session has successful payments
        payments = session_attributes.get('payments', [])
        
        if payments:
            # Get the first payment
            payment_data = payments[0]
            payment_id = payment_data['id']
            payment_attrs = payment_data['attributes']
            
            if payment_attrs['status'] == 'paid':
                # Process the payment
                return process_payment_from_paymongo(payment_id, payment_attrs, booking_id)
        
        return Response({
            'success': False,
            'session_status': session_attributes.get('status'),
            'message': 'No successful payment found for this session'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)

# flightapp/views.py
@api_view(['POST'])
@permission_classes([AllowAny])
def process_payment_callback(request):
    """
    Process payment callback from PayMongo Checkout Session
    """
    try:
        print("\n=== PROCESSING PAYMENT CALLBACK ===")
        print(f"Request data: {request.data}")
        print(f"Request headers: {dict(request.headers)}")
        
        # Check if this is a PayMongo webhook
        if request.data.get('type') == 'checkout_session.payment_succeeded':
            # This is a webhook notification
            session_data = request.data.get('data', {})
            session_id = session_data.get('id')
            attributes = session_data.get('attributes', {})
            
            print(f"Webhook: Checkout session {session_id}")
            
            # Get metadata
            metadata = attributes.get('metadata', {})
            booking_id = metadata.get('booking_id')
            
            if booking_id:
                # Retrieve the checkout session to get payment details
                session_url = f"{paymongo_service.api_url}/checkout_sessions/{session_id}"
                session_response = requests.get(session_url, headers=paymongo_service.headers)
                
                if session_response.status_code == 200:
                    session_details = session_response.json()
                    payments = session_details['data']['attributes'].get('payments', [])
                    
                    if payments:
                        payment_id = payments[0]['id']
                        
                        # Now process the payment with the payment ID
                        return process_payment_with_id(payment_id, booking_id)
        
        # If not a webhook, try to get from query params or body
        booking_id = request.data.get('booking_id') or request.query_params.get('booking_id')
        payment_success = request.data.get('payment_success') or request.query_params.get('payment_success')
        
        print(f"Booking ID: {booking_id}")
        print(f"Payment Success: {payment_success}")
        
        if not booking_id:
            return Response({
                'success': False,
                'error': 'No booking ID provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # If payment was successful but we don't have payment ID yet
        # We need to poll PayMongo for completed payments for this booking
        if payment_success == 'true':
            return handle_successful_payment_without_id(booking_id)
        
        # If payment failed/cancelled
        elif payment_success == 'false':
            return Response({
                'success': False,
                'booking_id': booking_id,
                'status': 'cancelled',
                'message': 'Payment was cancelled by user'
            })
        
        else:
            return Response({
                'success': False,
                'error': 'Invalid payment status'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def paymongo_webhook(request):
    """
    PayMongo webhook for real-time payment processing
    This gets called immediately when payment succeeds
    """
    try:
        print("\n=== PAYMONGO WEBHOOK RECEIVED ===")
        
        # Verify webhook signature (optional but recommended)
        signature = request.headers.get('paymongo-signature')
        print(f"Signature: {signature}")
        
        event_data = request.data
        event_type = event_data.get('type')
        
        print(f"Event Type: {event_type}")
        print(f"Event Data: {json.dumps(event_data, indent=2)}")
        
        if event_type == 'checkout_session.payment_succeeded':
            # Payment succeeded via checkout session
            session_data = event_data.get('data', {})
            session_id = session_data.get('id')
            attributes = session_data.get('attributes', {})
            
            print(f"✅ Payment succeeded for session: {session_id}")
            
            # Get metadata
            metadata = attributes.get('metadata', {})
            booking_id = metadata.get('booking_id')
            
            if not booking_id:
                # Try to get from payments
                payments = attributes.get('payments', [])
                if payments:
                    payment_attrs = payments[0].get('attributes', {})
                    payment_metadata = payment_attrs.get('metadata', {})
                    booking_id = payment_metadata.get('booking_id')
            
            if booking_id:
                print(f"Processing payment for booking {booking_id}")
                
                # Process the payment
                payments = attributes.get('payments', [])
                if payments:
                    payment_data = payments[0]
                    payment_id = payment_data['id']
                    payment_attrs = payment_data['attributes']
                    
                    # Process this payment
                    return process_payment_webhook(payment_id, payment_attrs, booking_id)
                else:
                    print("❌ No payments found in session")
        
        elif event_type == 'payment.paid':
            # Direct payment succeeded
            payment_data = event_data.get('data', {})
            payment_id = payment_data.get('id')
            payment_attrs = payment_data.get('attributes', {})
            
            print(f"✅ Direct payment succeeded: {payment_id}")
            
            # Get metadata
            metadata = payment_attrs.get('metadata', {})
            booking_id = metadata.get('booking_id')
            
            if booking_id:
                print(f"Processing direct payment for booking {booking_id}")
                return process_payment_webhook(payment_id, payment_attrs, booking_id)
        
        # Return success to PayMongo
        return Response({"success": True}, status=200)
        
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=400)

# In flightapp/views.py, update process_payment_webhook:

def process_payment_webhook(payment_id, payment_attrs, booking_id):
    """
    Process payment from webhook and save to database
    """
    from django.db import transaction
    from app.models import Booking, Payment, BookingDetail, Seat
    from decimal import Decimal
    
    try:
        print(f"\n💾 Processing payment for booking {booking_id}")
        print(f"Payment ID: {payment_id}")
        print(f"Payment Status: {payment_attrs.get('status')}")
        
        with transaction.atomic():
            # Get booking (with lock to prevent race conditions)
            try:
                booking = Booking.objects.select_for_update().get(id=booking_id)
                print(f"Found booking: {booking.id}, Status: {booking.status}")
            except Booking.DoesNotExist:
                print(f"❌ Booking {booking_id} not found")
                return Response({"error": "Booking not found"}, status=404)
            
            # Check if payment already exists
            existing_payment = Payment.objects.filter(
                transaction_id=payment_id
            ).first()
            
            if existing_payment:
                print(f"✅ Payment already exists: {existing_payment.id}")
                return Response({
                    "success": True,
                    "message": "Payment already processed",
                    "payment_id": existing_payment.id,
                    "booking_status": booking.status
                })
            
            # Convert amount from centavos to PHP
            amount = Decimal(str(payment_attrs['amount'] / 100))
            print(f"Amount: {amount} PHP")
            
            # Get payment method
            payment_method = "Unknown"
            source = payment_attrs.get('source', {})
            source_type = source.get('type', '')
            
            if source_type == 'gcash':
                payment_method = 'GCash'
            elif source_type == 'card':
                payment_method = 'Credit Card'
            elif source_type == 'grab_pay':
                payment_method = 'Grab Pay'
            elif source_type == 'paymaya':
                payment_method = 'PayMaya'
            else:
                payment_method = source_type.capitalize() if source_type else 'Unknown'
            
            print(f"Payment Method: {payment_method}")
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                method=payment_method,
                transaction_id=payment_id,
                status='Completed',
                payment_date=timezone.now()
            )
            
            print(f"✅ Payment saved to database: {payment.id}")
            
            # Update booking status
            booking.status = 'Confirmed'
            booking.save()
            print(f"✅ Booking status updated to: {booking.status}")
            
            # Update all booking details status
            updated_details = booking.details.all().update(status='confirmed')
            print(f"✅ Updated {updated_details} booking details")
            
            # Mark seats as unavailable
            seat_count = 0
            for detail in booking.details.all():
                if detail.seat:
                    detail.seat.is_available = False
                    detail.seat.save()
                    seat_count += 1
            print(f"✅ Marked {seat_count} seats as unavailable")
            
            print(f"🎉 Payment processing COMPLETED for booking {booking_id}")
            
            return Response({
                "success": True,
                "message": "Payment processed successfully",
                "payment_id": payment.id,
                "booking_id": booking_id,
                "booking_status": "confirmed",
                "booking_reference": f"CSUCC{booking.id:08d}",
                "amount": float(amount),
                "method": payment_method
            })
            
    except Exception as e:
        print(f"❌ Error in payment processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=400)


def send_booking_confirmation_email(booking):
    """
    Send booking confirmation email
    """
    # You can implement email sending here
    # For now, just log it
    print(f"\n📧 Would send confirmation email for booking {booking.id}")
    print(f"   To: {booking.user.email if booking.user else 'No user email'}")
    print(f"   Reference: CSUCC{booking.id:08d}")
    print(f"   Amount: {booking.total_amount}")

def process_payment_with_id(payment_id, booking_id):
    """Process payment when we have the payment ID"""
    try:
        from .services.paymongo_service import paymongo_service
        
        print(f"Processing payment {payment_id} for booking {booking_id}")
        
        # Get payment details
        payment_url = f"{paymongo_service.api_url}/payments/{payment_id}"
        payment_response = requests.get(payment_url, headers=paymongo_service.headers)
        
        if payment_response.status_code == 200:
            payment_data = payment_response.json()['data']
            payment_attributes = payment_data['attributes']
            
            if payment_attributes['status'] == 'paid':
                # Create payment record
                from django.db import transaction
                from app.models import Booking, Payment
                from decimal import Decimal
                
                with transaction.atomic():
                    booking = Booking.objects.get(id=booking_id)
                    
                    # Convert amount from centavos to PHP
                    amount = Decimal(str(payment_attributes['amount'] / 100))
                    
                    # Get payment method
                    payment_method = "Unknown"
                    source = payment_attributes.get('source', {})
                    if source.get('type') == 'gcash':
                        payment_method = 'GCash'
                    elif source.get('type') == 'card':
                        payment_method = 'Credit Card'
                    elif source.get('type') == 'grab_pay':
                        payment_method = 'Grab Pay'
                    else:
                        payment_method = source.get('type', 'Unknown').capitalize()
                    
                    # Create payment record
                    payment = Payment.objects.create(
                        booking=booking,
                        amount=amount,
                        method=payment_method,
                        transaction_id=payment_id,
                        status='Completed'
                    )
                    
                    # Update booking status
                    booking.status = 'Confirmed'
                    booking.save()
                    
                    # Update booking details
                    booking.details.all().update(status='confirmed')
                    
                    # Mark seats as unavailable
                    for detail in booking.details.all():
                        if detail.seat:
                            detail.seat.is_available = False
                            detail.seat.save()
                    
                    print(f"✅ Payment processed: {payment.id}")
                    
                    return Response({
                        'success': True,
                        'payment_id': payment.id,
                        'booking_status': 'confirmed',
                        'booking_reference': f"CSUCC{booking.id:08d}",
                        'message': 'Payment processed successfully'
                    })
        
        return Response({
            'success': False,
            'error': 'Payment not found or not completed'
        })
        
    except Exception as e:
        print(f"Error processing payment: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        })


def handle_successful_payment_without_id(booking_id):
    """Handle case where payment succeeded but we don't have payment ID"""
    try:
        from .services.paymongo_service import paymongo_service
        
        print(f"Looking for payments for booking {booking_id}")
        
        # Search for recent payments (last 5 minutes)
        import time
        five_minutes_ago = int(time.time()) - 300
        
        # List checkout sessions with metadata
        sessions_url = f"{paymongo_service.api_url}/checkout_sessions"
        sessions_response = requests.get(sessions_url, headers=paymongo_service.headers)
        
        if sessions_response.status_code == 200:
            sessions = sessions_response.json()['data']
            
            for session in sessions:
                attributes = session['attributes']
                metadata = attributes.get('metadata', {})
                
                if metadata.get('booking_id') == str(booking_id):
                    # Check if session has payments
                    payments = attributes.get('payments', [])
                    
                    for payment in payments:
                        payment_attrs = payment['attributes']
                        
                        if payment_attrs['status'] == 'paid':
                            # Found a successful payment!
                            return process_payment_with_id(payment['id'], booking_id)
        
        # If no payment found, check directly in payments
        payments_url = f"{paymongo_service.api_url}/payments?created[gte]={five_minutes_ago}"
        payments_response = requests.get(payments_url, headers=paymongo_service.headers)
        
        if payments_response.status_code == 200:
            payments = payments_response.json()['data']
            
            for payment in payments:
                attributes = payment['attributes']
                metadata = attributes.get('metadata', {})
                
                if metadata.get('booking_id') == str(booking_id) and attributes['status'] == 'paid':
                    return process_payment_with_id(payment['id'], booking_id)
        
        return Response({
            'success': False,
            'error': 'No completed payment found for this booking',
            'booking_id': booking_id,
            'status': 'pending_verification'
        })
        
    except Exception as e:
        print(f"Error finding payment: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        })

# In flightapp/views.py, update the check_payment_status function:

@api_view(['GET'])
@permission_classes([AllowAny])
def check_payment_status(request, booking_id):
    """
    Check if payment has been processed for a booking
    """
    try:
        print(f"\n=== CHECKING PAYMENT STATUS ===")
        print(f"Booking ID: {booking_id}")
        
        # Get the booking
        try:
            booking = Booking.objects.get(id=booking_id)
            print(f"Booking found: {booking.id}, Status: {booking.status}")
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Booking {booking_id} not found'
            }, status=404)
        
        # Check if booking is already confirmed
        if booking.status == 'Confirmed':
            print(f"✅ Booking already confirmed in database")
            payment = Payment.objects.filter(booking=booking, status='Completed').first()
            return Response({
                'success': True,
                'paid': True,
                'payment_id': payment.id if payment else None,
                'booking_id': booking_id,
                'booking_reference': f"CSUCC{booking.id:08d}",
                'booking_status': booking.status,
                'amount': float(payment.amount) if payment else 0,
                'method': payment.method if payment else None,
                'message': 'Booking is already confirmed'
            })
        
        # Check database for completed payment
        payment = Payment.objects.filter(booking=booking, status='Completed').first()
        if payment:
            print(f"✅ Found completed payment in database: {payment.id}")
            return Response({
                'success': True,
                'paid': True,
                'payment_id': payment.id,
                'booking_id': booking_id,
                'booking_reference': f"CSUCC{booking.id:08d}",
                'booking_status': booking.status,
                'amount': float(payment.amount),
                'method': payment.method,
                'message': 'Payment found in database'
            })
        
        # SEARCH PAYMONGO FOR PAYMENTS
        print(f"🔍 Searching PayMongo for payments...")
        
        try:
            # Option 1: Search checkout sessions
            print(f"  1. Searching checkout sessions...")
            sessions_url = f"{paymongo_service.api_url}/checkout_sessions"
            sessions_response = requests.get(sessions_url, headers=paymongo_service.headers, timeout=10)
            
            if sessions_response.status_code == 200:
                sessions_data = sessions_response.json()
                sessions = sessions_data.get('data', [])
                print(f"    Found {len(sessions)} checkout sessions")
                
                for session in sessions:
                    session_id = session['id']
                    attributes = session.get('attributes', {})
                    metadata = attributes.get('metadata', {})
                    
                    if metadata.get('booking_id') == str(booking_id):
                        print(f"    ✅ Found checkout session for booking {booking_id}")
                        print(f"      Session ID: {session_id}")
                        print(f"      Session Status: {attributes.get('status')}")
                        
                        # Check payments in this session
                        payments = attributes.get('payments', [])
                        print(f"      Payments in session: {len(payments)}")
                        
                        for payment_data in payments:
                            payment_attrs = payment_data.get('attributes', {})
                            payment_id = payment_data.get('id')
                            payment_status = payment_attrs.get('status')
                            
                            print(f"      Payment {payment_id}: {payment_status}")
                            
                            if payment_status == 'paid':
                                print(f"      ✅ Found PAID payment!")
                                # Process this payment
                                return process_payment_from_paymongo(
                                    payment_id, payment_attrs, booking
                                )
            
            # Option 2: Search payments directly (if webhook created them)
            print(f"  2. Searching payments directly...")
            payments_url = f"{paymongo_service.api_url}/payments"
            payments_response = requests.get(payments_url, headers=paymongo_service.headers, timeout=10)
            
            if payments_response.status_code == 200:
                payments_data = payments_response.json()
                payments = payments_data.get('data', [])
                print(f"    Found {len(payments)} total payments")
                
                # Filter payments from last 24 hours for this booking
                import time
                one_day_ago = int(time.time()) - (24 * 60 * 60)
                
                for payment_data in payments:
                    payment_attrs = payment_data.get('attributes', {})
                    created_at = payment_attrs.get('created_at', 0)
                    
                    # Check if payment is recent
                    if created_at >= one_day_ago:
                        metadata = payment_attrs.get('metadata', {})
                        
                        if metadata.get('booking_id') == str(booking_id):
                            payment_id = payment_data.get('id')
                            payment_status = payment_attrs.get('status')
                            
                            print(f"    ✅ Found payment for booking {booking_id}: {payment_status}")
                            
                            if payment_status == 'paid':
                                print(f"    ✅ Payment is PAID! Processing...")
                                return process_payment_from_paymongo(
                                    payment_id, payment_attrs, booking
                                )
            
        except Exception as e:
            print(f"⚠️ Error searching PayMongo: {str(e)}")
        
        # No payment found yet
        print(f"⏳ No payment found yet for booking {booking_id}")
        return Response({
            'success': True,
            'paid': False,
            'booking_id': booking_id,
            'booking_status': booking.status,
            'message': 'Payment not yet processed. Please complete payment first.'
        })
        
    except Exception as e:
        print(f"❌ Error in check_payment_status: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)

def process_payment_immediately(payment_id, payment_attrs, booking):
    """Process payment immediately when found in PayMongo"""
    from django.db import transaction
    from decimal import Decimal
    
    try:
        with transaction.atomic():
            # Convert amount from centavos to PHP
            amount = Decimal(str(payment_attrs['amount'] / 100))
            
            # Get payment method
            payment_method = "Unknown"
            source = payment_attrs.get('source', {})
            if source.get('type') == 'gcash':
                payment_method = 'GCash'
            elif source.get('type') == 'card':
                payment_method = 'Credit Card'
            elif source.get('type') == 'grab_pay':
                payment_method = 'Grab Pay'
            else:
                payment_method = source.get('type', 'Unknown').capitalize()
            
            # Check if payment already exists
            existing_payment = Payment.objects.filter(
                transaction_id=payment_id
            ).first()
            
            if existing_payment:
                return Response({
                    'success': True,
                    'paid': True,
                    'payment_id': existing_payment.id,
                    'booking_reference': f"CSUCC{booking.id:08d}",
                    'booking_status': booking.status,
                    'message': 'Payment already processed'
                })
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                method=payment_method,
                transaction_id=payment_id,
                status='Completed'
            )
            
            # Update booking status
            booking.status = 'Confirmed'
            booking.save()
            
            # Update booking details
            booking.details.all().update(status='confirmed')
            
            # Mark seats as unavailable
            for detail in booking.details.all():
                if detail.seat:
                    detail.seat.is_available = False
                    detail.seat.save()
            
            print(f"✅ IMMEDIATELY processed payment: {payment.id}")
            
            return Response({
                'success': True,
                'paid': True,
                'payment_id': payment.id,
                'booking_id': booking.id,
                'booking_reference': f"CSUCC{booking.id:08d}",
                'booking_status': 'confirmed',
                'amount': float(amount),
                'method': payment_method,
                'message': 'Payment processed successfully!'
            })
            
    except Exception as e:
        print(f"Error processing payment immediately: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def test_paymongo_setup(request):
    """
    Test PayMongo setup and authentication
    """
    import base64
    from .services.paymongo_service import paymongo_service
    
    # Get the raw secret key
    secret_key = paymongo_service.secret_key
    
    # Recreate the auth header manually
    auth_string = f"{secret_key}:"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    # Test headers
    test_headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {encoded_auth}"
    }
    
    # Make a test request to PayMongo
    import requests
    try:
        test_response = requests.get(
            "https://api.paymongo.com/v1/payment_intents",
            headers=test_headers,
            timeout=10
        )
        
        response_info = {
            "status_code": test_response.status_code,
            "success": test_response.status_code == 200,
            "response_body": test_response.text if test_response.content else "No content"
        }
        
    except Exception as e:
        response_info = {
            "error": str(e),
            "success": False
        }
    
    return Response({
        "debug_info": {
            "secret_key_found": bool(secret_key),
            "secret_key_prefix": secret_key[:10] + "..." if secret_key else None,
            "secret_key_length": len(secret_key) if secret_key else 0,
            "auth_string": auth_string,
            "encoded_auth": encoded_auth,
            "headers_created": test_headers,
            "api_url": paymongo_service.api_url
        },
        "paymongo_test": response_info,
        "message": "✅ Key found in environment" if secret_key else "❌ Key not found"
    })    


# Add this to flightapp/views.py

@api_view(['GET'])
@permission_classes([AllowAny])
def check_booking_payment(request, booking_id):
    """
    Check payment status for a booking and process if found
    """
    try:
        print(f"\n=== CHECKING BOOKING PAYMENT ===")
        print(f"Booking ID: {booking_id}")
        
        # Get the booking
        try:
            booking = Booking.objects.get(id=booking_id)
            print(f"Found booking: {booking.id}, Status: {booking.status}")
        except Booking.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Booking {booking_id} not found'
            }, status=404)
        
        # Check if booking is already confirmed
        if booking.status == 'Confirmed':
            print(f"✅ Booking already confirmed")
            payment = Payment.objects.filter(booking=booking, status='Completed').first()
            return Response({
                'success': True,
                'paid': True,
                'booking_status': 'confirmed',
                'booking_id': booking_id,
                'booking_reference': f"CSUCC{booking.id:08d}",
                'payment_id': payment.id if payment else None,
                'message': 'Booking is already confirmed'
            })
        
        # Search PayMongo for payments for this booking
        print(f"🔍 Searching PayMongo for booking {booking_id}...")
        
        # Look for checkout sessions with this booking ID in metadata
        sessions_url = f"{paymongo_service.api_url}/checkout_sessions"
        response = requests.get(sessions_url, headers=paymongo_service.headers, timeout=10)
        
        if response.status_code == 200:
            sessions = response.json()['data']
            print(f"Found {len(sessions)} sessions")
            
            for session in sessions:
                attributes = session['attributes']
                metadata = attributes.get('metadata', {})
                
                # Check if this session is for our booking
                if metadata.get('booking_id') == str(booking_id):
                    print(f"✅ Found checkout session for booking {booking_id}")
                    print(f"Session ID: {session['id']}")
                    print(f"Session Status: {attributes.get('status')}")
                    
                    # Check payments in this session
                    payments = attributes.get('payments', [])
                    print(f"Number of payments in session: {len(payments)}")
                    
                    for payment_data in payments:
                        payment_attrs = payment_data['attributes']
                        print(f"Payment Status: {payment_attrs['status']}")
                        
                        if payment_attrs['status'] == 'paid':
                            print(f"✅ Found PAID payment in session!")
                            payment_id = payment_data['id']
                            
                            # Get payment details
                            payment_url = f"{paymongo_service.api_url}/payments/{payment_id}"
                            payment_response = requests.get(payment_url, headers=paymongo_service.headers)
                            
                            if payment_response.status_code == 200:
                                payment_details = payment_response.json()['data']
                                
                                # Process this payment
                                return process_payment_webhook(
                                    payment_id, 
                                    payment_details['attributes'], 
                                    booking_id
                                )
        
        # Also search payments directly
        print(f"🔍 Searching payments directly...")
        payments_url = f"{paymongo_service.api_url}/payments"
        payments_response = requests.get(payments_url, headers=paymongo_service.headers, timeout=10)
        
        if payments_response.status_code == 200:
            payments = payments_response.json()['data']
            print(f"Found {len(payments)} total payments")
            
            for payment_data in payments:
                payment_attrs = payment_data['attributes']
                metadata = payment_attrs.get('metadata', {})
                
                if metadata.get('booking_id') == str(booking_id) and payment_attrs['status'] == 'paid':
                    print(f"✅ Found direct PAID payment for booking {booking_id}")
                    return process_payment_webhook(
                        payment_data['id'], 
                        payment_attrs, 
                        booking_id
                    )
        
        # No payment found yet
        print(f"⏳ No payment found yet for booking {booking_id}")
        return Response({
            'success': True,
            'paid': False,
            'booking_status': booking.status,
            'booking_id': booking_id,
            'message': 'Payment not yet processed. Please complete payment and refresh.'
        })
        
    except Exception as e:
        print(f"❌ Error checking payment: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)
    



# Add this new endpoint for simple status checking
@api_view(['GET'])
@permission_classes([AllowAny])
def check_booking_status(request, booking_id):
    """
    Simple endpoint to check booking status (no PayMongo search)
    For frontend polling after payment
    """
    try:
        print(f"\n=== SIMPLE BOOKING STATUS CHECK ===")
        print(f"Booking ID: {booking_id}")
        
        booking = Booking.objects.get(id=booking_id)
        payment = Payment.objects.filter(booking=booking, status='Completed').first()
        
        return Response({
            'success': True,
            'booking_id': booking_id,
            'booking_reference': f"CSUCC{booking.id:08d}",
            'booking_status': booking.status,
            'has_payment': payment is not None,
            'payment_id': payment.id if payment else None,
            'paid': booking.status == 'Confirmed' or payment is not None,
            'message': 'Booking status checked'
        })
        
    except Booking.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Booking not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)    
    


# In flightapp/views.py, update the get_seat_class_features function:

@api_view(['GET'])
@permission_classes([AllowAny])
def get_seat_class_features(request):
    """
    API endpoint to get seat class features from database
    """
    try:
        # Get all seat classes
        seat_classes = SeatClass.objects.all()
        
        features_data = {}
        for seat_class in seat_classes:
            # Get features for this seat class
            class_features = SeatClassFeature.objects.filter(
                seat_class=seat_class
            ).order_by('display_order').values_list('feature', flat=True)
            
            if class_features.exists():
                features_data[seat_class.name.lower().replace(' ', '_')] = list(class_features)
            # Don't add empty arrays - only add if features exist
        
        return Response({
            'success': True,
            'data': features_data
        })
        
    except Exception as e:
        print(f"Error loading seat class features: {str(e)}")
        # Return empty data instead of error
        return Response({
            'success': True,
            'data': {}
        })
    


# Django views.py
@api_view(['GET'])
@permission_classes([AllowAny])
def get_booking_by_reference(request, reference):
    """Get booking by reference number (CSUCC00000071)"""
    try:
        # Extract ID from reference
        booking_id = int(reference.replace('CSUCC', ''))
        booking = Booking.objects.get(id=booking_id)
        serializer = BookingSerializer(booking)
        return Response({
            'success': True,
            'booking': serializer.data
        })
    except (ValueError, Booking.DoesNotExist):
        return Response({
            'success': False,
            'error': 'Booking not found'
        }, status=404)

@api_view(['POST'])
@permission_classes([AllowAny])
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    try:
        booking = Booking.objects.get(id=booking_id)
        booking.status = 'cancelled'
        booking.save()
        return Response({
            'success': True,
            'message': 'Booking cancelled successfully'
        })
    except Booking.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Booking not found'
        }, status=404)    
    


    # Add this function in views.py (anywhere after the imports)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_seats_with_schedule_info(request, schedule_id):
    """
    Get seats with schedule price information
    """
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        seats = Seat.objects.filter(schedule=schedule).select_related(
            'seat_class', 
            'schedule', 
            'schedule__flight',
            'schedule__flight__route'
        ).order_by('row', 'column')
        
        seat_data = []
        for seat in seats:
            # Calculate final price
            try:
                final_price = seat.final_price
            except:
                # Fallback calculation
                base_price = schedule.price if schedule.price else Decimal('0.00')
                multiplier = seat.seat_class.price_multiplier if seat.seat_class else Decimal('1.00')
                adjustment = seat.price_adjustment if seat.price_adjustment else Decimal('0.00')
                final_price = (base_price * multiplier) + adjustment
            
            seat_info = {
                'id': seat.id,
                'seat_code': f"{seat.row}{seat.column}" if seat.row and seat.column else seat.seat_number,
                'seat_number': seat.seat_number,
                'row': seat.row,
                'column': seat.column,
                'is_available': seat.is_available,
                'final_price': float(final_price),
                'price_adjustment': float(seat.price_adjustment) if seat.price_adjustment else 0.0,
                'has_extra_legroom': seat.has_extra_legroom,
                'is_exit_row': seat.is_exit_row,
                'is_bulkhead': seat.is_bulkhead,
                'is_window': seat.is_window,
                'is_aisle': seat.is_aisle,
                'features': [],
            }
            
            # Add features
            if seat.has_extra_legroom:
                seat_info['features'].append("Extra Legroom")
            if seat.is_exit_row:
                seat_info['features'].append("Exit Row")
            if seat.is_bulkhead:
                seat_info['features'].append("Bulkhead")
            if seat.is_window:
                seat_info['features'].append("Window")
            if seat.is_aisle:
                seat_info['features'].append("Aisle")
            
            if seat.seat_class:
                seat_info['seat_class'] = {
                    'id': seat.seat_class.id,
                    'name': seat.seat_class.name,
                    'price_multiplier': float(seat.seat_class.price_multiplier)
                }
            
            seat_data.append(seat_info)
        
        return JsonResponse({
            'success': True,
            'schedule_id': schedule_id,
            'schedule_price': float(schedule.price) if schedule.price else 0.00,
            'flight_number': schedule.flight.flight_number if schedule.flight else '',
            'airline': schedule.flight.airline.code if schedule.flight and schedule.flight.airline else '',
            'seats': seat_data,
            'total_seats': len(seat_data),
            'available_seats': seats.filter(is_available=True).count()
        })
        
    except Schedule.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Schedule not found'
        }, status=404)
    except Exception as e:
        print(f"Error in get_seats_with_schedule_info: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    


@api_view(['GET'])
@permission_classes([AllowAny])
def test_seat_data(request, schedule_id):
    """Test endpoint to see what seat data looks like"""
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        seats = Seat.objects.filter(schedule=schedule)[:3]
        
        data = {
            'schedule': {
                'id': schedule.id,
                'price': float(schedule.price) if schedule.price else 0,
                'flight_number': schedule.flight.flight_number if schedule.flight else None
            },
            'seat_count': Seat.objects.filter(schedule=schedule).count(),
            'sample_seats': []
        }
        
        for seat in seats:
            seat_data = {
                'id': seat.id,
                'seat_code': f"{seat.row}{seat.column}" if seat.row and seat.column else seat.seat_number,
                'row': seat.row,
                'column': seat.column,
                'seat_number': seat.seat_number,
                'is_available': seat.is_available,
                'price_adjustment': float(seat.price_adjustment) if seat.price_adjustment else 0,
                'has_extra_legroom': seat.has_extra_legroom,
                'is_exit_row': seat.is_exit_row,
                'is_bulkhead': seat.is_bulkhead,
                'is_window': seat.is_window,
                'is_aisle': seat.is_aisle,
            }
            
            if seat.seat_class:
                seat_data['seat_class'] = {
                    'id': seat.seat_class.id,
                    'name': seat.seat_class.name,
                    'price_multiplier': float(seat.seat_class.price_multiplier)
                }
            
            # Calculate price
            base_price = schedule.price if schedule.price else Decimal('0.00')
            multiplier = seat.seat_class.price_multiplier if seat.seat_class else Decimal('1.00')
            adjustment = seat.price_adjustment if seat.price_adjustment else Decimal('0.00')
            calculated_price = (base_price * multiplier) + adjustment
            
            seat_data['calculated_price'] = float(calculated_price)
            
            # Try to get from property
            try:
                seat_data['final_price_property'] = float(seat.final_price)
            except:
                seat_data['final_price_property'] = 'Error accessing property'
            
            data['sample_seats'].append(seat_data)
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  


def process_payment_webhook(payment_id, payment_attrs, booking_id):
    """
    Process payment from webhook and save to database + send confirmation email
    """
    from django.db import transaction
    from app.models import Booking, Payment, BookingDetail, Seat
    from decimal import Decimal
    
    try:
        print(f"\n💾 Processing payment for booking {booking_id}")
        print(f"Payment ID: {payment_id}")
        print(f"Payment Status: {payment_attrs.get('status')}")
        
        with transaction.atomic():
            # Get booking (with lock to prevent race conditions)
            try:
                booking = Booking.objects.select_for_update().get(id=booking_id)
                print(f"Found booking: {booking.id}, Status: {booking.status}")
            except Booking.DoesNotExist:
                print(f"❌ Booking {booking_id} not found")
                return Response({"error": "Booking not found"}, status=404)
            
            # Check if payment already exists
            existing_payment = Payment.objects.filter(
                transaction_id=payment_id
            ).first()
            
            if existing_payment:
                print(f"✅ Payment already exists: {existing_payment.id}")
                
                # Still send email if booking is confirmed but email wasn't sent
                if booking.status == 'Confirmed':
                    EmailService.send_booking_confirmation(booking, existing_payment)
                
                return Response({
                    "success": True,
                    "message": "Payment already processed",
                    "payment_id": existing_payment.id,
                    "booking_status": booking.status
                })
            
            # Convert amount from centavos to PHP
            amount = Decimal(str(payment_attrs['amount'] / 100))
            print(f"Amount: {amount} PHP")
            
            # Get payment method
            payment_method = "Unknown"
            source = payment_attrs.get('source', {})
            source_type = source.get('type', '')
            
            if source_type == 'gcash':
                payment_method = 'GCash'
            elif source_type == 'card':
                payment_method = 'Credit Card'
            elif source_type == 'grab_pay':
                payment_method = 'Grab Pay'
            elif source_type == 'paymaya':
                payment_method = 'PayMaya'
            else:
                payment_method = source_type.capitalize() if source_type else 'Unknown'
            
            print(f"Payment Method: {payment_method}")
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                method=payment_method,
                transaction_id=payment_id,
                status='Completed',
                payment_date=timezone.now()
            )
            
            print(f"✅ Payment saved to database: {payment.id}")
            
            # Update booking status
            booking.status = 'Confirmed'
            booking.save()
            print(f"✅ Booking status updated to: {booking.status}")
            
            # Update all booking details status
            updated_details = booking.details.all().update(status='confirmed')
            print(f"✅ Updated {updated_details} booking details")
            
            # Mark seats as unavailable
            seat_count = 0
            for detail in booking.details.all():
                if detail.seat:
                    detail.seat.is_available = False
                    detail.seat.save()
                    seat_count += 1
            print(f"✅ Marked {seat_count} seats as unavailable")
            
            # 🎉 SEND BOOKING CONFIRMATION EMAIL
            print(f"📧 Sending booking confirmation email...")
            email_sent = EmailService.send_booking_confirmation(booking, payment)
            
            if email_sent:
                print(f"✅ Booking confirmation email sent successfully!")
            else:
                print(f"⚠️ Failed to send booking confirmation email - will retry via admin")
                # Optionally: Queue for retry or notify admin
            
            print(f"🎉 Payment processing COMPLETED for booking {booking_id}")
            
            return Response({
                "success": True,
                "message": "Payment processed successfully",
                "payment_id": payment.id,
                "booking_id": booking_id,
                "booking_status": "confirmed",
                "booking_reference": f"CSUCC{booking.id:08d}",
                "amount": float(amount),
                "method": payment_method,
                "email_sent": email_sent
            })
            
    except Exception as e:
        print(f"❌ Error in payment processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_seats_with_schedule_info(request, schedule_id):
    """
    Get seats with schedule and aircraft information
    """
    try:
        schedule = Schedule.objects.select_related(
            'flight__aircraft',
            'flight__airline'
        ).get(id=schedule_id)
        
        seats = Seat.objects.filter(schedule=schedule).select_related(
            'seat_class', 
            'schedule', 
            'schedule__flight',
            'schedule__flight__route'
        ).order_by('row', 'column')
        
        # Get aircraft model
        aircraft_model = schedule.flight.aircraft.model if schedule.flight.aircraft else "Airbus A321"
        
        seat_data = []
        for seat in seats:
            # Calculate final price
            try:
                final_price = seat.final_price
            except:
                # Fallback calculation
                base_price = schedule.price if schedule.price else Decimal('0.00')
                multiplier = seat.seat_class.price_multiplier if seat.seat_class else Decimal('1.00')
                adjustment = seat.price_adjustment if seat.price_adjustment else Decimal('0.00')
                final_price = (base_price * multiplier) + adjustment
            
            seat_info = {
                'id': seat.id,
                'seat_code': f"{seat.row}{seat.column}" if seat.row and seat.column else seat.seat_number,
                'seat_number': seat.seat_number,
                'row': seat.row,
                'column': seat.column,
                'is_available': seat.is_available,
                'final_price': float(final_price),
                'price_adjustment': float(seat.price_adjustment) if seat.price_adjustment else 0.0,
                'has_extra_legroom': seat.has_extra_legroom,
                'is_exit_row': seat.is_exit_row,
                'is_bulkhead': seat.is_bulkhead,
                'is_window': seat.is_window,
                'is_aisle': seat.is_aisle,
                'features': [],
            }
            
            # Add features
            if seat.has_extra_legroom:
                seat_info['features'].append("Extra Legroom")
            if seat.is_exit_row:
                seat_info['features'].append("Exit Row")
            if seat.is_bulkhead:
                seat_info['features'].append("Bulkhead")
            if seat.is_window:
                seat_info['features'].append("Window")
            if seat.is_aisle:
                seat_info['features'].append("Aisle")
            
            if seat.seat_class:
                seat_info['seat_class'] = {
                    'id': seat.seat_class.id,
                    'name': seat.seat_class.name,
                    'price_multiplier': float(seat.seat_class.price_multiplier)
                }
            
            seat_data.append(seat_info)
        
        return JsonResponse({
            'success': True,
            'schedule_id': schedule_id,
            'schedule_price': float(schedule.price) if schedule.price else 0.00,
            'aircraft_model': aircraft_model,  # Add aircraft model
            'aircraft_capacity': schedule.flight.aircraft.capacity if schedule.flight.aircraft else 220,
            'flight_number': schedule.flight.flight_number if schedule.flight else '',
            'airline': schedule.flight.airline.code if schedule.flight and schedule.flight.airline else '',
            'airline_name': schedule.flight.airline.name if schedule.flight and schedule.flight.airline else '',
            'seats': seat_data,
            'total_seats': len(seat_data),
            'available_seats': seats.filter(is_available=True).count()
        })
        
    except Schedule.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Schedule not found'
        }, status=404)
    except Exception as e:
        print(f"Error in get_seats_with_schedule_info: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    


@api_view(['GET'])
@permission_classes([AllowAny])
def download_boarding_pass(request, booking_detail_id):
    """
    Download boarding pass PDF for a specific booking detail
    """
    try:
        response = BoardingPassPDFService.download_boarding_pass(booking_detail_id)
        if response:
            return response
        else:
            return Response({
                'success': False,
                'error': 'Booking detail not found'
            }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def download_itinerary(request, booking_id):
    """
    Download full itinerary PDF for a booking
    """
    try:
        response = BoardingPassPDFService.download_itinerary(booking_id)
        if response:
            return response
        else:
            return Response({
                'success': False,
                'error': 'Booking not found'
            }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)