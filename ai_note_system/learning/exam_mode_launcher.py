"""
Exam Mode Launcher module for AI Note System.
Provides functionality to create a distraction-free environment for focused study and exams.
"""

import os
import sys
import logging
import subprocess
import time
import json
import platform
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import threading

# Setup logging
logger = logging.getLogger("ai_note_system.learning.exam_mode_launcher")

class ExamModeLauncher:
    """
    Exam Mode Launcher class for creating a distraction-free environment.
    Handles closing applications, blocking websites, and enforcing focus periods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Exam Mode Launcher.
        
        Args:
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.config = config or {}
        self.os_type = platform.system().lower()  # 'windows', 'darwin' (macOS), or 'linux'
        self.active = False
        self.start_time = None
        self.end_time = None
        self.timer_thread = None
        self.break_times = []
        self.blocked_apps = self.config.get("blocked_apps", [])
        self.blocked_sites = self.config.get("blocked_sites", [])
        self.allowed_apps = self.config.get("allowed_apps", [])
        
        logger.debug(f"Initialized ExamModeLauncher for {self.os_type}")
    
    def start_exam_mode(self, duration_minutes: int, 
                       close_apps: bool = True, 
                       block_sites: bool = True,
                       break_policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start exam mode for the specified duration.
        
        Args:
            duration_minutes (int): Duration of exam mode in minutes
            close_apps (bool): Whether to close distracting applications
            block_sites (bool): Whether to block distracting websites
            break_policy (Dict[str, Any], optional): Break policy configuration
                Example: {"interval_minutes": 25, "break_duration_minutes": 5}
        
        Returns:
            Dict[str, Any]: Result of starting exam mode
        """
        if self.active:
            logger.warning("Exam mode is already active")
            return {"success": False, "message": "Exam mode is already active"}
        
        logger.info(f"Starting exam mode for {duration_minutes} minutes")
        
        self.active = True
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=duration_minutes)
        
        # Set up break times if break policy is provided
        if break_policy:
            self._setup_break_times(duration_minutes, break_policy)
        
        result = {"success": True, "actions": []}
        
        # Close distracting applications
        if close_apps:
            closed_apps = self._close_applications()
            result["actions"].append(f"Closed {len(closed_apps)} applications")
            result["closed_apps"] = closed_apps
        
        # Block distracting websites
        if block_sites:
            blocked_sites = self._block_websites()
            result["actions"].append(f"Blocked {len(blocked_sites)} websites")
            result["blocked_sites"] = blocked_sites
        
        # Start timer thread
        self._start_timer_thread(duration_minutes)
        
        result["start_time"] = self.start_time.isoformat()
        result["end_time"] = self.end_time.isoformat()
        result["duration_minutes"] = duration_minutes
        
        if break_policy:
            result["break_times"] = [bt.isoformat() for bt in self.break_times]
        
        logger.info(f"Exam mode started: {result}")
        return result
    
    def stop_exam_mode(self) -> Dict[str, Any]:
        """
        Stop exam mode and restore normal environment.
        
        Returns:
            Dict[str, Any]: Result of stopping exam mode
        """
        if not self.active:
            logger.warning("Exam mode is not active")
            return {"success": False, "message": "Exam mode is not active"}
        
        logger.info("Stopping exam mode")
        
        self.active = False
        end_time = datetime.now()
        
        # Stop timer thread
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(1)  # Wait for thread to finish
        
        # Unblock websites
        unblocked_sites = self._unblock_websites()
        
        result = {
            "success": True,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": end_time.isoformat(),
            "duration_minutes": (end_time - self.start_time).total_seconds() / 60 if self.start_time else 0,
            "actions": [f"Unblocked {len(unblocked_sites)} websites"],
            "unblocked_sites": unblocked_sites
        }
        
        # Reset state
        self.start_time = None
        self.end_time = None
        self.break_times = []
        
        logger.info(f"Exam mode stopped: {result}")
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of exam mode.
        
        Returns:
            Dict[str, Any]: Current status
        """
        if not self.active:
            return {"active": False}
        
        now = datetime.now()
        remaining_seconds = (self.end_time - now).total_seconds() if self.end_time else 0
        
        # Find next break if any
        next_break = None
        for break_time in self.break_times:
            if break_time > now:
                next_break = break_time
                break
        
        return {
            "active": self.active,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "elapsed_minutes": (now - self.start_time).total_seconds() / 60 if self.start_time else 0,
            "remaining_minutes": remaining_seconds / 60,
            "next_break": next_break.isoformat() if next_break else None,
            "blocked_apps": self.blocked_apps,
            "blocked_sites": self.blocked_sites
        }
    
    def _setup_break_times(self, duration_minutes: int, break_policy: Dict[str, Any]) -> None:
        """
        Set up break times based on the break policy.
        
        Args:
            duration_minutes (int): Total duration in minutes
            break_policy (Dict[str, Any]): Break policy configuration
        """
        interval_minutes = break_policy.get("interval_minutes", 25)
        
        if interval_minutes <= 0:
            logger.warning("Invalid break interval, no breaks will be scheduled")
            return
        
        # Calculate break times
        current_time = self.start_time
        while (current_time - self.start_time).total_seconds() / 60 < duration_minutes:
            current_time += timedelta(minutes=interval_minutes)
            if (current_time - self.start_time).total_seconds() / 60 < duration_minutes:
                self.break_times.append(current_time)
        
        logger.debug(f"Scheduled {len(self.break_times)} breaks")
    
    def _start_timer_thread(self, duration_minutes: int) -> None:
        """
        Start a timer thread to handle exam mode duration and breaks.
        
        Args:
            duration_minutes (int): Duration in minutes
        """
        def timer_func():
            logger.debug("Timer thread started")
            
            end_time = self.start_time + timedelta(minutes=duration_minutes)
            
            while self.active and datetime.now() < end_time:
                now = datetime.now()
                
                # Check for breaks
                for break_time in self.break_times[:]:
                    if now >= break_time:
                        self._handle_break(break_time)
                        self.break_times.remove(break_time)
                
                # Sleep for a bit to avoid high CPU usage
                time.sleep(1)
            
            # Auto-stop when time is up
            if self.active and datetime.now() >= end_time:
                logger.info("Exam mode duration completed, auto-stopping")
                self.stop_exam_mode()
        
        self.timer_thread = threading.Thread(target=timer_func)
        self.timer_thread.daemon = True
        self.timer_thread.start()
    
    def _handle_break(self, break_time: datetime) -> None:
        """
        Handle a scheduled break.
        
        Args:
            break_time (datetime): The break time
        """
        logger.info(f"Break time at {break_time.isoformat()}")
        
        # Notify user about the break
        self._show_notification("Break Time", "Time to take a short break!")
    
    def _close_applications(self) -> List[str]:
        """
        Close distracting applications based on the OS.
        
        Returns:
            List[str]: List of closed applications
        """
        closed_apps = []
        
        if not self.blocked_apps:
            logger.warning("No applications specified to close")
            return closed_apps
        
        logger.info(f"Closing applications: {self.blocked_apps}")
        
        try:
            if self.os_type == "windows":
                closed_apps = self._close_applications_windows()
            elif self.os_type == "darwin":
                closed_apps = self._close_applications_macos()
            elif self.os_type == "linux":
                closed_apps = self._close_applications_linux()
            else:
                logger.warning(f"Unsupported OS: {self.os_type}")
        except Exception as e:
            logger.error(f"Error closing applications: {str(e)}")
        
        return closed_apps
    
    def _close_applications_windows(self) -> List[str]:
        """
        Close applications on Windows using PowerShell.
        
        Returns:
            List[str]: List of closed applications
        """
        closed_apps = []
        
        for app in self.blocked_apps:
            try:
                # Get process IDs for the application
                cmd = f'Get-Process -Name "{app}" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'
                result = subprocess.run(["powershell", "-Command", cmd], 
                                       capture_output=True, text=True, check=False)
                
                if result.stdout.strip():
                    # Process exists, try to close it
                    process_ids = result.stdout.strip().split('\n')
                    for pid in process_ids:
                        if pid.strip():
                            kill_cmd = f'Stop-Process -Id {pid.strip()} -Force'
                            subprocess.run(["powershell", "-Command", kill_cmd], 
                                          capture_output=True, check=False)
                    
                    closed_apps.append(app)
                    logger.debug(f"Closed application: {app}")
            except Exception as e:
                logger.error(f"Error closing {app} on Windows: {str(e)}")
        
        return closed_apps
    
    def _close_applications_macos(self) -> List[str]:
        """
        Close applications on macOS using AppleScript.
        
        Returns:
            List[str]: List of closed applications
        """
        closed_apps = []
        
        for app in self.blocked_apps:
            try:
                # Check if the application is running
                check_cmd = f'osascript -e \'tell application "System Events" to count (every process whose name is "{app}")\''
                result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, check=False)
                
                if result.stdout.strip() != "0":
                    # Application is running, try to close it
                    close_cmd = f'osascript -e \'tell application "{app}" to quit\''
                    subprocess.run(close_cmd, shell=True, capture_output=True, check=False)
                    
                    closed_apps.append(app)
                    logger.debug(f"Closed application: {app}")
            except Exception as e:
                logger.error(f"Error closing {app} on macOS: {str(e)}")
        
        return closed_apps
    
    def _close_applications_linux(self) -> List[str]:
        """
        Close applications on Linux using killall.
        
        Returns:
            List[str]: List of closed applications
        """
        closed_apps = []
        
        for app in self.blocked_apps:
            try:
                # Check if the application is running
                check_cmd = f"pgrep -i {app}"
                result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, check=False)
                
                if result.stdout.strip():
                    # Application is running, try to close it
                    close_cmd = f"killall {app}"
                    subprocess.run(close_cmd, shell=True, capture_output=True, check=False)
                    
                    closed_apps.append(app)
                    logger.debug(f"Closed application: {app}")
            except Exception as e:
                logger.error(f"Error closing {app} on Linux: {str(e)}")
        
        return closed_apps
    
    def _block_websites(self) -> List[str]:
        """
        Block distracting websites by modifying the hosts file.
        
        Returns:
            List[str]: List of blocked websites
        """
        blocked_sites = []
        
        if not self.blocked_sites:
            logger.warning("No websites specified to block")
            return blocked_sites
        
        logger.info(f"Blocking websites: {self.blocked_sites}")
        
        try:
            # Determine hosts file location based on OS
            hosts_path = self._get_hosts_file_path()
            
            if not hosts_path or not os.path.exists(hosts_path):
                logger.error(f"Hosts file not found at {hosts_path}")
                return blocked_sites
            
            # Read current hosts file
            with open(hosts_path, 'r') as f:
                hosts_content = f.read()
            
            # Add marker for our blocks
            marker_start = "# BEGIN AI NOTE SYSTEM EXAM MODE BLOCKS"
            marker_end = "# END AI NOTE SYSTEM EXAM MODE BLOCKS"
            
            # Remove any existing blocks
            if marker_start in hosts_content and marker_end in hosts_content:
                start_idx = hosts_content.find(marker_start)
                end_idx = hosts_content.find(marker_end) + len(marker_end)
                hosts_content = hosts_content[:start_idx] + hosts_content[end_idx:]
            
            # Add new blocks
            block_entries = [f"127.0.0.1 {site}" for site in self.blocked_sites]
            block_entries.extend([f"127.0.0.1 www.{site}" for site in self.blocked_sites])
            
            new_block = f"\n{marker_start}\n"
            new_block += "\n".join(block_entries)
            new_block += f"\n{marker_end}\n"
            
            # Write updated hosts file
            with open(hosts_path, 'w') as f:
                f.write(hosts_content + new_block)
            
            blocked_sites = self.blocked_sites
            logger.debug(f"Blocked websites: {blocked_sites}")
            
            # Flush DNS cache
            self._flush_dns_cache()
            
        except Exception as e:
            logger.error(f"Error blocking websites: {str(e)}")
        
        return blocked_sites
    
    def _unblock_websites(self) -> List[str]:
        """
        Unblock websites by removing entries from the hosts file.
        
        Returns:
            List[str]: List of unblocked websites
        """
        unblocked_sites = []
        
        logger.info("Unblocking websites")
        
        try:
            # Determine hosts file location based on OS
            hosts_path = self._get_hosts_file_path()
            
            if not hosts_path or not os.path.exists(hosts_path):
                logger.error(f"Hosts file not found at {hosts_path}")
                return unblocked_sites
            
            # Read current hosts file
            with open(hosts_path, 'r') as f:
                hosts_content = f.read()
            
            # Remove our blocks
            marker_start = "# BEGIN AI NOTE SYSTEM EXAM MODE BLOCKS"
            marker_end = "# END AI NOTE SYSTEM EXAM MODE BLOCKS"
            
            if marker_start in hosts_content and marker_end in hosts_content:
                start_idx = hosts_content.find(marker_start)
                end_idx = hosts_content.find(marker_end) + len(marker_end)
                hosts_content = hosts_content[:start_idx] + hosts_content[end_idx:]
                
                # Write updated hosts file
                with open(hosts_path, 'w') as f:
                    f.write(hosts_content)
                
                unblocked_sites = self.blocked_sites
                logger.debug(f"Unblocked websites: {unblocked_sites}")
                
                # Flush DNS cache
                self._flush_dns_cache()
            
        except Exception as e:
            logger.error(f"Error unblocking websites: {str(e)}")
        
        return unblocked_sites
    
    def _get_hosts_file_path(self) -> str:
        """
        Get the path to the hosts file based on the OS.
        
        Returns:
            str: Path to the hosts file
        """
        if self.os_type == "windows":
            return r"C:\Windows\System32\drivers\etc\hosts"
        elif self.os_type in ["darwin", "linux"]:
            return "/etc/hosts"
        else:
            logger.error(f"Unsupported OS for hosts file: {self.os_type}")
            return ""
    
    def _flush_dns_cache(self) -> None:
        """
        Flush the DNS cache based on the OS.
        """
        try:
            if self.os_type == "windows":
                subprocess.run(["ipconfig", "/flushdns"], capture_output=True, check=False)
            elif self.os_type == "darwin":
                subprocess.run(["dscacheutil", "-flushcache"], capture_output=True, check=False)
                subprocess.run(["killall", "-HUP", "mDNSResponder"], capture_output=True, check=False)
            elif self.os_type == "linux":
                # Different Linux distributions have different ways to flush DNS
                subprocess.run(["systemd-resolve", "--flush-caches"], capture_output=True, check=False)
            
            logger.debug("Flushed DNS cache")
        except Exception as e:
            logger.error(f"Error flushing DNS cache: {str(e)}")
    
    def _show_notification(self, title: str, message: str) -> None:
        """
        Show a desktop notification based on the OS.
        
        Args:
            title (str): Notification title
            message (str): Notification message
        """
        try:
            if self.os_type == "windows":
                # Use PowerShell for Windows notifications
                ps_script = f'''
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

                $app_id = "AI Note System"
                $template = [Windows.UI.Notifications.ToastTemplateType]::ToastText02
                $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent($template)
                $text_nodes = $xml.GetElementsByTagName("text")
                $text_nodes[0].AppendChild($xml.CreateTextNode("{title}"))
                $text_nodes[1].AppendChild($xml.CreateTextNode("{message}"))
                $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app_id).Show($toast)
                '''
                subprocess.run(["powershell", "-Command", ps_script], capture_output=True, check=False)
            
            elif self.os_type == "darwin":
                # Use AppleScript for macOS notifications
                apple_script = f'display notification "{message}" with title "{title}"'
                subprocess.run(["osascript", "-e", apple_script], capture_output=True, check=False)
            
            elif self.os_type == "linux":
                # Use notify-send for Linux notifications
                subprocess.run(["notify-send", title, message], capture_output=True, check=False)
            
            logger.debug(f"Showed notification: {title} - {message}")
        except Exception as e:
            logger.error(f"Error showing notification: {str(e)}")

# Command-line interface
def main():
    """
    Command-line interface for the Exam Mode Launcher.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Exam Mode Launcher")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start exam mode")
    start_parser.add_argument("--duration", type=int, default=60, help="Duration in minutes")
    start_parser.add_argument("--no-close-apps", action="store_true", help="Don't close applications")
    start_parser.add_argument("--no-block-sites", action="store_true", help="Don't block websites")
    start_parser.add_argument("--break-interval", type=int, default=25, help="Break interval in minutes")
    start_parser.add_argument("--break-duration", type=int, default=5, help="Break duration in minutes")
    start_parser.add_argument("--blocked-apps", nargs="+", help="List of applications to block")
    start_parser.add_argument("--blocked-sites", nargs="+", help="List of websites to block")
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop exam mode")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get exam mode status")
    
    args = parser.parse_args()
    
    # Create config from arguments
    config = {}
    if args.command == "start":
        if args.blocked_apps:
            config["blocked_apps"] = args.blocked_apps
        if args.blocked_sites:
            config["blocked_sites"] = args.blocked_sites
    
    # Create launcher
    launcher = ExamModeLauncher(config)
    
    # Execute command
    if args.command == "start":
        break_policy = {
            "interval_minutes": args.break_interval,
            "break_duration_minutes": args.break_duration
        }
        
        result = launcher.start_exam_mode(
            duration_minutes=args.duration,
            close_apps=not args.no_close_apps,
            block_sites=not args.no_block_sites,
            break_policy=break_policy
        )
        
        print(json.dumps(result, indent=2))
    
    elif args.command == "stop":
        result = launcher.stop_exam_mode()
        print(json.dumps(result, indent=2))
    
    elif args.command == "status":
        result = launcher.get_status()
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()