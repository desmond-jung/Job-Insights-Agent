from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from functions.database import get_all_jobs
import os
import pickle


# First define scope for gmail api

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Get Gmail API Service"""
    creds = None
    # token.pickle stores the user's access abd refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # if no valid credentials available, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject ,message_text):
    """Create a message for an email"""
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_email(recipient_email):
    """Send job search results via email"""
    try:
        # get gmail service
        service = get_gmail_service()

        jobs = get_all_jobs()
        email_content = "Job Search Results:\n\n"
        for job in jobs:
            email_content += f"""
            Job Tit;e: {job['title']}
            Company: {job['company_name']}
            Location: {job['location']}
            Description: {job['description']}
            Seniority Level: {job.get('seniority_level', 'N/A')}
            Employment Type: {job.get('employment_type', 'N/A')}
            Years of Experience: {job.get('yoe', 'N/A')}
            Education: {job.get('education', 'N/A')}
            {'='*50}
            """

        # create and send message
        message = create_message(
            'me',
            recipient_email,
            'Your Job Search Results',
            email_content
        )

        sent_message = service.users().messages().send(
            userId = 'me', body=message
        ).execute()

        return f"Message Id: {sent_message['id']}"
    
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise


