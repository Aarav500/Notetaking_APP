"""
Oracle Email Delivery module for AI Note System.
Handles sending emails for password reset, reminders, and updates.
"""

import os
import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import oci
from oci.config import from_file
from oci.email import EmailClient
from oci.email.models import SendEmailDetails, EmailContent, Body, Message

# Setup logging
logger = logging.getLogger("ai_note_system.outputs.oracle_email_delivery")

class OracleEmailDelivery:
    """
    Oracle Email Delivery manager class for AI Note System.
    Handles sending emails for password reset, reminders, and updates.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the OracleEmailDelivery.
        
        Args:
            config_path (Optional[str]): Path to OCI config file. If None, uses environment variables.
        """
        self.sender = os.environ.get('EMAIL_SENDER')
        self.endpoint = os.environ.get('EMAIL_DELIVERY_ENDPOINT')
        self.compartment_id = os.environ.get('OCI_COMPARTMENT_ID')
        
        # Initialize OCI client
        try:
            if config_path:
                # Use config file if provided
                self.config = from_file(config_path)
                self.client = EmailClient(self.config)
            else:
                # Use instance principal authentication (for OCI compute instances)
                signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
                self.client = EmailClient(config={}, signer=signer)
                
            logger.debug(f"Connected to Oracle Email Delivery: {self.endpoint}")
        except Exception as e:
            logger.error(f"Error connecting to Oracle Email Delivery: {e}")
            raise
    
    def send_email(self, recipient: str, subject: str, body_text: str, body_html: Optional[str] = None) -> bool:
        """
        Send an email using Oracle Email Delivery.
        
        Args:
            recipient (str): Email address of the recipient
            subject (str): Email subject
            body_text (str): Plain text email body
            body_html (Optional[str]): HTML email body
            
        Returns:
            bool: True if successful
        """
        try:
            # Create email content
            body = Body(
                text=body_text,
                html=body_html if body_html else None
            )
            
            content = EmailContent(
                subject=subject,
                body=body
            )
            
            message = Message(
                subject=subject,
                body_text=body_text,
                body_html=body_html if body_html else None,
                from_address=self.sender,
                to_addresses=[recipient]
            )
            
            send_email_details = SendEmailDetails(
                compartment_id=self.compartment_id,
                content=content,
                sender_id=self.sender,
                recipients=[recipient]
            )
            
            # Send email
            response = self.client.send_email(
                send_email_details=send_email_details
            )
            
            logger.info(f"Sent email to {recipient}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_password_reset(self, recipient: str, reset_token: str, reset_url: str) -> bool:
        """
        Send a password reset email.
        
        Args:
            recipient (str): Email address of the recipient
            reset_token (str): Password reset token
            reset_url (str): URL for password reset
            
        Returns:
            bool: True if successful
        """
        subject = "Password Reset Request - AI Note System"
        
        body_text = f"""
Hello,

You have requested to reset your password for the AI Note System.

Please click the link below to reset your password:
{reset_url}?token={reset_token}

This link will expire in 24 hours.

If you did not request a password reset, please ignore this email.

Best regards,
AI Note System Team
"""
        
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4a86e8; color: white; padding: 10px; text-align: center; }}
        .content {{ padding: 20px; }}
        .button {{ display: inline-block; background-color: #4a86e8; color: white; padding: 10px 20px; 
                  text-decoration: none; border-radius: 4px; margin: 20px 0; }}
        .footer {{ font-size: 12px; color: #777; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Password Reset Request</h2>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>You have requested to reset your password for the AI Note System.</p>
            <p>Please click the button below to reset your password:</p>
            <p><a href="{reset_url}?token={reset_token}" class="button">Reset Password</a></p>
            <p>Or copy and paste this URL into your browser:</p>
            <p>{reset_url}?token={reset_token}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you did not request a password reset, please ignore this email.</p>
            <p>Best regards,<br>AI Note System Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message, please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(recipient, subject, body_text, body_html)
    
    def send_reminder(self, recipient: str, reminder_data: Dict[str, Any]) -> bool:
        """
        Send a reminder email.
        
        Args:
            recipient (str): Email address of the recipient
            reminder_data (Dict[str, Any]): Reminder data including title, description, due_date
            
        Returns:
            bool: True if successful
        """
        title = reminder_data.get("title", "Study Reminder")
        description = reminder_data.get("description", "")
        due_date = reminder_data.get("due_date", "")
        
        subject = f"Reminder: {title} - AI Note System"
        
        body_text = f"""
Hello,

This is a reminder for: {title}

Description: {description}
Due Date: {due_date}

Log in to your AI Note System account to view more details.

Best regards,
AI Note System Team
"""
        
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4a86e8; color: white; padding: 10px; text-align: center; }}
        .content {{ padding: 20px; }}
        .reminder {{ background-color: #f5f5f5; padding: 15px; border-left: 4px solid #4a86e8; margin: 20px 0; }}
        .button {{ display: inline-block; background-color: #4a86e8; color: white; padding: 10px 20px; 
                  text-decoration: none; border-radius: 4px; margin: 20px 0; }}
        .footer {{ font-size: 12px; color: #777; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Study Reminder</h2>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>This is a reminder for:</p>
            <div class="reminder">
                <h3>{title}</h3>
                <p><strong>Description:</strong> {description}</p>
                <p><strong>Due Date:</strong> {due_date}</p>
            </div>
            <p>Log in to your AI Note System account to view more details.</p>
            <p>Best regards,<br>AI Note System Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message, please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(recipient, subject, body_text, body_html)
    
    def send_update_notification(self, recipient: str, update_data: Dict[str, Any]) -> bool:
        """
        Send an update notification email.
        
        Args:
            recipient (str): Email address of the recipient
            update_data (Dict[str, Any]): Update data including title, description, changes
            
        Returns:
            bool: True if successful
        """
        title = update_data.get("title", "System Update")
        description = update_data.get("description", "")
        changes = update_data.get("changes", [])
        
        subject = f"Update Notification: {title} - AI Note System"
        
        changes_text = "\n".join([f"- {change}" for change in changes])
        
        body_text = f"""
Hello,

We have an important update for the AI Note System:

{title}

Description: {description}

Changes:
{changes_text}

Log in to your AI Note System account to explore the new features.

Best regards,
AI Note System Team
"""
        
        changes_html = "".join([f"<li>{change}</li>" for change in changes])
        
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4a86e8; color: white; padding: 10px; text-align: center; }}
        .content {{ padding: 20px; }}
        .update {{ background-color: #f5f5f5; padding: 15px; border-left: 4px solid #4a86e8; margin: 20px 0; }}
        .button {{ display: inline-block; background-color: #4a86e8; color: white; padding: 10px 20px; 
                  text-decoration: none; border-radius: 4px; margin: 20px 0; }}
        .footer {{ font-size: 12px; color: #777; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>System Update</h2>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>We have an important update for the AI Note System:</p>
            <div class="update">
                <h3>{title}</h3>
                <p><strong>Description:</strong> {description}</p>
                <p><strong>Changes:</strong></p>
                <ul>
                    {changes_html}
                </ul>
            </div>
            <p>Log in to your AI Note System account to explore the new features.</p>
            <p>Best regards,<br>AI Note System Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message, please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(recipient, subject, body_text, body_html)

def init_email_delivery(config_path: Optional[str] = None) -> OracleEmailDelivery:
    """
    Initialize the Oracle Email Delivery client.
    
    Args:
        config_path (Optional[str]): Path to OCI config file. If None, uses environment variables.
        
    Returns:
        OracleEmailDelivery: Initialized Oracle Email Delivery client
    """
    logger.info("Initializing Oracle Email Delivery client")
    
    try:
        email_client = OracleEmailDelivery(config_path)
        logger.info("Oracle Email Delivery client initialized successfully")
        return email_client
        
    except Exception as e:
        logger.error(f"Error initializing Oracle Email Delivery client: {e}")
        raise