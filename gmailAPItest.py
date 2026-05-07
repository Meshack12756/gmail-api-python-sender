from email.mime.text import MIMEText
import base64

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

import os
import pickle

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_authenticate():
    creds = None

    # Load saved login token
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Login if no valid credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)

    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    return {'raw': raw_message}

def send_message(service, user_id, message):
    sent_message = service.users().messages().send(
        userId=user_id,
        body=message
    ).execute()

    print("Message sent!")
    print("Message ID:", sent_message['id'])

# Authenticate
service = gmail_authenticate()

# Email details
sender = "me"
to = "meshackmcquin@gmail.com"

subject = "Hello from Meshack Company."
message_text = "This is a simple email sent using Python and Gmail API. Thank you for always choosing us."

# Create and send
message = create_message(sender, to, subject, message_text)
send_message(service, "me", message)