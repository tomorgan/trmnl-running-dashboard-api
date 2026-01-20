# Quick Start: Nutrition Data Endpoint

## Testing the Endpoint

Once deployed, test your new endpoint:

```bash
# Replace with your actual Azure Function App name and function key
FUNCTION_APP="your-app-name"
FUNCTION_KEY="your-function-key"

# Get 30 days of data (default)
curl "https://${FUNCTION_APP}.azurewebsites.net/api/nutrition-data?code=${FUNCTION_KEY}"

# Get last 7 days
curl "https://${FUNCTION_APP}.azurewebsites.net/api/nutrition-data?code=${FUNCTION_KEY}&days=7"

# Get full 90-day history
curl "https://${FUNCTION_APP}.azurewebsites.net/api/nutrition-data?code=${FUNCTION_KEY}&days=90"
```

## Sample Response (Abbreviated)

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
    "total_calories": 9600,
    "average_heartrate": 152.3
  },
  "weekly_averages": {
    "activities_per_week": 5.6,
    "distance_km_per_week": 33.2,
    "calories_per_week": 2240
  },
  "activities": [
    {
      "name": "Morning Run",
      "date": "2026-01-20",
      "distance_km": 8.5,
      "calories": 450,
      "average_heartrate": 155,
      "suffer_score": 42
    }
  ]
}
```

## Integration Examples

### Python
```python
import requests

FUNCTION_APP = "your-app-name"
FUNCTION_KEY = "your-function-key"
BASE_URL = f"https://{FUNCTION_APP}.azurewebsites.net"

def get_nutrition_data(days=30):
    """Fetch nutrition data from Azure Function."""
    response = requests.get(
        f"{BASE_URL}/api/nutrition-data",
        params={"code": FUNCTION_KEY, "days": days}
    )
    response.raise_for_status()
    return response.json()

# Get data and calculate nutritional needs
data = get_nutrition_data(days=7)

# Daily calorie burn from activities
daily_activity_calories = data['daily_averages']['calories_per_day']
print(f"Average daily activity calories: {daily_activity_calories}")

# Weekly training volume
weekly_km = data['weekly_averages']['distance_km_per_week']
print(f"Weekly distance: {weekly_km} km")

# Recent activity intensity
for activity in data['activities'][:5]:  # Last 5 activities
    print(f"{activity['name']}: {activity['calories']} cal, "
          f"suffer score: {activity['suffer_score']}")
```

### JavaScript/Node.js
```javascript
const FUNCTION_APP = 'your-app-name';
const FUNCTION_KEY = 'your-function-key';
const BASE_URL = `https://${FUNCTION_APP}.azurewebsites.net`;

async function getNutritionData(days = 30) {
  const url = `${BASE_URL}/api/nutrition-data?code=${FUNCTION_KEY}&days=${days}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  
  return await response.json();
}

// Usage
const data = await getNutritionData(7);

console.log(`Total activities: ${data.summary.total_activities}`);
console.log(`Total calories: ${data.summary.total_calories}`);
console.log(`Weekly avg distance: ${data.weekly_averages.distance_miles_per_week} miles`);

// Calculate nutritional recommendations
const baseCalories = 2000; // Base metabolic rate
const activityCalories = data.daily_averages.calories_per_day;
const recommendedCalories = baseCalories + activityCalories;

console.log(`Recommended daily calories: ${Math.round(recommendedCalories)}`);
```

## Key Metrics for Nutritional Planning

### Caloric Needs
```python
# Calculate total daily energy expenditure (TDEE)
BMR = 1800  # Your basal metabolic rate
activity_calories = data['daily_averages']['calories_per_day']
TDEE = BMR + activity_calories

# Adjust for training goals
if training_volume_increasing:
    target_calories = TDEE + 200  # Slight surplus
else:
    target_calories = TDEE  # Maintenance
```

### Recovery Assessment
```python
# High suffer scores indicate need for recovery nutrition
high_intensity_days = [
    a for a in data['activities'] 
    if a['suffer_score'] and a['suffer_score'] > 50
]

if high_intensity_days:
    print(f"Need extra recovery nutrition: {len(high_intensity_days)} hard workouts")
    # Recommend higher protein intake, anti-inflammatory foods
```

### Hydration Planning
```python
# Estimate fluid needs based on activity duration and temperature
total_activity_hours = data['summary']['total_moving_time_hours']
avg_temp = sum(
    a['average_temp_celsius'] for a in data['activities'] 
    if a['average_temp_celsius']
) / len([a for a in data['activities'] if a['average_temp_celsius']])

# Rule of thumb: 500-1000ml per hour of activity
estimated_fluid_ml = total_activity_hours * 750
print(f"Weekly fluid needs from activities: {estimated_fluid_ml}ml")
```

### Macro Distribution
```python
# Adjust macros based on training volume
weekly_distance = data['weekly_averages']['distance_km_per_week']

if weekly_distance > 50:  # High volume
    carb_percentage = 0.55  # 55% carbs for endurance
    protein_grams_per_kg = 1.6
elif weekly_distance > 30:  # Moderate
    carb_percentage = 0.50
    protein_grams_per_kg = 1.4
else:  # Low volume
    carb_percentage = 0.45
    protein_grams_per_kg = 1.2

print(f"Recommended carb %: {carb_percentage * 100}%")
print(f"Protein: {protein_grams_per_kg}g/kg body weight")
```

## Common Use Cases

### 1. Daily Calorie Adjustment
Pull last 7 days to adjust today's nutrition:
```bash
curl "https://${FUNCTION_APP}.azurewebsites.net/api/nutrition-data?code=${FUNCTION_KEY}&days=7"
```

### 2. Weekly Meal Planning
Pull last 30 days to plan next week's meals:
```bash
curl "https://${FUNCTION_APP}.azurewebsites.net/api/nutrition-data?code=${FUNCTION_KEY}&days=30"
```

### 3. Training Phase Analysis
Pull full 90 days to assess training periodization:
```bash
curl "https://${FUNCTION_APP}.azurewebsites.net/api/nutrition-data?code=${FUNCTION_KEY}&days=90"
```

## Troubleshooting

### Empty activities array
- Check you have activities in Strava during the requested period
- Verify Strava API credentials are configured correctly
- Ensure activities aren't marked as private in Strava

### Missing calorie/suffer_score data
- These require heart rate data during activities
- Make sure you wore an HR monitor during activities
- Older activities may not have been recorded with HR

### Slow response
- Requesting 90 days with many activities can take 5-10 seconds
- Consider caching results in your nutrition system
- Use smaller `days` parameter for faster responses

## Rate Limits

Strava API limits:
- 200 requests per 15 minutes
- 2,000 requests per day

This endpoint makes 1 Strava API call per request.

For production use, consider:
- Caching responses for 1-2 hours
- Only requesting updates when needed
- Using appropriate `days` parameter (shorter = faster)

## Security Note

⚠️ **Keep your function key secure!**
- Don't commit it to version control
- Don't share it publicly
- Rotate it regularly in Azure Portal

## Support

For full API documentation, see: [NUTRITION-ENDPOINT.md](NUTRITION-ENDPOINT.md)

For implementation details, see: [IMPLEMENTATION-SUMMARY.md](IMPLEMENTATION-SUMMARY.md)
