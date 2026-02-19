from django.utils import timezone
from app.models import Booking, BookingDetail, Students
from fbs_instructor.models import Activity, ActivityStudentBinding
import logging

logger = logging.getLogger(__name__)

def grade_booking(booking, activity_id):
    """
    Validates a booking against an activity's requirements and updates the student's grade.
    """
    try:
        if not activity_id:
            return

        activity = Activity.objects.get(id=activity_id)
        student = None
        
        # Try to find the student record for this user
        try:
            student = Students.objects.get(user=booking.user)
        except Students.DoesNotExist:
            logger.warning(f"User {booking.user.username} has no Student profile but tried to grade activity {activity_id}")
            return

        # Get the binding
        binding, created = ActivityStudentBinding.objects.get_or_create(
            activity=activity,
            student=student,
            defaults={'status': 'submitted'}
        )

        # Initialize score and feedback
        score = 0.0
        total_score = float(activity.total_points)
        feedback = []
        is_perfect = True

        # 1. Check Trip Type
        if activity.required_trip_type and booking.trip_type != activity.required_trip_type:
            feedback.append(f"❌ Incorrect Trip Type: Requires {activity.get_required_trip_type_display()}, got {booking.get_trip_type_display()}")
            is_perfect = False
        else:
            feedback.append("✅ Correct Trip Type")

        # Get first flight details (outbound)
        outbound_detail = booking.details.first()
        if not outbound_detail:
            feedback.append("❌ No flight details found")
            return

        # 2. Check Origin
        booked_origin = outbound_detail.schedule.flight.route.origin_airport.city
        if activity.required_origin and activity.required_origin.lower() not in booked_origin.lower():
             # Also check code
            booked_origin_code = outbound_detail.schedule.flight.route.origin_airport.code
            if activity.required_origin.upper() != booked_origin_code:
                feedback.append(f"❌ Incorrect Origin: Requires {activity.required_origin}, got {booked_origin} ({booked_origin_code})")
                is_perfect = False
            else:
                 feedback.append("✅ Correct Origin")
        else:
            feedback.append("✅ Correct Origin")

        # 3. Check Destination
        booked_dest = outbound_detail.schedule.flight.route.destination_airport.city
        if activity.required_destination and activity.required_destination.lower() not in booked_dest.lower():
            # Also check code
            booked_dest_code = outbound_detail.schedule.flight.route.destination_airport.code
            if activity.required_destination.upper() != booked_dest_code:
                feedback.append(f"❌ Incorrect Destination: Requires {activity.required_destination}, got {booked_dest} ({booked_dest_code})")
                is_perfect = False
            else:
                feedback.append("✅ Correct Destination")
        else:
            feedback.append("✅ Correct Destination")

        # 4. Check Seat Class
        # Allow checking either specific class or 'any' if not specified
        if activity.required_travel_class:
            booked_class = outbound_detail.seat_class.name if outbound_detail.seat_class else "Unknown"
            # Map activity choices to model names if needed, or simple string match
            # Activity choices: 'economy', 'premium_economy', 'business', 'first'
            # SeatClass names might be "Economy", "Business Class" etc. 
            
            req_class = activity.required_travel_class.lower()
            b_class = booked_class.lower()
            
            if req_class not in b_class:
                 feedback.append(f"❌ Incorrect Seat Class: Requires {activity.get_required_travel_class_display()}, got {booked_class}")
                 is_perfect = False
            else:
                 feedback.append("✅ Correct Seat Class")

        # Calculate Final Grade
        if is_perfect:
            score = total_score
            binding.status = 'submitted' # Or 'graded' if we want to auto-approve
            feedback.insert(0, "🌟 PERFECT SCORE! All requirements met.")
        else:
            score = 0 # Or partial points
            binding.status = 'submitted'
            feedback.insert(0, "⚠️ Requirements not fully met.")
            
        # Update Binding
        binding.grade = score
        binding.feedback = "\n".join(feedback)
        binding.submitted_at = timezone.now()
        binding.save()
        
        # Update Booking to link
        booking.activity = activity
        booking.is_graded = True
        booking.save()
        
        logger.info(f"Graded booking {booking.id} for activity {activity.title}. Score: {score}")

    except Exception as e:
        logger.error(f"Error grading booking: {str(e)}")
        import traceback
        traceback.print_exc() 
