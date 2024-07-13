import streamlit as st
import pickle
import imaplib
import email
from email.header import decode_header
import chardet

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

def decode_text(text):
    try:
        # Attempt to decode using utf-8
        return text.decode('utf-8')
    except (UnicodeDecodeError, AttributeError):
        # If decoding fails, use chardet to detect encoding
        detected_encoding = chardet.detect(text)['encoding']
        if detected_encoding:
            return text.decode(detected_encoding)
        return text



# Your Zoho Mail credentials
username = st.text_input("Email", "dannywalex@zohomail.com")
password = st.text_input("Password", "$Sthelen69", type="password")

if st.button("Fetch Emails"):
    if username and password:
        try:
            # Connect to the server
            mail = imaplib.IMAP4_SSL("imap.zoho.com")

            # Login to your account
            mail.login(username, password)

            # Select the mailbox you want to use
            mail.select("inbox")

            # Search for all emails in the mailbox
            status, messages = mail.search(None, "ALL")
            mail_ids = messages[0].split()

            emails = []
            for mail_id in mail_ids:
                # Fetch the email by ID
                status, msg_data = mail.fetch(mail_id, "(RFC822)")

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        # Parse the email content
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = decode_text(subject)
                            email_details = {"subject": subject, "body": ""}

                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                if "attachment" not in content_disposition:
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        body = decode_text(payload)
                                        email_details["body"] += body
                                else:
                                    payload = msg.get_payload(decode=True)
                                    if payload:
                                        body = decode_text(payload)
                                        email_details["body"] = body
                                emails.append(email_details)

            mail.logout()

            for email in emails:
                st.write(f"Subject: {email['subject']}")
                st.write(f"Body: {email.get('body', 'No body content')}")
                st.write("---")

        except Exception as e:
            st.error(f"Failed to fetch emails: {e}")
    else:
        st.warning("Please enter your email and password.")


