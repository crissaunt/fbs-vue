from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction


# ============================================================
# COUNTRY MODEL
# ============================================================
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=5, unique=True, blank=True, null=True)  # e.g., PH, US
    currency = models.CharField(max_length=10, blank=True, null=True)
    
    def __str__(self):
        return self.name


# ============================================================
# AIRLINE + SEAT CLASS + AIRCRAFT
# ============================================================
class Airline(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class SeatClass(models.Model):
    name = models.CharField(max_length=50)
    price_multiplier = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=1.00
    )
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="seat_classes", null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("airline", "name")

    def __str__(self):
        return f"{self.name} (x{self.price_multiplier}) - {self.airline.code if self.airline else ''}"


class Aircraft(models.Model):
    model = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="aircrafts")

    def __str__(self):
        return f"{self.model} ({self.airline.code})"


# ============================================================
# AIRPORT (WITH DOMESTIC / INTERNATIONAL TYPE)
# ============================================================
class Airport(models.Model):
    AIRPORT_TYPE_CHOICES = [
        ('domestic', 'Domestic'),
        ('international', 'International'),
        ('unknown', 'Unknown'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="airports")
    location = models.CharField(max_length=150, null=True, blank=True)
    airport_type = models.CharField(max_length=20, choices=AIRPORT_TYPE_CHOICES, default='domestic')

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_airport_type_display()})"

    @property
    def is_international(self):
        return self.airport_type == "international"

    @property
    def is_domestic(self):
        return self.airport_type == "domestic"
    
    @property
    def is_philippine_airport(self):
        """Check if this is a Philippine airport"""
        if self.country:
            return self.country.name.strip().lower() == 'philippines'
        return False

# ============================================================
# ROUTE (DOMESTIC OR INTERNATIONAL LOGIC) - FIXED
# ============================================================
class Route(models.Model):
    origin_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    destination_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.origin_airport.code} → {self.destination_airport.code}"

    @property
    def is_domestic(self):
        """True if both airports are in the same country."""
        if not (self.origin_airport.country and self.destination_airport.country):
            return (
                self.origin_airport.airport_type in ('domestic', 'unknown') and
                self.destination_airport.airport_type in ('domestic', 'unknown')
            )
        
        return self.origin_airport.country.name.strip().lower() == self.destination_airport.country.name.strip().lower()

    @property
    def is_international(self):
        """True if origin and destination are in different countries."""
        if not (self.origin_airport.country and self.destination_airport.country):
            return (
                self.origin_airport.airport_type == 'international' or
                self.destination_airport.airport_type == 'international'
            )
        
        return self.origin_airport.country.name.strip().lower() != self.destination_airport.country.name.strip().lower()
    
    @property
    def is_philippine_domestic(self):
        """Check if this is a domestic route within the Philippines"""
        if self.origin_airport.country and self.destination_airport.country:
            origin_is_ph = self.origin_airport.country.name.strip().lower() == 'philippines'
            dest_is_ph = self.destination_airport.country.name.strip().lower() == 'philippines'
            return origin_is_ph and dest_is_ph
        return False


# ============================================================
# FLIGHT + SCHEDULE + SEAT
# ============================================================
class Flight(models.Model):
    flight_number = models.CharField(max_length=20, unique=True)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="flights")
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, related_name="flights")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")

    def __str__(self):
        return f"{self.flight_number} ({self.airline.code})"


# In your models.py, update the duration method in the Schedule model:

