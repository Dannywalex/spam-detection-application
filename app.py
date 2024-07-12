import streamlit as st
import requests
import pickle
import time
from requests_oauthlib import OAuth2Session

# Load the token
try:
    with open('token.pkl', 'rb') as token_file:
        token = pickle.load(token_file)
except FileNotFoundError:
    st.error('token.pkl not found. Please run tokens.py first to obtain tokens.')
    st.stop()

# Zoho API credentials
client_id = '1000.CPBA8L32MSF7LFDZLGER6OE5GGT6AA'
client_secret = '9d9a0660b87dedaad28f1c3890796d6b86d5bc7a32'
token_url = 'https://accounts.zoho.com/oauth/v2/token'

# Initialize OAuth2 session with the token
zoho = OAuth2Session(client_id, token=token)

def get_headers(access_token):
    return {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }
def fetch_account_details(access_token):
    url = 'https://mail.zoho.com/api/accounts'
    headers = get_headers(access_token)
    response = requests.get(url, headers=headers)
    return response.json()

def fetch_emails(access_token):
    url = 'https://mail.zoho.com/api/accounts/8848984000000008002/messages/view'
    headers = get_headers(access_token)
    response = requests.get(url, headers=headers)
    return response.json()

def refresh_access_token():
    refresh_token = token['refresh_token']
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
    with open('token.pkl', 'wb') as token_file:
        pickle.dump(new_token, token_file)
    st.session_state['access_token'] = new_token['access_token']
    st.session_state['token_expires_at'] = time.time() + new_token['expires_in']
    st.write('New Access Token:', new_token)

if 'access_token' not in st.session_state:
    st.session_state['access_token'] = token['access_token']
    st.session_state['refresh_token'] = token['refresh_token']
    st.session_state['token_expires_at'] = time.time() + token['expires_in']

if time.time() > st.session_state['token_expires_at']:
    st.write('Access token expired, refreshing...')
    refresh_access_token()

access_token = st.session_state['access_token']

# Fetch and display account details
account_details = fetch_account_details(access_token)
st.write("Account Details:", account_details)

if st.button('Fetch Emails'):
    if 'data' in account_details:
        account_id = account_details['data'][0]['accountId']  # Adjust this line based on your account details response
        emails_response = fetch_emails(access_token)
        if emails_response.get('status', {}).get('description') == 'success':
            emails = emails_response.get('data', [])
            st.session_state['emails'] = emails
        else:
            st.error(f'Failed to fetch emails: {emails_response}')
    else:
        st.error('No account data found.')

# Load pre-trained model and vectorizer
try:
    with open('model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('vectorizer.pkl', 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)
except FileNotFoundError:
    st.error('Model or vectorizer file not found.')
    st.stop()


def predict_spam(email_contents):
    email_vectors = vectorizer.transform(email_contents)
    predictions = model.predict(email_vectors)
    return predictions


# Predict and display spam status
if 'emails' in st.session_state:
    emails = st.session_state['emails']
    if not emails:
        st.write("No emails found.")
    else:
        email_contents = [email.get('content', '') for email in emails]
        predictions = predict_spam(email_contents)
        st.session_state['predictions'] = predictions

if 'predictions' in st.session_state:
    emails = st.session_state['emails']
    predictions = st.session_state['predictions']

    for i, email in enumerate(emails):
        st.write(f"Subject: {email.get('subject', 'No Subject')}")
        st.write(f"From: {email.get('fromAddress', 'Unknown')}")
        st.write(f"Content: {email.get('content', 'No Content')}")
        st.write(f"Spam: {'Yes' if predictions[i] else 'No'}")
        st.write("---")
