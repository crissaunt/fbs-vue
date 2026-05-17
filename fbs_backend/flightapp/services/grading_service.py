from django.utils import timezone
from app.models import Booking, BookingDetail, Students
from fbs_instructor.models import Activity, ActivityStudentBinding
import logging
import json
import math

logger = logging.getLogger(__name__)

def grade_booking(booking, activity_id):
    """
    Validates a booking against an activity's requirements and updates the student's grade.
    Now generates a semantic rubric_breakdown for UI display.
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

        # 1. Rubric Logic (Matches Frontend categories for consistency)
        # We group points into 5 major categories (20% each)
        rubric_breakdown = [
            {"label": "Accuracy of Booking", "level": 1, "ratio": 0.0, "status": "Poor", "description": "", "criteria": []},
            {"label": "Technical Skill", "level": 1, "ratio": 0.0, "status": "Poor", "description": "", "criteria": []},
            {"label": "Organization of Steps", "level": 1, "ratio": 0.0, "status": "Poor", "description": "", "criteria": []},
            {"label": "Completeness", "level": 1, "ratio": 0.0, "status": "Poor", "description": "", "criteria": []},
            {"label": "Professionalism", "level": 1, "ratio": 0.0, "status": "Poor", "description": "", "criteria": []}
        ]

        # Helper to get category by keyword
        def get_cat(key):
            for cat in rubric_breakdown:
                if key.lower() in cat["label"].lower(): return cat
            return rubric_breakdown[0]

        # 2. Extract Data
        details = booking.details.all()
        all_schedules = []
        seen_schedule_ids = set()
        for d in details:
            if d.schedule_id not in seen_schedule_ids:
                all_schedules.append(d.schedule)
                seen_schedule_ids.add(d.schedule_id)
        all_schedules.sort(key=lambda s: s.departure_time)

        # --- MATCHING HELPERS ---
        def norm_str(s):
            return (str(s) or "").lower().strip()
        
        def match_exact(req, actual):
            if not req: return True
            return norm_str(req) == norm_str(actual)
            
        def normalize_addon_name(name):
            import re
            n = norm_str(name)
            n = re.sub(r'^assistance:\s*', '', n)
            n = re.sub(r'^assistance service:\s*', '', n)
            n = re.sub(r'^meal:\s*', '', n)
            n = re.sub(r'^extra baggage\s*', '', n)
            n = re.sub(r'extra baggage', 'baggage', n)
            n = re.sub(r'\s*(kg|kgs)([\s_-])', 'kg ', n)
            return n.strip()

        # 1. ACCURACY OF BOOKING (Trip Type, Origin, Destination, Dates)
        acc = get_cat("Accuracy")
        acc_criteria = []
        
        is_tt_met = match_exact(activity.required_trip_type, booking.trip_type)
        acc_criteria.append({"label": "Trip Type", "isMet": is_tt_met})
        
        normalized_trip_type = norm_str(activity.required_trip_type).replace(" ", "_")
        
        if normalized_trip_type == 'one_way':
            o_met = False; d_met = False; date_met = False
            if all_schedules:
                out = all_schedules[0]
                o_met = match_exact(activity.required_origin, out.flight.route.origin_airport.code)
                d_met = match_exact(activity.required_destination, out.flight.route.destination_airport.code)
                req_dep_date = activity.required_departure_date
                date_met = not req_dep_date or req_dep_date == out.departure_time.date()
            acc_criteria.append({"label": "Origin", "isMet": o_met})
            acc_criteria.append({"label": "Destination", "isMet": d_met})
            acc_criteria.append({"label": "Departure Date", "isMet": date_met})
            
        elif normalized_trip_type == 'round_trip':
            ro_met = False; rd_met = False; ro_date_met = False; rret_date_met = False
            if len(all_schedules) >= 1:
                out = all_schedules[0]
                o_met = match_exact(activity.required_origin, out.flight.route.origin_airport.code)
                d_met = match_exact(activity.required_destination, out.flight.route.destination_airport.code)
                ro_met = o_met and d_met
                req_dep_date = activity.required_departure_date
                ro_date_met = not req_dep_date or req_dep_date == out.departure_time.date()
            if len(all_schedules) >= 2:
                ret = all_schedules[1]
                o2_met = match_exact(activity.required_destination, ret.flight.route.origin_airport.code)
                d2_met = match_exact(activity.required_origin, ret.flight.route.destination_airport.code)
                rd_met = o2_met and d2_met
                req_ret_date = activity.required_return_date
                rret_date_met = not req_ret_date or req_ret_date == ret.departure_time.date()
                
            acc_criteria.append({"label": "Outbound Route", "isMet": ro_met})
            acc_criteria.append({"label": "Return Route", "isMet": rd_met})
            acc_criteria.append({"label": "Outbound Date", "isMet": ro_date_met})
            acc_criteria.append({"label": "Return Date", "isMet": rret_date_met})
            
        elif normalized_trip_type == 'multi_city':
            req_segs = activity.segments.all().order_by('order')
            for i, rs in enumerate(req_segs):
                if i < len(all_schedules):
                    bs = all_schedules[i]
                    o_met = match_exact(rs.origin, bs.flight.route.origin_airport.code)
                    d_met = match_exact(rs.destination, bs.flight.route.destination_airport.code)
                    date_met = not rs.departure_date or rs.departure_date == bs.departure_time.date()
                    acc_criteria.append({"label": f"Leg {i+1} Route", "isMet": o_met and d_met})
                    acc_criteria.append({"label": f"Leg {i+1} Date", "isMet": date_met})
                else:
                    acc_criteria.append({"label": f"Leg {i+1} Route", "isMet": False})
                    acc_criteria.append({"label": f"Leg {i+1} Date", "isMet": False})
        else:
            acc_criteria.append({"label": "Origin", "isMet": False})
            acc_criteria.append({"label": "Destination", "isMet": False})
            acc_criteria.append({"label": "Dates", "isMet": False})

        acc["ratio"] = sum(1 for c in acc_criteria if c["isMet"]) / len(acc_criteria) if acc_criteria else 1.0
        acc["criteria"] = acc_criteria

        # 2. TECHNICAL SKILL (Travel Class, Fare Type, Category, Passport)
        tech = get_cat("Technical")
        tech_criteria = []
        
        booked_pax = []
        seen_p = set()
        for d in details:
            if d.passenger and d.passenger.id not in seen_p:
                booked_pax.append(d.passenger)
                seen_p.add(d.passenger.id)
                
        outbound_detail = details.filter(schedule=all_schedules[0]).first() if all_schedules else None
        booked_class = norm_str(outbound_detail.seat_class.name if outbound_detail and outbound_detail.seat_class else "")
        req_class = norm_str(activity.required_travel_class).replace('_', '')
        is_class_met = req_class in booked_class or booked_class in req_class or not req_class
        tech_criteria.append({"label": "Travel Class", "isMet": is_class_met})
        
        # Fare Type Check
        req_fare = norm_str(activity.required_seat_class)
        booked_fare = norm_str(outbound_detail.fare_family_name if outbound_detail else "")
        is_fare_met = not req_fare or req_fare in booked_fare or booked_fare in req_fare
        tech_criteria.append({"label": "Fare Type", "isMet": is_fare_met})
        
        req_pax = activity.passengers.all()
        all_pax_category = True
        all_pax_passport = True
        
        for rp in req_pax:
            ap = next((p for p in booked_pax if norm_str(p.first_name) == norm_str(rp.first_name) and norm_str(p.last_name) == norm_str(rp.last_name)), None)
            if not ap:
                all_pax_category = False
                all_pax_passport = False
                continue
            
            # Category — PassengerInfo uses ph_discount_type (none/senior/pwd)
            def normC(s):
                return norm_str(s).replace('(none)', '').replace('citizen', '').replace(' ', '').replace('-', '').replace('_', '')
            
            actCat = normC(ap.ph_discount_type)
            expCat = normC(rp.passenger_category)
            if 'senior' in expCat:
                cat_met = 'senior' in actCat
            elif 'pwd' in expCat:
                cat_met = 'pwd' in actCat
            else:
                cat_met = 'senior' not in actCat and 'pwd' not in actCat
                
            if not cat_met:
                all_pax_category = False
                
            # Passport
            if activity.require_passport:
                if not match_exact(rp.passport_number, ap.passport_number):
                    all_pax_passport = False
                    
        tech_criteria.append({"label": "Category", "isMet": all_pax_category})
        
        # Always append Passport Info, just like frontend. If not required, it's always met.
        if not activity.require_passport:
            tech_criteria.append({"label": "Passport Info", "isMet": True})
        else:
            tech_criteria.append({"label": "Passport Info", "isMet": all_pax_passport})

        tech["ratio"] = sum(1 for c in tech_criteria if c["isMet"]) / len(tech_criteria) if tech_criteria else 1.0
        tech["criteria"] = tech_criteria

        # 3. ORGANIZATION (Passenger granular checks + seating)
        org = get_cat("Organization")
        org_criteria = []
        
        org_fields = []
        for rp in req_pax:
            ap = next((p for p in booked_pax if norm_str(p.first_name) == norm_str(rp.first_name) and norm_str(p.last_name) == norm_str(rp.last_name)), None)
            
            # Name met
            name_met = bool(ap)
            org_fields.append({"label": "Name", "isMet": name_met})
            
            # Gender met
            def get_frontend_gender(title, g):
                gf = norm_str(g)
                if not gf:
                    tf = norm_str(title).replace('.','')
                    if tf in ['mr','male']: return 'mr'
                    if tf in ['mrs','female']: return 'mrs'
                    if tf == 'ms': return 'ms'
                if gf in ['mr','male']: return 'mr'
                if gf in ['mrs','female']: return 'mrs'
                return gf
            
            # PassengerInfo has no 'gender' field — it uses 'title' (MR/MRS/MS).
            # Pass empty string for gender so get_frontend_gender falls back to title.
            gen_met = get_frontend_gender(ap.title if ap else '', '') == get_frontend_gender('', rp.gender) if ap else False
            org_fields.append({"label": "Gender", "isMet": gen_met})
            
            # DOB met
            dob_met = (ap.date_of_birth == rp.date_of_birth) if ap else False
            org_fields.append({"label": "DOB", "isMet": dob_met})
            
            # Nationality met
            nat_met = match_exact(rp.nationality, ap.nationality) if ap else False
            org_fields.append({"label": "Nationality", "isMet": nat_met})
            
            # Assigned Seat
            seating_met = False
            if ap:
                pax_details = [d for d in details if d.passenger_id == ap.id]
                if pax_details and len(pax_details) >= len(all_schedules):
                    if norm_str(rp.passenger_category) == 'infant' or norm_str(rp.passenger_type) == 'infant':
                        seating_met = True
                    else:
                        seating_met = all(d.seat_id for d in pax_details)
            org_fields.append({"label": "Assigned Seat", "isMet": seating_met})
            
            # Add to criteria
            pax_all_met = name_met and gen_met and dob_met and nat_met and seating_met
            org_criteria.append({"label": f"Pax {rp.first_name} Details", "isMet": pax_all_met})

        org["ratio"] = sum(1 for f in org_fields if f["isMet"]) / len(org_fields) if org_fields else 1.0
        org["criteria"] = org_criteria

        # 4. COMPLETENESS (Pax Counts, Add-ons)
        comp = get_cat("Completeness")
        comp_criteria = []
        
        pax_counts_met = (
            sum(1 for p in booked_pax if (p.passenger_type or '').lower() in ('adult',)) == activity.required_passengers and
            sum(1 for p in booked_pax if (p.passenger_type or '').lower() in ('child',)) == activity.required_children and
            sum(1 for p in booked_pax if (p.passenger_type or '').lower() in ('infant',)) == activity.required_infants
        )
        comp_criteria.append({"label": "Passenger Counts", "isMet": pax_counts_met})

        req_addons = activity.activity_addons.all()
        if req_addons:
            for ra in req_addons:
                req_fn = norm_str(ra.passenger.first_name)
                req_ln = norm_str(ra.passenger.last_name)
                
                pax_details = [d for d in details if norm_str(d.passenger.first_name) == req_fn and norm_str(d.passenger.last_name) == req_ln]
                all_actual_addons = []
                for d in pax_details:
                    all_actual_addons.extend(d.addons.all())
                
                try: req_addon_name = ra.addon.name if ra.addon else 'Unknown Addon'
                except Exception: req_addon_name = 'Unknown Addon'
                
                norm_req = normalize_addon_name(req_addon_name)
                req_id = ra.addon_id or (ra.addon.id if ra.addon else None)
                
                is_met = False
                for a in all_actual_addons:
                    if req_id and a.id == req_id:
                        is_met = True; break
                    norm_a = normalize_addon_name(a.name)
                    if norm_req == norm_a:
                        is_met = True; break
                    if len(norm_req) >= 3 and len(norm_a) >= 3 and (norm_req in norm_a or norm_a in norm_req):
                        is_met = True; break
                
                comp_criteria.append({"label": f"Add-on: {req_addon_name} ({ra.passenger.first_name})", "isMet": is_met})
        else:
            comp_criteria.append({"label": "Add-ons Compliance", "isMet": True})

        comp["ratio"] = sum(1 for c in comp_criteria if c["isMet"]) / len(comp_criteria) if comp_criteria else 1.0
        comp["criteria"] = comp_criteria

        # 5. PROFESSIONALISM (Route Integrity, Budget, Data Integrity)
        prof = get_cat("Professionalism")
        prof_criteria = []
        
        # Route Integrity
        if normalized_trip_type == 'multi_city':
            route_met = False
            if all_schedules and activity.segments.count() <= len(all_schedules):
                route_met = True
                req_segs = activity.segments.all().order_by('order')
                for i, rs in enumerate(req_segs):
                    bs = all_schedules[i]
                    if not (match_exact(rs.origin, bs.flight.route.origin_airport.code) and match_exact(rs.destination, bs.flight.route.destination_airport.code)):
                        route_met = False
                        break
        else:
            route_met = False
            if all_schedules:
                out = all_schedules[0]
                o_met = match_exact(activity.required_origin, out.flight.route.origin_airport.code)
                d_met = match_exact(activity.required_destination, out.flight.route.destination_airport.code)
                route_met = o_met and d_met

        prof_criteria.append({"label": "Flight Route Integrity", "isMet": route_met})
        prof_criteria.append({"label": "Budget Compliance", "isMet": is_class_met})
        
        # Data Integrity
        data_integrity = True
        if org_fields:
            data_integrity = all(f["isMet"] for f in org_fields[:5]) # Name, Gender, DOB, Nationality, Seating of Pax 1
            
        prof_criteria.append({"label": "Data Integrity", "isMet": data_integrity})
        prof["ratio"] = sum(1 for c in prof_criteria if c["isMet"]) / len(prof_criteria) if prof_criteria else 1.0
        prof["criteria"] = prof_criteria


        # Final Score Calculation — MUST match frontend gradingLogic.js GRADING_THRESHOLDS exactly.
        # Each rubric type has DIFFERENT thresholds in the frontend — we replicate them here.
        GRADING_THRESHOLDS = {
            "accuracy": [(1.0, 5, "Excellent"), (0.8, 4, "Very Good"), (0.5, 3, "Satisfactory"), (0.2, 2, "Needs Improvement"), (0.0, 1, "Poor")],
            "tech":     [(1.0, 5, "Excellent"), (0.7, 4, "Very Good"), (0.4, 3, "Satisfactory"), (0.1, 2, "Needs Improvement"), (0.0, 1, "Poor")],
            "org":      [(1.0, 5, "Excellent"), (0.8, 4, "Very Good"), (0.5, 3, "Satisfactory"), (0.2, 2, "Needs Improvement"), (0.0, 1, "Poor")],
            "comp":     [(1.0, 5, "Excellent"), (0.5, 3, "Satisfactory"), (0.01, 2, "Needs Improvement"), (0.0, 1, "Poor")],
            "prof":     [(1.0, 5, "Excellent"), (0.7, 4, "Very Good"), (0.4, 3, "Satisfactory"), (0.1, 2, "Needs Improvement"), (0.0, 1, "Poor")],
        }

        def apply_level(cat, rubric_key):
            r = cat["ratio"]
            for threshold, level, status in GRADING_THRESHOLDS[rubric_key]:
                if r >= threshold:
                    cat["level"] = level
                    cat["status"] = status
                    return

        apply_level(get_cat("Accuracy"), "accuracy")
        apply_level(get_cat("Technical"), "tech")
        apply_level(get_cat("Organization"), "org")
        apply_level(get_cat("Completeness"), "comp")
        apply_level(get_cat("Professionalism"), "prof")

        # Score formula MUST match frontend exactly:
        # calculatedScore = sumOfRatios * (totalPoints / 5)
        # where sumOfRatios = acc.ratio + tech.ratio + org.ratio + comp.ratio + prof.ratio
        sum_of_ratios = sum(c["ratio"] for c in rubric_breakdown)
        total_points = float(activity.total_points)
        # Use math.floor(val + 0.5) to mimic Javascript's Math.round
        earned_score = math.floor((sum_of_ratios * (total_points / 5.0)) + 0.5)

        # Update Binding
        binding.grade = earned_score
        binding.rubric_breakdown = rubric_breakdown # Save the detailed JSON
        binding.status = 'graded' if grand_total_ratio > 0 else 'submitted'
        binding.submitted_at = timezone.now()
        binding.save()
        
        # Link booking
        booking.activity = activity
        booking.is_graded = True
        booking.save()
        
        logger.info(f"Graded booking {booking.id} Score: {earned_score}")
        
        return {
            "total": earned_score,
            "rubric_breakdown": rubric_breakdown
        }

    except Exception as e:
        logger.error(f"❌ Error grading booking {booking.id} for activity {activity_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

