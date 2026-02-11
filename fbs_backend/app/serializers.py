from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Added first_name and last_name to the fields
        fields = ['id', 'username', 'email', 'first_name', 'last_name']