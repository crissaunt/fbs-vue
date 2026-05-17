import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import (
    Country, Airline, Airport, Aircraft, SeatClass, Route, Flight, Schedule,
    Seat, SeatRequirement, AddOnType, AddOn, MealCategory, MealOption,
    BaggageOption, AssistanceService, InsuranceProvider, TravelInsurancePlan,
    Booking, BookingDetail, BookingTax, CheckInDetail, Payment
)

def clear_flight_data():
    print("🧹 Cleaning up old flight, booking, and addon data (preserving Users, Students, and Instructors)...")
    
    # We delete bookings and payments first to avoid foreign key constraints
    models_to_clear = [
        CheckInDetail, BookingTax, BookingDetail, Booking, Payment,
        Seat, Schedule, Flight, Route, Aircraft, SeatClass, Airline,
        Airport, Country, AddOn, AddOnType, MealOption, MealCategory,
        BaggageOption, AssistanceService, TravelInsurancePlan, InsuranceProvider,
        SeatRequirement
    ]
    
    for model in models_to_clear:
        try:
            model.objects.all().delete()
            print(f"  ✅ Cleared {model.__name__}")
        except Exception as e:
            print(f"  ⚠️ Error clearing {model.__name__}: {e}")

def seed_real_data():
    # 1. Clear old flight assets
    clear_flight_data()
    print("\n🚀 Starting Seeding of 30 Real Flight Schedules & Assets...\n")

    # 2. Countries
    print("🌍 Seeding Countries...")
    ph = Country.objects.create(name="Philippines", code="PH", currency="PHP")
    sg = Country.objects.create(name="Singapore", code="SG", currency="SGD")
    jp = Country.objects.create(name="Japan", code="JP", currency="JPY")
    kr = Country.objects.create(name="South Korea", code="KR", currency="KRW")
    us = Country.objects.create(name="United States", code="US", currency="USD")

    # 3. Airlines
    print("✈️ Seeding Airlines...")
    pr = Airline.objects.create(name="Philippine Airlines", code="PR")
    ceb = Airline.objects.create(name="Cebu Pacific", code="5J")
    aa = Airline.objects.create(name="AirAsia Philippines", code="Z2")

    # 4. Seat Classes
    print("🛋️ Seeding Seat Classes...")
    seat_classes = {}
    for al, classes in [
        (pr, [("Economy", 1.0, "#3B82F6"), ("Premium Economy", 1.5, "#8B5CF6"), ("Business", 2.5, "#EF4444")]),
        (ceb, [("Economy", 1.0, "#F59E0B"), ("Premium Economy", 1.4, "#10B981")]),
        (aa, [("Economy", 1.0, "#EF4444"), ("Premium Economy", 1.4, "#EC4899")]),
    ]:
        seat_classes[al.code] = []
        for name, mult, color in classes:
            sc = SeatClass.objects.create(
                airline=al,
                name=name,
                price_multiplier=Decimal(str(mult)),
                color=color,
                is_active=True
            )
            seat_classes[al.code].append(sc)

    # 5. Aircrafts (with automatic default layouts based on generated SeatClasses)
    print("✈️ Seeding Aircrafts...")
    ac_pr = Aircraft.objects.create(model="Airbus A321neo", capacity=168, airline=pr)
    ac_ceb = Aircraft.objects.create(model="Airbus A320neo", capacity=180, airline=ceb)
    ac_aa = Aircraft.objects.create(model="Airbus A320-200", capacity=180, airline=aa)

    # 6. Airports (Realistic Philippine & Regional Hubs)
    print("📍 Seeding Airports...")
    airports = {
        "MNL": Airport.objects.create(name="Ninoy Aquino International Airport", code="MNL", city="Manila", country=ph, airport_type="international", latitude=14.5086, longitude=121.0194),
        "CEB": Airport.objects.create(name="Mactan-Cebu International Airport", code="CEB", city="Cebu", country=ph, airport_type="international", latitude=10.3075, longitude=123.9794),
        "DVO": Airport.objects.create(name="Francisco Bangoy International Airport", code="DVO", city="Davao", country=ph, airport_type="international", latitude=7.1253, longitude=125.6453),
        "PPS": Airport.objects.create(name="Puerto Princesa International Airport", code="PPS", city="Palawan", country=ph, airport_type="international", latitude=9.7421, longitude=118.7588),
        "CGY": Airport.objects.create(name="Laguindingan Airport", code="CGY", city="Cagayan de Oro", country=ph, airport_type="domestic", latitude=8.4153, longitude=124.4697),
        "TAC": Airport.objects.create(name="Daniel Z. Romualdez Airport", code="TAC", city="Tacloban", country=ph, airport_type="domestic", latitude=11.2269, longitude=125.0281),
        "KLO": Airport.objects.create(name="Kalibo International Airport", code="KLO", city="Kalibo", country=ph, airport_type="international", latitude=11.5933, longitude=122.3789),
        "SIN": Airport.objects.create(name="Singapore Changi Airport", code="SIN", city="Changi", country=sg, airport_type="international", latitude=1.3644, longitude=103.9915),
        "NRT": Airport.objects.create(name="Narita International Airport", code="NRT", city="Tokyo", country=jp, airport_type="international", latitude=35.7767, longitude=140.3864),
        "ICN": Airport.objects.create(name="Incheon International Airport", code="ICN", city="Seoul", country=kr, airport_type="international", latitude=37.4602, longitude=126.4407),
    }

    # 7. Routes (Realistic pricing and routes)
    print("🗺️ Seeding Routes...")
    routes = []
    route_pairs = [
        ("MNL", "CEB", 1800), ("CEB", "MNL", 1800),
        ("MNL", "DVO", 2500), ("DVO", "MNL", 2500),
        ("MNL", "PPS", 1900), ("PPS", "MNL", 1900),
        ("MNL", "CGY", 2100), ("CGY", "MNL", 2100),
        ("MNL", "TAC", 1600), ("TAC", "MNL", 1600),
        ("MNL", "KLO", 1750), ("KLO", "MNL", 1750),
        ("MNL", "SIN", 5500), ("SIN", "MNL", 5500),
        ("MNL", "NRT", 8500), ("NRT", "MNL", 8500),
        ("MNL", "ICN", 7800), ("ICN", "MNL", 7800),
        ("CEB", "DVO", 1900), ("DVO", "CEB", 1900),
        ("CEB", "SIN", 5900), ("SIN", "CEB", 5900),
    ]
    for orig, dest, price in route_pairs:
        r = Route.objects.create(
            origin_airport=airports[orig],
            destination_airport=airports[dest],
            base_price=Decimal(price)
        )
        routes.append(r)

    # 8. Flights
    print("✈️ Seeding Flights...")
    flights = []
    for i, route in enumerate(routes):
        # Rotate among the three airlines
        if i % 3 == 0:
            al = pr
            ac = ac_pr
            code = "PR"
        elif i % 3 == 1:
            al = ceb
            ac = ac_ceb
            code = "5J"
        else:
            al = aa
            ac = ac_aa
            code = "Z2"
        
        f = Flight.objects.create(
            flight_number=f"{code}{100 + i}",
            airline=al,
            aircraft=ac,
            route=route
        )
        flights.append(f)

    # 9. Seat Requirements
    print("💺 Seeding Seat Requirements...")
    requirements_data = [
        ("Extra Legroom", "has_extra_legroom", 1200.00, "ph-star"),
        ("Exit Row", "is_exit_row", 800.00, "ph-exit"),
        ("Bulkhead", "is_bulkhead", 400.00, "ph-layout"),
        ("Window Seat", "is_window", 150.00, "ph-circle"),
        ("Aisle Seat", "is_aisle", 120.00, "ph-arrows-horizontal"),
        ("Wheelchair Accessible", "is_wheelchair_accessible", 0.00, "ph-wheelchair"),
        ("Bassinet", "has_bassinet", 500.00, "ph-baby"),
    ]
    seat_reqs = {}
    for name, code, price, icon in requirements_data:
        req = SeatRequirement.objects.create(
            name=name,
            code=code,
            price=Decimal(price),
            icon=icon,
            description=f"{name} option."
        )
        seat_reqs[code] = req

    # 10. Seeding 30 Schedules & Generating Seats
    print("📅 Seeding 30 schedules...")
    schedules = []
    # Start dates tomorrow to keep schedules purely in the future
    start_date = timezone.now().replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    for i in range(30):
        flight = flights[i % len(flights)]
        dep_time = start_date + timedelta(days=i, hours=(i % 3) * 4)
        arr_time = dep_time + timedelta(hours=2)
        
        s = Schedule.objects.create(
            flight=flight,
            departure_time=dep_time,
            arrival_time=arr_time,
            price=flight.route.base_price,
            status='Open',
            gate=f"Gate {random.randint(1, 15)}"
        )
        
        # Generate seats synchronously
        s.generate_seats()
        schedules.append(s)
        print(f"  ✈️ Schedule {i+1}/30: {s.flight.flight_number} ({s.flight.route.origin_airport.code} -> {s.flight.route.destination_airport.code}) on {s.departure_time.strftime('%Y-%m-%d %H:%M')}")

    # Customize some seats to have Exit Rows and Extra Legroom for grading!
    print("🛠️ Customizing seats (Exit Rows, Bulkheads, Extra Legroom)...")
    for s in schedules:
        seats = Seat.objects.filter(schedule=s)
        for seat in seats:
            modified = False
            # Front rows are premium bulkhead / extra legroom
            if seat.row in [1, 2]:
                seat.has_extra_legroom = True
                seat.is_bulkhead = True
                modified = True
            # Middle rows are exit rows
            elif seat.row in [12, 13]:
                seat.is_exit_row = True
                modified = True
                
            if modified:
                seat.save() # Updates auto adjustment in DB
                # Bind requirements Many-to-Many
                if seat.has_extra_legroom:
                    seat.requirements.add(seat_reqs["has_extra_legroom"])
                if seat.is_exit_row:
                    seat.requirements.add(seat_reqs["is_exit_row"])
                if seat.is_bulkhead:
                    seat.requirements.add(seat_reqs["is_bulkhead"])
                if seat.is_window:
                    seat.requirements.add(seat_reqs["is_window"])
                if seat.is_aisle:
                    seat.requirements.add(seat_reqs["is_aisle"])
        print(f"  ✅ Custom seats configured for {s.flight.flight_number}")

    # 11. Add-On Types
    print("🎒 Seeding Add-On Types...")
    type_meal = AddOnType.objects.create(name="Meal", description="Pre-booked delicious inflight meals.")
    type_baggage = AddOnType.objects.create(name="Baggage", description="Prepaid extra baggage allowance.")
    type_insurance = AddOnType.objects.create(name="Insurance", description="Comprehensive travel insurance protection.")
    type_assistance = AddOnType.objects.create(name="Assistance", description="Special assistance services.")

    # Meal Categories
    main_course = MealCategory.objects.create(name="Main Course", display_order=1)
    beverages = MealCategory.objects.create(name="Beverages", display_order=2)
    light_meals = MealCategory.objects.create(name="Light Meals", display_order=3)

    # ── PAL Addons ──
    print("🍲 Seeding PAL Add-Ons & Wrapper AddOn Models...")
    meals_pr = [
        ('Filipino Favorite - Chicken Adobo', 'Tender chicken marinated in soy and vinegar, served with garlic rice.', 'standard', main_course, 450.00),
        ("Cattleman's Roast Beef", 'Slow-roasted beef with mushroom gravy and mashed potatoes.', 'standard', main_course, 550.00),
        ('Seafood Pasta with White Wine Sauce', 'Fresh catch in a light creamy sauce.', 'standard', main_course, 480.00),
    ]
    for name, desc, mtype, cat, price in meals_pr:
        mo = MealOption.objects.create(airline=pr, name=name, description=desc, meal_type=mtype, category=cat, price=Decimal(price))
        AddOn.objects.create(airline=pr, type=type_meal, meal_option=mo, name=name, description=desc, price=Decimal(price))
        
    baggage_pr = [(10, 800.00), (20, 1400.00), (30, 2000.00)]
    for weight, price in baggage_pr:
        bo = BaggageOption.objects.create(airline=pr, weight_kg=weight, name=f"{weight}kg Extra Baggage", price=Decimal(price))
        AddOn.objects.create(airline=pr, type=type_baggage, baggage_option=bo, name=f"{weight}kg Extra Baggage", description=f"Prepaid baggage allowance of {weight}kg.", price=Decimal(price))
        
    assist_pr = [
        ('PAL Wheelchair Assistance', 'wheelchair', 'Full gate-to-aircraft wheelchair assistance.', 0.00, True),
        ('Mabuhay Lounge Access', 'boarding', 'Exclusive lounge access at major terminals.', 1200.00, False),
    ]
    for name, stype, desc, price, included in assist_pr:
        as_obj = AssistanceService.objects.create(airline=pr, name=name, service_type=stype, description=desc, price=Decimal(price), is_included=included)
        AddOn.objects.create(airline=pr, type=type_assistance, assistance_service=as_obj, name=name, description=desc, price=Decimal(price), included=included)

    # ── CEB Addons ──
    print("🍲 Seeding Cebu Pacific Add-Ons & Wrapper AddOn Models...")
    meals_ceb = [
        ('Beef Pares with Garlic Rice', 'Classic Filipino beef stew with savory-sweet sauce.', 'standard', main_course, 350.00),
        ('Chicken Sisig Meal', 'Spicy minced chicken with calamansi, topped on rice.', 'standard', main_course, 350.00),
        ('Vegetable Salpicao (V)', 'Sautéed mushrooms with garlic and bell peppers.', 'vegetarian', light_meals, 280.00),
    ]
    for name, desc, mtype, cat, price in meals_ceb:
        mo = MealOption.objects.create(airline=ceb, name=name, description=desc, meal_type=mtype, category=cat, price=Decimal(price))
        AddOn.objects.create(airline=ceb, type=type_meal, meal_option=mo, name=name, description=desc, price=Decimal(price))
        
    baggage_ceb = [(20, 650.00), (28, 1150.00), (32, 1450.00)]
    for weight, price in baggage_ceb:
        bo = BaggageOption.objects.create(airline=ceb, weight_kg=weight, name=f"{weight}kg Prepaid Baggage", price=Decimal(price))
        AddOn.objects.create(airline=ceb, type=type_baggage, baggage_option=bo, name=f"{weight}kg Prepaid Baggage", description=f"Prepaid baggage allowance of {weight}kg.", price=Decimal(price))
        
    assist_ceb = [
        ('CEB Wheelchair Service', 'wheelchair', 'Assistance for passengers with reduced mobility.', 0.00, True),
        ('CEB Priority Boarding', 'boarding', 'Board first before general passengers.', 350.00, False),
    ]
    for name, stype, desc, price, included in assist_ceb:
        as_obj = AssistanceService.objects.create(airline=ceb, name=name, service_type=stype, description=desc, price=Decimal(price), is_included=included)
        AddOn.objects.create(airline=ceb, type=type_assistance, assistance_service=as_obj, name=name, description=desc, price=Decimal(price), included=included)

    # ── AA Addons ──
    print("🍲 Seeding AirAsia Add-Ons & Wrapper AddOn Models...")
    meals_aa = [
        ("Pak Nasser's Nasi Lemak", 'Coconut rice with spicy sambal, rendang and egg.', 'standard', main_course, 250.00),
        ("Uncle Chin's Chicken Rice", 'Hainanese-style chicken rice with ginger sauce.', 'standard', main_course, 250.00),
    ]
    for name, desc, mtype, cat, price in meals_aa:
        mo = MealOption.objects.create(airline=aa, name=name, description=desc, meal_type=mtype, category=cat, price=Decimal(price))
        AddOn.objects.create(airline=aa, type=type_meal, meal_option=mo, name=name, description=desc, price=Decimal(price))
        
    baggage_aa = [(15, 450.00), (20, 550.00), (30, 950.00)]
    for weight, price in baggage_aa:
        bo = BaggageOption.objects.create(airline=aa, weight_kg=weight, name=f"{weight}kg Value Baggage", price=Decimal(price))
        AddOn.objects.create(airline=aa, type=type_baggage, baggage_option=bo, name=f"{weight}kg Value Baggage", description=f"Prepaid baggage allowance of {weight}kg.", price=Decimal(price))
        
    assist_aa = [
        ('Xpress Boarding Service', 'boarding', 'Skip the line and board first.', 400.00, False),
        ('AirAsia Wheelchair Assistance', 'wheelchair', 'Airport wheelchair assistance for all zones.', 0.00, True),
    ]
    for name, stype, desc, price, included in assist_aa:
        as_obj = AssistanceService.objects.create(airline=aa, name=name, service_type=stype, description=desc, price=Decimal(price), is_included=included)
        AddOn.objects.create(airline=aa, type=type_assistance, assistance_service=as_obj, name=name, description=desc, price=Decimal(price), included=included)

    # 12. Travel Insurance
    print("🛡️ Seeding Travel Insurance...")
    prov_allianz = InsuranceProvider.objects.create(code='ALLIANZ', name='Allianz Travel Insurance', default_commission_rate=15.00)
    prov_axa = InsuranceProvider.objects.create(code='AXA', name='AXA Philippines', default_commission_rate=15.00)
    
    plan_basic = TravelInsurancePlan.objects.create(
        provider=prov_allianz, name='Allianz Basic Cover',
        description='Essential travel protection covering emergency medical up to ₱500,000, flight delays, and lost baggage.',
        retail_price=Decimal('299.00'), wholesale_price=Decimal('220.00'), coverage_duration_days=30, plan_type='basic', is_active=True
    )
    plan_basic.airlines.set([pr, ceb, aa])
    
    plan_premium = TravelInsurancePlan.objects.create(
        provider=prov_axa, name='AXA SmartTravel Plus',
        description='Wider protection for regional travel: ₱2,000,000 medical, trip cancellation, and 24/7 hotline.',
        retail_price=Decimal('799.00'), wholesale_price=Decimal('600.00'), coverage_duration_days=45, plan_type='standard', is_active=True
    )
    plan_premium.airlines.set([pr, ceb])
    
    # Create the wrapper AddOn records for Insurance
    for plan in [plan_basic, plan_premium]:
        for al in plan.airlines.all():
            AddOn.objects.create(
                airline=al,
                type=type_insurance,
                insurance_plan=plan,
                name=plan.name,
                description=plan.description,
                price=plan.retail_price,
                included=False
            )

    print("\n🌟 Successfully seeded 30 high-fidelity schedules and comprehensive flight assets to Supabase!")

if __name__ == "__main__":
    seed_real_data()
