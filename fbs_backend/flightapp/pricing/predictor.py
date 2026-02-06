"""
Flight Price Prediction System
Mimics Cebu Pacific & Philippine Airlines pricing algorithms
Uses Random Forest for high accuracy (98.4% R² score based on research)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
import joblib
import os
from typing import Dict, List, Optional
from django.db.models import Avg, Count, Min, Max
from django.utils import timezone

# Import your models
from app.models import (
    Schedule, Booking, BookingDetail, Route, SeatClass, 
    Seat, Airline, Airport, PassengerInfo
)


class FlightPriceFeatures:
    """
    Feature engineering for flight price prediction.
    Extracts all features used by real airline revenue management systems.
    """
    
    def __init__(self, schedule: Schedule, seat_class: SeatClass, 
                 booking_date: datetime = None):
        self.schedule = schedule
        self.seat_class = seat_class
        self.booking_date = booking_date or timezone.now()
        self.flight = schedule.flight
        self.route = self.flight.route
        self.aircraft = self.flight.aircraft
        
    def extract_features(self) -> Dict:
        """
        Extract all pricing features for ML model.
        Based on research: days_left, airline, route, class, time, duration, demand
        """
        features = {}
        
        # 1. TIME-BASED FEATURES (Critical for yield management)
        departure = self.schedule.departure_time
        days_until_departure = (departure.date() - self.booking_date.date()).days
        features['days_left'] = max(0, days_until_departure)
        
        # Lead time categories (Cebu Pacific style)
        if days_until_departure >= 60:
            features['lead_time_category'] = 'promo'
            features['advance_booking_discount'] = 0.30  # 30% off
        elif days_until_departure >= 30:
            features['lead_time_category'] = 'early'
            features['advance_booking_discount'] = 0.15  # 15% off
        elif days_until_departure >= 14:
            features['lead_time_category'] = 'standard'
            features['advance_booking_discount'] = 0.0
        elif days_until_departure >= 7:
            features['lead_time_category'] = 'last_minute'
            features['advance_booking_discount'] = -0.20  # 20% increase
        else:
            features['lead_time_category'] = 'urgent'
            features['advance_booking_discount'] = -0.40  # 40% increase
        
        # Day of week (Friday/Sunday = expensive)
        features['departure_dow'] = departure.weekday()  # 0=Monday
        features['is_weekend'] = departure.weekday() >= 5
        features['is_peak_day'] = departure.weekday() in [4, 6]  # Friday, Sunday
        
        # Hour of day (business hours = expensive)
        features['departure_hour'] = departure.hour
        if 6 <= departure.hour <= 9 or 17 <= departure.hour <= 20:
            features['time_category'] = 'peak'
            features['time_multiplier'] = 1.25
        elif 10 <= departure.hour <= 16:
            features['time_category'] = 'standard'
            features['time_multiplier'] = 1.0
        else:
            features['time_category'] = 'off_peak'
            features['time_multiplier'] = 0.85
        
        # Month/Seasonality
        features['departure_month'] = departure.month
        if departure.month in [12, 4, 5]:  # Christmas, Summer
            features['season'] = 'high'
            features['season_multiplier'] = 1.3
        elif departure.month in [3, 6, 10, 11]:  # Low season
            features['season'] = 'low'
            features['season_multiplier'] = 0.9
        else:
            features['season'] = 'normal'
            features['season_multiplier'] = 1.0
        
        # 2. ROUTE FEATURES
        features['route_id'] = self.route.id
        features['origin_code'] = self.route.origin_airport.code
        features['dest_code'] = self.route.destination_airport.code
        features['is_domestic'] = self.route.is_domestic
        features['is_international'] = self.route.is_international
        features['is_philippine_domestic'] = self.route.is_philippine_domestic
        
        # Route popularity (based on historical bookings)
        features['route_popularity'] = self._calculate_route_popularity()
        
        # Distance proxy (duration)
        duration_mins = self._get_duration_minutes()
        features['duration_minutes'] = duration_mins
        features['is_long_haul'] = duration_mins > 180
        
        # 3. AIRLINE & CLASS FEATURES
        features['airline_id'] = self.flight.airline.id
        features['airline_code'] = self.flight.airline.code
        features['seat_class_id'] = self.seat_class.id
        features['seat_class_name'] = self.seat_class.name
        features['class_multiplier'] = float(self.seat_class.price_multiplier)
        
        # 4. DEMAND & INVENTORY FEATURES (Real-time yield management)
        features['total_capacity'] = self.aircraft.capacity
        features['available_seats'] = self._get_available_seats_count()
        features['occupancy_rate'] = 1 - (features['available_seats'] / features['total_capacity'])
        
        # Load factor pricing (higher occupancy = higher price)
        if features['occupancy_rate'] >= 0.9:
            features['demand_multiplier'] = 1.5  # Almost full
        elif features['occupancy_rate'] >= 0.75:
            features['demand_multiplier'] = 1.2  # High demand
        elif features['occupancy_rate'] >= 0.5:
            features['demand_multiplier'] = 1.0  # Normal
        else:
            features['demand_multiplier'] = 0.85  # Low demand
        
        # 5. COMPETITIVE & HISTORICAL FEATURES
        features['historical_avg_price'] = self._get_historical_avg_price()
        features['historical_min_price'] = self._get_historical_min_price()
        features['historical_max_price'] = self._get_historical_max_price()
        
        # Booking velocity (how fast seats are selling)
        features['booking_velocity'] = self._calculate_booking_velocity()
        
        # 6. EVENTS & EXTERNAL FACTORS
        features['is_holiday_period'] = self._check_holiday_period()
        features['days_to_holiday'] = self._days_to_nearest_holiday()
        
        return features
    
    def _get_duration_minutes(self) -> int:
        """Calculate flight duration in minutes"""
        if self.schedule.arrival_time and self.schedule.departure_time:
            delta = self.schedule.arrival_time - self.schedule.departure_time
            return int(delta.total_seconds() / 60)
        return 120  # Default 2 hours
    
    def _get_available_seats_count(self) -> int:
        """Get count of available seats for this schedule and class"""
        return Seat.objects.filter(
            schedule=self.schedule,
            seat_class=self.seat_class,
            is_available=True
        ).count()
    
    def _calculate_route_popularity(self) -> float:
        """
        Calculate route popularity score (0-1) based on historical bookings
        """
        # Count bookings in last 90 days for this route
        ninety_days_ago = timezone.now() - timedelta(days=90)
        
        route_bookings = BookingDetail.objects.filter(
            schedule__flight__route=self.route,
            booking_date__gte=ninety_days_ago
        ).count()
        
        # Normalize (assume 1000 bookings is max popularity)
        popularity = min(route_bookings / 1000, 1.0)
        return round(popularity, 2)
    
    def _calculate_booking_velocity(self) -> float:
        """
        Calculate how fast seats are being booked (seats per day)
        High velocity = surge pricing
        """
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        recent_bookings = BookingDetail.objects.filter(
            schedule=self.schedule,
            booking_date__gte=seven_days_ago
        ).count()
        
        velocity = recent_bookings / 7.0  # bookings per day
        return round(velocity, 2)
    
    def _get_historical_avg_price(self) -> float:
        """Get average historical price for this route and class"""
        avg = BookingDetail.objects.filter(
            schedule__flight__route=self.route,
            seat_class=self.seat_class
        ).aggregate(avg_price=Avg('price'))['avg_price']
        
        return float(avg) if avg else float(self.route.base_price)
    
    def _get_historical_min_price(self) -> float:
        """Get minimum historical price"""
        min_price = BookingDetail.objects.filter(
            schedule__flight__route=self.route,
            seat_class=self.seat_class
        ).aggregate(min_price=Min('price'))['min_price']
        
        return float(min_price) if min_price else float(self.route.base_price) * 0.7
    
    def _get_historical_max_price(self) -> float:
        """Get maximum historical price"""
        max_price = BookingDetail.objects.filter(
            schedule__flight__route=self.route,
            seat_class=self.seat_class
        ).aggregate(max_price=Max('price'))['max_price']
        
        return float(max_price) if max_price else float(self.route.base_price) * 1.5
    
    def _check_holiday_period(self) -> bool:
        """Check if departure is during Philippine holiday periods"""
        departure = self.schedule.departure_time.date()
        year = departure.year
        
        # Philippine holidays (simplified)
        holidays = [
            (12, 20, 12, 31),  # Christmas/New Year
            (4, 1, 4, 15),     # Holy Week
            (5, 1, 5, 31),     # Summer vacation
            (10, 31, 11, 2),   # Undas
        ]
        
        for start_month, start_day, end_month, end_day in holidays:
            try:
                start_date = datetime(year, start_month, start_day).date()
                end_date = datetime(year, end_month, end_day).date()
                if start_date <= departure <= end_date:
                    return True
            except ValueError:
                continue
        
        return False
    
    def _days_to_nearest_holiday(self) -> int:
        """Calculate days to nearest major holiday"""
        departure = self.schedule.departure_time.date()
        year = departure.year
        
        # Major holidays
        holiday_dates = [
            datetime(year, 12, 25).date(),  # Christmas
            datetime(year, 1, 1).date(),    # New Year
            datetime(year, 5, 1).date(),    # Labor Day
            datetime(year, 6, 12).date(),   # Independence Day
        ]
        
        days_list = [abs((holiday - departure).days) for holiday in holiday_dates]
        return min(days_list) if days_list else 365


class PricePredictionModel:
    """
    Machine Learning Price Predictor
    Uses Random Forest (best accuracy: 98.4% R²) based on research [^2^]
    Falls back to rule-based system if model not trained
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.model_path = 'pricing/models/price_predictor.pkl'
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if exists"""
        if os.path.exists(self.model_path):
            try:
                data = joblib.load(self.model_path)
                self.model = data['model']
                self.scaler = data['scaler']
                self.feature_columns = data['feature_columns']
            except Exception:
                pass
    
    def predict(self, features: Dict) -> Dict:
        """
        Predict price using ML model or rule-based fallback
        Returns dict with predicted price and factors
        """
        if self.model:
            return self._ml_predict(features)
        else:
            return self._rule_based_predict(features)
    
    def _ml_predict(self, features: Dict) -> Dict:
        """Use trained Random Forest model"""
        # Convert features to DataFrame
        df = pd.DataFrame([features])
        
        # Select only features used by model
        X = df[self.feature_columns]
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        
        return {
            'predicted_price': round(prediction, 2),
            'method': 'machine_learning',
            'confidence': 'high',
            'factors': self._extract_feature_importance(features)
        }
    
    def _rule_based_predict(self, features: Dict) -> Dict:
        """
        Rule-based pricing algorithm (Cebu Pacific/Philippine Airlines style)
        Used when ML model is not available
        """
        base_price = float(self.schedule.flight.route.base_price)
        
        # Start with base price
        price = base_price
        
        # Apply multipliers
        adjustments = []
        
        # 1. Seat class multiplier (Economy, Premium, Business)
        class_mult = features['class_multiplier']
        price *= class_mult
        adjustments.append(f"Class multiplier: {class_mult}x")
        
        # 2. Advance booking discount/increase
        advance_adj = features['advance_booking_discount']
        if advance_adj > 0:
            price *= (1 - advance_adj)
            adjustments.append(f"Advance booking discount: {advance_adj*100}%")
        elif advance_adj < 0:
            price *= (1 + abs(advance_adj))
            adjustments.append(f"Last-minute premium: {abs(advance_adj)*100}%")
        
        # 3. Time of day multiplier
        time_mult = features['time_multiplier']
        price *= time_mult
        adjustments.append(f"Time of day: {time_mult}x")
        
        # 4. Seasonality
        season_mult = features['season_multiplier']
        price *= season_mult
        if season_mult != 1.0:
            adjustments.append(f"Seasonal adjustment: {season_mult}x")
        
        # 5. Demand/Load factor
        demand_mult = features['demand_multiplier']
        price *= demand_mult
        if demand_mult != 1.0:
            adjustments.append(f"Demand multiplier: {demand_mult}x")
        
        # 6. Route popularity
        pop_mult = 1 + (features['route_popularity'] * 0.2)  # Up to 20% increase
        price *= pop_mult
        if pop_mult > 1.0:
            adjustments.append(f"Popular route premium: {(pop_mult-1)*100:.1f}%")
        
        # 7. Booking velocity (surge pricing)
        velocity = features['booking_velocity']
        if velocity > 5:  # More than 5 bookings per day
            surge = min(velocity * 0.05, 0.3)  # Max 30% surge
            price *= (1 + surge)
            adjustments.append(f"High demand surge: {surge*100:.1f}%")
        
        # 8. Holiday premium
        if features['is_holiday_period']:
            price *= 1.4
            adjustments.append("Holiday period premium: 40%")
        elif features['days_to_holiday'] <= 3:
            price *= 1.2
            adjustments.append("Pre-holiday premium: 20%")
        
        # Round to nearest 50 (Philippine Peso style pricing)
        price = round(price / 50) * 50
        
        # Ensure minimum price
        price = max(price, base_price * 0.5)
        
        return {
            'predicted_price': round(price, 2),
            'base_price': base_price,
            'method': 'rule_based',
            'confidence': 'medium',
            'adjustments': adjustments,
            'factors': {
                'days_left': features['days_left'],
                'occupancy_rate': features['occupancy_rate'],
                'lead_time_category': features['lead_time_category'],
                'demand_level': 'high' if features['demand_multiplier'] > 1 else 'normal'
            }
        }
    
    def _extract_feature_importance(self, features: Dict) -> Dict:
        """Extract which features most influenced the price"""
        # Simplified for rule-based, would use model.feature_importances_ for ML
        return {
            'primary_factors': ['days_left', 'occupancy_rate', 'seat_class'],
            'demand_level': features['occupancy_rate'],
            'urgency': 'high' if features['days_left'] < 7 else 'low'
        }


class DynamicPricingEngine:
    """
    Main pricing engine that mimics real airline systems
    Integrates with your existing Booking and Schedule models
    """
    
    def __init__(self):
        self.predictor = PricePredictionModel()
    
    def get_price(self, schedule: Schedule, seat_class: SeatClass, 
                  passenger_type: str = 'Adult') -> Dict:
        """
        Get dynamic price for a specific schedule and seat class
        Returns comprehensive pricing information
        """
        # Extract features
        feature_extractor = FlightPriceFeatures(schedule, seat_class)
        features = feature_extractor.extract_features()
        
        # Get prediction
        prediction = self.predictor.predict(features)
        
        # Apply passenger type discounts (Child/Infant)
        final_price = self._apply_passenger_discount(
            prediction['predicted_price'], 
            passenger_type
        )
        
        # Add taxes (Philippine specific)
        tax_breakdown = self._calculate_taxes(final_price, features, schedule)
        
        return {
            'base_fare': round(prediction['predicted_price'], 2),
            'final_price': round(final_price, 2),
            'total_with_taxes': round(final_price + sum(tax_breakdown.values()), 2),
            'passenger_type': passenger_type,
            'taxes': tax_breakdown,
            'pricing_method': prediction['method'],
            'confidence': prediction['confidence'],
            'price_factors': prediction.get('factors', {}),
            'adjustments': prediction.get('adjustments', []),
            'features': features  # Include for transparency/debugging
        }
    
    def _apply_passenger_discount(self, price: float, passenger_type: str) -> float:
        """Apply discounts for children and infants"""
        if passenger_type == 'Child':
            return price * 0.75  # 25% discount
        elif passenger_type == 'Infant':
            return price * 0.10  # 90% discount (usually just taxes)
        return price
    
    def _calculate_taxes(self, base_fare: float, features: Dict, 
                        schedule: Schedule) -> Dict:
        """
        Calculate Philippine-specific taxes
        Based on TIEZA and airline fee structures
        """
        taxes = {}
        
        # 1. Philippine Travel Tax (TIEZA) - International only
        if features['is_international']:
            taxes['travel_tax'] = 1620.00  # Economy class rate
        
        # 2. Passenger Service Charge (Terminal Fee)
        if features['is_domestic']:
            taxes['terminal_fee'] = 200.00  # Domestic terminal
        else:
            taxes['terminal_fee'] = 550.00  # International terminal
        
        # 3. Aviation Security Fee
        taxes['security_fee'] = 50.00
        
        # 4. VAT (12% on domestic flights)
        if features['is_domestic']:
            taxes['vat'] = round(base_fare * 0.12, 2)
        
        # 5. Fuel Surcharge (YQ) - varies by distance
        duration = features['duration_minutes']
        if duration < 60:
            taxes['fuel_surcharge'] = 200.00
        elif duration < 120:
            taxes['fuel_surcharge'] = 350.00
        else:
            taxes['fuel_surcharge'] = 500.00
        
        return taxes
    
    def get_price_history(self, route: Route, days: int = 30) -> List[Dict]:
        """
        Get historical price data for a route
        Useful for showing price trends to customers
        """
        start_date = timezone.now() - timedelta(days=days)
        
        history = BookingDetail.objects.filter(
            schedule__flight__route=route,
            booking_date__gte=start_date
        ).values(
            'booking_date__date',
            'seat_class__name'
        ).annotate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price'),
            booking_count=Count('id')
        ).order_by('booking_date__date')
        
        return list(history)
    
    def predict_future_prices(self, schedule: Schedule, 
                             days_ahead: int = 7) -> List[Dict]:
        """
        Predict price trends for next N days
        Helps customers decide when to book
        """
        predictions = []
        current_date = timezone.now()
        
        for i in range(days_ahead):
            future_date = current_date + timedelta(days=i)
            
            # Simulate booking on future date
            feature_extractor = FlightPriceFeatures(
                schedule, 
                SeatClass.objects.first(),  # Default class
                future_date
            )
            features = feature_extractor.extract_features()
            prediction = self.predictor.predict(features)
            
            predictions.append({
                'date': future_date.date(),
                'predicted_price': prediction['predicted_price'],
                'confidence': prediction['confidence']
            })
        
        return predictions


# ============================================================
# MODEL TRAINING UTILITIES
# ============================================================

class PriceModelTrainer:
    """
    Train the ML model using historical booking data
    Run this periodically (weekly/monthly) to update model
    """
    
    def __init__(self):
        self.model_dir = 'pricing/models'
        os.makedirs(self.model_dir, exist_ok=True)
    
    def prepare_training_data(self) -> pd.DataFrame:
        """
        Prepare dataset from BookingDetail history
        Format: features -> price
        """
        # Get all completed bookings with prices
        bookings = BookingDetail.objects.filter(
            price__gt=0
        ).select_related(
            'schedule', 'schedule__flight', 'schedule__flight__route',
            'seat_class', 'schedule__flight__aircraft'
        )
        
        data = []
        for booking in bookings:
            try:
                feature_extractor = FlightPriceFeatures(
                    booking.schedule,
                    booking.seat_class,
                    booking.booking_date
                )
                features = feature_extractor.extract_features()
                features['actual_price'] = float(booking.price)
                data.append(features)
            except Exception:
                continue
        
        return pd.DataFrame(data)
    
    def train(self):
        """
        Train Random Forest model
        Research shows RF achieves 98.4% R² vs XGBoost 97.7% [^2^]
        """
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import r2_score, mean_absolute_error
        
        print("Preparing training data...")
        df = self.prepare_training_data()
        
        if len(df) < 100:
            print(f"Insufficient data: {len(df)} samples. Need at least 100.")
            return False
        
        # Select numeric features for ML
        feature_cols = [
            'days_left', 'departure_dow', 'departure_hour', 
            'duration_minutes', 'total_capacity', 'available_seats',
            'occupancy_rate', 'class_multiplier', 'route_popularity',
            'booking_velocity', 'historical_avg_price', 'is_weekend',
            'is_holiday_period', 'days_to_holiday'
        ]
        
        # Handle categorical features
        df['airline_code'] = df['airline_code'].astype('category').cat.codes
        df['seat_class_name'] = df['seat_class_name'].astype('category').cat.codes
        
        feature_cols.extend(['airline_code', 'seat_class_name'])
        
        X = df[feature_cols]
        y = df['actual_price']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest
        print("Training Random Forest model...")
        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"Model Performance:")
        print(f"  R² Score: {r2:.4f} (Target: >0.95)")
        print(f"  MAE: ₱{mae:.2f}")
        
        # Save model
        model_data = {
            'model': model,
            'scaler': scaler,
            'feature_columns': feature_cols,
            'metrics': {'r2': r2, 'mae': mae},
            'trained_at': datetime.now().isoformat()
        }
        
        joblib.dump(model_data, os.path.join(self.model_dir, 'price_predictor.pkl'))
        print(f"Model saved to {self.model_dir}/price_predictor.pkl")
        
        return True


# ============================================================
# DJANGO INTEGRATION - Update your BookingDetail model
# ============================================================

def calculate_booking_price(booking_detail: BookingDetail) -> Decimal:
    """
    Use this in your BookingDetail.save() method
    Replaces the existing _calculate_price() method
    """
    engine = DynamicPricingEngine()
    
    result = engine.get_price(
        schedule=booking_detail.schedule,
        seat_class=booking_detail.seat_class or booking_detail.seat.seat_class,
        passenger_type=booking_detail.passenger.passenger_type
    )
    
    return Decimal(str(result['base_fare']))


# ============================================================
# CSV EXPORT FOR EXTERNAL TRAINING (Tutorial compatibility)
# ============================================================

def export_pricing_data_to_csv(filepath: str = 'flight_pricing_data.csv'):
    """
    Export historical data to CSV for tutorial/training purposes
    Format compatible with standard ML tutorials
    """
    trainer = PriceModelTrainer()
    df = trainer.prepare_training_data()
    
    # Select relevant columns for tutorial
    export_cols = [
        'airline_code', 'origin_code', 'dest_code',
        'seat_class_name', 'days_left', 'departure_hour',
        'departure_dow', 'duration_minutes', 'is_weekend',
        'is_holiday_period', 'occupancy_rate', 'route_popularity',
        'actual_price'
    ]
    
    export_df = df[export_cols]
    export_df.to_csv(filepath, index=False)
    print(f"Exported {len(export_df)} records to {filepath}")
    
    return filepath