
import os
import django
from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Route, Flight, Schedule, Airline, Aircraft, SeatClass, FareBundle

def add_custom_flight():
    print("🚀 Adding Manila (MNL) to Puerto Princesa (PPS) flights...")
    
    # 1. Get/Create Airports
    def get_or_create_airport(code, name, city, country_name='Philippines'):
        from app.models import Country
        country, _ = Country.objects.get_or_create(name=country_name, defaults={'code': 'PH'})
        if not country.code:
            country.code = 'PH'
            country.save()
        airport, created = Airport.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'city': city,
                'country': country,
                'airport_type': 'domestic'
            }
        )
        if created:
            print(f"✅ Created Airport: {name} ({code})")
        return airport

    origin = get_or_create_airport('MNL', 'Ninoy Aquino International Airport', 'Manila')
    dest = get_or_create_airport('PPS', 'Puerto Princesa International Airport', 'Puerto Princesa')

    # 2. Get/Create Route
    route, created = Route.objects.get_or_create(
        origin_airport=origin,
        destination_airport=dest,
        defaults={'base_price': Decimal('3200.00')}
    )
    if created:
        print(f"✅ Created new route: {origin.code} -> {dest.code}")

    # 3. Get/Create Airline and Aircraft
    airline, _ = Airline.objects.get_or_create(code='5J', defaults={'name': 'Cebu Pacific'})
    aircraft, _ = Aircraft.objects.get_or_create(
        model='Airbus A321neo', 
        airline=airline,
        defaults={'capacity': 236}
    )
    print(f"✅ Ensured Airline ({airline.code}) and Aircraft ({aircraft.model}) exist.")

    # 4. Create Seat Classes for the Airline
    sc_economy, _ = SeatClass.objects.get_or_create(
        airline=airline, name='Economy', 
        defaults={'price_multiplier': Decimal('1.00'), 'color': '#3B82F6'}
    )
    sc_business, _ = SeatClass.objects.get_or_create(
        airline=airline, name='Business', 
        defaults={'price_multiplier': Decimal('2.50'), 'color': '#8B5CF6'}
    )
    print(f"✅ Ensured seat classes (Economy, Business) exist for {airline.code}")

    # 5. Create Fare Bundles for Economy
    FareBundle.objects.get_or_create(
        seat_class=sc_economy, type_code='basic',
        defaults={'name': 'Go Basic', 'markup_fee': Decimal('0.00'), 'display_order': 1}
    )
    FareBundle.objects.get_or_create(
        seat_class=sc_economy, type_code='flex',
        defaults={'name': 'Go Flexi', 'markup_fee': Decimal('800.00'), 'display_order': 2}
    )

    # 6. Create Flight
    flight_num = f"{airline.code}637"
    flight, created = Flight.objects.get_or_create(
        flight_number=flight_num,
        defaults={
            'airline': airline,
            'aircraft': aircraft,
            'route': route,
            'total_stops': 0
        }
    )
    if created:
        print(f"✅ Created new flight: {flight.flight_number}")
    else:
        print(f"ℹ️ Flight {flight.flight_number} already exists.")

    # 7. Create Schedules for the next 7 days
    now = datetime.now()
    count = 0
    for i in range(1, 8):
        future_date = now + timedelta(days=i)
        dep_time = datetime.combine(future_date.date(), datetime.min.time()).replace(
            hour=14, minute=30
        )
        arr_time = dep_time + timedelta(minutes=85) # 1h 25m flight
        
        schedule, s_created = Schedule.objects.get_or_create(
            flight=flight, 
            departure_time=dep_time,
            defaults={
                'arrival_time': arr_time,
                'price': Decimal('3500.00'),
                'status': 'Open'
            }
        )
        
        # Manually trigger seat generation if it's new or has no seats
        if s_created or schedule.seats.count() == 0:
            print(f"💺 Generating seat map for schedule on {dep_time.date()}...")
            schedule.generate_seats()
            count += 1
        
    print(f"✨ Successfully processed {count} schedules for {flight.flight_number} with seat maps!")
    print(f"Total schedules now in DB: {Schedule.objects.count()}")

if __name__ == "__main__":
    add_custom_flight()
