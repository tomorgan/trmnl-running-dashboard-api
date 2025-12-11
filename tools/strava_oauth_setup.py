"""
Strava OAuth Setup Helper

This script helps you get your initial Strava OAuth refresh token.
Run this once during initial setup.
"""
import webbrowser
import requests
from urllib.parse import urlparse, parse_qs


def setup_strava_oauth():
    """Guide user through Strava OAuth flow."""
    
    print("=" * 60)
    print("Strava OAuth Setup for TRMNL Running Dashboard")
    print("=" * 60)
    print()
    
    # Get client credentials
    client_id = input("Enter your Strava Client ID: ").strip()
    client_secret = input("Enter your Strava Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("\n❌ Error: Client ID and Secret are required")
        return
    
    # Build authorization URL
    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri=http://localhost"
        f"&approval_prompt=force"
        f"&scope=activity:read_all"
    )
    
    print("\n📝 Opening Strava authorization page in your browser...")
    print("\nIf it doesn't open automatically, go to:")
    print(f"\n{auth_url}\n")
    
    webbrowser.open(auth_url)
    
    print("=" * 60)
    print("After authorizing, you'll be redirected to localhost with a code.")
    print("The browser will show an error (that's expected).")
    print("=" * 60)
    print()
    print("Copy the FULL URL from your browser's address bar.")
    print("It will look like: http://localhost/?state=&code=XXXXX&scope=read,activity:read_all")
    print()
    
    redirect_url = input("Paste the full redirect URL here: ").strip()
    
    # Extract authorization code
    try:
        parsed = urlparse(redirect_url)
        params = parse_qs(parsed.query)
        auth_code = params.get('code', [None])[0]
        
        if not auth_code:
            print("\n❌ Error: Could not find authorization code in URL")
            return
        
        print(f"\n✅ Found authorization code: {auth_code[:10]}...")
        
    except Exception as e:
        print(f"\n❌ Error parsing URL: {e}")
        return
    
    # Exchange code for tokens
    print("\n🔄 Exchanging authorization code for tokens...")
    
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
        
        print("\n✅ Successfully obtained tokens!")
        print("\n" + "=" * 60)
        print("SAVE THESE VALUES")
        print("=" * 60)
        print()
        print(f"STRAVA_CLIENT_ID={client_id}")
        print(f"STRAVA_CLIENT_SECRET={client_secret}")
        print(f"STRAVA_REFRESH_TOKEN={token_data['refresh_token']}")
        print()
        print("Add these to your:")
        print("  • local.settings.json (for local development)")
        print("  • Azure Function App Settings (for production)")
        print()
        print("=" * 60)
        
        # Show athlete info
        if 'athlete' in token_data:
            athlete = token_data['athlete']
            print(f"\n👤 Authenticated as: {athlete.get('firstname')} {athlete.get('lastname')}")
        
        print("\n✅ Setup complete!")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error exchanging code for token: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return


if __name__ == "__main__":
    setup_strava_oauth()
