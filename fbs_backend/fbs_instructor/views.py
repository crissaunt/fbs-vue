# ============================================================================
# DJANGO IMPORTS
# ============================================================================
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json
from django.core.mail import send_mail
from django.conf import settings

# ============================================================================
# DJANGO REST FRAMEWORK IMPORTS
# ============================================================================
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# ============================================================================
# PYTHON STANDARD LIBRARY
# ============================================================================
import random
import string
import threading
import traceback
from decimal import Decimal

# ============================================================================
# CROSS-APP IMPORTS (from app.models)
# ============================================================================
from app.models import AddOn, Airline, Airport, Students, UserProfile, Booking

# ============================================================================
# LOCAL APP IMPORTS (from fbs_instructor)
# ============================================================================
from .models import (
    Activity,
    ActivityPassenger,
    Instructor,
    Section,
    SectionEnrollment,
    ActivityStudentBinding,
    ActivityAddOn,
    ActivitySegment,
    UserSession  # NEW: Our custom session model
)
from .serializers import LoginSerializer, UserSerializer
from .authentication import MultiSessionTokenAuthentication  # NEW: Our custom auth
from .permissions import IsInstructor  # NEW: Custom permission

import traceback
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


# ==========================================
# HELPER FUNCTION: Get Client IP
# ==========================================
def get_client_ip(request):
    """Get the client's IP address from the request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ==========================================
# 1. LOGIN VIEW (Multi-Session Support)
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny])
def Login_view(request):
    """
    Enhanced login with TRUE multi-device/multi-tab support
    Each login creates a unique session with its own token
    """
    print(f"\n{'='*60}")
    print(f"? LOGIN REQUEST")
    print(f"{'='*60}")
    
    # 1. Validate Input
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        print(f"? Validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 2. Get the specific user who is trying to login
    user = serializer.validated_data['user']
    print(f"? User authenticated: {user.username}")

    # 3. Check Role using UserProfile
    try:
        profile = UserProfile.objects.get(user=user)
        role = profile.role or ('admin' if (user.is_superuser or user.is_staff) else None)
        if role is None:
             role = 'student' # Default fallback
        print(f"✅ Profile found: {role}")
    except UserProfile.DoesNotExist:
        if user.is_superuser or user.is_staff:
            role = 'admin'
        else:
            print(f"❌ No profile found for user: {user.username}")
            return Response({"error": "Profile not found"}, status=status.HTTP_403_FORBIDDEN)

    # 4. Create a NEW session for this login (allows multiple simultaneous logins)
    try:
        session = UserSession.objects.create(
            user=user,
            session_token=UserSession.generate_token(),
            role=role,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            is_active=True
        )
        print(f"? New session created: {session.session_token[:16]}... (Role: {session.role})")
    except Exception as e:
        print(f"? Session creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": f"Failed to create session: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 5. Determine Route based on role
    dashboard_route = '/'
    if profile.role == 'instructor':
        dashboard_route = '/instructor/dashboard'
    elif profile.role == 'student':
        dashboard_route = '/student/dashboard'
    elif profile.role == 'admin':
        dashboard_route = '/admin'

    print(f"? Login successful - Redirecting to: {dashboard_route}")
    print(f"{'='*60}\n")

    # 6. Return the UNIQUE session token (NOT the old DRF token)
    return Response({
        "message": "Login successful",
        "token": session.session_token,  # This is unique per login
        "session_id": session.id,
        "user": UserSerializer(user).data,
        "role": profile.role,
        "dashboard_route": dashboard_route
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    data = request.data
    role = data.get('role') 
    username = data.get('username')
    email = data.get('email')
    id_number = data.get('id_number')
    
    # Validation checks
    if not username or not email or not data.get('password') or not id_number:
        return Response({"error": "Missing required fields (username, email, password, ID number)"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": f"Username '{username}' is already taken."}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({"error": f"Email '{email}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)

    if role == 'student' and Students.objects.filter(student_number=id_number).exists():
        return Response({"error": f"Student ID '{id_number}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)
    
    if role == 'instructor' and Instructor.objects.filter(instructor_id=id_number).exists():
        return Response({"error": f"Instructor ID '{id_number}' is already registered."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            # 1. Create the User (single source of truth)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', '')
            )

            # 2. Assign Role in UserProfile (auto-created by signal)
            profile = UserProfile.objects.get(user=user)
            profile.role = role
            profile.save()

            # 3. Create role-specific record
            if role == 'student':
                Students.objects.create(
                    user=user,
                    student_number=id_number,
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    email=email,
                    phone_number=data.get('phone_number', ''),
                    mi=data.get('mi', ''),
                    gender=data.get('gender', ''),
                    password=''
                )
            elif role == 'instructor':
                Instructor.objects.create(
                    user=user,
                    instructor_id=id_number,
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    email=email,
                    middle_initial=data.get('mi', '')
                )

            return Response({
                "message": "Registration successful!",
                "username": user.username,
                "role": role
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 2. INSTRUCTOR DASHBOARD (Session-Based)
# ==========================================
@api_view(['GET', 'POST'])
@authentication_classes([MultiSessionTokenAuthentication])  # NEW: Use custom auth
@permission_classes([IsAuthenticated, IsInstructor]) 
def instructor_dashboard(request):
    user = request.user 
    session_obj = request.session_obj  # Our UserSession object
    
    print(f"\n{'='*60}")
    print(f"??? INSTRUCTOR DASHBOARD REQUEST")
    print(f"{'='*60}")
    print(f"User: {user.username} (ID: {user.id})")
    print(f"Session Token: {session_obj.session_token[:16]}...")
    print(f"Session Role: {session_obj.role}")
    print(f"Session ID: {session_obj.id}")
    
    # 1. Verification Logic - Check session role matches
    try:
        if session_obj.role != 'instructor':
            print(f"? ERROR: Session role is '{session_obj.role}', not 'instructor'")
            return Response({
                "error": "Access denied. This session is not authorized for instructor access.",
                "session_role": session_obj.role,
                "required_role": "instructor"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Double-check with UserProfile
        if not hasattr(user, 'userprofile') or user.userprofile.role != 'instructor':
            print(f"? ERROR: User profile role mismatch")
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
        
        print("? Session and profile verified as instructor")
            
    except Exception as e:
        print(f"? ERROR during verification: {str(e)}")
        traceback.print_exc()
        return Response({"error": "Profile verification failed."}, status=status.HTTP_403_FORBIDDEN)

    # 2. Handling the POST (Creating a new section)
    if request.method == 'POST':
        try:
            Section.objects.create(
                section_name=request.data.get('section_name'),
                section_code=request.data.get('section_code'),
                semester=request.data.get('semester'),
                academic_year=request.data.get('academic_year'),
                schedule=request.data.get('schedule', ''),
                description=request.data.get('description', ''),
                instructor=user
            )
            print(f"? Section created: {request.data.get('section_name')}")
            return Response({"message": "Section created successfully!"}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            print("? ERROR: Section code already exists")
            return Response({"error": "Section code already exists for your account."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"? ERROR creating section: {str(e)}")
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # 3. Handling the GET (Fetching data)
    sections = Section.objects.filter(instructor=user).values(
        'id', 'section_name', 'section_code', 'semester', 'academic_year', 'schedule', 'description', 'is_active'
    ).order_by('-id') 
    
    print(f"? Found {sections.count()} sections for instructor")
    print(f"{'='*60}\n")
    
    return Response({
        'sections': list(sections),
        'user': {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        },
        'session_info': {
            'session_id': session_obj.id,
            'role': session_obj.role,
            'last_activity': session_obj.last_activity.isoformat()
        }
    }, status=status.HTTP_200_OK)


# ==========================================
# REMAINING VIEWS (All need custom auth)
# ==========================================

@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def section_details(request, section_id):
    user = request.user
    
    try:
        section = Section.objects.get(id=section_id, instructor=user)
        activities = Activity.objects.filter(section=section).order_by('-created_at')
        
        activities_data = []
        for activity in activities:
            activities_data.append({
                'id': activity.id,
                'title': activity.title,
                'description': activity.description or '',
                'activity_type': activity.activity_type,
                'due_date': activity.due_date,
                'total_points': float(activity.total_points),
                'created_at': activity.created_at,
                'required_trip_type': activity.required_trip_type,
                'required_origin': activity.required_origin,
                'required_destination': activity.required_destination,
            })
        
        return Response({
            'id': section.id,
            'section_name': section.section_name,
            'section_code': section.section_code,
            'semester': section.semester,
            'academic_year': section.academic_year,
            'schedule': section.schedule,
            'description': section.description,
            'is_locked': section.is_locked,
            'is_active': section.is_active,
            'created_at': section.created_at,
            'activities': activities_data
        }, status=status.HTTP_200_OK)
        
    except Section.DoesNotExist:
        return Response({"error": "Section not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH', 'PUT', 'DELETE'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def update_section(request, section_id):
    user = request.user
    section = get_object_or_404(Section, id=section_id, instructor=user)
    
    if request.method == 'DELETE':
        section_name = section.section_name
        section.delete()
        return Response({"message": f"Section '{section_name}' deleted successfully!"}, status=status.HTTP_200_OK)
    
    data = request.data
    
    # Update fields if they exist in the request
    if 'section_name' in data:
        section.section_name = data['section_name']
    if 'section_code' in data:
        # Check for uniqueness if code is changed
        new_code = data['section_code']
        if new_code != section.section_code:
            if Section.objects.filter(section_code=new_code, instructor=user).exists():
                return Response({"error": "Section code already exists for your account."}, status=status.HTTP_400_BAD_REQUEST)
            section.section_code = new_code
    if 'semester' in data:
        section.semester = data['semester']
    if 'academic_year' in data:
        section.academic_year = data['academic_year']
    if 'schedule' in data:
        section.schedule = data['schedule']
    if 'description' in data:
        section.description = data['description']
    if 'is_locked' in data:
        section.is_locked = data['is_locked']
    if 'is_active' in data:
        section.is_active = data['is_active']
        
    try:
        section.save()
        return Response({
            "message": "Section updated successfully!",
            "section": {
                "id": section.id,
                "section_name": section.section_name,
                "section_code": section.section_code,
                "is_locked": section.is_locked,
                "is_active": section.is_active
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def delete_activity(request, section_id, activity_id):
    user = request.user
    
    try:
        section = Section.objects.get(id=section_id, instructor=user)
        activity = Activity.objects.get(id=activity_id, section=section)
        activity_title = activity.title
        activity.delete()
        
        return Response({
            'message': f'Activity "{activity_title}" deleted successfully!'
        }, status=status.HTTP_200_OK)
        
    except Section.DoesNotExist:
        return Response({"error": "Section not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)
    except Activity.DoesNotExist:
        return Response({"error": "Activity not found in this section."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EnrollStudentView(APIView):
    authentication_classes = [MultiSessionTokenAuthentication]
    permission_classes = [IsAuthenticated, IsInstructor]
    
    def post(self, request, section_id):
        student_num = request.data.get('student_number')
        section = get_object_or_404(Section, id=section_id, instructor=request.user)
        
        if section.is_locked:
            return Response({"error": "This section is currently locked. New enrollments are not allowed."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            student = Students.objects.get(student_number=student_num)
        except Students.DoesNotExist:
            return Response({"error": "Student number not found."}, status=status.HTTP_404_NOT_FOUND)
        
        existing_enrollment = SectionEnrollment.objects.filter(student=student).first()
        
        if existing_enrollment:
            enrolled_section = existing_enrollment.section
            return Response({
                "error": f"Student {student.first_name} {student.last_name} is already enrolled in section '{enrolled_section.section_name}' ({enrolled_section.section_code}). Students can only be enrolled in one section at a time."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        enrollment, created = SectionEnrollment.objects.get_or_create(
            section=section,
            student=student
        )
        
        if not created:
            return Response({"error": "Student is already enrolled in this section."}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({"message": f"Successfully enrolled {student.first_name}!"}, status=status.HTTP_201_CREATED)

class UnenrollStudentView(APIView):
    authentication_classes = [MultiSessionTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, section_id, student_id):
        # 1. Verify the section belongs to the instructor
        section = get_object_or_404(Section, id=section_id, instructor=request.user)
        
        # 2. Verify the student exists and is enrolled in this section
        student = get_object_or_404(Students, id=student_id)
        enrollment = SectionEnrollment.objects.filter(section=section, student=student).first()
        
        if not enrollment:
            return Response({"error": "Student is not enrolled in this section."}, status=status.HTTP_404_NOT_FOUND)
            
        # 3. Delete the enrollment
        enrollment.delete()
        
        return Response({"message": f"Successfully unenrolled {student.first_name}."}, status=status.HTTP_200_OK)
    

@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def Enroll_Student_list(request, section_id):
    section = get_object_or_404(Section, id=section_id, instructor=request.user)
    enrollments = section.enrollments.all().select_related('student')
    
    student_data = [
        {
            "id": e.student.id,
            "student_number": e.student.student_number,
            "first_name": e.student.first_name,
            "last_name": e.student.last_name,
            "email": e.student.email,
            "enrolled_at": e.enrolled_at.strftime("%Y-%m-%d")
        } for e in enrollments
    ]
    
    return Response(student_data, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def create_activity(request, section_id):
    instructor = request.user
    section = get_object_or_404(Section, id=section_id, instructor=instructor)

    if request.method == 'GET':
        airports = Airport.objects.all().order_by('code')
        addons = AddOn.objects.select_related('type', 'airline').all()
        
        # ? NEW: Fetch all students for randomization
        from app.models import Students  # Import your Students model
        students = Students.objects.all()
        
        return Response({
            'airports': [
                {'code': a.code, 'name': a.name, 'location': a.location} 
                for a in airports
            ],
            'available_addons': [
                {
                    'id': ad.id, 
                    'name': ad.name, 
                    'price': str(ad.price), 
                    'description': ad.description or '', 
                    'airline': {'code': ad.airline.code} if ad.airline else None,
                    'type': {'name': ad.type.name} if ad.type else None
                } 
                for ad in addons
            ],
            # ? NEW: Send students data
            'students': [
                {
                    'first_name': s.first_name,
                    'middle_name': s.mi or '',
                    'last_name': s.last_name,
                    'gender': s.gender or ''
                }
                for s in students
            ],
            'section_schedule': section.schedule or "" 
        }, status=status.HTTP_200_OK)

    if request.method == 'POST':
        data = request.data
        
        try:
            required_passengers = int(data.get('required_passengers', 1))
            required_children = int(data.get('required_children', 0))
            required_infants = int(data.get('required_infants', 0))

            if required_passengers < 1:
                return Response({"error": "At least one adult passenger is required"}, status=400)
            if required_infants > required_passengers:
                return Response({"error": "Number of infants cannot exceed number of adults"}, status=400)

            with transaction.atomic():
                activity = Activity.objects.create(
                    title=data.get('title'),
                    description=data.get('description', ""),
                    activity_type=data.get('activity_type', 'Flight Booking'),
                    section=section,
                    required_trip_type=data.get('required_trip_type', 'one_way'),
                    required_origin=data.get('required_origin'),
                    required_destination=data.get('required_destination'),
                    required_departure_date=data.get('required_departure_date') or None,
                    required_return_date=data.get('required_return_date') or None,
                    required_travel_class=data.get('required_travel_class', 'economy'),
                    required_passengers=required_passengers,
                    required_children=required_children,
                    required_infants=required_infants,
                    require_passenger_details=data.get('require_passenger_details', False),
                    require_passport=data.get('require_passport', False),
                    instructions=data.get('instructions'),
                    total_points=float(data.get('total_points', 100)),
                    due_date=data.get('due_date'),
                    addon_grading_enabled=data.get('require_addons', False),
                    time_limit_minutes=data.get('time_limit_minutes') or None,
                )

                # --- Handle Multi-City Segments ---
                if data.get('required_trip_type') == 'multi_city':
                    segments_data = data.get('segments', [])
                    for index, s_data in enumerate(segments_data):
                        ActivitySegment.objects.create(
                            activity=activity,
                            origin=s_data.get('origin', ''),
                            destination=s_data.get('destination', ''),
                            departure_date=s_data.get('departure_date'),
                            order=index
                        )

                passengers_data = data.get('passengers', [])
                
                for index, p_data in enumerate(passengers_data):
                    passenger = ActivityPassenger.objects.create(
                        activity=activity,
                        first_name=p_data.get('first_name', ''),
                        middle_name=p_data.get('middle_name', ''),
                        last_name=p_data.get('last_name', ''),
                        passenger_type=p_data.get('passenger_type', 'adult'),
                        gender=p_data.get('gender', ''),
                        date_of_birth=p_data.get('date_of_birth') or None,
                        nationality=p_data.get('nationality', ''),
                        passport_number=p_data.get('passport_number', ''),
                        is_primary=(index == 0)
                    )

                    selected_addons = p_data.get('selected_addons', [])
                    
                    for addon_item in selected_addons:
                        try:
                            addon_instance = AddOn.objects.get(id=addon_item['id'])
                            ActivityAddOn.objects.create(
                                activity=activity,
                                addon=addon_instance,
                                passenger=passenger,
                                is_required=addon_item.get('is_required', False),
                                quantity_per_passenger=addon_item.get('quantity', 1),
                                notes=addon_item.get('notes', ''),
                                points_value=10.00
                            )
                        except AddOn.DoesNotExist:
                            continue
                        except Exception as e:
                            print(f"Error creating ActivityAddOn: {str(e)}")
                            continue

                return Response({
                    "message": "Activity created successfully!",
                    "activity_id": activity.id
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def activity_details(request, activity_id):
    try:
        activity = get_object_or_404(
            Activity.objects.select_related('section').prefetch_related('passengers'),
            id=activity_id,
            section__instructor=request.user
        )
        
        # Helper function to safely get passenger attributes
        def get_passenger_field(passenger, field_name, default=''):
            """Safely get passenger field value"""
            return getattr(passenger, field_name, default) or default
        
        # Build passenger data with all possible fields
        passengers_data = []
        for p in activity.passengers.all():
            passenger_info = {
                "first_name": get_passenger_field(p, 'first_name'),
                "middle_name": (
                    get_passenger_field(p, 'middle_name') or 
                    get_passenger_field(p, 'middleName') or 
                    get_passenger_field(p, 'middle_initial')
                ),
                "last_name": get_passenger_field(p, 'last_name'),
                "gender": 'Mr.' if get_passenger_field(p, 'gender', 'mr').lower() == 'mr' else ('Mrs.' if get_passenger_field(p, 'gender', 'mr').lower() == 'mrs' else 'Ms.'),
                "type": get_passenger_field(p, 'passenger_type', 'Adult').capitalize(),
                "nationality": get_passenger_field(p, 'nationality'),
                "date_of_birth": get_passenger_field(p, 'date_of_birth'),
                "passport_number": get_passenger_field(p, 'passport_number'),
                "email": get_passenger_field(p, 'email'),
                "phone": get_passenger_field(p, 'phone'),
                "seat_preference": get_passenger_field(p, 'seat_preference'),
                "special_requirements": get_passenger_field(p, 'special_requirements'),
            }
            passengers_data.append(passenger_info)
        
        data = {
            "id": activity.id,
            "title": activity.title,
            "description": activity.description,
            "section_name": activity.section.section_name if activity.section else "",
            "section_code": activity.section.section_code if activity.section else "",
            "required_trip_type": activity.get_required_trip_type_display() if hasattr(activity, 'get_required_trip_type_display') else activity.required_trip_type,
            "required_origin": activity.required_origin if hasattr(activity, 'required_origin') else "",
            "required_destination": activity.required_destination if hasattr(activity, 'required_destination') else "",
            "required_departure_date": activity.required_departure_date.strftime("%Y-%m-%d") if activity.required_departure_date else "",
            "required_return_date": activity.required_return_date.strftime("%Y-%m-%d") if activity.required_return_date else "",
            "required_travel_class": activity.get_required_travel_class_display() if hasattr(activity, 'get_required_travel_class_display') else activity.required_travel_class,
            "required_passengers": activity.required_passengers if hasattr(activity, 'required_passengers') else 0,
            "required_children": activity.required_children if hasattr(activity, 'required_children') else 0,
            "required_infants": activity.required_infants if hasattr(activity, 'required_infants') else 0,
            "instructions": activity.instructions if hasattr(activity, 'instructions') else "",
            "due_date": activity.due_date.strftime("%B %d, %Y") if activity.due_date else "",
            "activity_code": activity.activity_code if hasattr(activity, 'activity_code') else "",
            "is_code_active": activity.is_code_active if hasattr(activity, 'is_code_active') else False,
            "total_points": float(activity.total_points) if activity.total_points else 100,
            "grades_released": activity.grades_released if hasattr(activity, 'grades_released') else False,
            "passengers": passengers_data,
            "segments": [
                {
                    "origin": s.origin,
                    "destination": s.destination,
                    "departure_date": s.departure_date.strftime("%Y-%m-%d") if s.departure_date else "",
                    "order": s.order
                }
                for s in activity.segments.all()
            ]
        }
        
        return Response(data)
        
    except Activity.DoesNotExist:
        return Response(
            {"error": "Activity not found or you don't have permission to view it"},
            status=404
        )
    except Exception as e:
        traceback.print_exc()
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=500
        )


@api_view(['POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def activate_activity(request, activity_id):
    try:
        activity = get_object_or_404(
            Activity,
            id=activity_id,
            section__instructor=request.user
        )
        
        if activity.is_code_active and activity.activity_code:
            return Response({
                "message": "Activity is already activated",
                "activity_code": activity.activity_code,
                "already_active": True
            })
        
        if not activity.activity_code:
            max_attempts = 10
            for _ in range(max_attempts):
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                if not Activity.objects.filter(activity_code=code).exclude(id=activity_id).exists():
                    activity.activity_code = code
                    break
            else:
                return Response(
                    {"error": "Could not generate a unique activity code. Please try again."},
                    status=500
                )
        
        activity.is_code_active = True
        
        if hasattr(activity, 'code_generated_at'):
            activity.code_generated_at = timezone.now()
        
        if hasattr(activity, 'status'):
            activity.status = 'published'
        
        activity.save()
        
        enrolled_students_count = Activity_Student_Bind(activity)
        
        return Response({
            "message": "Activity Activated Successfully",
            "activity_code": activity.activity_code,
            "already_active": False,
            "students_notified": enrolled_students_count
        })

    except Activity.DoesNotExist:
        return Response(
            {"error": "Activity not found or you don't have permission to activate it"},
            status=404
        )
    except Exception as e:
        traceback.print_exc()
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=500
        )

@api_view(['POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def release_activity_grades(request, activity_id):
    """
    Toggle the release status of grades for an activity.
    When released, students can see their scores.
    """
    try:
        activity = get_object_or_404(
            Activity,
            id=activity_id,
            section__instructor=request.user
        )
        
        # Toggle released status
        activity.grades_released = not activity.grades_released
        activity.save()
        
        print(f"? Grades for activity {activity_id} release status set to: {activity.grades_released}")
        
        return Response({
            "message": "Grades released successfully" if activity.grades_released else "Grades hide successfully",
            "grades_released": activity.grades_released
        }, status=status.HTTP_200_OK)
        
    except Activity.DoesNotExist:
        return Response(
            {"error": "Activity not found or you don't have permission"},
            status=404
        )
    except Exception as e:
        traceback.print_exc()
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=500
        )


def calculate_submission_score(activity, booking):
    """
    Advanced Deductive Scoring System (Aviation Professional Mode)
    Matches the frontend calculation: 
     - Compliance: 40% (Origin, Destination, Class, Trip Type)
     - Passengers: 30% (Counts, Passenger Details)
     - Completion: 30% (Departure Date, Return Date)
    """
    if not booking:
        return 0.0
        
    total_points = float(activity.total_points or 100)
    
    # Extract actual details
    first_detail = booking.details.first()
    if not first_detail:
        return 0.0

    actual_origin = first_detail.schedule.flight.route.origin_airport.code.lower() if first_detail.schedule.flight.route.origin_airport else ""
    actual_destination = first_detail.schedule.flight.route.destination_airport.code.lower() if first_detail.schedule.flight.route.destination_airport else ""
    actual_class = first_detail.seat_class.name.lower() if first_detail.seat_class else ""
    actual_trip_type = booking.trip_type

    req_origin = (activity.required_origin or "").lower()
    req_destination = (activity.required_destination or "").lower()
    req_class = (activity.required_travel_class or "").lower()
    req_trip_type = activity.required_trip_type

    # --- 1. Compliance (40% base) ---
    comp_penalty = 0
    if req_origin and req_origin != actual_origin:
        comp_penalty += 40
    if req_destination and req_destination != actual_destination:
        comp_penalty += 40
    if req_trip_type and req_trip_type != actual_trip_type:
        comp_penalty += 20
    if req_class and req_class != actual_class:
        comp_penalty += 10
        
    comp_score = max(0, (total_points * 0.4) - (comp_penalty / 100.0 * total_points))

    # --- 2. Passengers (30% base) ---
    pax_penalty = 0
    unique_passengers = {d.passenger_id: d.passenger for d in booking.details.all() if d.passenger}.values()
    
    pax_counts = {'adult': 0, 'child': 0, 'infant': 0}
    for p in unique_passengers:
        t = (p.passenger_type or 'adult').lower()
        if t in pax_counts: pax_counts[t] += 1
    
    if pax_counts['adult'] != activity.required_passengers: pax_penalty += 10
    if pax_counts['child'] != activity.required_children: pax_penalty += 5
    if pax_counts['infant'] != activity.required_infants: pax_penalty += 5

    expected_passengers = activity.passengers.all()
    for exp in expected_passengers:
        actual = next((p for p in unique_passengers if p.first_name.lower() == exp.first_name.lower() and p.last_name.lower() == exp.last_name.lower()), None)
        if not actual:
            pax_penalty += 25
        else:
            actual_gen = (getattr(actual, 'title', '') or getattr(actual, 'gender', '') or '').lower().replace('.', '').strip()
            exp_gen = (exp.gender or '').lower().replace('.', '').strip()
            if actual_gen != exp_gen: pax_penalty += 2
            
            if actual.date_of_birth != exp.date_of_birth: pax_penalty += 5
            if (actual.nationality or '').lower() != (exp.nationality or '').lower(): pax_penalty += 3
            if (actual.passport_number or '').strip() != (exp.passport_number or '').strip(): pax_penalty += 10

    pax_score = max(0, (total_points * 0.3) - (pax_penalty / 100.0 * total_points))

    # --- 3. Completion (30% base) ---
    date_penalty = 0
    actual_departure_date = None
    actual_return_date = None
    
    for d in booking.details.all():
        o_code = d.schedule.flight.route.origin_airport.code.lower() if d.schedule.flight.route.origin_airport else ""
        d_code = d.schedule.flight.route.destination_airport.code.lower() if d.schedule.flight.route.destination_airport else ""
        
        if req_origin and o_code == req_origin:
            actual_departure_date = d.schedule.departure_time.date()
        if req_trip_type == 'round_trip' and req_origin and d_code == req_origin:
            actual_return_date = d.schedule.departure_time.date()

    if activity.required_departure_date and activity.required_departure_date != actual_departure_date:
        date_penalty += 15
    if activity.required_trip_type == 'round_trip' and activity.required_return_date and activity.required_return_date != actual_return_date:
        date_penalty += 15

    completion_score = max(0, (total_points * 0.3) - (date_penalty / 100.0 * total_points))

    # --- 4. Final Calculation ---
    final_grade = comp_score + pax_score + completion_score
    return round(float(final_grade), 1)


def get_flight_notification_html(student, activity, section):
    """
    Generates a beautiful Boarding Pass style HTML email for activity notifications.
    """
    origin = (activity.required_origin or "SYS").upper()
    destination = (activity.required_destination or "TASK").upper()
    due_date = activity.due_date.strftime('%B %d, %Y') if activity.due_date else 'No due date'
    title = activity.title
    section_name = section.section_name
    first_name = student.first_name
    total_points = float(activity.total_points) if activity.total_points else 100
    
    # Try to get the base URL from settings, or default to a common one
    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
    login_url = f"{base_url}/login"

    release_date = timezone.now().strftime('%B %d, %Y')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      .boarding-pass {{
        border: 1px solid #e5e7eb;
        border-radius: 0px;
        overflow: hidden;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        max-width: 600px;
        margin: 20px auto;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      }}
      .header {{
        background: linear-gradient(135deg, #FF579A 0%, #E91E63 100%);
        color: white;
        padding: 24px;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-weight: 900;
        font-size: 14px;
      }}
      .hero {{
        background-color: #ffffff;
        padding: 40px 30px;
        text-align: center;
        position: relative;
      }}
      .status-badge {{
        background-color: #FFF0F6;
        color: #FF579A;
        padding: 6px 20px;
        border-radius: 0px;
        font-weight: 900;
        font-size: 11px;
        display: inline-block;
        margin-bottom: 20px;
        letter-spacing: 1px;
        border: 1px solid #FF579A;
      }}
      .details-container {{
        padding: 0 30px 40px;
      }}
      .details-box {{
        background: #FFF9FB;
        border: 1px solid #FFF0F6;
        border-radius: 0px;
        padding: 24px;
      }}
      .detail-label {{
        font-size: 10px;
        text-transform: uppercase;
        color: #FF579A;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
      }}
      .detail-value {{
        font-size: 15px;
        font-weight: 700;
        color: #C2185B;
      }}
      .footer {{
        background-color: #FFF0F6;
        padding: 20px;
        text-align: center;
        font-size: 11px;
        color: #FF579A;
        font-weight: 500;
      }}
    </style>
    </head>
    <body>
      <div class="boarding-pass">
        <div class="header">FBS | Activity Dispatch</div>
        <div class="hero">
          <div class="status-badge">BOARDING NOW</div>
          <h1 style="margin:0; font-size: 28px; color: #1e3a8a; font-weight: 900; letter-spacing: -0.5px;">Flight Notification</h1>
          <p style="color: #64748b; font-size: 15px; margin-top: 10px; font-weight: 500;">Hello <strong>{first_name}</strong>, a new activity has been activated for your section.</p>
        </div>
        
        <div class="details-container">
           <div class="details-box">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td width="100%">
                    <div class="detail-label">Activity Name</div>
                    <div class="detail-value" style="font-size: 18px; color: #1e3a8a;">{title}</div>
                  </td>
                </tr>
                <tr><td height="20"></td></tr>
                <tr>
                  <td width="100%">
                     <table width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                          <td width="33%">
                            <div class="detail-label">Date Released</div>
                            <div class="detail-value">{release_date}</div>
                          </td>
                          <td width="33%" style="text-align: center;">
                            <div class="detail-label">Due Date</div>
                            <div class="detail-value">{due_date}</div>
                          </td>
                          <td width="33%" style="text-align: right;">
                            <div class="detail-label">Total Points</div>
                            <div class="detail-value" style="color: #7c3aed;">{total_points:.0f} pts</div>
                          </td>
                        </tr>
                        <tr><td height="12"></td><td></td><td></td></tr>
                        <tr>
                          <td colspan="3">
                            <div class="detail-label">Gate / Section</div>
                            <div class="detail-value">{section_name}</div>
                          </td>
                        </tr>
                     </table>
                  </td>
                </tr>
              </table>
           </div>
        </div>
        
        <div class="footer">
          Terminal 1 | This is an automated flight system notification.<br>
          &copy; {timezone.now().year} Flight Booking System. Verified Instructor Dispatch.
        </div>
      </div>
    </body>
    </html>
    """

