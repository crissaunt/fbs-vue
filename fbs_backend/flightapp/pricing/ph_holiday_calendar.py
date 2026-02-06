"""
Philippine Holiday & Fiesta Calendar for Flight Pricing
Captures unique cultural events that drive domestic travel demand
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional
import calendar

class PhilippineCalendar:
    """
    Comprehensive Philippine holiday and fiesta calendar
    Used for dynamic pricing predictions
    """
    
    # Fixed Date Holidays
    FIXED_HOLIDAYS = {
        (1, 1): ("New Year's Day", "high", 5),      # name, impact_level, days_of_effect
        (2, 14): ("Valentine's Day", "medium", 2),
        (4, 9): ("Araw ng Kagitingan", "medium", 3),
        (5, 1): ("Labor Day", "high", 4),
        (6, 12): ("Independence Day", "medium", 3),
        (8, 21): ("Ninoy Aquino Day", "low", 2),
        (8, 30): ("National Heroes Day", "high", 4),  # Last Monday of August (moved)
        (11, 1): ("All Saints' Day", "high", 5),    # Undas - massive migration
        (11, 2): ("All Souls' Day", "high", 3),
        (11, 30): ("Bonifacio Day", "medium", 2),
        (12, 8): ("Feast of Immaculate Conception", "medium", 2),
        (12, 24): ("Christmas Eve", "high", 3),
        (12, 25): ("Christmas Day", "critical", 7),
        (12, 30): ("Rizal Day", "medium", 2),
        (12, 31): ("New Year's Eve", "high", 4),
    }
    
    # Movable Holidays (approximate dates for 2024-2026)
    HOLY_WEEK_DATES = {
        2024: (3, 24, 3, 31),   # Palm Sunday to Easter Sunday
        2025: (4, 13, 4, 20),
        2026: (4, 5, 4, 12),
    }
    
    # Chinese New Year (Lunar)
    CHINESE_NEW_YEAR = {
        2024: (2, 10),
        2025: (1, 29),
        2026: (2, 17),
    }
    
    # Eid'l Fitr (movable Islamic holiday)
    EID_FITR = {
        2024: (4, 10),
        2025: (3, 31),
        2026: (3, 20),
    }
    
    # Major Regional Fiestas (City/Province, Month, Day, Name, Impact)
    FIESTAS = [
        # JANUARY
        ("Cebu", 1, 15, "Sinulog Festival", "critical"),           # Cebu flights spike
        ("Kalibo", 1, 21, "Ati-Atihan Festival", "high"),          # Boracay gateway
        ("Manila", 1, 9, "Feast of Black Nazarene", "high"),       # Quiapo
        
        # FEBRUARY
        ("Baguio", 2, 1, "Panagbenga Festival", "high"),           # Month-long flower festival
        ("Tacloban", 2, 29, "Pintados-Kasadyaan", "medium"),       # Leyte
        
        # MARCH
        ("Davao", 3, 16, "Araw ng Dabaw", "high"),                 # Davao City Day
        
        # APRIL - May vary with Holy Week
        
        # MAY
        ("Lucban", 5, 15, "Pahiyas Festival", "high"),             # Quezon
        ("Pulilan", 5, 14, "Pulilan Carabao Festival", "medium"),  # Bulacan
        ("Davao", 5, 3, "Flores de Mayo", "medium"),               # Santacruzan
        
        # JUNE
        ("Cagayan de Oro", 6, 28, "Higalaay Festival", "high"),    # Kagay-an Festival
        
        # AUGUST
        ("Davao", 8, 3, "Kadayawan Festival", "critical"),         # Davao's biggest
        
        # OCTOBER
        ("Bacolod", 10, 19, "MassKara Festival", "high"),          # Negros
        
        # DECEMBER
        ("Cebu", 12, 16, "Simbang Gabi Start", "high"),            # 9 days before Christmas
    ]
    
    # Long weekends (predicted for 2024-2025)
    LONG_WEEKENDS = [
        # 2024
        (2024, 2, 24, 2, 26),   # EDSA People Power
        (2024, 3, 28, 4, 1),    # Holy Week (Maundy Thursday to Easter Monday)
        (2024, 4, 6, 4, 9),     # Araw ng Kagitingan
        (2024, 5, 1, 5, 1),     # Labor Day
        (2024, 8, 24, 8, 26),   # National Heroes Day
        (2024, 11, 1, 11, 3),   # All Saints' Day weekend
        (2024, 12, 24, 12, 25), # Christmas
        (2024, 12, 30, 2025, 1, 1), # Rizal Day to New Year
        
        # 2025
        (2025, 1, 29, 2, 1),    # Chinese New Year weekend
        (2025, 4, 17, 4, 20),   # Holy Week
        (2025, 5, 1, 5, 4),     # Labor Day weekend
        (2025, 6, 12, 6, 15),   # Independence Day weekend
        (2025, 8, 23, 8, 25),   # National Heroes Day
        (2025, 10, 31, 11, 2),  # Undas weekend
        (2025, 12, 24, 12, 26), # Christmas
        (2025, 12, 30, 2026, 1, 2), # New Year
    ]
    
    # Payday schedule (15th and 30th/last day of month)
    # These dates see higher booking activity
    PAYDAY_DATES = [15, 30]  # Will adjust for last day of month
    
    # Typhoon season impact (June - November)
    TYPHOON_SEASON = (6, 11)  # Start month, end month
    
    # School breaks (Philippine academic calendar)
    SCHOOL_BREAKS = [
        ((3, 15), (6, 1)),      # Summer break (approximate)
        ((10, 28), (11, 5)),    # Undas break
        ((12, 15), (1, 5)),     # Christmas break
    ]
    
    @classmethod
    def get_holiday_impact(cls, check_date: date) -> Dict:
        """
        Calculate holiday/fiesta impact on a specific date
        Returns impact score and details
        """
        impact = {
            'is_holiday': False,
            'holiday_name': None,
            'impact_level': 'none',
            'impact_score': 0.0,  # 0.0 to 2.0 multiplier
            'days_to_holiday': 365,
            'is_long_weekend': False,
            'is_fiesta': False,
            'fiesta_location': None,
            'is_payday': False,
            'is_typhoon_season': False,
            'is_school_break': False,
        }
        
        year = check_date.year
        month = check_date.month
        day = check_date.day
        
        # Check fixed holidays
        if (month, day) in cls.FIXED_HOLIDAYS:
            name, level, duration = cls.FIXED_HOLIDAYS[(month, day)]
            impact['is_holiday'] = True
            impact['holiday_name'] = name
            impact['impact_level'] = level
            impact['impact_score'] = cls._level_to_score(level)
        
        # Check Holy Week (movable)
        if year in cls.HOLY_WEEK_DATES:
            start_m, start_d, end_m, end_d = cls.HOLY_WEEK_DATES[year]
            holy_week_start = date(year, start_m, start_d)
            holy_week_end = date(year, end_m, end_d)
            
            if holy_week_start <= check_date <= holy_week_end:
                impact['is_holiday'] = True
                impact['holiday_name'] = "Holy Week"
                impact['impact_level'] = 'critical'
                impact['impact_score'] = 2.0
        
        # Check Chinese New Year
        if year in cls.CHINESE_NEW_YEAR:
            cny_month, cny_day = cls.CHINESE_NEW_YEAR[year]
            cny_date = date(year, cny_month, cny_day)
            if check_date == cny_date:
                impact['is_holiday'] = True
                impact['holiday_name'] = "Chinese New Year"
                impact['impact_level'] = 'high'
                impact['impact_score'] = 1.5
        
        # Check Eid'l Fitr
        if year in cls.EID_FITR:
            eid_month, eid_day = cls.EID_FITR[year]
            eid_date = date(year, eid_month, eid_day)
            if check_date == eid_date:
                impact['is_holiday'] = True
                impact['holiday_name'] = "Eid'l Fitr"
                impact['impact_level'] = 'medium'
                impact['impact_score'] = 1.3
        
        # Check fiestas
        for location, f_month, f_day, f_name, f_impact in cls.FIESTAS:
            if month == f_month and day == f_day:
                impact['is_fiesta'] = True
                impact['fiesta_location'] = location
                impact['fiesta_name'] = f_name
                # Increase impact if it's a major festival
                if f_impact == 'critical':
                    impact['impact_score'] = max(impact['impact_score'], 2.0)
                    impact['impact_level'] = 'critical'
                else:
                    impact['impact_score'] = max(impact['impact_score'], 1.4)
        
        # Check long weekends
        for lw in cls.LONG_WEEKENDS:
            if len(lw) == 6:  # Cross-year long weekend
                start_year, start_month, start_day, end_year, end_month, end_day = lw
                start = date(start_year, start_month, start_day)
                end = date(end_year, end_month, end_day)
            else:
                lw_year, start_month, start_day, end_month, end_day = lw
                start = date(lw_year, start_month, start_day)
                end = date(lw_year, end_month, end_day)
            
            if start <= check_date <= end:
                impact['is_long_weekend'] = True
                impact['impact_score'] = max(impact['impact_score'], 1.6)
        
        # Calculate days to nearest major holiday
        impact['days_to_holiday'] = cls._days_to_nearest_major_holiday(check_date)
        
        # Payday effect (15th and last day of month)
        last_day = calendar.monthrange(year, month)[1]
        if day in [15, 30] or day == last_day:
            impact['is_payday'] = True
            impact['impact_score'] += 0.1  # Small boost
        
        # Typhoon season (June-November)
        if cls.TYPHOON_SEASON[0] <= month <= cls.TYPHOON_SEASON[1]:
            impact['is_typhoon_season'] = True
            # Slight discount during typhoon season due to lower demand
            if impact['impact_score'] == 0:
                impact['impact_score'] = -0.1
        
        # School break periods
        for (start_m, start_d), (end_m, end_d) in cls.SCHOOL_BREAKS:
            start = date(year, start_m, start_d)
            end = date(year, end_m, end_d)
            if start <= check_date <= end:
                impact['is_school_break'] = True
                impact['impact_score'] = max(impact['impact_score'], 1.3)
                break
        
        return impact
    
    @classmethod
    def _level_to_score(cls, level: str) -> float:
        """Convert impact level to numeric score"""
        levels = {
            'none': 0.0,
            'low': 0.3,
            'medium': 0.8,
            'high': 1.5,
            'critical': 2.0,
        }
        return levels.get(level, 0.0)
    
    @classmethod
    def _days_to_nearest_major_holiday(cls, check_date: date) -> int:
        """Calculate days to nearest major holiday (Christmas, Holy Week, etc.)"""
        year = check_date.year
        
        major_dates = []
        
        # Add fixed major holidays
        for (m, d), (name, level, _) in cls.FIXED_HOLIDAYS.items():
            if level in ['high', 'critical']:
                try:
                    major_dates.append(date(year, m, d))
                    # Also check next year for year-end dates
                    if m == 12:
                        major_dates.append(date(year + 1, m, d))
                except ValueError:
                    continue
        
        # Add Holy Week
        if year in cls.HOLY_WEEK_DATES:
            start_m, start_d, _, _ = cls.HOLY_WEEK_DATES[year]
            major_dates.append(date(year, start_m, start_d))
        
        # Add Chinese New Year
        if year in cls.CHINESE_NEW_YEAR:
            cny_m, cny_d = cls.CHINESE_NEW_YEAR[year]
            major_dates.append(date(year, cny_m, cny_d))
        
        # Calculate minimum days
        days_list = [abs((holiday - check_date).days) for holiday in major_dates]
        return min(days_list) if days_list else 365
    
    @classmethod
    def get_route_fiesta_factor(cls, origin: str, dest: str, check_date: date) -> float:
        """
        Calculate fiesta-driven demand for specific routes
        e.g., Manila-Cebu spikes during Sinulog
        """
        impact = cls.get_holiday_impact(check_date)
        
        if not impact['is_fiesta']:
            return 1.0
        
        fiesta_location = impact['fiesta_location']
        
        # Map airports to cities/provinces
        airport_to_city = {
            'MNL': 'Manila', 'CEB': 'Cebu', 'DVO': 'Davao',
            'BCD': 'Bacolod', 'ILO': 'Iloilo', 'KLO': 'Kalibo',
            'TAG': 'Tagbilaran', 'CGY': 'Cagayan de Oro',
            'PPS': 'Puerto Princesa', 'CRK': 'Clark',
        }
        
        origin_city = airport_to_city.get(origin, origin)
        dest_city = airport_to_city.get(dest, dest)
        
        # If fiesta is at destination, demand increases (inbound)
        # If fiesta is at origin, demand increases (outbound after fiesta)
        if fiesta_location in [origin_city, dest_city]:
            return 1.5 if impact['impact_level'] == 'critical' else 1.3
        
        return 1.0
    
    @classmethod
    def get_seasonal_factor(cls, month: int) -> float:
        """
        Get seasonal demand factor
        December = highest, June-Sept (rainy) = lower
        """
        seasonal_multipliers = {
            1: 1.2,   # Post-holiday but Sinulog
            2: 1.1,   # Panagbenga
            3: 1.0,   # Summer start
            4: 1.1,   # Holy Week
            5: 1.2,   # Summer peak
            6: 0.9,   # Rainy season start
            7: 0.9,   # Rainy season
            8: 1.0,   # Kadayawan
            9: 0.9,   # Typhoon peak
            10: 1.0,  # MassKara
            11: 1.3,  # Undas
            12: 1.5,  # Christmas (highest)
        }
        return seasonal_multipliers.get(month, 1.0)


class PisoFareDetector:
    """
    Detects and predicts "Piso Fare" and seat sale events
    Common in Cebu Pacific and AirAsia Philippines
    """
    
    # Historical patterns of seat sales
    TYPICAL_SALE_MONTHS = [1, 3, 6, 9, 11]  # Common sale periods
    
    # Sale duration patterns
    SALE_DURATION_DAYS = 3  # Usually 3-day sales
    
    @classmethod
    def is_likely_sale_period(cls, check_date: date) -> Dict:
        """
        Predict if date falls within likely sale period
        Based on historical patterns of Philippine LCCs
        """
        month = check_date.month
        
        likelihood = 'low'
        if month in cls.TYPICAL_SALE_MONTHS:
            likelihood = 'medium'
            # Usually first week or mid-month
            if check_date.day <= 7 or (15 <= check_date.day <= 18):
                likelihood = 'high'
        
        # Check if it's payday (common sale start dates)
        last_day = calendar.monthrange(check_date.year, check_date.month)[1]
        if check_date.day in [15, 30, last_day]:
            likelihood = 'high'
        
        return {
            'is_sale_period': likelihood in ['medium', 'high'],
            'likelihood': likelihood,
            'expected_discount': 0.50 if likelihood == 'high' else 0.30,  # 50% or 30% off
        }
    
    @classmethod
    def calculate_sale_impact(cls, booking_date: date, departure_date: date) -> float:
        """
        Calculate if booking was made during a sale
        Affects historical price analysis
        """
        sale_info = cls.is_likely_sale_period(booking_date)
        
        if not sale_info['is_sale_period']:
            return 1.0
        
        # If departure is far out (60+ days), more likely to be sale price
        days_to_departure = (departure_date - booking_date).days
        
        if days_to_departure >= 60 and sale_info['likelihood'] == 'high':
            return 1.0 - sale_info['expected_discount']
        
        return 1.0