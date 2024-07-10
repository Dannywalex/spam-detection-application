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
import joblib


client_id = '1000.CPBA8L32MSF7LFDZLGER6OE5GGT6AA'
client_secret = '9d9a0660b87dedaad28f1c3890796d6b86d5bc7a32'
redirect_uri = 'https://email-spam-detection-bluruuqhzkcgr58hbheduu.streamlit.app'
authorization_base_url = 'https://accounts.zoho.com/oauth/v2/auth'

zoho = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['ZohoMail.messages.ALL'])
authorization_url, state = zoho.authorization_url(authorization_base_url)

st.write(f'[Authorize Zoho]({authorization_url})')

authorization_response = st.text_input('Paste the full redirect URL here:')


if authorization_response:
    zoho = OAuth2Session(client_id, redirect_uri=redirect_uri)
    token = zoho.fetch_token(
        'https://accounts.zoho.com/oauth/v2/token',
        client_secret=client_secret,
        authorization_response=authorization_response
    )
    st.write('Access Token:', token)


def get_headers(access_token):
    return {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }


def send_email(access_token, from_address, to_address, subject, content):
    url = 'https://mail.zoho.com/api/accounts/856879721/messages'
    headers = get_headers(access_token)
    email_data = {
        "fromAddress": from_address,
        "toAddress": [to_address],
        "subject": subject,
        "content": content
    }

    response = requests.post(url, headers=headers, json=email_data)
    return response


def fetch_emails(access_token):
    url = 'https://mail.zoho.com/api/accounts/856879721/messages'
    headers = get_headers(access_token)

    response = requests.get(url, headers=headers)
    return response.json()


if 'access_token' in st.session_state:
    access_token = st.session_state['access_token']

    if st.button('Fetch Emails'):
        emails_response = fetch_emails(access_token)
        if emails_response.get('status', 'error') == 'success':
            emails = emails_response.get('data', [])
            st.session_state['emails'] = emails
        else:
            st.error(f'Failed to fetch emails: {emails_response}')

import joblib

# Load pre-trained model
model = joblib.load('model.pkl')

def predict_spam(email_contents):
    predictions = model.predict(email_contents)
    return predictions

if 'emails' in st.session_state:
    emails = st.session_state['emails']
    email_contents = [email.get('content', '') for email in emails]
    predictions = predict_spam(email_contents)
    st.session_state['predictions'] = predictions

#display results
if 'predictions' in st.session_state:
    emails = st.session_state['emails']
    predictions = st.session_state['predictions']

    for i, email in enumerate(emails):
        st.write(f"Subject: {email.get('subject', 'No Subject')}")
        st.write(f"From: {email.get('fromAddress', 'Unknown')}")
        st.write(f"Content: {email.get('content', 'No Content')}")
        st.write(f"Spam: {'Yes' if predictions[i] else 'No'}")
        st.write("---")