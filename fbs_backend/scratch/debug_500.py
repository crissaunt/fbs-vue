import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

try:
    from flightapp.views import ScheduleViewSet
    print("SUCCESS: ScheduleViewSet imported successfully")
    
    # Try to instantiate and call get_queryset
    from rest_framework.test import APIRequestFactory
    factory = APIRequestFactory()
    request = factory.get('/flightapp/api/schedules/?origin=MNL&destination=PPS&start_date=2026-05-10&end_date=2026-05-16')
    
    view = ScheduleViewSet.as_view({'get': 'list'})
    response = view(request)
    print(f"RESPONSE STATUS: {response.status_code}")
    if response.status_code == 500:
        print(f"RESPONSE DATA: {response.data}")
except Exception as e:
    import traceback
    traceback.print_exc()