def _send_activity_notification_worker(activity, enrolled_students, section):
    """Background worker to send emails without blocking the main request"""
    for enrollment in enrolled_students:
        student = enrollment.student
        if student.email:
            subject = f"New Activity Activated: {activity.title}"
            message = (
                f"Hello {student.first_name},\n\n"
                f"A new activity '{activity.title}' has been released in your section: "
                f"{section.section_name} ({section.section_code}).\n\n"
                f"You can now access and complete this task in the Flight Booking System.\n\n"
                f"Due Date: {activity.due_date.strftime('%B %d, %Y') if activity.due_date else 'No due date'}\n\n"
                f"Good luck!\n\n"
                f"--- This is an automated notification ---"
            )
            html_message = get_flight_notification_html(student, activity, section)
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL or 'fbs@example.com',
                    [student.email],
                    fail_silently=True,
                    html_message=html_message
                )
            except Exception as e:
                print(f"Error sending activation email to {student.email}: {str(e)}")

def Activity_Student_Bind(activity):
    from .models import ActivityStudentBinding
    
    section = activity.section
    enrolled_students = SectionEnrollment.objects.filter(section=section).select_related('student', 'student__user')
    students_bound = 0
    
    # Process bindings synchronously (fast database operations)
    for enrollment in enrolled_students:
        student = enrollment.student
        binding, created = ActivityStudentBinding.objects.get_or_create(
            activity=activity,
            student=student,
            defaults={
                'assigned_at': timezone.now(),
                'status': 'assigned'
            }
        )
        if created:
            students_bound += 1
            
    # Dispatch emails in the background (slow network operations)
    if enrolled_students.exists():
        # Pass necessary data to the thread
        # Note: We pass the queryset or list to ensure the thread can access the data
        email_thread = threading.Thread(
            target=_send_activity_notification_worker, 
            args=(activity, list(enrolled_students), section)
        )
        email_thread.daemon = True # Ensure it doesn't block server shutdown
        email_thread.start()
    
    return students_bound


