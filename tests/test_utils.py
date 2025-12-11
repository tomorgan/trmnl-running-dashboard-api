"""
Unit tests for utility functions.
"""
import pytest
from datetime import datetime, timedelta
from utils import (
    get_week_start,
    generate_week_label,
    calculate_weeks_until_event,
    get_weekly_target,
    calculate_pace,
    meters_to_miles,
    seconds_to_minutes,
    calculate_progress_percentage
)


def test_get_week_start():
    """Test week start calculation returns Monday."""
    week_start = get_week_start()
    assert week_start.weekday() == 0  # Monday is 0
    assert week_start.hour == 0
    assert week_start.minute == 0


def test_generate_week_label():
    """Test week label generation."""
    label = generate_week_label()
    assert "Week of" in label
    assert "," in label


def test_calculate_weeks_until_event():
    """Test weeks until event calculation."""
    # Future event
    future_date = (datetime.now() + timedelta(days=56)).strftime("%Y-%m-%d")
    weeks = calculate_weeks_until_event(future_date)
    assert weeks == 8
    
    # Past event
    past_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    weeks = calculate_weeks_until_event(past_date)
    assert weeks == 0
    
    # Invalid date
    weeks = calculate_weeks_until_event("invalid")
    assert weeks == 0


def test_get_weekly_target():
    """Test weekly target lookup from training schedule."""
    schedule = '[{"weeks_until": 12, "target_miles": 20}, {"weeks_until": 8, "target_miles": 25}, {"weeks_until": 4, "target_miles": 30}]'
    
    # Exact match
    assert get_weekly_target(8, schedule) == 25.0
    
    # Between brackets (should use lower bound)
    assert get_weekly_target(10, schedule) == 20.0
    
    # Below all entries
    assert get_weekly_target(15, schedule) == 20.0
    
    # Above all entries
    assert get_weekly_target(2, schedule) == 30.0
    
    # No schedule provided
    assert get_weekly_target(8) == 25.0
    
    # Invalid JSON
    assert get_weekly_target(8, "invalid json") == 25.0


def test_calculate_pace():
    """Test pace calculation."""
    # 8:39 pace (8367m in 45 minutes)
    pace = calculate_pace(8367.2, 2700)
    assert pace.startswith("8:")
    
    # Zero distance
    assert calculate_pace(0, 2700) == "0:00"
    
    # Zero time
    assert calculate_pace(8367.2, 0) == "0:00"


def test_meters_to_miles():
    """Test meters to miles conversion."""
    assert meters_to_miles(8047) == 5.0  # ~5 miles
    assert meters_to_miles(1609) == 1.0  # ~1 mile
    assert meters_to_miles(0) == 0.0


def test_seconds_to_minutes():
    """Test seconds to minutes conversion."""
    assert seconds_to_minutes(3600) == 60
    assert seconds_to_minutes(2700) == 45
    assert seconds_to_minutes(90) == 2  # Rounds 1.5 to 2


def test_calculate_progress_percentage():
    """Test progress percentage calculation."""
    assert calculate_progress_percentage(15.5, 25.0) == 62
    assert calculate_progress_percentage(25.0, 25.0) == 100
    assert calculate_progress_percentage(30.0, 25.0) == 100  # Caps at 100
    assert calculate_progress_percentage(0, 25.0) == 0
    assert calculate_progress_percentage(10, 0) == 0  # Avoid division by zero
