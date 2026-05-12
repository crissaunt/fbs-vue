import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Country, Airport

print("--- Countries ---")
for c in Country.objects.all():
    print(f"{c.name}: {c.code}")

print("\n--- Philippine Airports ---")
ph_airports = Airport.objects.filter(country__code='PH')
if not ph_airports.exists():
    print("NO Philippine airports found with code 'PH'!")
else:
    for a in ph_airports:
        print(f"{a.name} ({a.code})")

print("\n--- All Airports ---")
for a in Airport.objects.all():
    print(f"{a.name} ({a.code}) - {a.country.name} ({a.country.code})")
