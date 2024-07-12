from requests_oauthlib import OAuth2Session
import time
import pickle

# Zoho API credentials
client_id = '1000.CPBA8L32MSF7LFDZLGER6OE5GGT6AA'
client_secret = '9d9a0660b87dedaad28f1c3890796d6b86d5bc7a32'
redirect_uri = 'https://email-spam-detection-bluruuqhzkcgr58hbheduu.streamlit.app'
authorization_base_url = 'https://accounts.zoho.com/oauth/v2/auth'
token_url = 'https://accounts.zoho.com/oauth/v2/token'

# Initialize OAuth2 session
zoho = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['ZohoMail.messages.READ','offline_access'])

# Step 1: Redirect user to Zoho for authorization
authorization_url, state = zoho.authorization_url(authorization_base_url)
print(f'Please go to this URL and authorize access: {authorization_url}')

# Get the authorization response URL from the user
authorization_response = input('Paste the full redirect URL here: ')


# Fetch the access and refresh tokens
zoho = OAuth2Session(client_id, redirect_uri=redirect_uri, state=state)
token = zoho.fetch_token(token_url, authorization_response=authorization_response, client_secret=client_secret, include_client_id=True)

# Save the token to a file for later use
with open('token.pkl', 'wb') as token_file:
    pickle.dump(zoho.token, token_file)

print('Tokens have been successfully obtained and saved.')
