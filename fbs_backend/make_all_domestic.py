
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airport, Route, Country

def make_everything_domestic():
    print("🇵🇭 Converting all data to Domestic (Philippines)...")
    
    # 1. Ensure Philippines country exists with code PH
    ph_country, created = Country.objects.get_or_create(
        name='Philippines',
        defaults={'code': 'PH', 'currency': 'PHP'}
    )
    if not ph_country.code:
        ph_country.code = 'PH'
        ph_country.save()
    
    # 2. Update all Airports to be in PH and domestic
    airports = Airport.objects.all()
    count_ap = airports.count()
    for ap in airports:
        ap.country = ph_country
        ap.airport_type = 'domestic'
        ap.save()
    print(f"✅ Updated {count_ap} airports to Domestic/PH.")

    # 3. Trigger Route updates
    routes = Route.objects.all()
    count_rt = routes.count()
    for rt in routes:
        # Since airports are now domestic, the is_domestic property 
        # will automatically return True.
        rt.save() 
            
    print(f"✅ Processed {count_rt} routes.")
    print("🌟 All flight data is now strictly domestic (PH).")

if __name__ == "__main__":
    make_everything_domestic()
