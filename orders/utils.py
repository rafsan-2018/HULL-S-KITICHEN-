import json, requests, os
from dotenv import load_dotenv
load_dotenv()


def get_paypal_oauth_token():
    """
    Retrieve OAuth token from PayPal API.
    
    Returns:
        str: Access token.
    """
    client_id = os.getenv('PAYPAL_ID')
    client_secret = os.getenv('PAYPAL_SECRET')
    base_url = os.getenv('PAYPAL_BASE_URL')

    auth_response = requests.post(
        f'{base_url}/oauth2/token',
        headers={
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        },
        auth=(client_id, client_secret),
        data={'grant_type': 'client_credentials'}
    )

    if auth_response.status_code == 200:
        auth_response_data = auth_response.json()
        return auth_response_data['access_token']
    else:
        raise Exception(f"Failed to retrieve OAuth token: {auth_response.status_code} {auth_response.text}")