class Schedule(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open for Booking'),
        ('Closed', 'Closed'),
        ('On Flight', 'On Flight'),
        ('Arrived', 'Arrived'),
    ]

    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="schedules")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Open')

    class Meta:
        indexes = [
            models.Index(fields=['departure_time', 'status']),
            models.Index(fields=['flight', 'departure_time']),
        ]

    def __str__(self):
        return f"{self.flight.flight_number} {self.departure_time}"

    def duration(self):
        """Calculate flight duration safely handling None values"""
        if not self.departure_time or not self.arrival_time:
            return "N/A"
        
        diff = self.arrival_time - self.departure_time
        total_minutes = int(diff.total_seconds() // 60)
        hours, minutes = divmod(total_minutes, 60)
        days = diff.days

        if days > 0:
            return f"{hours}h {minutes}m (+{days}d)"
        return f"{hours}h {minutes}m"

    def clean(self):
        """Validate schedule times"""
        if self.arrival_time <= self.departure_time:
            raise ValidationError("Arrival time must be after departure time")
        
        # Don't allow schedules in the past
        if self.departure_time < timezone.now():
            raise ValidationError("Cannot create schedule in the past")

    @property
    def is_open(self):
        return self.status == "Open"


# Add this to your existing Seat model or update it
class Seat(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="seats" , null=True)
    seat_class = models.ForeignKey(SeatClass, on_delete=models.CASCADE, related_name="seats" , null=True)
    seat_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
    
    # Add row and column for easier mapping
    row = models.PositiveIntegerField(null=True)
    column = models.CharField(max_length=1, null=True)  # A, B, C, D, E, F
    
    # Add seat features
    has_extra_legroom = models.BooleanField(default=False)
    is_exit_row = models.BooleanField(default=False)
    is_bulkhead = models.BooleanField(default=False)
    is_window = models.BooleanField(default=False)
    is_aisle = models.BooleanField(default=False)
    
    price_adjustment = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Additional price for premium seats"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['schedule', 'seat_number'],
                name='unique_seat_per_schedule'
            ),
            models.UniqueConstraint(
                fields=['schedule', 'row', 'column'],
                name='unique_position_per_schedule'
            )
        ]
        indexes = [
            models.Index(fields=['schedule', 'is_available']),
            models.Index(fields=['schedule', 'seat_class']),
            models.Index(fields=['schedule', 'row', 'column']),
        ]

    def __str__(self):
        return f"{self.seat_number} - {self.seat_class.name}"

    @property
    def seat_code(self):
        """Return seat code like '1A'"""
        return f"{self.row}{self.column}"

    @property
    def final_price(self):
        """Calculate final price including adjustments"""
        base_price = self.schedule.price if self.schedule else 0
        multiplier = self.seat_class.price_multiplier if self.seat_class else 1
        return (base_price * multiplier) + self.price_adjustment

    @property
    def seat_features(self):
        """Return list of seat features"""
        features = []
        if self.has_extra_legroom:
            features.append("Extra Legroom")
        if self.is_exit_row:
            features.append("Exit Row")
        if self.is_bulkhead:
            features.append("Bulkhead")
        if self.is_window:
            features.append("Window")
        if self.is_aisle:
            features.append("Aisle")
        return features




