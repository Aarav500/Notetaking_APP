"""
Reminder manager module for AI Note System.
Handles scheduling and sending reminders for spaced repetition reviews.
"""

import os
import logging
import json
import time
import threading
import schedule
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Setup logging
logger = logging.getLogger("ai_note_system.outputs.reminder_manager")

class ReminderManager:
    """
    Manager for scheduling and sending reminders.
    """
    
    def __init__(self, db_manager=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the reminder manager.
        
        Args:
            db_manager: Database manager instance
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.db_manager = db_manager
        self.config = config or {}
        self.scheduler_thread = None
        self.scheduler_running = False
        self.notification_handlers = {
            "email": self.send_email_notification,
            "desktop": self.send_desktop_notification,
            "slack": self.send_slack_notification,
            "discord": self.send_discord_notification
        }
    
    def schedule_reminder(
        self,
        item_id: str,
        item_type: str,
        reminder_time: Union[str, datetime],
        channels: List[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Schedule a reminder for an item.
        
        Args:
            item_id (str): ID of the item
            item_type (str): Type of item (note, question, etc.)
            reminder_time (Union[str, datetime]): Time to send the reminder
            channels (List[str]): Notification channels to use
            metadata (Dict[str, Any], optional): Additional metadata
            
        Returns:
            Dict[str, Any]: Reminder data
        """
        logger.info(f"Scheduling reminder for {item_type} {item_id}")
        
        # Convert reminder_time to datetime if it's a string
        if isinstance(reminder_time, str):
            try:
                reminder_time = datetime.fromisoformat(reminder_time)
            except ValueError:
                logger.error(f"Invalid reminder time format: {reminder_time}")
                return {"error": f"Invalid reminder time format: {reminder_time}"}
        
        # Use default channels if not provided
        if channels is None:
            channels = self.config.get("DEFAULT_REMINDER_CHANNELS", ["desktop"])
        
        # Create reminder data
        reminder_data = {
            "item_id": item_id,
            "item_type": item_type,
            "reminder_time": reminder_time.isoformat(),
            "channels": channels,
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        # Add metadata if provided
        if metadata:
            reminder_data["metadata"] = metadata
        
        # Save reminder data
        self.save_reminder(reminder_data)
        
        # Schedule the reminder if the scheduler is running
        if self.scheduler_running:
            self._schedule_single_reminder(reminder_data)
        
        return reminder_data
    
    def save_reminder(self, reminder_data: Dict[str, Any]) -> bool:
        """
        Save reminder data.
        
        Args:
            reminder_data (Dict[str, Any]): Reminder data
            
        Returns:
            bool: True if successful, False otherwise
        """
        # If database manager is available, use it
        if self.db_manager:
            return self.save_reminder_to_db(reminder_data)
        
        # Otherwise, use a simple file-based approach
        return self.save_reminder_to_file(reminder_data)
    
    def save_reminder_to_db(self, reminder_data: Dict[str, Any]) -> bool:
        """
        Save reminder data to the database.
        
        Args:
            reminder_data (Dict[str, Any]): Reminder data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # This is a placeholder for database integration
            # In a real implementation, this would update the database
            
            logger.debug(f"Reminder data saved to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving reminder data to database: {str(e)}")
            return False
    
    def save_reminder_to_file(self, reminder_data: Dict[str, Any]) -> bool:
        """
        Save reminder data to a file.
        
        Args:
            reminder_data (Dict[str, Any]): Reminder data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a file path for the reminder data
            file_path = self.get_reminder_data_path(reminder_data["item_id"], reminder_data["item_type"])
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save the data to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(reminder_data, f, indent=2)
            
            logger.debug(f"Reminder data saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving reminder data to file: {str(e)}")
            return False
    
    def get_reminder_data_path(self, item_id: str, item_type: str) -> str:
        """
        Get the file path for reminder data.
        
        Args:
            item_id (str): ID of the item
            item_type (str): Type of item (note, question, etc.)
            
        Returns:
            str: File path
        """
        # Get the path to the data directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(os.path.dirname(current_dir))
        data_dir = os.path.join(project_dir, "data", "reminders")
        
        # Create a file name based on item type and ID
        file_name = f"{item_type}_{item_id}.json"
        
        return os.path.join(data_dir, file_name)
    
    def get_reminders(
        self,
        item_id: Optional[str] = None,
        item_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get reminders based on filters.
        
        Args:
            item_id (str, optional): Filter by item ID
            item_type (str, optional): Filter by item type
            status (str, optional): Filter by status
            limit (int): Maximum number of reminders to return
            
        Returns:
            List[Dict[str, Any]]: List of reminders
        """
        # If database manager is available, use it
        if self.db_manager:
            return self.get_reminders_from_db(item_id, item_type, status, limit)
        
        # Otherwise, use a simple file-based approach
        return self.get_reminders_from_files(item_id, item_type, status, limit)
    
    def get_reminders_from_db(
        self,
        item_id: Optional[str] = None,
        item_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get reminders from the database.
        
        Args:
            item_id (str, optional): Filter by item ID
            item_type (str, optional): Filter by item type
            status (str, optional): Filter by status
            limit (int): Maximum number of reminders to return
            
        Returns:
            List[Dict[str, Any]]: List of reminders
        """
        try:
            # This is a placeholder for database integration
            # In a real implementation, this would query the database
            
            # For now, return an empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting reminders from database: {str(e)}")
            return []
    
    def get_reminders_from_files(
        self,
        item_id: Optional[str] = None,
        item_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get reminders from files.
        
        Args:
            item_id (str, optional): Filter by item ID
            item_type (str, optional): Filter by item type
            status (str, optional): Filter by status
            limit (int): Maximum number of reminders to return
            
        Returns:
            List[Dict[str, Any]]: List of reminders
        """
        try:
            # Get the path to the data directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(os.path.dirname(current_dir))
            data_dir = os.path.join(project_dir, "data", "reminders")
            
            # Ensure directory exists
            if not os.path.exists(data_dir):
                return []
            
            # Get all reminder data files
            files = os.listdir(data_dir)
            
            # Filter by item type if specified
            if item_type:
                files = [f for f in files if f.startswith(f"{item_type}_")]
            
            # Filter by item ID if specified
            if item_id:
                files = [f for f in files if f.endswith(f"_{item_id}.json")]
            
            # Load reminder data from each file
            reminders = []
            
            for file in files:
                file_path = os.path.join(data_dir, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Filter by status if specified
                    if status and data.get("status") != status:
                        continue
                    
                    reminders.append(data)
                    
                    # Stop if we've reached the limit
                    if len(reminders) >= limit:
                        break
                
                except Exception as e:
                    logger.error(f"Error loading reminder data from {file_path}: {str(e)}")
                    continue
            
            # Sort by reminder time
            reminders.sort(key=lambda x: x.get("reminder_time", "2099-12-31T00:00:00"))
            
            return reminders
            
        except Exception as e:
            logger.error(f"Error getting reminders from files: {str(e)}")
            return []
    
    def update_reminder_status(
        self,
        item_id: str,
        item_type: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update the status of a reminder.
        
        Args:
            item_id (str): ID of the item
            item_type (str): Type of item (note, question, etc.)
            status (str): New status
            metadata (Dict[str, Any], optional): Additional metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the reminder data
            reminders = self.get_reminders(item_id, item_type, limit=1)
            
            if not reminders:
                logger.warning(f"No reminder found for {item_type} {item_id}")
                return False
            
            reminder_data = reminders[0]
            
            # Update status
            reminder_data["status"] = status
            reminder_data["updated_at"] = datetime.now().isoformat()
            
            # Add metadata if provided
            if metadata:
                if "metadata" not in reminder_data:
                    reminder_data["metadata"] = {}
                reminder_data["metadata"].update(metadata)
            
            # Save updated reminder data
            return self.save_reminder(reminder_data)
            
        except Exception as e:
            logger.error(f"Error updating reminder status: {str(e)}")
            return False
    
    def start_scheduler(self) -> bool:
        """
        Start the scheduler for sending reminders.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.scheduler_running:
            logger.warning("Scheduler is already running")
            return True
        
        try:
            # Create a new thread for the scheduler
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_running = True
            self.scheduler_thread.start()
            
            logger.info("Reminder scheduler started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
            self.scheduler_running = False
            return False
    
    def stop_scheduler(self) -> bool:
        """
        Stop the scheduler for sending reminders.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.scheduler_running:
            logger.warning("Scheduler is not running")
            return True
        
        try:
            # Set the flag to stop the scheduler
            self.scheduler_running = False
            
            # Wait for the thread to finish
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            logger.info("Reminder scheduler stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
            return False
    
    def _run_scheduler(self) -> None:
        """
        Run the scheduler loop.
        """
        logger.info("Starting scheduler loop")
        
        # Schedule a job to check for due reminders every minute
        schedule.every(1).minutes.do(self._check_due_reminders)
        
        # Schedule existing reminders
        self._schedule_existing_reminders()
        
        # Run the scheduler loop
        while self.scheduler_running:
            schedule.run_pending()
            time.sleep(1)
        
        logger.info("Scheduler loop stopped")
    
    def _schedule_existing_reminders(self) -> None:
        """
        Schedule existing reminders.
        """
        # Get all scheduled reminders
        reminders = self.get_reminders(status="scheduled")
        
        # Schedule each reminder
        for reminder in reminders:
            self._schedule_single_reminder(reminder)
    
    def _schedule_single_reminder(self, reminder: Dict[str, Any]) -> None:
        """
        Schedule a single reminder.
        
        Args:
            reminder (Dict[str, Any]): Reminder data
        """
        try:
            # Get reminder time
            reminder_time = datetime.fromisoformat(reminder["reminder_time"])
            
            # Skip if the reminder time is in the past
            if reminder_time < datetime.now():
                logger.warning(f"Reminder time is in the past: {reminder_time}")
                return
            
            # Schedule the reminder
            schedule.every().day.at(reminder_time.strftime("%H:%M")).do(
                self._send_reminder,
                reminder=reminder
            ).tag(f"{reminder['item_type']}_{reminder['item_id']}")
            
            logger.debug(f"Scheduled reminder for {reminder['item_type']} {reminder['item_id']} at {reminder_time}")
            
        except Exception as e:
            logger.error(f"Error scheduling reminder: {str(e)}")
    
    def _check_due_reminders(self) -> None:
        """
        Check for due reminders and send them.
        """
        try:
            # Get current time
            now = datetime.now()
            
            # Get all scheduled reminders
            reminders = self.get_reminders(status="scheduled")
            
            # Check each reminder
            for reminder in reminders:
                try:
                    # Get reminder time
                    reminder_time = datetime.fromisoformat(reminder["reminder_time"])
                    
                    # Check if the reminder is due
                    if reminder_time <= now:
                        # Send the reminder
                        self._send_reminder(reminder)
                except Exception as e:
                    logger.error(f"Error checking reminder: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error checking due reminders: {str(e)}")
    
    def _send_reminder(self, reminder: Dict[str, Any]) -> None:
        """
        Send a reminder.
        
        Args:
            reminder (Dict[str, Any]): Reminder data
        """
        try:
            logger.info(f"Sending reminder for {reminder['item_type']} {reminder['item_id']}")
            
            # Get item details
            item_details = self._get_item_details(reminder["item_id"], reminder["item_type"])
            
            # Send notifications through each channel
            for channel in reminder["channels"]:
                if channel in self.notification_handlers:
                    try:
                        self.notification_handlers[channel](reminder, item_details)
                    except Exception as e:
                        logger.error(f"Error sending {channel} notification: {str(e)}")
            
            # Update reminder status
            self.update_reminder_status(
                reminder["item_id"],
                reminder["item_type"],
                "sent",
                {"sent_at": datetime.now().isoformat()}
            )
            
        except Exception as e:
            logger.error(f"Error sending reminder: {str(e)}")
    
    def _get_item_details(self, item_id: str, item_type: str) -> Dict[str, Any]:
        """
        Get details for an item.
        
        Args:
            item_id (str): ID of the item
            item_type (str): Type of item (note, question, etc.)
            
        Returns:
            Dict[str, Any]: Item details
        """
        # If database manager is available, use it
        if self.db_manager:
            try:
                # This is a placeholder for database integration
                # In a real implementation, this would query the database
                pass
            except Exception as e:
                logger.error(f"Error getting item details from database: {str(e)}")
        
        # Return a default item details dictionary
        return {
            "id": item_id,
            "type": item_type,
            "title": f"{item_type.capitalize()} {item_id}",
            "url": f"pansophy://review/{item_type}/{item_id}"
        }
    
    def send_email_notification(self, reminder: Dict[str, Any], item_details: Dict[str, Any]) -> bool:
        """
        Send an email notification.
        
        Args:
            reminder (Dict[str, Any]): Reminder data
            item_details (Dict[str, Any]): Item details
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get email configuration
            email_config = self.config.get("EMAIL", {})
            
            if not email_config:
                logger.warning("Email configuration not found")
                return False
            
            # Get required configuration
            smtp_server = email_config.get("SMTP_SERVER")
            smtp_port = email_config.get("SMTP_PORT", 587)
            smtp_username = email_config.get("SMTP_USERNAME")
            smtp_password = email_config.get("SMTP_PASSWORD")
            from_email = email_config.get("FROM_EMAIL")
            to_email = email_config.get("TO_EMAIL")
            
            if not all([smtp_server, smtp_username, smtp_password, from_email, to_email]):
                logger.warning("Incomplete email configuration")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg["From"] = from_email
            msg["To"] = to_email
            msg["Subject"] = f"Reminder: Review {item_details['title']}"
            
            # Create message body
            body = f"""
            <html>
            <body>
                <h2>Time to review: {item_details['title']}</h2>
                <p>This is a reminder to review your note.</p>
                <p><a href="{item_details['url']}">Click here to review</a></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, "html"))
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False
    
    def send_desktop_notification(self, reminder: Dict[str, Any], item_details: Dict[str, Any]) -> bool:
        """
        Send a desktop notification.
        
        Args:
            reminder (Dict[str, Any]): Reminder data
            item_details (Dict[str, Any]): Item details
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Try to import platform-specific notification libraries
            try:
                # For Windows
                import win10toast
                
                # Create toaster
                toaster = win10toast.ToastNotifier()
                
                # Show notification
                toaster.show_toast(
                    f"Review {item_details['title']}",
                    "Time to review your note.",
                    duration=10,
                    threaded=True
                )
                
                logger.info("Desktop notification sent (Windows)")
                return True
                
            except ImportError:
                try:
                    # For macOS
                    import pync
                    
                    # Show notification
                    pync.notify(
                        "Time to review your note.",
                        title=f"Review {item_details['title']}",
                        open=item_details['url']
                    )
                    
                    logger.info("Desktop notification sent (macOS)")
                    return True
                    
                except ImportError:
                    try:
                        # For Linux
                        import notify2
                        
                        # Initialize notify2
                        notify2.init("AI Note System")
                        
                        # Create notification
                        notification = notify2.Notification(
                            f"Review {item_details['title']}",
                            "Time to review your note."
                        )
                        
                        # Show notification
                        notification.show()
                        
                        logger.info("Desktop notification sent (Linux)")
                        return True
                        
                    except ImportError:
                        logger.warning("No desktop notification library found")
                        return False
            
        except Exception as e:
            logger.error(f"Error sending desktop notification: {str(e)}")
            return False
    
    def send_slack_notification(self, reminder: Dict[str, Any], item_details: Dict[str, Any]) -> bool:
        """
        Send a Slack notification.
        
        Args:
            reminder (Dict[str, Any]): Reminder data
            item_details (Dict[str, Any]): Item details
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get Slack configuration
            slack_config = self.config.get("SLACK", {})
            
            if not slack_config:
                logger.warning("Slack configuration not found")
                return False
            
            # Get webhook URL
            webhook_url = slack_config.get("WEBHOOK_URL")
            
            if not webhook_url:
                logger.warning("Slack webhook URL not found")
                return False
            
            # Import requests
            import requests
            
            # Create message payload
            payload = {
                "text": f"Time to review: {item_details['title']}",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Time to review: {item_details['title']}*"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "This is a reminder to review your note."
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Review Now"
                                },
                                "url": item_details['url']
                            }
                        ]
                    }
                ]
            }
            
            # Send the message
            response = requests.post(webhook_url, json=payload)
            
            # Check response
            if response.status_code == 200:
                logger.info("Slack notification sent")
                return True
            else:
                logger.warning(f"Error sending Slack notification: {response.status_code} {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
            return False
    
    def send_discord_notification(self, reminder: Dict[str, Any], item_details: Dict[str, Any]) -> bool:
        """
        Send a Discord notification.
        
        Args:
            reminder (Dict[str, Any]): Reminder data
            item_details (Dict[str, Any]): Item details
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get Discord configuration
            discord_config = self.config.get("DISCORD", {})
            
            if not discord_config:
                logger.warning("Discord configuration not found")
                return False
            
            # Get webhook URL
            webhook_url = discord_config.get("WEBHOOK_URL")
            
            if not webhook_url:
                logger.warning("Discord webhook URL not found")
                return False
            
            # Import requests
            import requests
            
            # Create message payload
            payload = {
                "content": f"Time to review: {item_details['title']}",
                "embeds": [
                    {
                        "title": f"Review {item_details['title']}",
                        "description": "This is a reminder to review your note.",
                        "color": 5814783,  # Blue color
                        "url": item_details['url']
                    }
                ]
            }
            
            # Send the message
            response = requests.post(webhook_url, json=payload)
            
            # Check response
            if response.status_code == 204:
                logger.info("Discord notification sent")
                return True
            else:
                logger.warning(f"Error sending Discord notification: {response.status_code} {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Error sending Discord notification: {str(e)}")
            return False


def schedule_reminder(
    item_id: str,
    item_type: str,
    reminder_time: Union[str, datetime],
    channels: List[str] = None,
    db_manager=None,
    config: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Schedule a reminder for an item.
    
    Args:
        item_id (str): ID of the item
        item_type (str): Type of item (note, question, etc.)
        reminder_time (Union[str, datetime]): Time to send the reminder
        channels (List[str]): Notification channels to use
        db_manager: Database manager instance
        config (Dict[str, Any], optional): Configuration dictionary
        metadata (Dict[str, Any], optional): Additional metadata
        
    Returns:
        Dict[str, Any]: Reminder data
    """
    reminder_manager = ReminderManager(db_manager, config)
    return reminder_manager.schedule_reminder(item_id, item_type, reminder_time, channels, metadata)

def get_reminders(
    item_id: Optional[str] = None,
    item_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db_manager=None,
    config: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Get reminders based on filters.
    
    Args:
        item_id (str, optional): Filter by item ID
        item_type (str, optional): Filter by item type
        status (str, optional): Filter by status
        limit (int): Maximum number of reminders to return
        db_manager: Database manager instance
        config (Dict[str, Any], optional): Configuration dictionary
        
    Returns:
        List[Dict[str, Any]]: List of reminders
    """
    reminder_manager = ReminderManager(db_manager, config)
    return reminder_manager.get_reminders(item_id, item_type, status, limit)

def start_reminder_scheduler(
    db_manager=None,
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Start the scheduler for sending reminders.
    
    Args:
        db_manager: Database manager instance
        config (Dict[str, Any], optional): Configuration dictionary
        
    Returns:
        bool: True if successful, False otherwise
    """
    reminder_manager = ReminderManager(db_manager, config)
    return reminder_manager.start_scheduler()

def stop_reminder_scheduler(
    db_manager=None,
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Stop the scheduler for sending reminders.
    
    Args:
        db_manager: Database manager instance
        config (Dict[str, Any], optional): Configuration dictionary
        
    Returns:
        bool: True if successful, False otherwise
    """
    reminder_manager = ReminderManager(db_manager, config)
    return reminder_manager.stop_scheduler()