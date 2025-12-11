# TRMNL Running Dashboard API

Azure Function API that provides running data from Strava for the TRMNL Running Dashboard display.

## Features

- 🏃 Fetches weekly running data from Strava API
- 🌤️ Daily weather forecasts for training plan
- 📊 Dynamic training schedule based on weeks until event
- 💬 Daily rotating inspirational quotes
- 🔄 Auto-refreshing OAuth tokens
- ☁️ Serverless Azure Function deployment

## Architecture

```
TRMNL Device → Azure Function → Strava API
                      ↓          OpenWeatherMap API
                Environment Config
                (Event, Schedule, Quotes)
```

## Environment Variables

Set these in Azure Function App Settings or `local.settings.json`:

### Required
- `STRAVA_CLIENT_ID` - Your Strava API application client ID
- `STRAVA_CLIENT_SECRET` - Your Strava API application secret
- `STRAVA_REFRESH_TOKEN` - OAuth refresh token (obtained during setup)
- `NEXT_EVENT_NAME` - Name of your target race (e.g., "London Marathon 2026")
- `NEXT_EVENT_DATE` - ISO date of event (e.g., "2026-04-26")
- `OPENWEATHER_API_KEY` - OpenWeatherMap API key for weather forecasts
- `WEATHER_LAT` - Latitude for weather location (e.g., "51.507351")
- `WEATHER_LON` - Longitude for weather location (e.g., "-0.127758")

### Optional
- `TRAINING_SCHEDULE` - JSON array of weekly mileage targets (see below)
- `WEEKLY_PLAN` - JSON array of daily workouts (see below)

## Training Schedule Format

Define your training plan as a JSON array in the `TRAINING_SCHEDULE` environment variable:

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

The API will automatically select the appropriate weekly target based on how many weeks remain until your event.

**Default**: If not provided, defaults to 25 miles per week.

## Weekly Plan Format

Define your weekly training plan in the `WEEKLY_PLAN` environment variable:

```json
[
  {"day": "Monday", "workout": "Rest day"},
  {"day": "Tuesday", "workout": "Easy 5 miles"},
  {"day": "Wednesday", "workout": "Tempo 6 miles"},
  {"day": "Thursday", "workout": "Easy 4 miles"},
  {"day": "Friday", "workout": "Rest day"},
  {"day": "Saturday", "workout": "Long run 10 miles"},
  {"day": "Sunday", "workout": "Recovery 3 miles"}
]
```

The API will return this plan in the response so it can be displayed on your TRMNL dashboard.

**Default**: If not provided, returns empty array.

## Strava Setup

### 1. Create Strava API Application

1. Go to https://www.strava.com/settings/api
2. Create a new application
3. Set Authorization Callback Domain to `localhost`
4. Note your **Client ID** and **Client Secret**

### 2. Get Initial OAuth Token

Run the setup helper script:

```bash
cd tools
python strava_oauth_setup.py
```

This will:
1. Open a browser for Strava authorization
2. Exchange the code for tokens
3. Display your `STRAVA_REFRESH_TOKEN` to save

## Weather API Setup

### 1. Get OpenWeatherMap API Key

1. Sign up at https://openweathermap.org/
2. Subscribe to the **Daily Forecast 16 Days** API
3. Get your API key from your account dashboard
4. Note your API key

### 2. Find Your Location Coordinates

1. Go to https://www.latlong.net/
2. Enter your city or address
3. Note the **Latitude** and **Longitude** values
4. Add these as `WEATHER_LAT` and `WEATHER_LON` environment variables

## Local Development

### Prerequisites
- Python 3.9+
- Azure Functions Core Tools v4
- Strava API application

### Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/trmnl-running-dashboard-api.git
   cd trmnl-running-dashboard-api
   ```

2. Create virtual environment
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure local settings
   ```bash
   cp local.settings.json.example local.settings.json
   # Edit local.settings.json with your values
   ```

5. Run locally
   ```bash
   func start
   ```

6. Test endpoint
   ```bash
   # Health check
   curl "http://localhost:7071/api/health?code=<your-local-function-key>"
   
   # Running data
   curl "http://localhost:7071/api/running-data?code=<your-local-function-key>"
   ```
   
   Note: Local development uses a default function key. Check the terminal output when running `func start` for the key, or it may work without the key parameter locally.

## Deployment to Azure

### Manual Deployment (Recommended)

**Prerequisites:**
- Azure CLI installed and logged in (`az login`)
- Azure Functions Core Tools v4
- Azure Function App created (see AZURE-DEPLOYMENT.md)

**Deploy:**
```bash
# From project directory
func azure functionapp publish <your-function-app-name>
```

**After first deployment or environment changes:**

In Azure Portal → Function App → Configuration → Application settings, add all the environment variables listed in the "Environment Variables" section above.

Click **Save** after adding settings.

**Get Function Key (Required for API access):**
1. Azure Portal → Your Function App → Functions → running-data
2. Click **Function Keys**
3. Copy the `default` key value
4. Use this key when calling the API: `?code=<your-function-key>`

**Enable CORS (for TRMNL access):**
- Azure Portal → Function App → CORS
- Add: `https://usetrmnl.com` or `*`
- Click **Save**

**API URL Format:**
```
https://<your-function-app-name>.azurewebsites.net/api/running-data?code=<your-function-key>
```

## API Response Format

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
  "quote": "The miracle isn't that I finished. The miracle is that I had the courage to start.",
  "weekly_plan": [
    {
      "day": "Monday",
      "day_short": "Mon",
      "workout": "Rest day",
      "completed": false
    },
    {
      "day": "Tuesday",
      "day_short": "Tue",
      "workout": "Easy 5 miles",
      "completed": true,
      "distance_miles": 5.2,
      "duration_minutes": 45,
      "pace_per_mile": "8:39",
      "weather": {
        "temp_morning": 12.5,
        "feels_like_morning": 10.3,
        "precipitation_prob": 20,
        "description": "partly cloudy"
      }
    },
    {
      "day": "Wednesday",
      "day_short": "Wed",
      "workout": "Tempo 6 miles",
      "completed": false,
      "weather": {
        "temp_morning": 14.2,
        "feels_like_morning": 13.1,
        "precipitation_prob": 5,
        "description": "clear sky"
      }
    }
  ]
}
```

## Testing

```bash
# Run unit tests
pytest tests/

# Test with mock data
python -m tests.test_with_mock_data
```

## Troubleshooting

### "Unauthorized" Error
- Check your `STRAVA_REFRESH_TOKEN` is valid
- Re-run OAuth setup to get a new token

### No Activities Returned
- Ensure you have runs logged in Strava this week (Monday onwards)
- Check Strava API scope includes `activity:read_all`

### Wrong Weekly Target
- Verify `TRAINING_SCHEDULE` JSON is valid
- Check `NEXT_EVENT_DATE` is set correctly
- API uses current week to calculate weeks_until_event

### No Weather Data
- Verify `OPENWEATHER_API_KEY`, `WEATHER_LAT`, and `WEATHER_LON` are set correctly
- Check your OpenWeatherMap subscription includes Daily Forecast API
- Weather data only shows for future days (past days in the week won't have forecasts)

## Project Structure

```
trmnl-running-dashboard-api/
├── function_app.py              # Main Azure Function
├── strava_client.py             # Strava API integration
├── weather_client.py            # Weather API integration
├── quotes.py                    # Running quotes
├── utils.py                     # Helper functions
├── requirements.txt             # Python dependencies
├── host.json                    # Azure Functions config
├── local.settings.json.example  # Example config
├── tools/
│   └── strava_oauth_setup.py   # OAuth helper script
└── tests/
    ├── test_strava_client.py
    ├── test_utils.py
    └── mock_strava_response.json
```

## Related Projects

- [A custom plugin for TRMNL e-ink displays that shows your weekly running progress, upcoming events, and recent runs.](https://github.com/tomorgan/trmnl-running-dashboard)

## License

MIT