# ============================================================
# TRAVEL INSURANCE SYSTEM
# ============================================================
class InsuranceProvider(models.Model):
    """
    Actual insurance company (e.g., Allianz, AXA, AIG).
    Owns the policy and handles claims.
    """
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    
    # Commission rate for sellers (airlines/booking platforms)
    default_commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=15.00,
        help_text="Default commission percentage for sellers"
    )
    
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class InsuranceBenefit(models.Model):
    """Individual benefits that can be added to insurance plans"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    icon_class = models.CharField(max_length=50, blank=True, null=True, help_text="CSS class for icon (e.g., 'fas fa-stethoscope')")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which benefits are displayed")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        
    def __str__(self):
        return self.name


class InsuranceCoverageType(models.Model):
    """Type of coverage (Medical, Baggage, Cancellation, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="e.g., PHP, per day, per hour"
    )
    icon_class = models.CharField(max_length=50, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class TravelInsurancePlan(models.Model):
    """
    Insurance plans sold during flight booking.
    Owned by an insurance provider, sold by OTA or airline.
    """
    provider = models.ForeignKey(
        InsuranceProvider,
        on_delete=models.CASCADE,
        related_name="insurance_plans"
    )

    # Optional: only shown for selected airlines
    airlines = models.ManyToManyField(
        'Airline',
        blank=True,
        related_name="insurance_plans",
        help_text="Leave empty if available for all airlines"
    )

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    # Price shown to customers
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # What provider actually charges (for commission calculation)
    wholesale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        help_text="Amount paid to insurance provider"
    )

    coverage_duration_days = models.PositiveIntegerField(default=30)

    plan_type = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic'),
            ('standard', 'Standard'),
            ('premium', 'Premium'),
            ('comprehensive', 'Comprehensive'),
        ],
        default='standard'
    )

    best_for = models.CharField(max_length=200, blank=True, null=True)

    # Clear disclosure fields
    policy_document_url = models.URLField(blank=True, null=True)
    terms_conditions_url = models.URLField(blank=True, null=True)
    claims_contact = models.TextField(blank=True, null=True)

    # Seller type - who's selling this?
    seller_type = models.CharField(
        max_length=20,
        choices=[
            ('booking_platform', 'Booking Platform (OTA)'),
            ('airline', 'Airline'),
            ('third_party', 'Third-Party Agent'),
        ],
        default='booking_platform'
    )

    benefits = models.ManyToManyField(
        InsuranceBenefit,
        blank=True,
        related_name='insurance_plans'
    )

    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'retail_price']
        unique_together = ('provider', 'name')

    def __str__(self):
        return f"{self.provider.name} - {self.name}"

    @property
    def commission_amount(self):
        """Commission earned by seller"""
        if self.wholesale_price:
            return self.retail_price - self.wholesale_price
        return Decimal('0.00')

    @property
    def commission_rate(self):
        """Commission percentage"""
        if self.retail_price > 0:
            return (self.commission_amount / self.retail_price) * 100
        return Decimal('0.00')

    @property
    def formatted_price(self):
        return f"₱{self.retail_price:,.2f}"
    
    @property
    def coverages(self):
        """Get all coverages for this plan"""
        return self.plan_coverages.all().select_related('coverage_type')
    
    @property
    def coverage_summary(self):
        """Generate a summary of coverage amounts"""
        summary = []
        for coverage in self.coverages:
            if coverage.amount > 0:
                if coverage.coverage_type.unit:
                    summary.append(f"{coverage.coverage_type.name}: ₱{coverage.amount:,.0f} {coverage.coverage_type.unit}")
                else:
                    summary.append(f"{coverage.coverage_type.name}: ₱{coverage.amount:,.0f}")
        return " | ".join(summary[:3])

    @property
    def disclosure_text(self):
        """Legal disclosure text"""
        seller = "booking platform" if self.seller_type == 'booking_platform' else "airline"
        return f"This travel insurance is underwritten by {self.provider.name} and sold through this {seller} as an authorized distributor."

