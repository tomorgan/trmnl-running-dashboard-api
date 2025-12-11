"""
Strava API client for fetching running activities.
"""
import os
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StravaClient:
    """Client for interacting with Strava API v3."""
    
    TOKEN_URL = "https://www.strava.com/oauth/token"
    ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
    
    def __init__(self, client_id=None, client_secret=None, refresh_token=None):
        """
        Initialize Strava client.
        
        Args:
            client_id (str): Strava API client ID
            client_secret (str): Strava API client secret
            refresh_token (str): OAuth refresh token
        """
        self.client_id = client_id or os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('STRAVA_CLIENT_SECRET')
        self.refresh_token = refresh_token or os.getenv('STRAVA_REFRESH_TOKEN')
        self.access_token = None
        
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise ValueError("Missing required Strava credentials in environment variables")
    
    def refresh_access_token(self):
        """
        Refresh the access token using the refresh token.
        
        Returns:
            str: New access token
            
        Raises:
            Exception: If token refresh fails
        """
        logger.info("Refreshing Strava access token")
        
        try:
            response = requests.post(
                self.TOKEN_URL,
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'refresh_token': self.refresh_token,
                    'grant_type': 'refresh_token'
                },
                timeout=10
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            logger.info("Successfully refreshed access token")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh access token: {e}")
            raise Exception(f"Strava token refresh failed: {e}")
    
    def get_activities(self, after_timestamp=None, per_page=50):
        """
        Get athlete activities from Strava.
        
        Args:
            after_timestamp (int): Unix timestamp to get activities after
            per_page (int): Number of activities per page (max 200)
        
        Returns:
            list: List of activity dictionaries
            
        Raises:
            Exception: If API request fails
        """
        if not self.access_token:
            self.refresh_access_token()
        
        params = {
            'per_page': min(per_page, 200)
        }
        
        if after_timestamp:
            params['after'] = after_timestamp
        
        try:
            logger.info(f"Fetching activities from Strava (after: {after_timestamp})")
            
            response = requests.get(
                self.ACTIVITIES_URL,
                headers={'Authorization': f'Bearer {self.access_token}'},
                params=params,
                timeout=10
            )
            
            # If unauthorized, try refreshing token once
            if response.status_code == 401:
                logger.warning("Access token expired, refreshing...")
                self.refresh_access_token()
                response = requests.get(
                    self.ACTIVITIES_URL,
                    headers={'Authorization': f'Bearer {self.access_token}'},
                    params=params,
                    timeout=10
                )
            
            response.raise_for_status()
            activities = response.json()
            
            logger.info(f"Fetched {len(activities)} activities from Strava")
            return activities
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch activities: {e}")
            raise Exception(f"Strava API request failed: {e}")
    
    def get_weekly_runs(self, week_start_datetime):
        """
        Get all running activities from the current week.
        
        Args:
            week_start_datetime (datetime): Start of the week
        
        Returns:
            list: List of run activities with relevant fields
        """
        # Convert datetime to Unix timestamp
        after_timestamp = int(week_start_datetime.timestamp())
        
        # Get all activities after week start
        activities = self.get_activities(after_timestamp=after_timestamp)
        
        # Filter for runs only and extract relevant data
        runs = []
        for activity in activities:
            if activity.get('type') == 'Run':
                runs.append({
                    'id': activity.get('id'),
                    'name': activity.get('name'),
                    'distance': activity.get('distance', 0),  # meters
                    'moving_time': activity.get('moving_time', 0),  # seconds
                    'elapsed_time': activity.get('elapsed_time', 0),  # seconds
                    'start_date': activity.get('start_date'),  # ISO format
                })
        
        logger.info(f"Filtered {len(runs)} runs from {len(activities)} activities")
        return runs
