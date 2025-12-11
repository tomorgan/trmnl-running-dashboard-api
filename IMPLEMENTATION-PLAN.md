# TRMNL Running Dashboard API - Implementation Plan

## Overview

Azure Function-based API that combines Strava activity data with configuration to provide running dashboard data for TRMNL display.

## Architecture

```
┌─────────────────┐
│  TRMNL Device   │
└────────┬────────┘
         │ HTTPS GET
         ▼
┌─────────────────────┐
│  Azure Function     │
│  (HTTP Trigger)     │
└────────┬────────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌──────────────┐    ┌──────────────┐
│ Strava API   │    │ Environment  │
│ (OAuth 2.0)  │    │ Variables    │
└──────────────┘    └──────────────┘
```

## Technology Stack

- **Runtime**: Python 3.9+ (Azure Functions v2)
- **Framework**: Azure Functions HTTP Trigger
- **External API**: Strava API v3
- **Authentication**: Strava OAuth 2.0 with refresh tokens
- **Configuration**: Environment variables / Azure App Settings

## Data Sources

### 1. Strava API
**Endpoint**: `GET /athlete/activities`
- Fetches activities from the current week
- Extracts: distance, duration, date, pace
- Requires OAuth 2.0 authentication

**Authentication Flow**:
- Initial setup: Manual OAuth to get refresh token
- Runtime: Auto-refresh access token using refresh token
- Store in environment: `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, `STRAVA_REFRESH_TOKEN`

### 2. Environment Variables
- `NEXT_EVENT_NAME` - e.g., "London Marathon 2026"
- `NEXT_EVENT_DATE` - ISO format: "2026-04-26"
- `TRAINING_SCHEDULE` - JSON array of weekly targets based on weeks until event
  - Format: `[{"weeks_until": 12, "target_miles": 20}, {"weeks_until": 8, "target_miles": 25}, ...]`
  - Function will find the matching week and use that target
  - Falls back to last entry if no exact match
- `STRAVA_CLIENT_ID` - Strava API credentials
- `STRAVA_CLIENT_SECRET` - Strava API credentials
- `STRAVA_REFRESH_TOKEN` - OAuth refresh token

### 3. Quotes (Hardcoded)
- `quotes.py` - Python list of 20+ running quotes
- Random selection per request OR daily rotation

### 4. Calculated Fields
- `weekly_miles` - Sum of distances from Strava activities this week
- `target_miles` - Lookup from `TRAINING_SCHEDULE` based on weeks until event
- `progress_percentage` - `(weekly_miles / target_miles) * 100`, capped at 100
- `weeks_until_event` - Calculate from `NEXT_EVENT_DATE` to today
- `week_label` - Generate from current date (e.g., "Week of Dec 2-8, 2025")
- `runs[].date_formatted` - Transform ISO date to "Mon, Dec 2" format
- `runs[].pace_per_mile` - Calculate from distance and duration

## Project Structure

```
trmnl-running-dashboard-api/
├── .github/
│   └── workflows/
│       └── deploy.yml           # GitHub Actions for Azure deployment
├── function_app.py              # Main Azure Function HTTP trigger
├── strava_client.py             # Strava API integration
├── quotes.py                    # Hardcoded running quotes
├── utils.py                     # Helper functions (calculations, formatting)
├── requirements.txt             # Python dependencies
├── host.json                    # Azure Functions host config
├── local.settings.json.example  # Example environment variables
├── .gitignore
├── .funcignore
├── README.md
└── tests/
    ├── test_strava_client.py
    ├── test_utils.py
    └── mock_strava_response.json
```

## Implementation Phases

### Phase 1: Local Development Setup ✅ (Next)
1. Create project structure
2. Set up Python virtual environment
3. Install dependencies (azure-functions, requests, python-dateutil)
4. Create configuration files
5. Set up local testing environment

### Phase 2: Strava Integration
1. Create Strava OAuth helper for initial token exchange
2. Implement token refresh logic
3. Build Strava API client
4. Fetch and parse activities
5. Calculate pace from distance/duration
6. Filter activities to current week
7. Test with mock data and real Strava API

### Phase 3: Data Processing & Business Logic
1. Implement quote selection (daily rotation)
2. Calculate weekly totals
3. Calculate progress percentage
4. Generate week label
5. Calculate weeks until event
6. Format dates for display
7. Transform Strava data to API response format

### Phase 4: Azure Function Implementation
1. Create HTTP trigger function
2. Implement request handling
3. Error handling and logging
4. Environment variable loading
5. Response formatting (JSON)
6. CORS configuration for TRMNL
7. Local testing with Azure Functions Core Tools

### Phase 5: Testing & Validation
1. Unit tests for utilities
2. Integration tests for Strava client
3. End-to-end tests for function
4. Test with different scenarios (no runs, many runs, etc.)
5. Validate against plugin's expected JSON structure
6. Performance testing (response time < 2s)

### Phase 6: Deployment
1. Create Azure Function App resource
2. Configure application settings (environment variables)
3. Set up GitHub Actions deployment workflow
4. Deploy to Azure
5. Test production endpoint
6. Configure TRMNL plugin with production URL

### Phase 7: Documentation & Monitoring
1. README with setup instructions
2. Strava OAuth setup guide
3. Azure deployment guide
4. Environment variables documentation
5. Set up Application Insights (optional)
6. Create troubleshooting guide

## Strava API Details

### Authentication Flow

**One-time Setup** (Manual):
```
1. Create Strava API Application at https://www.strava.com/settings/api
2. Get authorization code:
   https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all
