"""
Weather API client for fetching daily forecasts.
"""
import os
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WeatherClient:
    """Client for interacting with OpenWeatherMap API."""
    
    FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast/daily"
    
    def __init__(self, api_key=None, lat=None, lon=None):
        """
        Initialize Weather client.
        
        Args:
            api_key (str): OpenWeatherMap API key
            lat (str): Latitude for weather location
            lon (str): Longitude for weather location
        """
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.lat = lat or os.getenv('WEATHER_LAT')
        self.lon = lon or os.getenv('WEATHER_LON')
        
        if not all([self.api_key, self.lat, self.lon]):
            raise ValueError("Missing required weather API credentials in environment variables")
    
    def get_daily_forecast(self, days=7):
        """
        Get daily weather forecast.
        
        Args:
            days (int): Number of days to forecast (1-16)
        
        Returns:
            dict: Weather forecast data with daily forecasts keyed by date
            
        Raises:
            Exception: If API request fails
        """
        try:
            logger.info(f"Fetching {days}-day weather forecast")
            
            params = {
                'lat': self.lat,
                'lon': self.lon,
                'cnt': min(days, 16),
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(
                self.FORECAST_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Process forecast data into a dict keyed by date
            forecasts_by_date = {}
            if 'list' in data:
                for day in data['list']:
                    # Convert Unix timestamp to date string
                    forecast_date = datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d')
                    
                    weather_info = {
                        'temp_morning': day.get('temp', {}).get('morn'),
                        'feels_like_morning': day.get('feels_like', {}).get('morn'),
                        'precipitation_prob': day.get('pop', 0) * 100,  # Convert to percentage
                        'description': day.get('weather', [{}])[0].get('description', 'Unknown')
                    }
                    
                    forecasts_by_date[forecast_date] = weather_info
            
            logger.info(f"Successfully fetched forecast for {len(forecasts_by_date)} days")
            return forecasts_by_date
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch weather forecast: {e}")
            raise Exception(f"Weather API request failed: {e}")
