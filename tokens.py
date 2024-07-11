import requests
from requests_oauthlib import OAuth2Session
import time

client_id = '1000.CPBA8L32MSF7LFDZLGER6OE5GGT6AA'
client_secret = '9d9a0660b87dedaad28f1c3890796d6b86d5bc7a32'
redirect_uri = 'https://email-spam-detection-bluruuqhzkcgr58hbheduu.streamlit.app'
authorization_base_url = 'https://accounts.zoho.com/oauth/v2/auth'
token_url = 'https://accounts.zoho.com/oauth/v2/token'

def get_authorization_url():
    zoho = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['ZohoMail.messages.READ', 'offline_access'])
    authorization_url, state = zoho.authorization_url(authorization_base_url)
    return authorization_url, state

def fetch_token(authorization_response, state):
    zoho = OAuth2Session(client_id, redirect_uri=redirect_uri, state=state)
    token = zoho.fetch_token(
        token_url,
        authorization_response=authorization_response,
        client_secret=client_secret,
        include_client_id=True
    )
    return token

def refresh_access_token(refresh_token):
    extra = {
        'client_id': client_id,
        'client_secret': client_secret,
    }
    zoho = OAuth2Session(client_id, token={
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': -30,
    })
    new_token = zoho.refresh_token(token_url, **extra)
    return new_token

def get_headers(access_token):
    return {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }

def fetch_emails(access_token, account_id):
    url = f'https://mail.zoho.com/api/accounts/{account_id}/messages/view'
    headers = get_headers(access_token)
    response = requests.get(url, headers=headers)
    return response.json()