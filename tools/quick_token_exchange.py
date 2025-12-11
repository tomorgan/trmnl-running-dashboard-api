"""
Quick OAuth token exchange
"""
import requests

client_id = "your_strava_client_id"
client_secret = "your_strava_client_secret"
auth_code = "your_authorization_code"

print("Exchanging authorization code for tokens...")

try:
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code'
        },
        timeout=10
    )
    response.raise_for_status()
    
    token_data = response.json()
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Save these values:")
    print("=" * 60)
    print()
    print(f"STRAVA_CLIENT_ID={client_id}")
    print(f"STRAVA_CLIENT_SECRET={client_secret}")
    print(f"STRAVA_REFRESH_TOKEN={token_data['refresh_token']}")
    print()
    print("=" * 60)
    
    if 'athlete' in token_data:
        athlete = token_data['athlete']
        print(f"\n👤 Authenticated as: {athlete.get('firstname')} {athlete.get('lastname')}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    if hasattr(e, 'response') and e.response:
        print(f"Response: {e.response.text}")
