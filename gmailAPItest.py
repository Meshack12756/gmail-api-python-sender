import base64
import json
import os
import secrets
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Constants ---
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"
MAX_ATTEMPTS = 3


def gmail_authenticate():
    """Authenticate with Gmail API and return the service object."""
    creds = None

    # Load saved credentials if they exist
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Refresh or re-authenticate if credentials are missing or invalid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials for future use (JSON, not pickle)
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def create_message(sender, to, subject, message_text):
    """Create a base64-encoded email message."""
    message = MIMEText(message_text)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    return {"raw": raw_message}


def send_message(service, user_id, message):
    """Send an email message via the Gmail API."""
    sent_message = service.users().messages().send(
        userId=user_id,
        body=message
    ).execute()

    return sent_message


def main():
    # Generate a cryptographically secure 5-digit verification code
    verification_code = secrets.randbelow(90000) + 10000

    # Get recipient email
    recipient = input("Enter recipient email: ").strip()
    if not recipient:
        print("No recipient email provided. Exiting.")
        return

    # Build the email body
    body = f"""
Your verification code is:

{verification_code}

Enter this code in the terminal to verify.
"""

    # Authenticate with Gmail API
    try:
        service = gmail_authenticate()
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    # Create and send the email
    message = create_message(
        "me",
        recipient,
        "Email Verification Code",
        body
    )

    try:
        result = send_message(service, "me", message)
        print(f"Verification code sent! (Message ID: {result.get('id')})")
    except HttpError as e:
        print(f"Failed to send email: {e}")
        return

    # Prompt user to enter the code, with a limited number of attempts
    for attempt in range(1, MAX_ATTEMPTS + 1):
        user_code = input("Enter the verification code: ").strip()

        if user_code == str(verification_code):
            print("Verification successful!")
            return

        remaining = MAX_ATTEMPTS - attempt
        if remaining > 0:
            print(f"Invalid code. {remaining} attempt(s) remaining.")
        else:
            print("Too many failed attempts. Verification failed.")


if __name__ == "__main__":
    main()