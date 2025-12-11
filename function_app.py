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


@app.route(route="running-data", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
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


@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Simple health check endpoint."""
    return func.HttpResponse(
        json.dumps({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}),
        status_code=200,
        mimetype='application/json'
    )
