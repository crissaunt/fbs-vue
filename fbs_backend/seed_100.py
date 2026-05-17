import os
import django
import random
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Flight, Schedule, Seat, SeatClass, AddOnType

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

def run():
    print("🚀 Adding missing Add-ons...")
    AddOnType.objects.get_or_create(name="Extra Baggage 20kg")
    AddOnType.objects.get_or_create(name="Hot Meal")
    AddOnType.objects.get_or_create(name="Lounge Access")
    AddOnType.objects.get_or_create(name="Priority Boarding")

    print("🚀 Generating 100 new Schedules & Seats...")
    flights = list(Flight.objects.all())
    if not flights:
        print("❌ No flights found. Run seed_all_models_v4.py first.")
        return

    now = timezone.now()
    created_count = 0
    for i in range(100):
        flight = random.choice(flights)
        days_ahead = random.randint(1, 60)
        hour = random.randint(0, 23)
        minute = random.choice([0, 15, 30, 45])
        
        departure = (now + timedelta(days=days_ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        arrival = departure + timedelta(hours=random.randint(1, 4))
        
        schedule = Schedule.objects.create(
            flight=flight,
            departure_time=departure,
            arrival_time=arrival,
            status='Open',
            price=flight.route.base_price + Decimal(random.randint(500, 2000))
        )
        generate_seats(schedule)
        created_count += 1
        if created_count % 10 == 0:
            print(f"✅ Created {created_count}/100 schedules...")
            
    print("🎉 Done! 100 schedules, thousands of seats, and add-ons added successfully!")

if __name__ == "__main__":
    run()
