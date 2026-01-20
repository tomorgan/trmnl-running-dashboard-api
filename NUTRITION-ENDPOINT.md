# Nutrition Data API Endpoint

## Overview

The `/api/nutrition-data` endpoint provides comprehensive activity history and fitness metrics from Strava, designed for nutritional recommendation systems. This endpoint returns detailed information about your recent activities including distance, duration, elevation, heart rate, calories burned, and workload indicators.

## Endpoint

```
GET /api/nutrition-data?code=<your-function-key>&days=<number-of-days>
```

### Query Parameters

| Parameter | Type | Required | Default | Max | Description |
|-----------|------|----------|---------|-----|-------------|
| `days` | integer | No | 30 | 90 | Number of days to look back for activity history |

### Authentication

This endpoint uses Azure Function key authentication. Include your function key in the `code` query parameter.

## Response Format

The endpoint returns a comprehensive JSON response with the following structure:

```json
{
  "period": {
    "days": 30,
    "start_date": "2025-12-21",
    "end_date": "2026-01-20"
  },
  "summary": {
    "total_activities": 24,
    "total_distance_km": 142.5,
    "total_distance_miles": 88.5,
    "total_moving_time_hours": 12.5,
    "total_elevation_meters": 2450,
    "total_elevation_feet": 8038,
    "total_calories": 9600,
    "total_suffer_score": 850,
    "average_heartrate": 152.3,
    "average_calories_per_activity": 400,
    "average_suffer_score": 35.4
  },
  "weekly_averages": {
    "activities_per_week": 5.6,
    "distance_km_per_week": 33.2,
    "distance_miles_per_week": 20.6,
    "moving_time_hours_per_week": 2.9,
    "calories_per_week": 2240
  },
  "daily_averages": {
    "activities_per_day": 0.8,
    "distance_km_per_day": 4.75,
    "distance_miles_per_day": 2.95,
    "calories_per_day": 320
  },
  "activity_types": {
    "Run": {
      "count": 20,
      "total_distance_km": 130.2,
      "total_distance_miles": 80.9,
      "total_moving_time_hours": 11.2,
      "total_calories": 8800,
      "total_elevation_meters": 2200,
      "total_elevation_feet": 7218
    },
    "Ride": {
      "count": 3,
      "total_distance_km": 10.8,
      "total_distance_miles": 6.7,
      "total_moving_time_hours": 1.1,
      "total_calories": 650,
      "total_elevation_meters": 180,
      "total_elevation_feet": 591
    },
    "Swim": {
      "count": 1,
      "total_distance_km": 1.5,
      "total_distance_miles": 0.9,
      "total_moving_time_hours": 0.5,
      "total_calories": 150,
      "total_elevation_meters": 0,
      "total_elevation_feet": 0
    }
  },
  "activities": [
    {
      "id": 123456789,
      "name": "Morning Run",
      "type": "Run",
      "sport_type": "Run",
      "date": "2026-01-20",
      "datetime": "2026-01-20T06:30:00Z",
      "distance_km": 8.5,
      "distance_miles": 5.28,
      "duration_minutes": 45.2,
      "duration_hours": 0.75,
      "elevation_gain_meters": 120,
      "elevation_gain_feet": 394,
      "average_speed_kmh": 11.3,
      "average_speed_mph": 7.02,
      "average_pace_min_per_km": "5:18",
      "average_pace_min_per_mile": "8:32",
      "average_cadence": 168,
      "average_heartrate": 155,
      "max_heartrate": 178,
      "calories": 450,
      "suffer_score": 42,
      "has_heartrate": true,
      "average_temp_celsius": 12,
      "average_temp_fahrenheit": 53.6,
      "workout_type": 0,
      "trainer": false,
      "commute": false,
      "achievements": 2,
      "kudos": 5,
      "personal_records": 1
    }
  ]
}
```

## Data Fields Explained

### Period
- **days**: Number of days included in the response
- **start_date**: Beginning of the time period
- **end_date**: End of the time period (today)

### Summary Statistics
- **total_activities**: Total number of activities in period
- **total_distance_km/miles**: Combined distance across all activities
- **total_moving_time_hours**: Active time excluding stops
- **total_elevation_meters/feet**: Total vertical gain
- **total_calories**: Total estimated calories burned (if available from Strava)
- **total_suffer_score**: Cumulative Strava Suffer Score (relative effort metric)
- **average_heartrate**: Mean heart rate across all activities with HR data
- **average_calories_per_activity**: Mean calories per activity
- **average_suffer_score**: Mean Suffer Score per activity

### Weekly/Daily Averages
Normalized metrics to help understand typical training volume:
- Activities per period
- Distance per period (km and miles)
- Moving time per period
- Calories per period

### Activity Types Breakdown
Aggregated statistics grouped by activity type (Run, Ride, Swim, Walk, etc.):
- Count of activities
- Total distance (km and miles)
- Total moving time (hours)
- Total calories
- Total elevation (meters and feet)

### Individual Activities
Detailed array of each activity with:

**Basic Info:**
- `id`: Strava activity ID
- `name`: Activity name/title
- `type`: Activity type (Run, Ride, Swim, etc.)
- `sport_type`: More specific sport type
- `date`: Date of activity (YYYY-MM-DD)
- `datetime`: Full timestamp with timezone

**Distance & Duration:**
- `distance_km/miles`: Distance in both units
- `duration_minutes/hours`: Moving time (excludes stops)

**Elevation:**
- `elevation_gain_meters/feet`: Total vertical gain