3. Exchange code for tokens:
   POST https://www.strava.com/oauth/token
   {
     "client_id": "YOUR_CLIENT_ID",
     "client_secret": "YOUR_CLIENT_SECRET",
     "code": "AUTHORIZATION_CODE",
     "grant_type": "authorization_code"
   }
4. Save refresh_token to environment variables
```

**Runtime** (Automated):
```python
def refresh_access_token():
    response = requests.post('https://www.strava.com/oauth/token', data={
        'client_id': os.getenv('STRAVA_CLIENT_ID'),
        'client_secret': os.getenv('STRAVA_CLIENT_SECRET'),
        'refresh_token': os.getenv('STRAVA_REFRESH_TOKEN'),
        'grant_type': 'refresh_token'
    })
    return response.json()['access_token']
```

### Getting Activities

```python
def get_weekly_activities(access_token):
    # Get activities after Monday of current week
    week_start = get_week_start()
    
    response = requests.get(
        'https://www.strava.com/api/v3/athlete/activities',
        headers={'Authorization': f'Bearer {access_token}'},
        params={
            'after': int(week_start.timestamp()),
            'per_page': 50
        }
    )
    return response.json()
```

### Strava Activity Response (relevant fields)
```json
{
  "id": 12345,
  "name": "Morning Run",
  "distance": 8367.2,              // meters
  "moving_time": 2700,             // seconds
  "elapsed_time": 2800,
  "start_date": "2025-12-02T06:30:00Z",
  "type": "Run"                    // Filter for "Run" only
}
```

## Key Calculations

### Training Schedule Lookup
```python
import json

def get_weekly_target(weeks_until_event, training_schedule_json):
    """Get weekly target miles from training schedule"""
    schedule = json.loads(training_schedule_json)
    
    # Find exact match or closest week
    for entry in sorted(schedule, key=lambda x: x['weeks_until'], reverse=True):
        if weeks_until_event >= entry['weeks_until']:
            return entry['target_miles']
    
    # Fallback to first entry if before training starts
    return schedule[0]['target_miles'] if schedule else 25.0
```

**Example TRAINING_SCHEDULE environment variable:**
```json
[
  {"weeks_until": 16, "target_miles": 15},
  {"weeks_until": 12, "target_miles": 20},
  {"weeks_until": 8, "target_miles": 25},
  {"weeks_until": 6, "target_miles": 28},
  {"weeks_until": 4, "target_miles": 30},
  {"weeks_until": 2, "target_miles": 20},
  {"weeks_until": 1, "target_miles": 10}
]
```

This allows you to define a complete training plan that adjusts weekly targets automatically based on how many weeks remain until your event.

### Pace Calculation
```python
def calculate_pace(distance_meters, duration_seconds):
    """Calculate pace in min/mile"""
    distance_miles = distance_meters * 0.000621371
    if distance_miles == 0:
        return "0:00"
    
    minutes_per_mile = duration_seconds / 60 / distance_miles
    mins = int(minutes_per_mile)
    secs = int((minutes_per_mile - mins) * 60)
    return f"{mins}:{secs:02d}"
```

### Week Calculation
```python
from datetime import datetime, timedelta

def get_week_start():
    """Get Monday of current week"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)

def calculate_weeks_until_event(event_date_str):
    """Calculate weeks from now until event"""
    event_date = datetime.fromisoformat(event_date_str)
    today = datetime.now()
    days_diff = (event_date - today).days
    return max(0, days_diff // 7)
```

## Expected API Response

```json
{
  "weekly_miles": 15.5,
  "target_miles": 25.0,
  "weeks_until_event": 8,
  "event_name": "London Marathon 2026",
  "runs": [
    {
      "date": "2025-12-02",
      "distance_miles": 5.2,
      "duration_minutes": 45,
      "pace_per_mile": "8:39"
    }
  ],
  "quote": "The miracle isn't that I finished..."
}
```

## Dependencies (requirements.txt)

```
azure-functions>=1.18.0
requests>=2.31.0
python-dateutil>=2.8.2
```

## Security Considerations

1. Never commit tokens or secrets to git
2. Use Azure Key Vault for sensitive values (optional)
3. Implement rate limiting if needed
4. Validate incoming requests
5. Use HTTPS only (enforced by Azure)
6. Set appropriate CORS headers

## Performance Targets

- Response time: < 2 seconds
- Strava API call: < 1 second
- Cold start: < 5 seconds
- Memory usage: < 256 MB

## Error Handling

1. Strava API errors (401, 429, 500)
2. Invalid/expired refresh token
3. Missing environment variables
4. No activities found (return empty array)
5. Network errors
6. Date parsing errors

## Next Steps

After approval of this plan:
1. Create project structure with all files
2. Implement Strava OAuth helper script
3. Build core functionality
4. Test locally
5. Deploy to Azure
6. Integrate with TRMNL plugin

---

**Ready to proceed?** This plan provides a complete roadmap for building a production-ready Azure Function API that integrates with Strava and serves your TRMNL running dashboard.
