# Local Testing Guide

## ✅ Completed Setup Steps

1. ✅ Python 3.11.2 installed
2. ✅ Virtual environment created (`.venv`)
3. ✅ Dependencies installed
4. ✅ Azure Functions Core Tools installed
5. ✅ `local.settings.json` created

## 🔐 Strava OAuth Setup (Required)

### Step 1: Create Strava API Application

1. Go to https://www.strava.com/settings/api
2. Click "Create App" or use existing app
3. Fill in the form:
   - **Application Name**: TRMNL Running Dashboard (or your choice)
   - **Category**: Visualizer
   - **Website**: Your website or http://localhost
   - **Authorization Callback Domain**: `localhost`
4. Click "Create"
5. **Save your Client ID and Client Secret**

### Step 2: Run OAuth Setup Script

Open a NEW PowerShell window in the project directory and run:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run OAuth setup
cd tools
python strava_oauth_setup.py
```

The script will:
1. Ask for your Strava Client ID and Secret
2. Open a browser to Strava's authorization page
3. After you authorize, you'll be redirected to `http://localhost/?code=...`
4. **Copy the FULL URL from your browser** (even though it shows an error)
5. Paste it back into the terminal
6. The script will exchange the code for tokens and display your **STRAVA_REFRESH_TOKEN**

**Save these values - you'll need them next!**

## 📝 Configure Environment Variables

Edit `local.settings.json` and replace the placeholder values:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "STRAVA_CLIENT_ID": "YOUR_CLIENT_ID_HERE",
    "STRAVA_CLIENT_SECRET": "YOUR_CLIENT_SECRET_HERE",
    "STRAVA_REFRESH_TOKEN": "YOUR_REFRESH_TOKEN_HERE",
    "NEXT_EVENT_NAME": "London Marathon 2026",
    "NEXT_EVENT_DATE": "2026-04-26",
    "TRAINING_SCHEDULE": "[{\"weeks_until\": 16, \"target_miles\": 15}, {\"weeks_until\": 12, \"target_miles\": 20}, {\"weeks_until\": 8, \"target_miles\": 25}, {\"weeks_until\": 6, \"target_miles\": 28}, {\"weeks_until\": 4, \"target_miles\": 30}, {\"weeks_until\": 2, \"target_miles\": 20}, {\"weeks_until\": 1, \"target_miles\": 10}]"
  }
}
```

### Configure Your Event

Update these values in `local.settings.json`:
- `NEXT_EVENT_NAME` - Your race name
- `NEXT_EVENT_DATE` - Race date in YYYY-MM-DD format
- `TRAINING_SCHEDULE` - Your weekly mileage plan (optional)

## 🚀 Running the Function Locally

1. **Activate virtual environment** (if not already):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Start the Azure Function**:
   ```powershell
   func start
   ```

3. **Wait for startup** - You should see:
   ```
   Azure Functions Core Tools
   Core Tools Version: 4.x.x
   Function Runtime Version: 4.x.x
   
   Functions:
     get_running_data: [GET] http://localhost:7071/api/running-data
     health_check: [GET] http://localhost:7071/api/health
   ```

## 🧪 Testing the API

### Test 1: Health Check

Open a new PowerShell window and run:

```powershell
curl http://localhost:7071/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-05T13:46:00.000000"
}
```

### Test 2: Get Running Data

```powershell
curl http://localhost:7071/api/running-data
```

**Expected response:**
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

### Test 3: Open in Browser

Navigate to: http://localhost:7071/api/running-data

You should see formatted JSON with your running data.

## 📊 What the API Returns

- `weekly_miles` - Total miles run this week (Monday onwards)
- `target_miles` - Weekly target from training schedule
- `weeks_until_event` - Calculated from today to event date
- `event_name` - From environment variable
- `runs` - Array of runs from Strava this week
- `quote` - Changes daily

## 🐛 Troubleshooting

### No runs returned / weekly_miles is 0

**Cause**: No runs logged in Strava since Monday, or Strava API credentials incorrect

**Fix**:
1. Check you have runs in Strava from this week (Monday onwards)
2. Verify `STRAVA_REFRESH_TOKEN` is correct
3. Check function logs for Strava API errors

### "Missing required Strava credentials"

**Cause**: Environment variables not set

**Fix**:
1. Ensure `local.settings.json` has all Strava credentials
2. Restart the function (`Ctrl+C` then `func start` again)

### Wrong weekly target

**Cause**: Training schedule or event date misconfigured

**Fix**:
1. Verify `NEXT_EVENT_DATE` is in future
2. Check `TRAINING_SCHEDULE` JSON is valid
3. Calculate weeks until event manually to verify

### Function won't start

**Cause**: Virtual environment not activated or dependencies missing

**Fix**:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
func start
```

## 🔄 Testing Without Strava (Mock Data)

If you want to test without Strava API access, you can temporarily modify `function_app.py`:

Comment out lines 63-70 and replace with:
```python
# Mock data for testing
import json
with open('tests/mock_strava_response.json') as f:
    mock_activities = json.load(f)
runs = [r for r in mock_activities if r['type'] == 'Run']
```

## 📝 Viewing Logs

The function outputs detailed logs. Look for:
- `Running data request received` - Request started
- `Week: ...` - Calculated values
- `Fetched X runs from Strava` - Strava API success
- `Returning data: X/Y miles` - Final response

## ✅ Success Checklist

Before moving to deployment, verify:

- [ ] Function starts without errors
- [ ] Health check returns 200 OK
- [ ] Running data endpoint returns valid JSON
- [ ] Strava integration works (shows your actual runs)
- [ ] Weekly target is correct for weeks until event
- [ ] Quote changes daily
- [ ] Calculations are accurate (miles, pace, progress)

## 🚀 Next: Deploy to Azure

Once local testing is successful, you're ready to deploy to Azure!

See `README.md` for deployment instructions.

---

## Quick Reference Commands

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Start function
func start

# Test health
curl http://localhost:7071/api/health

# Test running data
curl http://localhost:7071/api/running-data

# Run tests
pytest tests/

# Stop function
Ctrl+C
```
