"""
Azure Function: TRMNL Running Dashboard API
Fetches running data from Strava and returns formatted JSON for TRMNL display.
"""
import azure.functions as func
import logging
import json
import os
from datetime import datetime

from strava_client import StravaClient
from weather_client import WeatherClient
from quotes import get_daily_quote
from utils import (
    get_week_start,
    generate_week_label,
    calculate_weeks_until_event,
    get_weekly_target,
    calculate_pace,
    format_date_for_display,
    meters_to_miles,
    seconds_to_minutes,
    calculate_progress_percentage,
    get_weekly_plan
)

app = func.FunctionApp()

logger = logging.getLogger(__name__)


@app.route(route="running-data", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def get_running_data(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function that returns running dashboard data.
    
    Returns:
        JSON response with weekly running stats, event info, and quote
    """
    logger.info('Running data request received')
    
    try:
        # Get environment configuration
        event_name = os.getenv('NEXT_EVENT_NAME', 'Next Running Event')
        event_date = os.getenv('NEXT_EVENT_DATE')
        training_schedule = os.getenv('TRAINING_SCHEDULE')
        weekly_plan_json = os.getenv('WEEKLY_PLAN')
        
        if not event_date:
            logger.error('NEXT_EVENT_DATE environment variable not set')
            return func.HttpResponse(
                json.dumps({'error': 'Event date not configured'}),
                status_code=500,
                mimetype='application/json'
            )
        
        # Calculate time-based values
        week_start = get_week_start()
        week_label = generate_week_label()
        weeks_until_event = calculate_weeks_until_event(event_date)
        target_miles = get_weekly_target(weeks_until_event, training_schedule)
        weekly_plan = get_weekly_plan(weekly_plan_json)
        
        logger.info(f'Week: {week_label}, Weeks until event: {weeks_until_event}, Target: {target_miles} miles')
        
        # Fetch runs from Strava
        try:
            strava = StravaClient()
            runs = strava.get_weekly_runs(week_start)
            logger.info(f'Fetched {len(runs)} runs from Strava')
        except Exception as e:
            logger.error(f'Strava API error: {e}')
            # Return response with no runs if Strava fails
            runs = []
        
        # Fetch weather forecast
        weather_by_date = {}
        try:
            weather = WeatherClient()
            weather_by_date = weather.get_daily_forecast(days=7)
            logger.info(f'Fetched weather forecast for {len(weather_by_date)} days')
        except Exception as e:
            logger.error(f'Weather API error: {e}')
            # Continue without weather data if API fails
            weather_by_date = {}
        
        # Process runs data
        weekly_miles = 0.0
        runs_by_date = {}
        
        for run in runs:
            distance_miles = meters_to_miles(run['distance'])
            duration_minutes = seconds_to_minutes(run['moving_time'])
            pace = calculate_pace(run['distance'], run['moving_time'])
            run_date = run['start_date'].split('T')[0]  # Extract date part
            
            weekly_miles += distance_miles
            
            # Store run by date for merging with plan
            runs_by_date[run_date] = {
                'distance_miles': distance_miles,
                'duration_minutes': duration_minutes,
                'pace_per_mile': pace
            }
        
        # Round weekly miles to 1 decimal
        weekly_miles = round(weekly_miles, 1)
        
        # Calculate progress
        progress_percentage = calculate_progress_percentage(weekly_miles, target_miles)
        
        # Get daily quote
        quote = get_daily_quote()
        
        # Process weekly plan - merge with actual runs
        from datetime import datetime, timedelta
        processed_plan = []
        day_abbreviations = {
            'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed',
            'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'
        }
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Get start of week (Monday)
        week_start_date = get_week_start()
        
        for day_plan in weekly_plan:
            day_name = day_plan['day']
            day_index = day_names.index(day_name) if day_name in day_names else 0
            day_date = (week_start_date + timedelta(days=day_index)).strftime('%Y-%m-%d')
            
            # Check if there's a run on this day
            run_data = runs_by_date.get(day_date)
            
            day_entry = {
                'day': day_name,
                'day_short': day_abbreviations.get(day_name, day_name[:3]),
                'workout': day_plan['workout'],
                'completed': run_data is not None
            }
            
            # Add run data if available
            if run_data:
                day_entry['distance_miles'] = run_data['distance_miles']
                day_entry['duration_minutes'] = run_data['duration_minutes']
                day_entry['pace_per_mile'] = run_data['pace_per_mile']
            
            # Add weather data if available
            weather_data = weather_by_date.get(day_date)
            if weather_data:
                day_entry['weather'] = {
                    'temp_morning': round(weather_data['temp_morning'], 1) if weather_data['temp_morning'] is not None else None,
                    'feels_like_morning': round(weather_data['feels_like_morning'], 1) if weather_data['feels_like_morning'] is not None else None,
                    'precipitation_prob': round(weather_data['precipitation_prob']),
                    'description': weather_data['description']
                }
            
            processed_plan.append(day_entry)
        
        # Build response
        response_data = {
            'weekly_miles': weekly_miles,
            'target_miles': target_miles,
            'weeks_until_event': weeks_until_event,
            'event_name': event_name,
            'quote': quote,
            'weekly_plan': processed_plan,
            'has_weekly_plan': len(processed_plan) > 0,
            'progress_percentage': progress_percentage
        }
        
        completed_count = sum(1 for day in processed_plan if day.get('completed', False))
        logger.info(f'Returning data: {weekly_miles}/{target_miles} miles, {completed_count} runs completed')
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',  # Allow TRMNL access
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except Exception as e:
        logger.error(f'Unexpected error: {e}', exc_info=True)
        return func.HttpResponse(
            json.dumps({'error': 'Internal server error', 'details': str(e)}),
            status_code=500,
            mimetype='application/json'
        )


@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Simple health check endpoint."""
    return func.HttpResponse(
        json.dumps({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}),
        status_code=200,
        mimetype='application/json'
    )


@app.route(route="nutrition-data", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def get_nutrition_data(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function that returns comprehensive activity data for nutrition planning.
    
    Query Parameters:
        days (optional): Number of days to look back (default: 30, max: 90)
    
    Returns:
        JSON response with detailed activity history and fitness metrics
    """
    logger.info('Nutrition data request received')
    
    try:
        # Get days parameter from query string
        days_param = req.params.get('days', '30')
        try:
            days = min(int(days_param), 90)  # Cap at 90 days
            days = max(days, 1)  # Minimum 1 day
        except ValueError:
            days = 30
        
        logger.info(f'Fetching data for past {days} days')
        
        # Fetch detailed activities from Strava
        try:
            strava = StravaClient()
            activities = strava.get_monthly_activities_detailed(days=days)
            logger.info(f'Fetched {len(activities)} activities from Strava')
        except Exception as e:
            logger.error(f'Strava API error: {e}')
            return func.HttpResponse(
                json.dumps({'error': 'Failed to fetch Strava data', 'details': str(e)}),
                status_code=500,
                mimetype='application/json'
            )
        
        # Calculate summary statistics
        total_activities = len(activities)
        total_distance_meters = sum(a['distance'] for a in activities)
        total_distance_km = round(total_distance_meters / 1000, 2)
        total_distance_miles = round(meters_to_miles(total_distance_meters), 2)
        total_moving_time_seconds = sum(a['moving_time'] for a in activities)
        total_moving_time_hours = round(total_moving_time_seconds / 3600, 2)
        total_elevation_meters = sum(a['total_elevation_gain'] for a in activities)
        total_elevation_feet = round(total_elevation_meters * 3.28084, 0)
        total_calories = sum(a['calories'] or 0 for a in activities)
        
        # Calculate activity type breakdown
        activity_types = {}
        for activity in activities:
            activity_type = activity['type'] or 'Unknown'
            if activity_type not in activity_types:
                activity_types[activity_type] = {
                    'count': 0,
                    'total_distance_km': 0,
                    'total_moving_time_hours': 0,
                    'total_calories': 0,
                    'total_elevation_meters': 0
                }
            activity_types[activity_type]['count'] += 1
            activity_types[activity_type]['total_distance_km'] += activity['distance'] / 1000
            activity_types[activity_type]['total_moving_time_hours'] += activity['moving_time'] / 3600
            activity_types[activity_type]['total_calories'] += activity['calories'] or 0
            activity_types[activity_type]['total_elevation_meters'] += activity['total_elevation_gain']
        
        # Round activity type statistics
        for activity_type in activity_types:
            activity_types[activity_type]['total_distance_km'] = round(activity_types[activity_type]['total_distance_km'], 2)
            activity_types[activity_type]['total_distance_miles'] = round(activity_types[activity_type]['total_distance_km'] * 0.621371, 2)
            activity_types[activity_type]['total_moving_time_hours'] = round(activity_types[activity_type]['total_moving_time_hours'], 2)
            activity_types[activity_type]['total_elevation_feet'] = round(activity_types[activity_type]['total_elevation_meters'] * 3.28084, 0)
        
        # Calculate average metrics for activities with data
        activities_with_hr = [a for a in activities if a['average_heartrate']]
        avg_heartrate = round(sum(a['average_heartrate'] for a in activities_with_hr) / len(activities_with_hr), 1) if activities_with_hr else None
        
        activities_with_calories = [a for a in activities if a['calories']]
        avg_calories_per_activity = round(sum(a['calories'] for a in activities_with_calories) / len(activities_with_calories), 0) if activities_with_calories else None
        
        activities_with_suffer = [a for a in activities if a['suffer_score']]
        total_suffer_score = sum(a['suffer_score'] for a in activities_with_suffer)
        avg_suffer_score = round(total_suffer_score / len(activities_with_suffer), 1) if activities_with_suffer else None
        
        # Calculate weekly averages
        weeks_in_period = days / 7
        weekly_activity_count = round(total_activities / weeks_in_period, 1)
        weekly_distance_km = round(total_distance_km / weeks_in_period, 2)
        weekly_distance_miles = round(total_distance_miles / weeks_in_period, 2)
        weekly_moving_time_hours = round(total_moving_time_hours / weeks_in_period, 2)
        weekly_calories = round(total_calories / weeks_in_period, 0) if total_calories > 0 else None
        
        # Calculate daily averages
        daily_activity_count = round(total_activities / days, 2)
        daily_distance_km = round(total_distance_km / days, 2)
        daily_distance_miles = round(total_distance_miles / days, 2)
        daily_calories = round(total_calories / days, 0) if total_calories > 0 else None
        
        # Prepare detailed activities list with formatted data
        activities_formatted = []
        for activity in activities:
            formatted = {
                'id': activity['id'],
                'name': activity['name'],
                'type': activity['type'],
                'sport_type': activity['sport_type'],
                'date': activity['start_date_local'][:10] if activity['start_date_local'] else activity['start_date'][:10],
                'datetime': activity['start_date_local'] or activity['start_date'],
                'distance_km': round(activity['distance'] / 1000, 2),
                'distance_miles': round(meters_to_miles(activity['distance']), 2),
                'duration_minutes': round(activity['moving_time'] / 60, 1),
                'duration_hours': round(activity['moving_time'] / 3600, 2),
                'elevation_gain_meters': round(activity['total_elevation_gain'], 0),
                'elevation_gain_feet': round(activity['total_elevation_gain'] * 3.28084, 0),
                'average_speed_kmh': round(activity['average_speed'] * 3.6, 2) if activity['average_speed'] else None,
                'average_speed_mph': round(activity['average_speed'] * 2.23694, 2) if activity['average_speed'] else None,
                'average_pace_min_per_km': calculate_pace(activity['distance'], activity['moving_time'], metric=True) if activity['distance'] > 0 else None,
                'average_pace_min_per_mile': calculate_pace(activity['distance'], activity['moving_time']) if activity['distance'] > 0 else None,
                'average_cadence': activity['average_cadence'],
                'average_heartrate': activity['average_heartrate'],
                'max_heartrate': activity['max_heartrate'],
                'calories': activity['calories'],
                'suffer_score': activity['suffer_score'],
                'has_heartrate': activity['has_heartrate'],
                'average_temp_celsius': activity['average_temp'],
                'average_temp_fahrenheit': round((activity['average_temp'] * 9/5) + 32, 1) if activity['average_temp'] else None,
                'workout_type': activity['workout_type'],
                'trainer': activity['trainer'],
                'commute': activity['commute'],
                'achievements': activity['achievement_count'],
                'kudos': activity['kudos_count'],
                'personal_records': activity['pr_count'],
            }
            activities_formatted.append(formatted)
        
        # Build comprehensive response
        response_data = {
            'period': {
                'days': days,
                'start_date': (datetime.now() - __import__('datetime').timedelta(days=days)).strftime('%Y-%m-%d'),
                'end_date': datetime.now().strftime('%Y-%m-%d'),
            },
            'summary': {
                'total_activities': total_activities,
                'total_distance_km': total_distance_km,
                'total_distance_miles': total_distance_miles,
                'total_moving_time_hours': total_moving_time_hours,
                'total_elevation_meters': round(total_elevation_meters, 0),
                'total_elevation_feet': total_elevation_feet,
                'total_calories': total_calories if total_calories > 0 else None,
                'total_suffer_score': total_suffer_score if activities_with_suffer else None,
                'average_heartrate': avg_heartrate,
                'average_calories_per_activity': avg_calories_per_activity,
                'average_suffer_score': avg_suffer_score,
            },
            'weekly_averages': {
                'activities_per_week': weekly_activity_count,
                'distance_km_per_week': weekly_distance_km,
                'distance_miles_per_week': weekly_distance_miles,
                'moving_time_hours_per_week': weekly_moving_time_hours,
                'calories_per_week': weekly_calories,
            },
            'daily_averages': {
                'activities_per_day': daily_activity_count,
                'distance_km_per_day': daily_distance_km,
                'distance_miles_per_day': daily_distance_miles,
                'calories_per_day': daily_calories,
            },
            'activity_types': activity_types,
            'activities': activities_formatted,
        }
        
        logger.info(f'Returning nutrition data: {total_activities} activities, {total_distance_km}km, {total_calories} calories')
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            mimetype='application/json',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except Exception as e:
        logger.error(f'Unexpected error: {e}', exc_info=True)
        return func.HttpResponse(
            json.dumps({'error': 'Internal server error', 'details': str(e)}),
            status_code=500,
            mimetype='application/json'
        )
