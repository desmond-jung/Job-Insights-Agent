import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import re

class EmailService:
    """Service for sending emails via Gmail"""
    
    def __init__(self):
        load_dotenv()
        self.gmail_user = os.getenv('GMAIL_USER')
        self.gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    
    def is_configured(self) -> bool:
        """Check if Gmail credentials are configured"""
        return bool(self.gmail_user and self.gmail_password)
    
    def validate_email(self, email: str) -> bool:
        """Basic email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def send_job_results_email(
        self, 
        recipient_email: str, 
        jobs: List[Dict], 
        subject: str = "Job Search Results"
    ) -> Dict[str, str]:
        """
        Send job search results via email
        
        Returns:
            Dict with 'success' (bool) and 'message' (str)
        """
        try:
            # Validate configuration
            if not self.is_configured():
                return {
                    'success': False,
                    'message': "❌ Gmail credentials not configured. Set GMAIL_USER and GMAIL_APP_PASSWORD in .env"
                }
            
            # Validate email
            if not self.validate_email(recipient_email):
                return {
                    'success': False,
                    'message': f"❌ Invalid email address: {recipient_email}"
                }
            
            # Validate jobs
            if not jobs:
                return {
                    'success': False,
                    'message': "❌ No jobs to send"
                }
            
            # Create email content
            from utils.email_templates import create_job_email_content
            html_content = create_job_email_content(jobs)
            
            # Send email
            success = self._send_gmail(recipient_email, subject, html_content)
            
            if success:
                return {
                    'success': True,
                    'message': f"✅ Successfully sent {len(jobs)} job results to {recipient_email}"
                }
            else:
                return {
                    'success': False,
                    'message': "❌ Failed to send email"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Error sending email: {str(e)}"
            }
    
    def _send_gmail(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """Send email using Gmail SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.gmail_user
            msg['To'] = recipient_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.gmail_user, self.gmail_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"❌ Gmail error: {str(e)}")
            return False

# Global instance
email_service = EmailService()
