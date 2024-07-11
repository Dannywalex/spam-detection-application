import streamlit as st
import pickle



feature_extraction = pickle.load(open('vectorizer.pkl','rb'))
model = pickle.load(open('model.pkl','rb'))
st.title("Email Spam Detection")
input_email = st.text_input("Enter the message")

if st.button('Predict'):



  #1. preprocess
  input_mail = ["Ok lar... Joking wif u oni..."]
  #2.vectorize
  input_data_feature = feature_extraction.transform([input_email])
  #3.predict
  prediction = model.predict(input_data_feature)
  #4.Display
  if prediction[0] == 1:
   st.header("Not Spam")
  else:
   st.header("Spam")


import streamlit as st
from requests_oauthlib import OAuth2Session
import requests
import pickle
import time

# Zoho API credentials
client_id = '1000.BXSL7XM9FXXCV868OTQL9OLLQ1RZBS'
client_secret = '88739ce863131beda2fd855e7b1d466401130301e9'
redirect_uri = 'https://email-spam-detection-bluruuqhzkcgr58hbheduu.streamlit.app'
authorization_base_url = 'https://accounts.zoho.com/oauth/v2/auth'

# Initialize OAuth2 session
zoho = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['ZohoMail.messages.ALL','offline_access'])
authorization_url, state = zoho.authorization_url(authorization_base_url)

# Store the state in session
if 'oauth_state' not in st.session_state:
    st.session_state['oauth_state'] = state

st.write(f'[Authorize Zoho]({authorization_url})')

# Get the authorization response URL from the user
authorization_response = st.text_input('Paste the full redirect URL here:')

if authorization_response:
    try:
        zoho = OAuth2Session(client_id, redirect_uri=redirect_uri, state=st.session_state['oauth_state'])

        # Extract the authorization code from the response URL
        authorization_code = authorization_response.split('code=')[1].split('&')[0]
        st.write(f"Authorization Code: {authorization_code}")

        token = zoho.fetch_token(
            'https://accounts.zoho.com/oauth/v2/token',
            code=authorization_code,
            client_secret=client_secret,
            include_client_id=True
        )
        st.session_state['access_token'] = token['access_token']
        st.session_state['refresh_token'] = token.get('refresh_token')
        st.session_state['token_expires_at'] = time.time() + token['expires_in']
        st.write('Access Token:', token)
    except Exception as e:
        st.error(f'Error fetching token: {e}')
        st.stop()


def get_headers(access_token):
    return {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }

def fetch_emails(access_token, account_id, folder='inbox', limit=20, start=0, status=None, search=None, from_date=None, to_date=None):
    url = f'https://mail.zoho.com/api/accounts/856879721/messages/view'
    headers = get_headers(access_token)
    params = {
        'folder': folder,
        'limit': limit,
        'start': start,
    }

    if status:
        params['status'] = status
    if search:
        params['search'] = search
    if from_date:
        params['fromDate'] = from_date
    if to_date:
        params['toDate'] = to_date

    response = requests.get(url, headers=headers)
    return response.json()

def refresh_access_token():
    refresh_token = st.session_state['refresh_token']
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
    st.session_state['access_token'] = new_token['access_token']
    st.session_state['token_expires_at'] = time.time() + new_token['expires_in']
    st.write('New Access Token:', new_token)

if 'access_token' in st.session_state:
    if 'token_expires_at' in st.session_state and time.time() > st.session_state['token_expires_at']:
        st.write('Access token expired, refreshing...')
        refresh_access_token()

    access_token = st.session_state['access_token']
    account_id = '856879721'  # replace with your actual account ID

    if st.button('Fetch Emails'):
        emails_response = fetch_emails(access_token, account_id)
        if emails_response.get('status') == 'success':
            emails = emails_response.get('data', [])
            st.session_state['emails'] = emails
        else:
            st.error(f'Failed to fetch emails: {emails_response}')

# Load pre-trained model and vectorizer
with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('vectorizer.pkl', 'rb') as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

def predict_spam(email_contents):
        email_vectors = vectorizer.transform(email_contents)
        predictions = model.predict(email_vectors)
        return predictions

if 'emails' in st.session_state:
    emails = st.session_state['emails']
    email_contents = [email.get('content', '') for email in emails]
    predictions = predict_spam(email_contents)
    st.session_state['predictions'] = predictions

# Display results
if 'predictions' in st.session_state:
    emails = st.session_state['emails']
    predictions = st.session_state['predictions']

    for i, email in enumerate(emails):
        st.write(f"Subject: {email.get('subject', 'No Subject')}")
        st.write(f"From: {email.get('fromAddress', 'Unknown')}")
        st.write(f"Content: {email.get('content', 'No Content')}")
        st.write(f"Spam: {'Yes' if predictions[i] else 'No'}")
        st.write("---")