# ============================================================
# MEAL CATEGORIES AND OPTIONS
# ============================================================
class MealCategory(models.Model):
    """Meal categories (e.g., Main Course, Dessert, Beverage)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = "Meal Categories"
    
    def __str__(self):
        return self.name


class MealOption(models.Model):
    """Individual meal options that can be purchased"""
    
    MEAL_TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('halal', 'Halal'),
        ('kosher', 'Kosher'),
        ('gluten_free', 'Gluten Free'),
        ('child', "Child's Meal"),
        ('infant', "Infant's Meal"),
    ]
    
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="meals")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, default='standard')
    category = models.ForeignKey(MealCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_included = models.BooleanField(default=False, help_text="Is this meal included in the base fare?")
    
    # Meal details
    calories = models.PositiveIntegerField(blank=True, null=True, help_text="Approximate calories")
    contains = models.TextField(blank=True, null=True, help_text="Ingredients/contents")
    allergens = models.TextField(blank=True, null=True, help_text="Common allergens (nuts, dairy, etc.)")
    
    # Availability
    available_on_domestic = models.BooleanField(default=True)
    available_on_international = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Flight timing applicability
    available_for_breakfast = models.BooleanField(default=True)
    available_for_lunch = models.BooleanField(default=True)
    available_for_dinner = models.BooleanField(default=True)
    
    image_url = models.URLField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        unique_together = ('airline', 'name')
    
    def __str__(self):
        return f"{self.name} ({self.airline.code}) - ₱{self.price}"
    
    @property
    def dietary_info(self):
        """Return dietary information"""
        info = [self.get_meal_type_display()]
        if self.allergens:
            info.append(f"Contains: {self.allergens}")
        return " • ".join(info)
    
    @property
    def is_free(self):
        return self.price == 0 or self.is_included


# ============================================================
# WHEELCHAIR AND ASSISTANCE SERVICES
# ============================================================
class AssistanceService(models.Model):
    """Special assistance services for passengers"""
    
    SERVICE_TYPE_CHOICES = [
        ('wheelchair', 'Wheelchair Assistance'),
        ('boarding', 'Pre-boarding Assistance'),
        ('medical', 'Medical Assistance'),
        ('unaccompanied_minor', 'Unaccompanied Minor'),
        ('pet', 'Pet Travel Assistance'),
        ('other', 'Other Special Assistance'),
    ]
    
    LEVEL_CHOICES = [
        ('basic', 'Basic Assistance'),
        ('standard', 'Standard Assistance'),
        ('premium', 'Premium Assistance'),
    ]
    
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="assistance_services")
    name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES, default='wheelchair')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='standard')
    description = models.TextField(blank=True, null=True)
    
    # Requirements and notes
    requires_advance_notice = models.PositiveIntegerField(
        default=48,
        help_text="Hours of advance notice required"
    )
    special_requirements = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_included = models.BooleanField(default=True, help_text="Is this service included in the base fare?")
    
    # Restrictions
    passenger_type_applicable = models.CharField(
        max_length=20,
        choices=[('all', 'All'), ('adults_only', 'Adults Only'), ('children_only', 'Children Only')],
        default='all'
    )
    
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = "Assistance Services"
    
    def __str__(self):
        return f"{self.name} ({self.airline.code})"
    
    @property
    def is_free(self):
        return self.price == 0 or self.is_included
    
    @property
    def advance_notice_text(self):
        if self.requires_advance_notice >= 24:
            days = self.requires_advance_notice // 24
            return f"Requires {days} day{'s' if days > 1 else ''} advance notice"
        return f"Requires {self.requires_advance_notice} hours advance notice"


# ============================================================
# BAGGAGE OPTIONS
# ============================================================
class BaggageOption(models.Model):
    """Extra baggage options that can be purchased"""
    
    WEIGHT_CHOICES = [
        (0, 'No Extra'),
        (5, '5kg'),
        (10, '10kg'),
        (15, '15kg'),
        (20, '20kg'),
        (25, '25kg'),
        (30, '30kg'),
        (32, '32kg'),
        (40, '40kg'),
    ]
    
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="baggage_options")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Baggage details
    weight_kg = models.IntegerField(choices=WEIGHT_CHOICES, default=0)
    dimensions = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 158cm (L+W+H)")
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_included = models.BooleanField(default=False, help_text="Is this baggage included in the base fare?")
    
    # Restrictions
    applies_domestic = models.BooleanField(default=True)
    applies_international = models.BooleanField(default=True)
    passenger_type_applicable = models.CharField(
        max_length=20,
        choices=[('all', 'All'), ('adults_only', 'Adults Only'), ('children_only', 'Children Only')],
        default='all'
    )
    
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'weight_kg']
        unique_together = ('airline', 'weight_kg')
    
    def __str__(self):
        return f"{self.weight_kg}kg Extra Baggage - ₱{self.price}"
    
    @property
    def formatted_weight(self):
        return f"{self.weight_kg}kg"
    
    @property
    def is_free(self):
        return self.price == 0 or self.is_included


class PlanCoverage(models.Model):
    """Coverage amounts per insurance plan"""
    insurance_plan = models.ForeignKey(
        TravelInsurancePlan,
        on_delete=models.CASCADE,
        related_name="plan_coverages"
    )
    coverage_type = models.ForeignKey(
        InsuranceCoverageType,
        on_delete=models.CASCADE,
        related_name="plan_coverage_links"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('insurance_plan', 'coverage_type')
        ordering = ['coverage_type__display_order']

    def __str__(self):
        return f"{self.insurance_plan.name} - {self.coverage_type.name}: ₱{self.amount:,.2f}"


class BookingInsuranceRecord(models.Model):
    """
    Records insurance purchase for EACH PASSENGER (not per booking).
    Tracks financials and policy details.
    """
    booking_detail = models.OneToOneField(
        'BookingDetail',
        on_delete=models.CASCADE,
        related_name='insurance_record',
        null=True,
        blank=True
    )
    
    insurance_plan = models.ForeignKey(
        TravelInsurancePlan,
        on_delete=models.PROTECT,
        related_name='sales'
    )
    
    # Policy details
    policy_number = models.CharField(max_length=100, unique=True, blank=True)
    insured_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Financial tracking
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    provider_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Coverage period
    coverage_start = models.DateTimeField(null=True, blank=True)
    coverage_end = models.DateTimeField(null=True, blank=True)
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('claimed', 'Claim Filed'),
        ('refunded', 'Refunded'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Timestamps
    purchased_at = models.DateTimeField(auto_now_add=True)
    policy_issued_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-purchased_at']

    def __str__(self):
        passenger_name = self.booking_detail.passenger.get_full_name() if self.booking_detail else "Unknown"
        return f"Policy {self.policy_number} - {passenger_name}"

    def save(self, *args, **kwargs):
        # Auto-calculate financials if not set
        if not self.sale_price:
            self.sale_price = self.insurance_plan.retail_price
        
        if not self.commission_rate:
            self.commission_rate = self.insurance_plan.commission_rate
        
        if not self.commission_amount:
            self.commission_amount = (self.sale_price * self.commission_rate) / 100
        
        if not self.provider_payout:
            self.provider_payout = self.sale_price - self.commission_amount
        
        # Generate policy number
        if not self.policy_number:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            prefix = self.insurance_plan.provider.code.upper()[:3]
            self.policy_number = f"{prefix}-{timestamp}-{self.booking_detail.id:06d}"
        
        # Set coverage dates based on flight schedule
        if not self.coverage_start and self.booking_detail:
            # Coverage typically starts 24 hours before departure
            self.coverage_start = self.booking_detail.schedule.departure_time - timezone.timedelta(hours=24)
            
        if not self.coverage_end and self.coverage_start:
            # Coverage ends after specified duration
            self.coverage_end = self.coverage_start + timezone.timedelta(
                days=self.insurance_plan.coverage_duration_days
            )
        
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        """Check if insurance is currently valid"""
        now = timezone.now()
        return (
            self.status == 'active' and
            self.coverage_start and
            self.coverage_end and
            self.coverage_start <= now <= self.coverage_end
        )


# ============================================================
# PASSENGERS
# ============================================================
class PassengerInfo(models.Model):
    TYPE_CHOICES = [("Adult", "Adult"), ("Child", "Child"), ("Infant", "Infant")]

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    passenger_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="Adult")

    # Infant linked to adult
    linked_adult = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="infants"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.passenger_type})"
    
    def get_full_name(self):
        """Return full name of passenger"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


