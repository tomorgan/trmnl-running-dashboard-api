"""
Utility functions for data processing and calculations.
"""
import json
import os
from datetime import datetime, timedelta


def get_week_start():
    """
    Get Monday of the current week at 00:00:00.
    
    Returns:
        datetime: Start of the week (Monday)
    """
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def get_week_end():
    """
    Get Sunday of the current week at 23:59:59.
    
    Returns:
        datetime: End of the week (Sunday)
    """
    week_start = get_week_start()
    sunday = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return sunday


def generate_week_label():
    """
    Generate a human-readable week label.
    
    Returns:
        str: Week label (e.g., "Week of Dec 2-8, 2025")
    """
    week_start = get_week_start()
    week_end = week_start + timedelta(days=6)
    
    # Format: "Week of Dec 2-8, 2025"
    start_str = week_start.strftime("%b %-d" if os.name != 'nt' else "%b %#d")
    end_str = week_end.strftime("%-d, %Y" if os.name != 'nt' else "%#d, %Y")
    
    return f"Week of {start_str}-{end_str}"


def calculate_weeks_until_event(event_date_str):
    """
    Calculate number of weeks from today until the event.
    
    Args:
        event_date_str (str): ISO format date string (YYYY-MM-DD)
    
    Returns:
        int: Number of complete weeks until event (minimum 0)
    """
    try:
        event_date = datetime.fromisoformat(event_date_str)
        today = datetime.now()
        days_diff = (event_date - today).days
        return max(0, days_diff // 7)
    except (ValueError, AttributeError):
        return 0


def get_weekly_target(weeks_until_event, training_schedule_json=None):
    """
    Get the weekly mileage target based on weeks until event.
    
    Args:
        weeks_until_event (int): Weeks remaining until event
        training_schedule_json (str): JSON string of training schedule
    
    Returns:
        float: Weekly target miles
    """
    if not training_schedule_json:
        return 25.0  # Default target
    
    try:
        schedule = json.loads(training_schedule_json)
        
        # Sort by weeks_until descending to find the right bracket
        sorted_schedule = sorted(schedule, key=lambda x: x['weeks_until'], reverse=True)
        
        # Find the first entry where weeks_until_event >= entry's weeks_until
        for entry in sorted_schedule:
            if weeks_until_event >= entry['weeks_until']:
                return float(entry['target_miles'])
        
        # If we're before the first entry, use it anyway
        if sorted_schedule:
            return float(sorted_schedule[0]['target_miles'])
        
        return 25.0  # Fallback default
        
    except (json.JSONDecodeError, KeyError, ValueError):
        return 25.0  # Fallback on error


def calculate_pace(distance_meters, duration_seconds, metric=False):
    """
    Calculate running pace in min/mile or min/km format.
    
    Args:
        distance_meters (float): Distance in meters
        duration_seconds (int): Duration in seconds
        metric (bool): If True, return pace per km; if False, return pace per mile
    
    Returns:
        str: Pace in "M:SS" format (e.g., "8:39" or "5:23")
    """
    if distance_meters == 0 or duration_seconds == 0:
        return "0:00"
    
    if metric:
        # Calculate minutes per kilometer
        distance_km = distance_meters / 1000
        minutes_per_unit = duration_seconds / 60 / distance_km
    else:
        # Calculate minutes per mile
        distance_miles = distance_meters * 0.000621371
        minutes_per_unit = duration_seconds / 60 / distance_miles
    
    mins = int(minutes_per_unit)
    secs = int((minutes_per_unit - mins) * 60)
    
    return f"{mins}:{secs:02d}"


def format_date_for_display(iso_date_str):
    """
    Format ISO date string for display.
    
    Args:
        iso_date_str (str): ISO format date string
    
    Returns:
        str: Formatted date (e.g., "Mon, Dec 2")
    """
    try:
        date_obj = datetime.fromisoformat(iso_date_str.replace('Z', '+00:00'))
        # Format: "Mon, Dec 2"
        return date_obj.strftime("%a, %b %-d" if os.name != 'nt' else "%a, %b %#d")
    except (ValueError, AttributeError):
        return iso_date_str


def meters_to_miles(meters):
    """
    Convert meters to miles.
    
    Args:
        meters (float): Distance in meters
    
    Returns:
        float: Distance in miles (rounded to 1 decimal)
    """
    miles = meters * 0.000621371
    return round(miles, 1)


def seconds_to_minutes(seconds):
    """
    Convert seconds to minutes.
    
    Args:
        seconds (int): Duration in seconds
    
    Returns:
        int: Duration in minutes (rounded)
    """
    return round(seconds / 60)


def calculate_progress_percentage(weekly_miles, target_miles):
    """
    Calculate progress percentage, capped at 100%.
    
    Args:
        weekly_miles (float): Miles run this week
        target_miles (float): Target miles for the week
    
    Returns:
        int: Progress percentage (0-100)
    """
    if target_miles == 0:
        return 0
    
    percentage = (weekly_miles / target_miles) * 100
    return min(100, round(percentage))


def get_weekly_plan(weekly_plan_json=None):
    """
    Parse and return the weekly training plan.
    
    Args:
        weekly_plan_json (str): JSON string of weekly plan
    
    Returns:
        list: List of daily workout dictionaries
    """
    if not weekly_plan_json:
        return []
    
    try:
        plan = json.loads(weekly_plan_json)
        return plan
    except (json.JSONDecodeError, ValueError):
        return []

