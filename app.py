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

import streamlit as st
import time
import pickle
from tokens import get_authorization_url, fetch_token, refresh_access_token, fetch_emails

# Store the state in session
if 'oauth_state' not in st.session_state:
    authorization_url, state = get_authorization_url()
    st.session_state['oauth_state'] = state
    st.write(f'[Authorize Zoho]({authorization_url})')

# Get the authorization response URL from the user
authorization_response = st.text_input('Paste the full redirect URL here:')

if authorization_response:
    try:
        token = fetch_token(authorization_response, st.session_state['oauth_state'])
        st.session_state['access_token'] = token['access_token']
        st.session_state['refresh_token'] = token.get('refresh_token')
        st.session_state['token_expires_at'] = time.time() + token['expires_in']
        st.write('Access Token:', token)
    except Exception as e:
        st.error(f'Error fetching token: {e}')
        st.stop()

if 'access_token' in st.session_state:
    if 'token_expires_at' in st.session_state and time.time() > st.session_state['token_expires_at']:
        st.write('Access token expired, refreshing...')
        new_token = refresh_access_token(st.session_state['refresh_token'])
        st.session_state['access_token'] = new_token['access_token']
        st.session_state['token_expires_at'] = time.time() + new_token['expires_in']
        st.write('New Access Token:', new_token)

    access_token = st.session_state['access_token']
    account_id = '856879721'

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