# ============================================================
# BOOKING SYSTEM
# ============================================================
class Booking(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='bookings')
    trip_type = models.CharField(
        max_length=20,
        choices=[
            ("one_way", "One Way"),
            ("round_trip", "Round Trip"),
            ("multi_city", "Multi City"),
        ]
    )

    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Price snapshots
    base_fare_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    insurance_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Booking {self.id} - {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        # Calculate totals when booking is first created
        if self._state.adding:
            self.base_fare_total = self._calculate_base_fare_total()
            self.insurance_total = self._calculate_insurance_total()
            self.tax_total = self._calculate_tax_total()
        super().save(*args, **kwargs)
    
    def _calculate_base_fare_total(self):
        total = Decimal('0.00')
        for detail in self.details.all():
            total += detail.price or Decimal('0.00')
        return total
    
    def _calculate_insurance_total(self):
        total = Decimal('0.00')
        for detail in self.details.all():
            if detail.has_insurance:
                total += detail.insurance_cost
        return total
    
    def _calculate_tax_total(self):
        total = Decimal('0.00')
        for detail in self.details.all():
            total += detail.tax_amount or Decimal('0.00')
        return total
    
    @property
    def payment(self):
        return self.payments.last()
    
    @property
    def total_amount(self):
        return self.base_fare_total + self.insurance_total + self.tax_total
    
    @property
    def has_insurance(self):
        """Check if any passenger has insurance"""
        return any(detail.has_insurance for detail in self.details.all())


# ============================================================
# ADD-ONS SYSTEM
# ============================================================
class AddOnType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class AddOn(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="addons", null=True)

    seat_class = models.ForeignKey(
        SeatClass, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="addons"
    )

    type = models.ForeignKey(
        AddOnType, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="addons"
    )
    
    # Link to insurance plan (for insurance add-ons)
    insurance_plan = models.ForeignKey(
        TravelInsurancePlan, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="addon_links"
    )
    
    # Links to service options
    meal_option = models.ForeignKey(
        MealOption, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="addon_links"
    )
    
    baggage_option = models.ForeignKey(
        BaggageOption, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="addon_links"
    )
    
    assistance_service = models.ForeignKey(
        AssistanceService, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="addon_links"
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    included = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ₱{self.price}"
    
    @property
    def is_insurance(self):
        """Check if this add-on is an insurance plan"""
        return self.insurance_plan is not None
    
    @property
    def is_meal(self):
        """Check if this add-on is a meal"""
        return self.meal_option is not None
    
    @property
    def is_baggage(self):
        """Check if this add-on is baggage"""
        return self.baggage_option is not None
    
    @property
    def is_assistance(self):
        """Check if this add-on is an assistance service"""
        return self.assistance_service is not None
    
    @property
    def get_insurance_plan(self):
        """Get the linked insurance plan if this is an insurance add-on"""
        return self.insurance_plan
    
    @property
    def get_meal_option(self):
        """Get the linked meal option"""
        return self.meal_option
    
    @property
    def get_baggage_option(self):
        """Get the linked baggage option"""
        return self.baggage_option
    
    @property
    def get_assistance_service(self):
        """Get the linked assistance service"""
        return self.assistance_service


# ============================================================
# BOOKING DETAIL
# ============================================================
class BookingDetail(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="details")
    passenger = models.ForeignKey(PassengerInfo, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True)
    seat_class = models.ForeignKey(SeatClass, on_delete=models.SET_NULL, null=True, blank=True)
    booking_date = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    addons = models.ManyToManyField(AddOn, blank=True, related_name='booking_details')
    
    class Meta:
        indexes = [
            models.Index(fields=['booking', 'seat']),
        ]

    def save(self, *args, **kwargs):
        # Only calculate price on creation
        is_new = self._state.adding
        if is_new and self.seat:
            self.price = self._calculate_price()
        super().save(*args, **kwargs)
    
    def _calculate_price(self):
        """Calculate price for this booking detail"""
        base_price = self.schedule.flight.route.base_price
        multiplier = self.seat.seat_class.price_multiplier if self.seat.seat_class else Decimal("1.0")

        days_diff = (self.schedule.departure_time.date() - timezone.now().date()).days

        if days_diff >= 30:
            factor = Decimal("0.8")      # advance booking discount
        elif 7 <= days_diff <= 29:
            factor = Decimal("1.0")      # normal
        else:
            factor = Decimal("1.5")      # last-minute fare increase

        return base_price * multiplier * factor
    
    @property
    def has_insurance(self):
        return hasattr(self, 'insurance_record') and self.insurance_record is not None
    
    @property
    def insurance_cost(self):
        if self.has_insurance:
            return self.insurance_record.sale_price
        return Decimal('0.00')
    
    @property
    def insurance_policy_number(self):
        if self.has_insurance:
            return self.insurance_record.policy_number
        return None
    
    @property
    def total_with_insurance(self):
        """Get total price including insurance"""
        return self.price + self.insurance_cost + self.tax_amount
    
    @property
    def total_amount(self):
        """Get total price including insurance and tax"""
        return self.price + self.insurance_cost + self.tax_amount


# ============================================================
# SIGNAL TO CREATE INSURANCE RECORD WHEN ADDED
# ============================================================
@receiver(post_save, sender=BookingDetail)
def create_insurance_record_if_needed(sender, instance, created, **kwargs):
    """
    Create insurance record when insurance addon is purchased.
    """
    # Only process if it's a new booking detail
    if created:
        return
    
    # Check if insurance was selected via addons
    insurance_addons = instance.addons.filter(is_insurance=True)
    
    # If insurance addon exists and no insurance record yet
    if insurance_addons.exists() and not instance.has_insurance:
        # Assuming only one insurance addon per passenger
        insurance_addon = insurance_addons.first()
        
        if insurance_addon.insurance_plan:
            BookingInsuranceRecord.objects.create(
                booking_detail=instance,
                insurance_plan=insurance_addon.insurance_plan,
                insured_amount=insurance_addon.insurance_plan.retail_price
            )
    
    # If insurance record exists but addon was removed
    elif instance.has_insurance and not insurance_addons.exists():
        # Remove the insurance record
        instance.insurance_record.delete()


# ============================================================
# SIGNAL — AUTO-GENERATE SEATS WHEN A NEW SCHEDULE IS CREATED
# ============================================================
@receiver(post_save, sender=Schedule)
def create_seats_for_schedule(sender, instance, created, **kwargs):
    """
    Auto-generate seats when a new schedule is created.
    This is now properly scoped to Schedule model only.
    """
    if created:
        from django.db import transaction
        
        SeatClass = apps.get_model('flightapp', 'SeatClass')
        Seat = apps.get_model('flightapp', 'Seat')
        
        aircraft = instance.flight.aircraft
        
        with transaction.atomic():
            # Get airline's seat classes or default classes
            seat_classes = SeatClass.objects.filter(
                airline=instance.flight.airline
            ).order_by('price_multiplier')
            
            if not seat_classes.exists():
                # Fallback to default seat classes
                seat_classes = SeatClass.objects.filter(airline__isnull=True)
            
            if seat_classes.exists():
                # Distribute seats across classes
                total_capacity = aircraft.capacity
                seats_per_class = total_capacity // seat_classes.count()
                remaining_seats = total_capacity % seat_classes.count()
                
                seat_number = 1
                seats_to_create = []
                
                for i, seat_class in enumerate(seat_classes):
                    # Add extra seats to first class if uneven distribution
                    class_capacity = seats_per_class + (1 if i < remaining_seats else 0)
                    
                    for j in range(class_capacity):
                        seats_to_create.append(Seat(
                            schedule=instance,
                            seat_class=seat_class,
                            seat_number=f"{seat_number:03d}",
                            is_available=True
                        ))
                        seat_number += 1
                
                Seat.objects.bulk_create(seats_to_create)


# ============================================================
# TAX SYSTEM FOR FLIGHT BOOKINGS (Models only, no calculation)
# ============================================================
class TaxType(models.Model):
    """
    Defines a tax, fee, or surcharge used in airfare pricing.
    Examples:
    - PH Travel Tax (TIEZA)
    - Passenger Service Charge (Terminal Fee)
    - VAT
    - Fuel Surcharge (YQ/YR)
    """

    TAX_CATEGORY_CHOICES = [
        ('government', 'Government Tax'),
        ('airport', 'Airport Fee'),
        ('airline', 'Airline Surcharge'),
    ]

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    category = models.CharField(
        max_length=20,
        choices=TAX_CATEGORY_CHOICES
    )

    # Calculation rules
    per_passenger = models.BooleanField(default=True)
    adult_only = models.BooleanField(default=False)

    # Route applicability
    applies_domestic = models.BooleanField(default=True)
    applies_international = models.BooleanField(default=True)

    applies_departure_country = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text="ISO country code (e.g. PH). Leave blank for all."
    )

    base_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Default rate if no override exists"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class AirlineTax(models.Model):
    """
    Airline-specific surcharge overrides.
    Example: Fuel surcharge (YQ/YR)
    """

    airline = models.ForeignKey(
        Airline,
        on_delete=models.CASCADE,
        related_name="tax_rates"
    )
    tax_type = models.ForeignKey(
        TaxType,
        on_delete=models.CASCADE,
        related_name="airline_rates"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('airline', 'tax_type')

    def __str__(self):
        return f"{self.airline.code} - {self.tax_type.code}"


class AirportFee(models.Model):
    """
    Airport-imposed fees such as terminal and security fees.
    """

    airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="fees"
    )
    tax_type = models.ForeignKey(
        TaxType,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('airport', 'tax_type')

    def __str__(self):
        return f"{self.airport.code} - {self.tax_type.name}"


class PassengerTypeTaxRate(models.Model):
    """
    Passenger-type specific tax rates.
    Used for Travel Tax, exemptions, discounts.
    """

    PASSENGER_TYPE_CHOICES = [
        ('adult', 'Adult'),
        ('child', 'Child'),
        ('infant', 'Infant'),
    ]

    tax_type = models.ForeignKey(
        TaxType,
        on_delete=models.CASCADE,
        related_name="passenger_rates"
    )
    passenger_type = models.CharField(
        max_length=10,
        choices=PASSENGER_TYPE_CHOICES
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('tax_type', 'passenger_type')

    def __str__(self):
        return f"{self.tax_type.code} - {self.passenger_type}: ₱{self.amount}"


class BookingTax(models.Model):
    """
    Snapshot of applied taxes at time of booking.
    """

    booking = models.ForeignKey(
        'Booking',
        on_delete=models.CASCADE,
        related_name='taxes'
    )
    tax_type = models.ForeignKey(
        TaxType,
        on_delete=models.PROTECT
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    passenger_type = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.booking.id} - {self.tax_type.code}: ₱{self.amount}"


# ============================================================
# PAYMENT
# ============================================================
class Payment(models.Model):
    PAYMENT_METHODS = [
        ("GCash", "GCash"),
        ("Credit Card", "Credit Card"),
        ("Cash", "Cash"),
        ("Paypal", "Paypal"),
    ]

    PAYMENT_STATUS = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="Pending")

    def __str__(self):
        return f"Payment {self.id} (Booking {self.booking.id})"


# ============================================================
# CHECK-IN DETAIL
# ============================================================
class CheckInDetail(models.Model):
    booking_detail = models.ForeignKey(BookingDetail, on_delete=models.CASCADE, related_name="checkins")
    check_in_time = models.DateTimeField(auto_now_add=True)
    boarding_pass = models.CharField(max_length=100, blank=True, null=True)
    baggage_count = models.PositiveIntegerField(default=0)
    baggage_weight = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Check-In {self.id} (Booking {self.booking_detail.booking.id})"


# ============================================================
# TRACK LOGS
# ============================================================
class TrackLog(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name="tracklogs")
    action = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"


# ============================================================
# UTILITY FUNCTIONS FOR SEAT BOOKING
# ============================================================
def reserve_seat_with_lock(seat_id, booking_detail_id):
    """
    Safely reserve a seat using database locking to prevent race conditions.
    """
    from django.db import transaction, DatabaseError
    
    try:
        with transaction.atomic():
            # Lock the seat row
            seat = Seat.objects.select_for_update().get(id=seat_id)
            
            if not seat.is_available:
                raise ValueError("Seat is already booked")
            
            # Update seat availability
            seat.is_available = False
            seat.save()
            
            # Update booking detail with seat
            booking_detail = BookingDetail.objects.get(id=booking_detail_id)
            booking_detail.seat = seat
            booking_detail.save()
            
            return True
            
    except Seat.DoesNotExist:
        raise ValueError("Seat not found")
    except DatabaseError as e:
        # Handle database errors (e.g., deadlock)
        raise Exception(f"Database error: {str(e)}")


# ============================================================
# ADD HELPER PROPERTIES
# ============================================================

# Add property to BookingDetail
@property
def booking_detail_total_amount(self):
    """Calculate total for this booking detail including insurance and tax."""
    return self.price + self.insurance_cost + self.tax_amount

BookingDetail.total_amount = booking_detail_total_amount

# Add properties to Booking
@property
def booking_total_amount(self):
    """Calculate total booking amount including insurance and tax."""
    return self.base_fare_total + self.insurance_total + self.tax_total

Booking.total_amount = booking_total_amount