@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated, IsInstructor])
def get_activity_submissions(request, activity_id):
    """
    Get all student submissions for a specific activity.
    Shows the status of each student enrolled in the section.
    """
    try:
        # 1. Get activity and verify instructor ownership
        activity = get_object_or_404(
            Activity.objects.select_related('section'),
            id=activity_id,
            section__instructor=request.user
        )
        
        # 2. Get all students enrolled in this section
        enrollments = SectionEnrollment.objects.filter(
            section=activity.section
        ).select_related('student', 'student__user')
        
        submissions_data = []
        
        for enrollment in enrollments:
            student = enrollment.student
            
            # Find the binding for this activity
            binding = ActivityStudentBinding.objects.filter(
                activity=activity,
                student=student
            ).first()
            
            # Find any confirmed booking for this activity by this student
            # We look for ANY booking linked to this activity for this user
            booking = Booking.objects.filter(
                user=student.user,
                activity=activity
            ).order_by('-created_at').first()
            
            submission = {
                "student_id": student.id,
                "student_number": student.student_number,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "status": binding.status if binding else "not_assigned",
                "binding_id": binding.id if binding else None,
                "grade": float(binding.grade) if (binding and binding.grade is not None) else None,
                "submitted_at": binding.submitted_at.isoformat() if binding and binding.submitted_at else None,
                "booking": None
            }
            
            if booking:
                submission["booking"] = {
                    "id": booking.id,
                    "status": booking.status,
                    "is_practice": booking.is_practice,
                    "total_amount": float(booking.total_amount),
                    "trip_type": booking.get_trip_type_display(),
                    "created_at": booking.created_at.isoformat(),
                    "details": [
                        {
                            "origin": d.schedule.flight.route.origin_airport.code,
                            "destination": d.schedule.flight.route.destination_airport.code,
                            "departure": d.schedule.departure_time.isoformat(),
                            "flight_number": d.schedule.flight.flight_number,
                            "seat_class": d.seat_class.name if d.seat_class else "N/A"
                        } for d in booking.details.all()
                    ],
                    "passengers": [
                        {
                            "name": p.get_full_name(),
                            "type": p.passenger_type
                        } for p in {d.passenger_id: d.passenger for d in booking.details.all()}.values()
                    ]
                }
                
                # If there's a confirmed booking but the binding is still 'assigned' or 'in_progress',
                # we should probably treat it as 'submitted' for the instructor's view
                if submission["status"] in ["assigned", "in_progress"] and booking.status == "Confirmed":
                    submission["status"] = "submitted"

                # Automatic Grading
                score = calculate_submission_score(activity, booking)
                submission["grade"] = score
                
                # Update binding with the score if it matches confirmed criteria
                if binding and booking.status == "Confirmed":
                    if binding.grade != Decimal(str(score)):
                        binding.grade = score
                        binding.status = 'graded'
                        binding.save()
                        submission["status"] = "graded"
            
            submissions_data.append(submission)
            
        # Sort submissions by grade descending (highest score first)
        submissions_data.sort(key=lambda x: x['grade'] if x['grade'] is not None else -1, reverse=True)
            
        return Response({
            "activity_id": activity.id,
            "activity_title": activity.title,
            "total_points": float(activity.total_points) if activity.total_points else 100,
            "grades_released": activity.grades_released,
            "submissions": submissions_data,
            "total_students": len(submissions_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# USER PROFILE MANAGEMENT
# ==========================================
@api_view(['GET', 'PATCH'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        data = serializer.data
        # Add avatar URL manually since it's on the profile
        if hasattr(user, 'userprofile') and user.userprofile.avatar:
            data['avatar'] = request.build_absolute_uri(user.userprofile.avatar.url)
        else:
            data['avatar'] = None
        return Response(data)

    elif request.method == 'PATCH':
        # Use our new serializer
        from .serializers import UserProfileUpdateSerializer
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # Return updated data with full avatar URL
            response_data = serializer.data
            if hasattr(user, 'userprofile') and user.userprofile.avatar:
                response_data['avatar'] = request.build_absolute_uri(user.userprofile.avatar.url)
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# LOGOUT VIEW
# ==========================================
@api_view(['POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout - Deactivate the current session only
    """
    try:
        session_obj = request.session_obj
        session_obj.deactivate()
        
        print(f"? Session {session_obj.id} deactivated for user {request.user.username}")
        
        return Response({
            "message": "Logged out successfully"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"? Error during logout: {str(e)}")
        return Response({
            "error": "Logout failed"
        }, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# SESSION VALIDATION
# ==========================================
@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def validate_session(request):
    """
    Validate current session
    """
    try:
        user = request.user
        session_obj = request.session_obj
        profile = user.userprofile
        
        return Response({
            "valid": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": profile.role
            },
            "session": {
                "id": session_obj.id,
                "role": session_obj.role,
                "created_at": session_obj.created_at.isoformat(),
                "last_activity": session_obj.last_activity.isoformat()
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"? Session validation error: {str(e)}")
        return Response({
            "valid": False,
            "error": "Session invalid"
        }, status=status.HTTP_401_UNAUTHORIZED)


# ==========================================
# SESSION MANAGEMENT - List all user sessions
# ==========================================
@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def list_sessions(request):
    """
    List all active sessions for the current user
    """
    try:
        sessions = UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-last_activity')
        
        sessions_data = [
            {
                "id": s.id,
                "role": s.role,
                "created_at": s.created_at.isoformat(),
                "last_activity": s.last_activity.isoformat(),
                "ip_address": s.ip_address,
                "is_current": s.id == request.session_obj.id
            }
            for s in sessions
        ]
        
        return Response({
            "sessions": sessions_data,
            "total": len(sessions_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)




# ==========================================
# 3. STUDENT DASHBOARD (Session-Based)
# ==========================================
@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])  # NEW: Use custom auth
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    user = request.user
    session_obj = request.session_obj  # Our UserSession object
    
    print(f"\n{'='*60}")
    print(f"? STUDENT DASHBOARD REQUEST")
    print(f"{'='*60}")
    print(f"User: {user.username} (ID: {user.id})")
    print(f"Session Token: {session_obj.session_token[:16]}...")
    print(f"Session Role: {session_obj.role}")
    print(f"Session ID: {session_obj.id}")
    
    # 1. Verify session role
    try:
        if session_obj.role != 'student':
            print(f"? ERROR: Session role is '{session_obj.role}', not 'student'")
            return Response({
                "error": "Access denied. This session is not authorized for student access.",
                "session_role": session_obj.role,
                "required_role": "student"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Double-check with UserProfile
        if not hasattr(user, 'userprofile') or user.userprofile.role != 'student':
            print(f"? ERROR: User profile role mismatch")
            return Response({"error": "Access denied. Student access only."}, status=status.HTTP_403_FORBIDDEN)
        
        print("? Session and profile verified as student")
            
    except Exception as e:
        print(f"? ERROR during verification: {str(e)}")
        traceback.print_exc()
        return Response({"error": "Profile verification failed."}, status=status.HTTP_403_FORBIDDEN)

    # 2. Get Students record
    student = None
    
    # Try multiple methods
    if hasattr(user, 'student_profile'):
        student = user.student_profile
        print(f"? Method 1: Found student via related_name")
    
    if not student:
        try:
            student = Students.objects.get(user=user)
            print(f"? Method 2: Found student via user FK")
        except Students.DoesNotExist:
            print("?? Method 2: No Students record with user FK")
        except Exception as e:
            print(f"?? Method 2 error: {str(e)}")
    
    if not student:
        try:
            student = Students.objects.get(email=user.email)
            print(f"? Method 3: Found student via email match")
        except Students.DoesNotExist:
            print("?? Method 3: No Students record with matching email")
        except Exception as e:
            print(f"?? Method 3 error: {str(e)}")
    
    if not student:
        print("? FATAL: Could not find Students record!")
        return Response({
            "error": "Student record not found. Please contact your administrator.",
            "not_enrolled": True,
            "debug_info": {
                "user_id": user.id,
                "user_email": user.email,
                "username": user.username
            }
        }, status=status.HTTP_403_FORBIDDEN)
    
    print(f"? Student record: {student.first_name} {student.last_name} (#{student.student_number})")
    
    # 3. Get enrolled section
    enrollment = SectionEnrollment.objects.filter(student=student, is_active=True).select_related('section').first()
    
    # Check if enrollment exists AND section is active
    if not enrollment or not enrollment.section.is_active:
        print("?? Student not enrolled in any session or section is disabled")
        return Response({
            'error': 'You are not enrolled in any section. Please contact your administrator.',
            'not_enrolled': True,
            'user': {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'student_number': student.student_number,
                'mi': student.mi if student.mi else '',
                'phone_number': student.phone_number if student.phone_number else ''
            },
            'section': None,
            'activities': [],
            'total_activities': 0,
        }, status=status.HTTP_403_FORBIDDEN)
    
    section = enrollment.section
    print(f"? Enrolled in: {section.section_name} ({section.section_code})")
    
    # 4. Get activities - either active OR already has progress (submitted/graded)
    from django.db.models import Q
    section_activities = Activity.objects.filter(
        Q(section=section) & 
        (Q(is_code_active=True) | Q(student_bindings__student=student, student_bindings__status__in=['submitted', 'graded']))
    ).distinct().order_by('-created_at')
    
    print(f"  Total visible activities: {section_activities.count()}")
    for act in section_activities:
        reason = "active" if act.is_code_active else "completed/graded"
        print(f"    - [{act.id}] {act.title} ({reason})")
    
    # 5. Build activities data
    from .models import ActivityStudentBinding
    
    activities_data = []
    for activity in section_activities:
        binding, created = ActivityStudentBinding.objects.get_or_create(
            activity=activity,
            student=student,
            defaults={
                'assigned_at': timezone.now(),
                'status': 'assigned'
            }
        )
        
        if created:
            print(f"  ? Created binding: {activity.title}")
        
        # Search for a confirmed booking for this activity
        booking_obj = Booking.objects.filter(
            user=user,
            activity=activity,
            status='Confirmed',
            is_practice=False
        ).first()

        if booking_obj and (binding.grade is None or binding.status in ['assigned', 'in_progress', 'submitted']):
            score = calculate_submission_score(activity, booking_obj)
            binding.grade = score
            binding.status = 'graded'
            binding.save()
            print(f"  ? Auto-graded dashboard activity {activity.id}: {score}")

        # ? Manual Grade Release Check
        effective_grade = float(binding.grade) if (binding.grade is not None and activity.grades_released) else None

        activities_data.append({
            'id': activity.id,
            'title': activity.title,
            'description': activity.description or '',
            'activity_type': activity.activity_type,
            'due_date': activity.due_date.strftime('%B %d, %Y') if activity.due_date else None,
            'total_points': float(activity.total_points),
            'created_at': activity.created_at.isoformat(),
            'required_trip_type': activity.required_trip_type,
            'required_origin': activity.required_origin,
            'required_destination': activity.required_destination,
            'required_travel_class': activity.required_travel_class,
            'required_passengers': activity.required_passengers,
            'required_children': activity.required_children,
            'required_infants': activity.required_infants,
            'status': binding.status,
            'assigned_at': binding.assigned_at.isoformat(),
            'is_active': activity.is_code_active,
            'section_id': section.id,
            'section_name': section.section_name,
            'section_code': section.section_code,
            'grade': effective_grade,
            'submitted_at': binding.submitted_at.isoformat() if binding.submitted_at else None,
            
            # ? NEW: Add completion status and booking ID
            'completed': booking_obj is not None,
            'confirmed_booking_id': booking_obj.id if booking_obj else None
        })
    
    section_data = {
        'id': section.id,
        'section_name': section.section_name,
        'section_code': section.section_code,
        'semester': section.semester,
        'academic_year': section.academic_year,
        'schedule': section.schedule,
        'description': section.description,
        'enrolled_at': enrollment.enrolled_at.strftime('%Y-%m-%d'),
        'activities_count': len(activities_data)
    }
    
    print(f"? Returning {len(activities_data)} activities")
    print(f"{'='*60}\n")
    
    return Response({
        'user': {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'student_number': student.student_number,
            'mi': student.mi if student.mi else '',
            'phone_number': student.phone_number if student.phone_number else ''
        },
        'section': section_data,
        'activities': activities_data,
        'total_activities': len(activities_data),
        'session_info': {
            'session_id': session_obj.id,
            'role': session_obj.role,
            'last_activity': session_obj.last_activity.isoformat()
        }
    }, status=status.HTTP_200_OK)



@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def student_activity_details(request, activity_id):
    """
    Get detailed information about a specific activity for the authenticated student
    ? UPDATED VERSION - Now includes activity_code for verification
    """
    user = request.user
    session_obj = request.session_obj
    
    print(f"\n{'='*60}")
    print(f"? STUDENT ACTIVITY DETAILS REQUEST")
    print(f"{'='*60}")
    print(f"User: {user.username} (ID: {user.id})")
    print(f"Activity ID: {activity_id}")
    print(f"Session Role: {session_obj.role}")
    
    # 1. Verify session role
    try:
        if session_obj.role != 'student':
            print(f"? ERROR: Session role is '{session_obj.role}', not 'student'")
            return Response({
                "error": "Access denied. This session is not authorized for student access.",
                "session_role": session_obj.role,
                "required_role": "student"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Double-check with UserProfile
        if not hasattr(user, 'userprofile') or user.userprofile.role != 'student':
            print(f"? ERROR: User profile role mismatch")
            return Response({
                "error": "Access denied. Student access only."
            }, status=status.HTTP_403_FORBIDDEN)
        
        print("? Session and profile verified as student")
            
    except Exception as e:
        print(f"? ERROR during verification: {str(e)}")
        traceback.print_exc()
        return Response({
            "error": "Profile verification failed."
        }, status=status.HTTP_403_FORBIDDEN)

    # 2. Get Students record
    student = None
    
    if hasattr(user, 'student_profile'):
        student = user.student_profile
        print(f"? Found student via related_name")
    
    if not student:
        try:
            student = Students.objects.get(user=user)
            print(f"? Found student via user FK")
        except Students.DoesNotExist:
            print("?? No Students record with user FK")
        except Exception as e:
            print(f"?? Error: {str(e)}")
    
    if not student:
        try:
            student = Students.objects.get(email=user.email)
            print(f"? Found student via email match")
        except Students.DoesNotExist:
            print("?? No Students record with matching email")
        except Exception as e:
            print(f"?? Error: {str(e)}")
    
    if not student:
        print("? FATAL: Could not find Students record!")
        return Response({
            "error": "Student record not found. Please contact your administrator.",
            "debug_info": {
                "user_id": user.id,
                "user_email": user.email,
                "username": user.username
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    print(f"? Student record: {student.first_name} {student.last_name} (#{student.student_number})")
    
    # 3. Get the activity
    try:
        activity = Activity.objects.select_related('section', 'section__instructor').prefetch_related('passengers').get(
            id=activity_id, 
            is_code_active=True
        )
        print(f"? Activity found: {activity.title}")
        print(f"? Activity code: {activity.activity_code}")
    except Activity.DoesNotExist:
        print(f"? Activity {activity_id} not found or inactive")
        return Response({
            "error": "Activity not found or is no longer active."
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"? Error fetching activity: {str(e)}")
        traceback.print_exc()
        return Response({
            "error": "Failed to retrieve activity details.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 4. Verify student has access to this activity (enrolled in section)
    try:
        enrollment = SectionEnrollment.objects.filter(
            student=student,
            section=activity.section
        ).first()
        
        if not enrollment:
            print(f"? Student not enrolled in section: {activity.section.section_code}")
            return Response({
                "error": "Access denied. You are not enrolled in the section for this activity.",
                "section_code": activity.section.section_code
            }, status=status.HTTP_403_FORBIDDEN)
        
        print(f"? Student enrolled in section: {activity.section.section_code}")
    except Exception as e:
        print(f"? Error checking enrollment: {str(e)}")
        traceback.print_exc()
        return Response({
            "error": "Failed to verify enrollment.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 5. Get or create ActivityStudentBinding
    try:
        binding, created = ActivityStudentBinding.objects.get_or_create(
            activity=activity,
            student=student,
            defaults={
                'assigned_at': timezone.now(),
                'status': 'assigned'
            }
        )
        
        if created:
            print(f"? Created new activity binding")
        else:
            print(f"? Using existing binding - Status: {binding.status}")
            
        # ? NEW: Automatic Grading Trigger for Student View
        booking_obj = Booking.objects.filter(
            user=user, activity=activity, status='Confirmed', is_practice=False
        ).first()

        if booking_obj and (binding.grade is None or binding.status in ['assigned', 'in_progress', 'submitted']):
            score = calculate_submission_score(activity, booking_obj)
            binding.grade = score
            binding.status = 'graded'
            binding.save()
            print(f"? Auto-graded student {user.username}: {score}")
            
    except Exception as e:
        print(f"? Error with ActivityStudentBinding: {str(e)}")
        traceback.print_exc()
        return Response({
            "error": "Failed to create or retrieve activity binding.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 6. Get instructor information
    instructor_data = None
    try:
        if activity.section and activity.section.instructor:
            instructor = activity.section.instructor
            instructor_data = {
                'id': instructor.id,
                'first_name': instructor.first_name,
                'last_name': instructor.last_name,
                'email': instructor.email,
                'employee_id': instructor.employee_id if hasattr(instructor, 'employee_id') else None
            }
            print(f"? Instructor: {instructor.first_name} {instructor.last_name}")
        else:
            print("?? No instructor assigned to this section")
    except Exception as e:
        print(f"?? Error fetching instructor: {str(e)}")
        # Continue without instructor data
    
    # 7. Get passenger information from ActivityPassenger model
    passengers_data = []
    try:
        # Get passengers from the activity
        activity_passengers = activity.passengers.all() if hasattr(activity, 'passengers') else []
        
        for passenger in activity_passengers:
            passenger_dict = {
                'type': passenger.passenger_type.capitalize() if hasattr(passenger, 'passenger_type') else 'Adult',
                'gender': 'Mr.' if getattr(passenger, 'gender', 'mr').lower() == 'mr' else 'Mrs.' if getattr(passenger, 'gender', 'mr').lower() == 'mrs' else 'Ms.',
                'first_name': getattr(passenger, 'first_name', ''),
                'last_name': getattr(passenger, 'last_name', ''),
                'middle_initial': getattr(passenger, 'middle_name', '') or getattr(passenger, 'middle_initial', ''),
                'nationality': getattr(passenger, 'nationality', 'Philippines'),
                'passport': getattr(passenger, 'passport_number', ''),
                'seat_preference': getattr(passenger, 'seat_preference', 'Window'),
                'has_reservation': getattr(passenger, 'has_reservation', False),
                'is_pwd': getattr(passenger, 'is_pwd', False)
            }
            
            # Handle date of birth
            if hasattr(passenger, 'date_of_birth') and passenger.date_of_birth:
                dob = passenger.date_of_birth
                passenger_dict['birth_day'] = str(dob.day).zfill(2)
                passenger_dict['birth_month'] = dob.strftime('%B')
                passenger_dict['birth_year'] = str(dob.year)
            else:
                passenger_dict['birth_day'] = '01'
                passenger_dict['birth_month'] = 'January'
                passenger_dict['birth_year'] = '1990'
            
            passengers_data.append(passenger_dict)
        
        print(f"? Found {len(passengers_data)} passengers from ActivityPassenger model")
        
    except Exception as e:
        print(f"?? Error fetching passengers: {str(e)}")
        traceback.print_exc()
        # Continue without passenger data
    
    # 8. Build response data
    try:
        # Helper functions for safe date formatting
        def safe_date_format(date_obj, format_string='%B %d, %Y'):
            """Safely format date, return None if date is None"""
            if date_obj:
                try:
                    return date_obj.strftime(format_string)
                except:
                    return str(date_obj)
            return None
        
        def safe_iso_format(date_obj):
            """Safely convert to ISO format, return None if date is None"""
            if date_obj:
                try:
                    return date_obj.isoformat()
                except:
                    return str(date_obj)
            return None
        
        # Search for a confirmed booking for this activity
        booking_obj = Booking.objects.filter(
            user=user,
            activity=activity,
            status='Confirmed',
            is_practice=False
        ).first()

        # Build activity data with PROPER field mapping
        activity_data = {
            'id': activity.id,
            'title': activity.title,
            'description': activity.description or activity.instructions or '',  # Use description OR instructions
            'activity_type': activity.activity_type,
            'due_date': safe_date_format(activity.due_date),
            'total_points': float(activity.total_points) if activity.total_points else 0.0,
            'created_at': safe_iso_format(activity.created_at),
            
            # Flight requirements - map from database field names
            'required_trip_type': activity.required_trip_type or '',
            'required_origin': activity.required_origin or '',
            'required_destination': activity.required_destination or '',
            'required_travel_class': activity.required_travel_class or '',
            'required_passengers': activity.required_passengers or 0,
            'required_children': activity.required_children or 0,
            'required_infants': activity.required_infants or 0,
            
            # Dates
            'departure_date': safe_iso_format(getattr(activity, 'required_departure_date', None)),
            'arrival_date': safe_iso_format(getattr(activity, 'required_return_date', None)),
            
            # Section info
            'section_id': activity.section.id,
            'section_name': activity.section.section_name,
            'section_code': activity.section.section_code,
            
            # Student progress
            'status': binding.status,
            'assigned_at': safe_iso_format(binding.assigned_at),
            'submitted_at': safe_iso_format(binding.submitted_at) if binding.submitted_at else None,
            'grade': float(binding.grade) if (binding.grade is not None and activity.grades_released) else None,
            'feedback': binding.feedback or '',
            
            # Activity status
            'is_active': activity.is_code_active,
            
            # Activity code for verification
            'activity_code': activity.activity_code or '',
            
            'segments': [
                {
                    'origin': s.origin,
                    'destination': s.destination,
                    'departure_date': s.departure_date.isoformat() if s.departure_date else None,
                    'order': s.order
                }
                for s in activity.segments.all().order_by('order')
            ],
            
            # Booking link
            # NEW: Add completion status and booking ID
            'completed': booking_obj is not None,
            'confirmed_booking_id': booking_obj.id if booking_obj else None
        }
        
        response_data = {
            'activity': activity_data,
            'student': {
                'id': student.id,
                'student_number': student.student_number,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email
            },
            'session_info': {
                'session_id': session_obj.id,
                'role': session_obj.role,
                'last_activity': safe_iso_format(session_obj.last_activity)
            }
        }
        
        # Add instructor data if available
        if instructor_data:
            response_data['instructor'] = instructor_data
        
        # Add passenger data if available
        if passengers_data:
            response_data['passengers'] = passengers_data
        
        print(f"? Returning activity details:")
        print(f"   - Title: {activity.title}")
        print(f"   - Code: {activity.activity_code}")
        print(f"   - Origin: {activity.required_origin} ? Destination: {activity.required_destination}")
        print(f"   - Passengers: {len(passengers_data)}")
        print(f"{'='*60}\n")
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"? Error building response data: {str(e)}")
        traceback.print_exc()
        return Response({
            "error": "Failed to build response data.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['POST'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def submit_grade(request, activity_id, student_id):
    """
    Submit or update a grade for a student's activity submission.
    """
    try:
        # 1. Verify instructor owns this activity
        activity = get_object_or_404(
            Activity,
            id=activity_id,
            section__instructor=request.user
        )
        
        # 2. Get the binding
        binding = get_object_or_404(
            ActivityStudentBinding,
            activity=activity,
            student_id=student_id
        )
        
        # 3. Update grade and status
        grade_value = request.data.get('grade')
        feedback_value = request.data.get('feedback', '')
        
        if grade_value is None:
            return Response({"error": "Grade is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        binding.grade = grade_value
        binding.feedback = feedback_value
        binding.status = 'graded'
        binding.save()
        
        return Response({
            "message": "Grade submitted successfully",
            "grade": float(binding.grade),
            "status": binding.status
        }, status=status.HTTP_200_OK)
    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ============================================================
# NEW: GET PRACTICE BOOKINGS (STUDENT)
# ============================================================
@api_view(['GET'])
@authentication_classes([MultiSessionTokenAuthentication])
@permission_classes([IsAuthenticated])
def get_student_practice_bookings(request):
    """
    Get all practice bookings for the authenticated student.
    Returns status mapped to success/fail/pending.
    """
    try:
        # Get user's practice bookings, newest first
        bookings = Booking.objects.filter(
            user=request.user, 
            is_practice=True
        ).prefetch_related(
            'details',
            'details__schedule__flight__route__origin_airport',
            'details__schedule__flight__route__destination_airport'
        ).order_by('-created_at')
        
        practice_bookings_data = []
        
        for booking in bookings:
            # Map booking status to our UI categories
            ui_status = 'pending'
            if booking.status in ['Confirmed', 'Completed', 'checkin', 'boarding']:
                ui_status = 'success'
            elif booking.status in ['Cancelled', 'Failed']:
                ui_status = 'fail'
            
            # Extract first route info as a summary
            first_detail = booking.details.first()
            route_summary = "Unknown Route"
            departure_date = None
            
            if first_detail and first_detail.schedule and first_detail.schedule.flight:
                origin = first_detail.schedule.flight.route.origin_airport.code
                dest = first_detail.schedule.flight.route.destination_airport.code
                route_summary = f"{origin} ✈ {dest}"
                departure_date = first_detail.schedule.departure_time.isoformat()
                
                if booking.trip_type == 'round_trip':
                    route_summary = f"{origin} ⇄ {dest}"
                elif booking.trip_type == 'multi_city':
                    route_summary += " (Multi-City)"

            practice_bookings_data.append({
                "id": booking.id,
                "status": booking.status,
                "ui_status": ui_status,
                "total_amount": float(booking.total_amount),
                "trip_type": booking.get_trip_type_display(),
                "created_at": booking.created_at.isoformat(),
                "activity_code_used": booking.activity_code_used,
                "route_summary": route_summary,
                "departure_date": departure_date,
                "passenger_count": booking.details.count()
            })
            
        return Response({
            "practice_bookings": practice_bookings_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        traceback.print_exc()
        return Response(
            {"error": f"Failed to load practice bookings: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==========================================
# ADMIN: LMS OVERVIEW STATS
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def admin_lms_overview(request):
    """
    Admin-only LMS analytics endpoint.
    Returns aggregated stats for the dashboard overview page.
    """
    from django.db.models import Count, Avg, Q
    from django.db.models.functions import TruncWeek, TruncMonth
    from datetime import timedelta

    try:
        # ── 1. Activity Status Breakdown (all bindings) ──
        status_breakdown = (
            ActivityStudentBinding.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )
        status_map = {s['status']: s['count'] for s in status_breakdown}
        total_bindings = sum(status_map.values())

        # ── 2. Completion Rate per Section ──
        sections = Section.objects.all().prefetch_related('enrollments')
        section_stats = []
        for sec in sections:
            bindings = ActivityStudentBinding.objects.filter(activity__section=sec)
            total = bindings.count()
            completed = bindings.filter(status='completed').count()
            avg_grade = bindings.filter(grade__isnull=False).aggregate(avg=Avg('grade'))['avg']
            section_stats.append({
                'name': f"{sec.section_name} ({sec.section_code})",
                'total': total,
                'completed': completed,
                'rate': round((completed / total * 100), 1) if total > 0 else 0,
                'avg_grade': round(float(avg_grade), 1) if avg_grade else None,
                'enrolled': sec.enrollments.count(),
            })
        # Sort by completion rate descending
        section_stats.sort(key=lambda x: x['rate'], reverse=True)

        # ── 3. Submission Timeline (last 8 weeks) ──
        eight_weeks_ago = timezone.now() - timedelta(weeks=8)
        weekly = (
            ActivityStudentBinding.objects
            .filter(submitted_at__gte=eight_weeks_ago, submitted_at__isnull=False)
            .annotate(week=TruncWeek('submitted_at'))
            .values('week')
            .annotate(count=Count('id'))
            .order_by('week')
        )
        timeline = [
            {'week': w['week'].strftime('%b %d'), 'count': w['count']}
            for w in weekly
        ]

        # ── 4. Top Performing Students (highest avg grade) ──
        from app.models import Students
        top_students = (
            ActivityStudentBinding.objects
            .filter(grade__isnull=False)
            .values('student__first_name', 'student__last_name', 'student__student_number')
            .annotate(avg_grade=Avg('grade'), completed=Count('id', filter=Q(status='completed')))
            .order_by('-avg_grade')[:8]
        )
        top_list = [
            {
                'name': f"{s['student__first_name']} {s['student__last_name']}",
                'student_number': s['student__student_number'],
                'avg_grade': round(float(s['avg_grade']), 1),
                'completed': s['completed'],
            }
            for s in top_students
        ]

        # ── 5. Totals ──
        totals = {
            'students': Students.objects.count(),
            'instructors': Instructor.objects.count(),
            'sections': Section.objects.count(),
            'activities': Activity.objects.count(),
            'bindings': total_bindings,
        }

        return Response({
            'totals': totals,
            'status_breakdown': status_map,
            'section_stats': section_stats,
            'timeline': timeline,
            'top_students': top_list,
        }, status=200)

    except Exception as e:
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)
