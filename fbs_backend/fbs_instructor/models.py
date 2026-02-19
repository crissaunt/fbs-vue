import string
import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from app.models import Students  # Correct path for Students
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets

class Instructor(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='instructor_profile', 
        null=True, 
        blank=True
    )
    instructor_id = models.CharField(max_length=50, unique=True, null=True)
    first_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=5, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def get_full_name(self):
        parts = [self.first_name, f"{self.middle_initial}." if self.middle_initial else None, self.last_name]
        return " ".join([p for p in parts if p])

    def __str__(self):
        return f"{self.instructor_id} - {self.get_full_name()}"
    
class Section(models.Model):
    section_name = models.CharField(max_length=200)
    section_code = models.CharField(max_length=50) 
    semester = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=20)
    schedule = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    instructor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sections', 
        null=False 
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['section_code', 'instructor'], name='unique_section_per_instructor')
        ]

    def __str__(self):
        return f"{self.section_code} - {self.section_name}"

class SectionEnrollment(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='section_enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['section', 'student']

    def __str__(self):
        return f"{self.student.student_number} - {self.section.section_code}"

class Activity(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    activity_type = models.CharField(max_length=50, default='Flight Booking')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='activities')
    
    # Flight Booking Requirements
    required_trip_type = models.CharField(
        max_length=20,
        choices=[("one_way", "One Way"), ("round_trip", "Round Trip"), ("multi_city", "Multi City")],
        default='one_way'
    )
    required_origin = models.CharField(max_length=100, blank=True)
    required_destination = models.CharField(max_length=100, blank=True)
    required_departure_date = models.DateField(null=True, blank=True)
    required_return_date = models.DateField(null=True, blank=True)
    required_travel_class = models.CharField(
        max_length=20,
        choices=[('economy', 'Economy'), ('premium_economy', 'Premium Economy'), ('business', 'Business'), ('first', 'First Class')],
        default='economy'
    )
    
    required_passengers = models.PositiveIntegerField(default=1)
    required_children = models.PositiveIntegerField(default=0)
    required_infants = models.PositiveIntegerField(default=0)
    require_passenger_details = models.BooleanField(default=True)
    require_passport = models.BooleanField(default=False)
    
    instructions = models.TextField()
    total_points = models.DecimalField(max_digits=6, decimal_places=2, default=100.00)
    due_date = models.DateTimeField()
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    addon_grading_enabled = models.BooleanField(default=True)
    required_addon_points = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    activity_code = models.CharField(max_length=8, unique=True, blank=True, null=True)
    is_code_active = models.BooleanField(default=False)
    code_generated_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=[('draft', 'Draft'), ('published', 'Published'), ('closed', 'Closed')], default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Activities"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class ActivityPassenger(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    passenger_type = models.CharField(max_length=10, choices=[('adult', 'Adult'), ('child', 'Child'), ('infant', 'Infant')], default='adult')
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)

class ActivityAddOn(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='activity_addons')
    # CHANGED: Changed from 'flightapp.AddOn' to 'app.AddOn' to match your folder structure
    addon = models.ForeignKey('app.AddOn', on_delete=models.CASCADE) 
    passenger = models.ForeignKey(ActivityPassenger, on_delete=models.CASCADE, related_name='passenger_addons')
    is_required = models.BooleanField(default=False)
    quantity_per_passenger = models.PositiveIntegerField(default=1)
    points_value = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)


# Add this to your fbs_instructor/models.py file

class ActivityStudentBinding(models.Model):
    """
    This model links activities to students who are enrolled in the section.
    Created automatically when an activity is activated.
    """
    activity = models.ForeignKey(
        Activity, 
        on_delete=models.CASCADE, 
        related_name='student_bindings'
    )
    student = models.ForeignKey(
        'app.Students',  # Reference to Students model in app
        on_delete=models.CASCADE,
        related_name='activity_bindings'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('assigned', 'Assigned'),
            ('in_progress', 'In Progress'),
            ('submitted', 'Submitted'),
            ('graded', 'Graded')
        ],
        default='assigned'
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('activity', 'student')  # Prevent duplicate bindings
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.activity.title} - {self.student.first_name} {self.student.last_name}"


class UserSession(models.Model):
    """
    Custom session model to support multiple simultaneous logins
    Each login creates a unique session with its own token
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sessions')
    session_token = models.CharField(max_length=64, unique=True, db_index=True)
    role = models.CharField(max_length=20)  # 'student', 'instructor', 'admin'
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} - {self.role} - {self.session_token[:8]}..."
    
    @staticmethod
    def generate_token():
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(48)
    
    def is_expired(self, timeout_hours=24):
        """Check if session has expired (default 24 hours)"""
        if not self.is_active:
            return True
        expiry_time = self.last_activity + timezone.timedelta(hours=timeout_hours)
        return timezone.now() > expiry_time
    
    def refresh(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def deactivate(self):
        """Deactivate this session"""
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    @classmethod
    def cleanup_expired_sessions(cls, timeout_hours=24):
        """Remove expired sessions (can be called by a periodic task)"""
        cutoff_time = timezone.now() - timezone.timedelta(hours=timeout_hours)
        expired = cls.objects.filter(last_activity__lt=cutoff_time)
        count = expired.count()
        expired.delete()
        return count