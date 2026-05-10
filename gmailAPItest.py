import base64
import random
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

import os
import pickle

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def gmail_authenticate():
    creds = None

    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.pkl", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)

    message["to"] = to
    message["from"] = sender
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    return {"raw": raw_message}


def send_message(service, user_id, message):
    sent_message = service.users().messages().send(
        userId=user_id,
        body=message
    ).execute()

    return sent_message


# Generate random 5-digit verification code
verification_code = random.randint(10000, 99999)

# Recipient email
recipient = input("Enter recipient email: ")

# Email body
body = f"""
Your verification code is:

{verification_code}

Enter this code in the terminal to verify.
"""

# Authenticate Gmail API
service = gmail_authenticate()

# Create email
message = create_message(
    "me",
    recipient,
    "Email Verification Code",
    body
)

# Send email
send_message(service, "me", message)

print("Verification code sent!")

# Ask user to input code
user_code = input("Enter the verification code: ")

# Verify
if user_code == str(verification_code):
    print("Verification successful!")
else:
    print("Invalid verification code.")