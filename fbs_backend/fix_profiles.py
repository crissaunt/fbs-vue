import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import UserProfile

print("Fixing missing UserProfiles...")
users = User.objects.all()
fixed = 0
for user in users:
    if not hasattr(user, 'userprofile'):
        role = 'instructor' if 'instructor' in user.username.lower() else 'student'
        if user.is_superuser:
            role = 'admin'
        UserProfile.objects.create(user=user, role=role)
        print(f"Created profile for {user.username} (Role: {role})")
        fixed += 1

print(f"Done! Fixed {fixed} missing profiles.")