**Speed & Pace:**
- `average_speed_kmh/mph`: Average speed in both units
- `average_pace_min_per_km`: Pace in min/km format (e.g., "5:18")
- `average_pace_min_per_mile`: Pace in min/mile format (e.g., "8:32")

**Performance Metrics:**
- `average_cadence`: Steps per minute (running) or RPM (cycling)
- `average_heartrate`: Mean heart rate during activity
- `max_heartrate`: Peak heart rate
- `calories`: Estimated energy expenditure
- `suffer_score`: Strava's relative effort metric (0-100+ scale)
- `has_heartrate`: Boolean indicating if HR data is available

**Environmental:**
- `average_temp_celsius/fahrenheit`: Temperature during activity

**Activity Attributes:**
- `workout_type`: Strava workout type code (0=default, 1=race, 2=long run, 3=workout)
- `trainer`: Indoor trainer activity (true/false)
- `commute`: Marked as commute (true/false)
- `achievements`: Number of achievements earned
- `kudos`: Number of kudos received
- `personal_records`: Number of PRs set

## Use Cases for Nutritional Planning

This endpoint provides data suitable for:

### 1. **Caloric Needs Assessment**
- Daily/weekly calorie burn from activities
- Activity intensity patterns
- Training volume trends

### 2. **Recovery Planning**
- Suffer Score indicates workout intensity
- Heart rate data shows cardiovascular stress
- Elevation gain indicates muscular load

### 3. **Macro Nutrient Timing**
- Activity times for meal planning
- Duration/intensity for carb loading decisions
- Training patterns for protein timing

### 4. **Hydration Strategy**
- Temperature data for fluid needs
- Duration and intensity for electrolyte planning
- Elevation for increased hydration needs

### 5. **Periodization Support**
- Weekly volume trends
- Training load progression
- Activity type distribution

## Example Requests

### Get last 30 days of data (default)
```bash
curl "https://your-function-app.azurewebsites.net/api/nutrition-data?code=your-function-key"
```

### Get last 7 days for recent adjustments
```bash
curl "https://your-function-app.azurewebsites.net/api/nutrition-data?code=your-function-key&days=7"
```

### Get full 90-day history for long-term patterns
```bash
curl "https://your-function-app.azurewebsites.net/api/nutrition-data?code=your-function-key&days=90"
```

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success - Returns activity data |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing function key |
| 500 | Server Error - Strava API failure or internal error |

## Error Response Format

```json
{
  "error": "Error description",
  "details": "Detailed error message"
}
```

## Data Availability Notes

### Optional Fields
Some fields may be `null` if not recorded by Strava:
- `calories`: Depends on heart rate data and Strava's calculation
- `suffer_score`: Requires heart rate data
- `average_heartrate/max_heartrate`: Only if HR monitor was used
- `average_temp`: Only if temperature sensor data available
- `average_cadence`: Only if cadence sensor/footpod used

### Activity Types
Common activity types include:
- Run
- Ride (cycling)
- Swim
- Walk
- Hike
- VirtualRide
- VirtualRun
- Workout
- WeightTraining
- Yoga

### Workout Type Codes
- `null` or `0`: Default run
- `1`: Race
- `2`: Long run
- `3`: Workout (intervals, tempo, etc.)

## Privacy & Permissions

This endpoint uses the existing Strava API credentials and requires the same permissions as the main `running-data` endpoint:
- **activity:read_all** - Read all activity data

No additional Strava scopes are required. The endpoint only accesses data you've already authorized.

## Rate Limits

- Strava API limits: 200 requests per 15 minutes, 2,000 per day
- This endpoint makes 1 Strava API call per request
- The endpoint caches no data; each request fetches fresh data from Strava

## Integration Example

### Python
```python
import requests

function_key = "your-function-key"
base_url = "https://your-function-app.azurewebsites.net"

response = requests.get(
    f"{base_url}/api/nutrition-data",
    params={
        "code": function_key,
        "days": 30
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Total activities: {data['summary']['total_activities']}")
    print(f"Total calories: {data['summary']['total_calories']}")
    print(f"Weekly average distance: {data['weekly_averages']['distance_km_per_week']} km")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### JavaScript/Node.js
```javascript
const functionKey = 'your-function-key';
const baseUrl = 'https://your-function-app.azurewebsites.net';

async function getNutritionData(days = 30) {
  const response = await fetch(
    `${baseUrl}/api/nutrition-data?code=${functionKey}&days=${days}`
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  return data;
}

getNutritionData(30).then(data => {
  console.log(`Total calories: ${data.summary.total_calories}`);
  console.log(`Activities: ${data.summary.total_activities}`);
  console.log(`Weekly distance: ${data.weekly_averages.distance_miles_per_week} miles`);
});
```

## Troubleshooting

### No activities returned
- Verify you have activities in Strava during the requested period
- Check Strava API credentials are valid
- Ensure activities are not marked as private

### Missing calories/suffer_score
- These require heart rate data during activities
- Ensure HR monitor was connected during activities
- Older activities may not have this data

### High response time
- Requesting 90 days with many activities can take 5-10 seconds
- Consider requesting fewer days for faster responses
- Strava API response time varies

## Related Endpoints

- `/api/running-data` - Current week's running data for TRMNL dashboard
- `/api/health` - Health check endpoint

## Version History

- **v1.0** (2026-01-20): Initial release
  - Comprehensive activity history (1-90 days)
  - All metrics available without additional Strava permissions
  - Support for all activity types
  - Detailed performance and environmental data
