import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(r'c:\Users\Crissaunt\Documents\GitHub\fbs-vue\fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
try:
    django.setup()
except Exception as e:
    print(f"Django setup warning: {e}")

from flightapp.ml.dynamic_pricing import dynamic_pricing
from django.utils import timezone

def test_pricing_fluctuation():
    origin = 'MNL'
    destination = 'CEB'
    airline = 'Philippine Airlines'
    
    # Test cases: Tomorrow vs 1 Week After
    now = timezone.now()
    dates = [
        ('Tomorrow', now + timedelta(days=1)),
        ('1 Week After', now + timedelta(days=7)),
        ('2 Weeks After', now + timedelta(days=14)),
        ('1 Month After', now + timedelta(days=30)),
    ]
    
    print(f"{'Timeframe':<15} | {'Date':<12} | {'Base Price':<10} | {'Final Price':<10} | {'Urgency Mult':<12}")
    print("-" * 70)
    
    for label, dep_time in dates:
        flight_data = {
            'origin': origin,
            'destination': destination,
            'airline_name': airline,
            'departure_time': dep_time.isoformat(),
            'arrival_time': (dep_time + timedelta(hours=1, minutes=30)).isoformat(),
            'duration_hours': 1.5,
            'total_stops': 0,
            'flight_number': 'PR-123',
            'base_price': 3000, # Assuming a fixed base for comparison
        }
        
        result = dynamic_pricing.get_price_for_user(flight_data)
        
        # Calculate manually what the urgency factor was (it's part of demand_factor)
        # We can see the factors in result['factors_applied']
        factors = result['factors_applied']
        demand_f = factors.get('demand_factor', 1.0)
        
        print(f"{label:<15} | {dep_time.strftime('%Y-%m-%d'):<12} | {result['base_price']:<10} | {result['final_price']:<10} | {demand_f:<12.4f}")

if __name__ == "__main__":
    test_pricing_fluctuation()
