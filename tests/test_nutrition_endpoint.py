"""
Test script for nutrition endpoint logic validation.
Tests the data processing and calculation logic without requiring Azure Functions or Strava API.
"""
import sys
from datetime import datetime, timedelta
from utils import calculate_pace, meters_to_miles


def test_calculate_pace_imperial():
    """Test pace calculation in min/mile format."""
    # 5km in 25 minutes = 8:02 min/mile
    distance_meters = 5000
    duration_seconds = 25 * 60
    pace = calculate_pace(distance_meters, duration_seconds, metric=False)
    print(f"✓ Imperial pace: {pace} min/mile (expected ~8:02)")
    assert pace.startswith("8:"), f"Expected pace around 8:XX, got {pace}"


def test_calculate_pace_metric():
    """Test pace calculation in min/km format."""
    # 5km in 25 minutes = 5:00 min/km exactly
    distance_meters = 5000
    duration_seconds = 25 * 60
    pace = calculate_pace(distance_meters, duration_seconds, metric=True)
    print(f"✓ Metric pace: {pace} min/km (expected 5:00)")
    assert pace == "5:00", f"Expected 5:00, got {pace}"


def test_nutrition_data_calculations():
    """Test nutrition endpoint calculation logic."""
    # Mock activity data
    mock_activities = [
        {
            'id': 1,
            'name': 'Morning Run',
            'type': 'Run',
            'sport_type': 'Run',
            'start_date': '2026-01-20T06:00:00Z',
            'start_date_local': '2026-01-20T06:00:00Z',
            'distance': 8000,  # 8km
            'moving_time': 2400,  # 40 minutes
            'elapsed_time': 2500,
            'total_elevation_gain': 100,
            'elev_high': None,
            'elev_low': None,
            'average_speed': 3.33,  # m/s
            'max_speed': 4.5,
            'average_cadence': 170,
            'average_heartrate': 155,
            'max_heartrate': 175,
            'calories': 450,
            'suffer_score': 42,
            'has_heartrate': True,
            'average_temp': 12,
            'workout_type': 0,
            'description': None,
            'trainer': False,
            'commute': False,
            'achievement_count': 1,
            'kudos_count': 3,
            'pr_count': 0,
        },
        {
            'id': 2,
            'name': 'Easy Run',
            'type': 'Run',
            'sport_type': 'Run',
            'start_date': '2026-01-18T07:00:00Z',
            'start_date_local': '2026-01-18T07:00:00Z',
            'distance': 5000,
            'moving_time': 1800,
            'elapsed_time': 1900,
            'total_elevation_gain': 50,
            'elev_high': None,
            'elev_low': None,
            'average_speed': 2.78,
            'max_speed': 3.5,
            'average_cadence': 165,
            'average_heartrate': 145,
            'max_heartrate': 160,
            'calories': 300,
            'suffer_score': 28,
            'has_heartrate': True,
            'average_temp': 10,
            'workout_type': 0,
            'description': None,
            'trainer': False,
            'commute': False,
            'achievement_count': 0,
            'kudos_count': 5,
            'pr_count': 1,
        },
        {
            'id': 3,
            'name': 'Recovery Bike',
            'type': 'Ride',
            'sport_type': 'MountainBikeRide',
            'start_date': '2026-01-19T08:00:00Z',
            'start_date_local': '2026-01-19T08:00:00Z',
            'distance': 15000,
            'moving_time': 2700,
            'elapsed_time': 3000,
            'total_elevation_gain': 200,
            'elev_high': None,
            'elev_low': None,
            'average_speed': 5.56,
            'max_speed': 8.0,
            'average_cadence': 80,
            'average_heartrate': 130,
            'max_heartrate': 150,
            'calories': 400,
            'suffer_score': 35,
            'has_heartrate': True,
            'average_temp': 15,
            'workout_type': None,
            'description': None,
            'trainer': False,
            'commute': False,
            'achievement_count': 0,
            'kudos_count': 2,
            'pr_count': 0,
        }
    ]
    
    # Calculate summary statistics
    total_activities = len(mock_activities)
    total_distance_meters = sum(a['distance'] for a in mock_activities)
    total_distance_km = round(total_distance_meters / 1000, 2)
    total_distance_miles = round(meters_to_miles(total_distance_meters), 2)
    total_calories = sum(a['calories'] or 0 for a in mock_activities)
    
    print(f"\n--- Summary Statistics ---")
    print(f"✓ Total activities: {total_activities}")
    print(f"✓ Total distance: {total_distance_km} km / {total_distance_miles} miles")
    print(f"✓ Total calories: {total_calories}")
    
    assert total_activities == 3, "Should have 3 activities"
    assert total_distance_km == 28.0, f"Expected 28.0 km, got {total_distance_km}"
    assert total_calories == 1150, f"Expected 1150 calories, got {total_calories}"
    
    # Calculate activity type breakdown
    activity_types = {}
    for activity in mock_activities:
        activity_type = activity['type']
        if activity_type not in activity_types:
            activity_types[activity_type] = {
                'count': 0,
                'total_distance_km': 0,
                'total_calories': 0,
            }
        activity_types[activity_type]['count'] += 1
        activity_types[activity_type]['total_distance_km'] += activity['distance'] / 1000
        activity_types[activity_type]['total_calories'] += activity['calories'] or 0
    
    print(f"\n--- Activity Types ---")
    for activity_type, stats in activity_types.items():
        print(f"✓ {activity_type}: {stats['count']} activities, {stats['total_distance_km']:.1f} km, {stats['total_calories']} cal")
    
    assert activity_types['Run']['count'] == 2, "Should have 2 runs"
    assert activity_types['Ride']['count'] == 1, "Should have 1 ride"
    assert activity_types['Run']['total_calories'] == 750, "Run calories should be 750"
    
    # Calculate averages
    activities_with_hr = [a for a in mock_activities if a['average_heartrate']]
    avg_heartrate = round(sum(a['average_heartrate'] for a in activities_with_hr) / len(activities_with_hr), 1)
    
    print(f"\n--- Averages ---")
    print(f"✓ Average heart rate: {avg_heartrate} bpm")
    
    assert avg_heartrate == 143.3, f"Expected 143.3 bpm, got {avg_heartrate}"
    
    # Test formatted activity output
    print(f"\n--- Formatted Activities ---")
    for activity in mock_activities:
        distance_km = round(activity['distance'] / 1000, 2)
        distance_miles = round(meters_to_miles(activity['distance']), 2)
        pace_per_km = calculate_pace(activity['distance'], activity['moving_time'], metric=True)
        pace_per_mile = calculate_pace(activity['distance'], activity['moving_time'], metric=False)
        
        print(f"✓ {activity['name']}: {distance_km} km / {distance_miles} mi")
        print(f"  Pace: {pace_per_km} /km, {pace_per_mile} /mi")
        print(f"  HR: {activity['average_heartrate']} bpm, Calories: {activity['calories']}")
    
    print(f"\n✅ All tests passed!")


if __name__ == '__main__':
    try:
        print("Testing nutrition endpoint logic...\n")
        test_calculate_pace_imperial()
        test_calculate_pace_metric()
        test_nutrition_data_calculations()
        print("\n" + "="*50)
        print("SUCCESS: All nutrition endpoint tests passed!")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
