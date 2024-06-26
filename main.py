import base64
import os
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from email_classifier import EmailClassifier

SCOPES = ['https://mail.google.com/']


def authenticate_gmail_api():
    """Authenticate the Gmail API and return the service."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


def fetch_emails(service, query=''):
    """Fetch emails within a specific timeframe."""
    date_threshold = (datetime.now() - timedelta(days=90)).strftime('%Y/%m/%d')
    query += f' before:{date_threshold}'
    try:
        response = service.users().messages().list(userId='me', q=query).execute()
        messages = response.get('messages', [])
        return messages
    except Exception as e:
        print(f'An error occurred while fetching emails: {e}')
        return []


def get_email_details(service, email_id):
    """Get the details of an email including sender, subject, and body."""
    try:
        email = service.users().messages().get(userId='me', id=email_id, format='full').execute()
        headers = email['payload']['headers']
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        sender = next(header['value'] for header in headers if header['name'] == 'From')
        body = get_email_body(email['payload'])
        return {
            'id': email_id,
            'sender': sender,
            'subject': subject,
            'body': body
        }
    except Exception as e:
        print(f'An error occurred while fetching email details: {e}')
        return {}


def get_email_body(payload):
    """Get the body of the email."""
    if 'parts' in payload:
        parts = payload['parts']
        for part in parts:
            if part['mimeType'] == 'text/plain':
                body = part['body']['data']
                return base64.urlsafe_b64decode(body).decode('utf-8')
    else:
        body = payload['body']['data']
        return base64.urlsafe_b64decode(body).decode('utf-8')
    return ''


def delete_emails(service, email_id):
    """Delete email."""
    try:
        service.users().messages().delete(userId='me', id=email_id).execute()
        print(f'Email with ID {email_id} deleted successfully.')
    except Exception as e:
        print(f'An error occurred while deleting email {email_id}: {e}')


def main():
    service = authenticate_gmail_api()
    if service:
        emails = fetch_emails(service)
        if emails:
            for email in emails:
                email_id = email['id']
                email_details = get_email_details(service, email_id)
                print("Running email classifier...")
                classifier = EmailClassifier()
                classification, reason = classifier.classify_email(email_details)
                print({"classification": classification, "reason": reason, "subject": email_details['subject']})
                # if classification == 'unimportant':
                #     delete_emails(service, email_id)
                #     print(f"Email with ID {email_id}, subject {email_details['subject']} is not important and has been "
                #           f"deleted.")
                # else:
                #     print(f"Email with ID {email_id} is important and will not be deleted.")


if __name__ == '__main__':
    main()
