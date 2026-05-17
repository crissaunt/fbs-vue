import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import (
    Country, Airline, Airport, Aircraft, SeatClass, Route, Flight, Schedule,
    Seat, AddOnType
)

def clear_flight_data():
    print("🧹 Cleaning up old dummy flight data...")
    models_to_clear = [
        Seat, Schedule, Flight, Route, Aircraft, SeatClass, Airline, Airport, AddOnType
    ]
    for model in models_to_clear:
        try:
            model.objects.all().delete()
        except Exception as e:
            print(f"  ⚠️ Could not clear {model.__name__}: {e}")
    print("✅ Cleanup complete.")

def generate_seats(schedule):
    aircraft = schedule.flight.aircraft
    layout = aircraft.get_layout_config()
    seat_classes_config = layout.get('seat_classes', [])
    
    if not seat_classes_config:
        sc = SeatClass.objects.filter(airline=aircraft.airline).first()
        if not sc: return
        for r in range(1, 16): # 15 rows
            for c in ['A', 'B', 'C', 'D', 'E', 'F']:
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
    clear_flight_data()
    print("\n🚀 Seeding REAL Philippine flight data...")

    # 1. Country
    ph, _ = Country.objects.get_or_create(name="Philippines", code="PH", currency="PHP")

    # 2. Airlines
    pal = Airline.objects.create(name="Philippine Airlines", code="PR")
    ceb = Airline.objects.create(name="Cebu Pacific", code="5J")
    airasia = Airline.objects.create(name="Philippines AirAsia", code="Z2")
    airlines = [pal, ceb, airasia]

    # 3. SeatClasses
    for a in airlines:
        SeatClass.objects.create(airline=a, name='Economy', price_multiplier=Decimal('1.0'))
        SeatClass.objects.create(airline=a, name='Premium Economy', price_multiplier=Decimal('1.5'))
        SeatClass.objects.create(airline=a, name='Business', price_multiplier=Decimal('2.5'))

    # 4. Airports
    airport_data = [
        ("Ninoy Aquino International Airport", "MNL", "Manila"),
        ("Mactan-Cebu International Airport", "CEB", "Cebu"),
        ("Francisco Bangoy International Airport", "DVO", "Davao"),
        ("Godofredo P. Ramos Airport", "MPH", "Caticlan (Boracay)"),
        ("Puerto Princesa International Airport", "PPS", "Puerto Princesa"),
        ("Iloilo International Airport", "ILO", "Iloilo"),
        ("Bacolod-Silay Airport", "BCD", "Bacolod"),
        ("Laguindingan Airport", "CGY", "Cagayan de Oro"),
    ]
    airports = {}
    for name, code, city in airport_data:
        ap = Airport.objects.create(name=name, code=code, city=city, country=ph, airport_type='domestic')
        airports[code] = ap

    # 5. Aircrafts
    aircrafts = []
    for a in airlines:
        ac1 = Aircraft.objects.create(model="Airbus A320", capacity=180, airline=a)
        ac2 = Aircraft.objects.create(model="Airbus A321neo", capacity=236, airline=a)
        aircrafts.extend([ac1, ac2])

    # 6. Routes
    routes_list = [
        ("MNL", "CEB", 2500), ("CEB", "MNL", 2500),
        ("MNL", "DVO", 3500), ("DVO", "MNL", 3500),
        ("MNL", "MPH", 4500), ("MPH", "MNL", 4500),
        ("MNL", "PPS", 3200), ("CEB", "DVO", 2800),
        ("CEB", "MPH", 2100), ("MNL", "ILO", 2300),
        ("MNL", "BCD", 2400), ("MNL", "CGY", 3100)
    ]
    routes = []
    for orig, dest, price in routes_list:
        r = Route.objects.create(
            origin_airport=airports[orig], destination_airport=airports[dest],
            base_price=Decimal(price)
        )
        routes.append(r)

    # 7. Flights
    flights = []
    for r in routes:
        for i in range(1, 3):
            al = random.choice(airlines)
            ac = random.choice([ac for ac in aircrafts if ac.airline == al])
            fn = f"{al.code} {random.randint(100, 999)}"
            f = Flight.objects.create(flight_number=fn, airline=al, aircraft=ac, route=r)
            flights.append(f)

    # 8. Schedules (30 realistic ones)
    schedules = []
    now = timezone.now().replace(minute=0, second=0, microsecond=0)
    for i in range(30):
        flight = random.choice(flights)
        # Random day within next 7 days
        days_ahead = random.randint(1, 7)
        hour = random.randint(6, 21) # Flights between 6 AM and 9 PM
        dep_time = now + timedelta(days=days_ahead, hours=hour - now.hour)
        # Flight duration roughly 1 hour 30 mins
        arr_time = dep_time + timedelta(hours=1, minutes=30)
        
        s = Schedule.objects.create(
            flight=flight, departure_time=dep_time,
            arrival_time=arr_time, status='Open',
            price=flight.route.base_price
        )
        generate_seats(s)
        schedules.append(s)

    # 9. AddOns
    AddOnType.objects.create(name="Extra Baggage 20kg", description="Additional 20kg check-in baggage", price=Decimal('850.00'), icon="mdi-bag-suitcase")
    AddOnType.objects.create(name="Travel Insurance", description="Comprehensive coverage for your trip", price=Decimal('450.00'), icon="mdi-shield-check")
    AddOnType.objects.create(name="Hot Meal (Chicken Adobo)", description="Classic Filipino Chicken Adobo", price=Decimal('350.00'), icon="mdi-food")
    AddOnType.objects.create(name="Seat Selector (Premium)", description="Choose a seat with extra legroom", price=Decimal('500.00'), icon="mdi-seat-passenger")

    print(f"✅ Successfully created {len(schedules)} REAL schedules with actual seats and add-ons!")
    print("🌟 Database is now ready for a real activity simulation.")

if __name__ == "__main__":
    seed_real_data()
