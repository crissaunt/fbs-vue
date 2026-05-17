import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import (
    Country, Airline, Airport, Aircraft, SeatClass, Route, Flight, Schedule,
    Seat, AddOnType, Booking, BookingDetail, CheckInDetail, Payment, BookingTax
)

def clear_flights():
    print("🧹 Cleaning up old dummy flight data...")
    # Delete bookings first to avoid foreign key constraints
    CheckInDetail.objects.all().delete()
    BookingTax.objects.all().delete()
    BookingDetail.objects.all().delete()
    Payment.objects.all().delete()
    Booking.objects.all().delete()
    
    # Delete flight-related data
    Seat.objects.all().delete()
    Schedule.objects.all().delete()
    Flight.objects.all().delete()
    Route.objects.all().delete()
    Aircraft.objects.all().delete()
    SeatClass.objects.all().delete()
    Airline.objects.all().delete()
    Airport.objects.all().delete()
    Country.objects.all().delete()
    AddOnType.objects.all().delete()
    print("✅ Old flight data cleared.")

def generate_seats(schedule):
    aircraft = schedule.flight.aircraft
    layout = aircraft.get_layout_config()
    seat_classes_config = layout.get('seat_classes', [])
    
    if not seat_classes_config:
        sc = SeatClass.objects.filter(airline=aircraft.airline).first()
        if not sc: return
        for r in range(1, 11):
            for c in ['A', 'B', 'C', 'D']:
                Seat.objects.get_or_create(
                    schedule=schedule,
                    seat_number=f"{r}{c}",
                    defaults={'seat_class': sc, 'row': r, 'column': c, 'is_available': True}
                )
        return
        
    for sc_config in seat_classes_config:
        class_id = sc_config.get('class_id')
        rows = sc_config.get('rows', 0)
        columns = sc_config.get('columns', 0)
        start_row = sc_config.get('start_row', 1)
        
        try:
            seat_class = SeatClass.objects.get(id=class_id)
        except SeatClass.DoesNotExist:
            continue
            
        for r in range(rows):
            row_num = start_row + r
            for c in range(columns):
                col_label = chr(65 + c)
                Seat.objects.get_or_create(
                    schedule=schedule,
                    seat_number=f"{row_num}{col_label}",
                    defaults={'seat_class': seat_class, 'row': row_num, 'column': col_label, 'is_available': True}
                )

def seed_real_data():
    clear_flights()
    print("\n🚀 Seeding REAL Philippine flight data...")

    # 1. Country
    ph = Country.objects.create(name="Philippines", code="PH", currency="PHP")

    # 2. Airlines
    airlines_data = [
        ("Philippine Airlines", "PR"),
        ("Cebu Pacific", "5J"),
        ("AirAsia Philippines", "Z2")
    ]
    airlines = []
    for name, code in airlines_data:
        a = Airline.objects.create(name=name, code=code)
        airlines.append(a)
        # 3. Seat Classes
        SeatClass.objects.create(airline=a, name='Economy', price_multiplier=Decimal('1.0'))
        SeatClass.objects.create(airline=a, name='Premium Economy', price_multiplier=Decimal('1.5'))
        SeatClass.objects.create(airline=a, name='Business', price_multiplier=Decimal('3.0'))

    # 4. Airports
    airports_data = [
        ("Ninoy Aquino International Airport", "MNL", "Manila"),
        ("Mactan-Cebu International Airport", "CEB", "Cebu"),
        ("Francisco Bangoy International Airport", "DVO", "Davao"),
        ("Godofredo P. Ramos Airport", "MPH", "Caticlan"),
        ("Puerto Princesa International Airport", "PPS", "Puerto Princesa"),
        ("Iloilo International Airport", "ILO", "Iloilo"),
        ("Bacolod-Silay Airport", "BCD", "Bacolod"),
        ("Bohol-Panglao International Airport", "TAG", "Tagbilaran"),
        ("Kalibo International Airport", "KLO", "Kalibo"),
        ("Laguindingan Airport", "CGY", "Cagayan de Oro")
    ]
    airports = []
    for name, code, city in airports_data:
        ap = Airport.objects.create(
            name=name, code=code, city=city,
            country=ph, airport_type='international' if code in ['MNL', 'CEB', 'DVO', 'KLO', 'PPS', 'ILO', 'TAG'] else 'domestic'
        )
        airports.append(ap)

    # 5. Aircrafts
    aircrafts = []
    for i, a in enumerate(airlines):
        aircrafts.append(Aircraft.objects.create(model="Airbus A320", capacity=180, airline=a))
        aircrafts.append(Aircraft.objects.create(model="Boeing 737-800", capacity=189, airline=a))
        aircrafts.append(Aircraft.objects.create(model="Airbus A321neo", capacity=236, airline=a))

    # 6. Routes
    routes = []
    # Create routes from Manila to all other airports
    mnl = airports[0]
    for dest in airports[1:]:
        price = Decimal(random.randint(1500, 3500))
        routes.append(Route.objects.create(origin_airport=mnl, destination_airport=dest, base_price=price))
        routes.append(Route.objects.create(origin_airport=dest, destination_airport=mnl, base_price=price))
    
    # Create routes from Cebu to major hubs
    ceb = airports[1]
    for dest in [airports[2], airports[3], airports[4], airports[5], airports[9]]: # DVO, MPH, PPS, ILO, CGY
        price = Decimal(random.randint(1200, 2800))
        routes.append(Route.objects.create(origin_airport=ceb, destination_airport=dest, base_price=price))
        routes.append(Route.objects.create(origin_airport=dest, destination_airport=ceb, base_price=price))

    # 7. Add-Ons
    AddOnType.objects.get_or_create(name="Extra Baggage 20kg", defaults={"description": "Additional 20kg checked baggage"})
    AddOnType.objects.get_or_create(name="Hot Meal", defaults={"description": "In-flight hot meal"})
    AddOnType.objects.get_or_create(name="Travel Insurance", defaults={"description": "Comprehensive travel insurance"})

    # 8. Flights & Schedules (Create exactly 30 realistic schedules)
    schedules = []
    now = timezone.now()
    
    for i in range(30):
        route = random.choice(routes)
        airline = random.choice(airlines)
        aircraft = random.choice([ac for ac in aircrafts if ac.airline == airline])
        
        # Create flight
        f = Flight.objects.create(
            flight_number=f"{airline.code}{random.randint(100, 999)}", 
            airline=airline,
            aircraft=aircraft, 
            route=route
        )
        
        # Schedule it between 1 to 14 days from now
        days_ahead = random.randint(1, 14)
        hour = random.randint(5, 22)
        minute = random.choice([0, 15, 30, 45])
        
        dept_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days_ahead)
        # Flight duration roughly 1 to 2 hours
        arr_time = dept_time + timedelta(hours=1, minutes=random.randint(0, 45))
        
        s = Schedule.objects.create(
            flight=f, 
            departure_time=dept_time,
            arrival_time=arr_time, 
            status='Open',
            price=f.route.base_price + Decimal(random.randint(-500, 500)) # Slight variation from base route price
        )
        
        print(f"✈️ Created Schedule: {f.flight_number} | {route.origin_airport.code} ➡️ {route.destination_airport.code} | {dept_time.strftime('%b %d, %H:%M')}")
        
        # Generate seats for this schedule
        generate_seats(s)
        schedules.append(s)

    print("\n🌟 Successfully injected 30 REAL Philippine flight schedules into the cloud database!")

if __name__ == "__main__":
    seed_real_data()
