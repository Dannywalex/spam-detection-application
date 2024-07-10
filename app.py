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

# Zoho API credentials
client_id = '1000.CPBA8L32MSF7LFDZLGER6OE5GGT6AA'
client_secret = '9d9a0660b87dedaad28f1c3890796d6b86d5bc7a32'
redirect_uri = 'https://email-spam-detection-bluruuqhzkcgr58hbheduu.streamlit.app'
authorization_base_url = 'https://accounts.zoho.com/oauth/v2/auth'

# Initialize OAuth2 session
zoho = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['ZohoMail.messages.ALL'])
authorization_url, state = zoho.authorization_url(authorization_base_url)

# Store the state in session
if 'oauth_state' not in st.session_state:
    st.session_state['oauth_state'] = state

st.write(f'[Authorize Zoho]({authorization_url})')

# Get the authorization response URL from the user
authorization_response = st.text_input('Paste the full redirect URL here:')

if authorization_response:
    zoho = OAuth2Session(client_id, redirect_uri=redirect_uri)
    token = zoho.fetch_token(
        'https://accounts.zoho.com/oauth/v2/token',
        client_secret=client_secret,
        authorization_response=authorization_response
    )
    st.session_state['access_token'] = token['access_token']
    st.write('Access Token:', token)

def get_headers(access_token):
    return {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }

def fetch_emails(access_token):
    url = 'https://mail.zoho.com/api/accounts/856879721/messages'
    headers = get_headers(access_token)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f'Error fetching emails: {e}')
        return None

# Load pre-trained model and vectorizer
with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('vectorizer.pkl', 'rb') as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

def predict_spam(email_contents):
    try:
        email_vectors = vectorizer.transform(email_contents)
        predictions = model.predict(email_vectors)
        return predictions
    except Exception as e:
        st.error(f'Error predicting spam: {e}')
        return []

if 'access_token' in st.session_state:
    access_token = st.session_state['access_token']

    if st.button('Fetch Emails'):
        emails_response = fetch_emails(access_token)
        if emails_response and emails_response.get('status', 'error') == 'success':
            emails = emails_response.get('data', [])
            st.session_state['emails'] = emails
        else:
            st.error(f'Failed to fetch emails: {emails_response}')

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

