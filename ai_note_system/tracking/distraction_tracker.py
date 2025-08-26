"""
Distraction Tracking & Intervention module for AI Note System.
Detects distraction patterns and provides interventions.
"""

import os
import logging
import json
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import threading
import sqlite3

# Setup logging
logger = logging.getLogger("ai_note_system.tracking.distraction_tracker")

# Import database manager
from ..database.db_manager import DatabaseManager

class DistractionTracker:
    """
    Tracks distraction patterns and provides interventions.
    """
    
    def __init__(
        self,
        user_id: str,
        db_manager: Optional[DatabaseManager] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Distraction Tracker.
        
        Args:
            user_id (str): ID of the user
            db_manager (DatabaseManager, optional): Database manager instance
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.user_id = user_id
        self.db_manager = db_manager
        self.config = config or {}
        
        # Default configuration
        self.inactivity_threshold = self.config.get("inactivity_threshold", 180)  # seconds
        self.switch_threshold = self.config.get("switch_threshold", 5)  # switches per minute
        self.intervention_frequency = self.config.get("intervention_frequency", 15)  # minutes
        
        # Initialize tracking state
        self.tracking_active = False
        self.tracking_thread = None
        self.last_activity_time = time.time()
        self.current_app = None
        self.app_switches = []
        self.inactivity_periods = []
        self.interventions = []
        
        # Initialize database if needed
        if self.db_manager:
            self._init_database()
        
        logger.info(f"Initialized Distraction Tracker for user {user_id}")
    
    def _init_database(self):
        """
        Initialize database tables for distraction tracking.
        """
        try:
            # Create app_switches table
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_switches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                from_app TEXT,
                to_app TEXT,
                duration INTEGER
            )
            ''')
            
            # Create inactivity_periods table
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inactivity_periods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration INTEGER
            )
            ''')
            
            # Create interventions table
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT
            )
            ''')
            
            # Create distraction_reports table
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS distraction_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                report_data TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            ''')
            
            self.db_manager.conn.commit()
            logger.debug("Initialized distraction tracking database tables")
            
        except sqlite3.Error as e:
            logger.error(f"Error initializing database tables: {e}")
    
    def start_tracking(self):
        """
        Start tracking distractions.
        """
        if self.tracking_active:
            logger.warning("Distraction tracking is already active")
            return
        
        self.tracking_active = True
        self.last_activity_time = time.time()
        
        # Start tracking thread
        self.tracking_thread = threading.Thread(target=self._tracking_loop)
        self.tracking_thread.daemon = True
        self.tracking_thread.start()
        
        logger.info("Started distraction tracking")
    
    def stop_tracking(self):
        """
        Stop tracking distractions.
        """
        if not self.tracking_active:
            logger.warning("Distraction tracking is not active")
            return
        
        self.tracking_active = False
        
        # Wait for tracking thread to finish
        if self.tracking_thread:
            self.tracking_thread.join(timeout=1.0)
            self.tracking_thread = None
        
        logger.info("Stopped distraction tracking")
    
    def _tracking_loop(self):
        """
        Main tracking loop that runs in a separate thread.
        """
        last_intervention_time = time.time()
        
        while self.tracking_active:
            try:
                # Get current time
                current_time = time.time()
                
                # Check for inactivity
                if current_time - self.last_activity_time > self.inactivity_threshold:
                    self._handle_inactivity()
                
                # Check for frequent app switching
                if self._check_frequent_switching():
                    self._handle_frequent_switching()
                
                # Check if it's time for an intervention
                if current_time - last_intervention_time > self.intervention_frequency * 60:
                    self._provide_intervention()
                    last_intervention_time = current_time
                
                # Sleep for a short time
                time.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error in tracking loop: {e}")
                time.sleep(5.0)  # Sleep longer on error
    
    def record_activity(self, app_name: str):
        """
        Record user activity in an application.
        
        Args:
            app_name (str): Name of the current application
        """
        current_time = time.time()
        
        # Update last activity time
        self.last_activity_time = current_time
        
        # Check if app has changed
        if self.current_app and app_name != self.current_app:
            # Record app switch
            switch = {
                "timestamp": datetime.now().isoformat(),
                "from_app": self.current_app,
                "to_app": app_name,
                "duration": 0  # Will be updated on next switch
            }
            
            # Update duration of previous switch if available
            if self.app_switches:
                prev_switch = self.app_switches[-1]
                prev_time = datetime.fromisoformat(prev_switch["timestamp"])
                curr_time = datetime.fromisoformat(switch["timestamp"])
                duration = int((curr_time - prev_time).total_seconds())
                prev_switch["duration"] = duration
            
            self.app_switches.append(switch)
            
            # Save to database if available
            if self.db_manager:
                self._save_app_switch(switch)
        
        # Update current app
        self.current_app = app_name
    
    def _save_app_switch(self, switch: Dict[str, Any]):
        """
        Save app switch to database.
        
        Args:
            switch (Dict[str, Any]): App switch data
        """
        try:
            self.db_manager.cursor.execute('''
            INSERT INTO app_switches (
                user_id, timestamp, from_app, to_app, duration
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                self.user_id,
                switch["timestamp"],
                switch["from_app"],
                switch["to_app"],
                switch["duration"]
            ))
            
            self.db_manager.conn.commit()
            
        except sqlite3.Error as e:
            logger.error(f"Error saving app switch: {e}")
    
    def _handle_inactivity(self):
        """
        Handle detected inactivity.
        """
        current_time = datetime.now()
        last_activity_time = datetime.fromtimestamp(self.last_activity_time)
        
        # Create inactivity period
        inactivity = {
            "start_time": last_activity_time.isoformat(),
            "end_time": current_time.isoformat(),
            "duration": int((current_time - last_activity_time).total_seconds())
        }
        
        self.inactivity_periods.append(inactivity)
        
        # Save to database if available
        if self.db_manager:
            self._save_inactivity(inactivity)
        
        logger.debug(f"Detected inactivity period of {inactivity['duration']} seconds")
    
    def _save_inactivity(self, inactivity: Dict[str, Any]):
        """
        Save inactivity period to database.
        
        Args:
            inactivity (Dict[str, Any]): Inactivity period data
        """
        try:
            self.db_manager.cursor.execute('''
            INSERT INTO inactivity_periods (
                user_id, start_time, end_time, duration
            ) VALUES (?, ?, ?, ?)
            ''', (
                self.user_id,
                inactivity["start_time"],
                inactivity["end_time"],
                inactivity["duration"]
            ))
            
            self.db_manager.conn.commit()
            
        except sqlite3.Error as e:
            logger.error(f"Error saving inactivity period: {e}")
    
    def _check_frequent_switching(self) -> bool:
        """
        Check if there is frequent app switching.
        
        Returns:
            bool: True if frequent switching is detected, False otherwise
        """
        # Get switches in the last minute
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_switches = [
            switch for switch in self.app_switches
            if datetime.fromisoformat(switch["timestamp"]) > one_minute_ago
        ]
        
        # Check if number of switches exceeds threshold
        return len(recent_switches) >= self.switch_threshold
    
    def _handle_frequent_switching(self):
        """
        Handle detected frequent app switching.
        """
        # Provide an immediate intervention
        self._provide_intervention(intervention_type="frequent_switching")
    
    def _provide_intervention(self, intervention_type: Optional[str] = None):
        """
        Provide an intervention based on distraction patterns.
        
        Args:
            intervention_type (str, optional): Type of intervention to provide
        """
        # Determine intervention type if not specified
        if not intervention_type:
            # Check recent distraction patterns
            if self._check_frequent_switching():
                intervention_type = "frequent_switching"
            elif self.inactivity_periods and time.time() - self.last_activity_time > self.inactivity_threshold:
                intervention_type = "inactivity"
            else:
                intervention_type = "regular"
        
        # Generate intervention message
        message = self._generate_intervention_message(intervention_type)
        
        # Create intervention
        intervention = {
            "timestamp": datetime.now().isoformat(),
            "type": intervention_type,
            "message": message,
            "response": None
        }
        
        self.interventions.append(intervention)
        
        # Save to database if available
        if self.db_manager:
            self._save_intervention(intervention)
        
        # Display intervention (in a real implementation, this would show a notification)
        print(f"\n[INTERVENTION] {message}")
        
        logger.info(f"Provided {intervention_type} intervention")
    
    def _generate_intervention_message(self, intervention_type: str) -> str:
        """
        Generate an intervention message based on the type.
        
        Args:
            intervention_type (str): Type of intervention
            
        Returns:
            str: Intervention message
        """
        if intervention_type == "frequent_switching":
            messages = [
                "You seem to be switching between apps frequently. Try focusing on one task for the next 15 minutes.",
                "Frequent app switching detected. Consider using the Pomodoro technique to improve focus.",
                "You might be experiencing digital distraction. Take a moment to refocus on your primary task."
            ]
        elif intervention_type == "inactivity":
            messages = [
                "It looks like you've been inactive for a while. Ready to get back to your study session?",
                "Taking a break? Remember to set a specific time to return to your work.",
                "Extended inactivity detected. If you're taking a break, that's great! Just make sure to return to your task afterward."
            ]
        else:  # regular
            messages = [
                "How's your focus? Remember to take a short break every 25-30 minutes of concentrated work.",
                "Quick check-in: Are you making progress on your intended task?",
                "Reminder: Setting specific goals for each study session can improve productivity."
            ]
        
        # Select a message (in a real implementation, this would be more sophisticated)
        import random
        return random.choice(messages)
    
    def _save_intervention(self, intervention: Dict[str, Any]):
        """
        Save intervention to database.
        
        Args:
            intervention (Dict[str, Any]): Intervention data
        """
        try:
            self.db_manager.cursor.execute('''
            INSERT INTO interventions (
                user_id, timestamp, type, message, response
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                self.user_id,
                intervention["timestamp"],
                intervention["type"],
                intervention["message"],
                intervention["response"]
            ))
            
            self.db_manager.conn.commit()
            
        except sqlite3.Error as e:
            logger.error(f"Error saving intervention: {e}")
    
    def record_intervention_response(self, intervention_id: int, response: str):
        """
        Record user response to an intervention.
        
        Args:
            intervention_id (int): ID of the intervention
            response (str): User response
        """
        # Update intervention in memory
        for intervention in self.interventions:
            if intervention.get("id") == intervention_id:
                intervention["response"] = response
                break
        
        # Update intervention in database if available
        if self.db_manager:
            try:
                self.db_manager.cursor.execute('''
                UPDATE interventions
                SET response = ?
                WHERE id = ? AND user_id = ?
                ''', (response, intervention_id, self.user_id))
                
                self.db_manager.conn.commit()
                
            except sqlite3.Error as e:
                logger.error(f"Error updating intervention response: {e}")
    
    def generate_weekly_report(self) -> Dict[str, Any]:
        """
        Generate a weekly distraction pattern report.
        
        Returns:
            Dict[str, Any]: Weekly distraction report
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Get distraction data for the week
        app_switches = self._get_app_switches(start_date, end_date)
        inactivity_periods = self._get_inactivity_periods(start_date, end_date)
        interventions = self._get_interventions(start_date, end_date)
        
        # Calculate metrics
        total_switches = len(app_switches)
        total_inactivity_minutes = sum(period.get("duration", 0) for period in inactivity_periods) / 60
        avg_switches_per_hour = total_switches / (168 / 7)  # Assuming 7 hours of tracking per day
        
        # Calculate most switched apps
        app_switch_counts = {}
        for switch in app_switches:
            from_app = switch.get("from_app")
            to_app = switch.get("to_app")
            
            if from_app:
                app_switch_counts[from_app] = app_switch_counts.get(from_app, 0) + 1
            if to_app:
                app_switch_counts[to_app] = app_switch_counts.get(to_app, 0) + 1
        
        most_switched_apps = sorted(
            [{"app": app, "count": count} for app, count in app_switch_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:5]
        
        # Calculate distraction patterns by hour
        hourly_patterns = {}
        for switch in app_switches:
            hour = datetime.fromisoformat(switch.get("timestamp", "")).hour
            hourly_patterns[hour] = hourly_patterns.get(hour, 0) + 1
        
        # Create report
        report = {
            "user_id": self.user_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "generated_at": datetime.now().isoformat(),
            "metrics": {
                "total_app_switches": total_switches,
                "total_inactivity_minutes": total_inactivity_minutes,
                "avg_switches_per_hour": avg_switches_per_hour,
                "most_switched_apps": most_switched_apps,
                "hourly_patterns": [{"hour": hour, "switches": count} for hour, count in hourly_patterns.items()]
            },
            "interventions": {
                "total_interventions": len(interventions),
                "by_type": {
                    "frequent_switching": len([i for i in interventions if i.get("type") == "frequent_switching"]),
                    "inactivity": len([i for i in interventions if i.get("type") == "inactivity"]),
                    "regular": len([i for i in interventions if i.get("type") == "regular"])
                }
            },
            "recommendations": self._generate_recommendations(
                total_switches, total_inactivity_minutes, avg_switches_per_hour, most_switched_apps
            )
        }
        
        # Save report to database if available
        if self.db_manager:
            self._save_report(report)
        
        return report
    
    def _get_app_switches(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get app switches within a date range.
        
        Args:
            start_date (datetime): Start date
            end_date (datetime): End date
            
        Returns:
            List[Dict[str, Any]]: App switches
        """
        if self.db_manager:
            try:
                self.db_manager.cursor.execute('''
                SELECT * FROM app_switches
                WHERE user_id = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp
                ''', (self.user_id, start_date.isoformat(), end_date.isoformat()))
                
                return [dict(row) for row in self.db_manager.cursor.fetchall()]
                
            except sqlite3.Error as e:
                logger.error(f"Error getting app switches: {e}")
                return []
        else:
            # Filter app switches from memory
            return [
                switch for switch in self.app_switches
                if start_date <= datetime.fromisoformat(switch["timestamp"]) <= end_date
            ]
    
    def _get_inactivity_periods(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get inactivity periods within a date range.
        
        Args:
            start_date (datetime): Start date
            end_date (datetime): End date
            
        Returns:
            List[Dict[str, Any]]: Inactivity periods
        """
        if self.db_manager:
            try:
                self.db_manager.cursor.execute('''
                SELECT * FROM inactivity_periods
                WHERE user_id = ? AND start_time BETWEEN ? AND ?
                ORDER BY start_time
                ''', (self.user_id, start_date.isoformat(), end_date.isoformat()))
                
                return [dict(row) for row in self.db_manager.cursor.fetchall()]
                
            except sqlite3.Error as e:
                logger.error(f"Error getting inactivity periods: {e}")
                return []
        else:
            # Filter inactivity periods from memory
            return [
                period for period in self.inactivity_periods
                if start_date <= datetime.fromisoformat(period["start_time"]) <= end_date
            ]
    
    def _get_interventions(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get interventions within a date range.
        
        Args:
            start_date (datetime): Start date
            end_date (datetime): End date
            
        Returns:
            List[Dict[str, Any]]: Interventions
        """
        if self.db_manager:
            try:
                self.db_manager.cursor.execute('''
                SELECT * FROM interventions
                WHERE user_id = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp
                ''', (self.user_id, start_date.isoformat(), end_date.isoformat()))
                
                return [dict(row) for row in self.db_manager.cursor.fetchall()]
                
            except sqlite3.Error as e:
                logger.error(f"Error getting interventions: {e}")
                return []
        else:
            # Filter interventions from memory
            return [
                intervention for intervention in self.interventions
                if start_date <= datetime.fromisoformat(intervention["timestamp"]) <= end_date
            ]
    
    def _generate_recommendations(
        self,
        total_switches: int,
        total_inactivity_minutes: float,
        avg_switches_per_hour: float,
        most_switched_apps: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate recommendations based on distraction patterns.
        
        Args:
            total_switches (int): Total number of app switches
            total_inactivity_minutes (float): Total inactivity time in minutes
            avg_switches_per_hour (float): Average switches per hour
            most_switched_apps (List[Dict[str, Any]]): Most switched apps
            
        Returns:
            List[str]: Recommendations
        """
        recommendations = []
        
        # Check for frequent app switching
        if avg_switches_per_hour > 10:
            recommendations.append(
                "You're switching between apps frequently. Try using the Pomodoro technique: "
                "25 minutes of focused work followed by a 5-minute break."
            )
        
        # Check for specific app distractions
        if most_switched_apps and most_switched_apps[0]["count"] > 50:
            app = most_switched_apps[0]["app"]
            recommendations.append(
                f"You frequently switch to {app}. Consider using app blockers during study sessions "
                f"or designating specific times for checking {app}."
            )
        
        # Check for inactivity
        if total_inactivity_minutes > 120:
            recommendations.append(
                "You have significant periods of inactivity. Try setting specific break times "
                "and using a timer to remind you when to return to your work."
            )
        
        # General recommendations
        recommendations.append(
            "Create a dedicated study environment with minimal distractions. "
            "Put your phone in another room or use Do Not Disturb mode."
        )
        
        recommendations.append(
            "Schedule your study sessions during your peak energy hours. "
            "Your distraction patterns suggest you might be more focused in the morning."
        )
        
        return recommendations
    
    def _save_report(self, report: Dict[str, Any]):
        """
        Save report to database.
        
        Args:
            report (Dict[str, Any]): Report data
        """
        try:
            self.db_manager.cursor.execute('''
            INSERT INTO distraction_reports (
                user_id, start_date, end_date, report_data, timestamp
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                self.user_id,
                report["start_date"],
                report["end_date"],
                json.dumps(report),
                datetime.now().isoformat()
            ))
            
            self.db_manager.conn.commit()
            
        except sqlite3.Error as e:
            logger.error(f"Error saving report: {e}")


def main():
    """
    Command-line interface for the Distraction Tracker.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Distraction Tracking & Intervention")
    parser.add_argument("--user", required=True, help="User ID")
    parser.add_argument("--action", choices=["start", "stop", "report"], required=True, help="Action to perform")
    parser.add_argument("--app", help="Current application name (for manual activity recording)")
    parser.add_argument("--inactivity", type=int, help="Inactivity threshold in seconds")
    parser.add_argument("--switches", type=int, help="Switch threshold per minute")
    parser.add_argument("--frequency", type=int, help="Intervention frequency in minutes")
    parser.add_argument("--output", help="Output file path for report")
    
    args = parser.parse_args()
    
    # Create configuration
    config = {}
    if args.inactivity:
        config["inactivity_threshold"] = args.inactivity
    if args.switches:
        config["switch_threshold"] = args.switches
    if args.frequency:
        config["intervention_frequency"] = args.frequency
    
    # Initialize tracker
    tracker = DistractionTracker(
        user_id=args.user,
        config=config
    )
    
    # Perform action
    if args.action == "start":
        tracker.start_tracking()
        print(f"Started distraction tracking for user {args.user}")
        
        # If app name provided, record activity
        if args.app:
            tracker.record_activity(args.app)
            print(f"Recorded activity in {args.app}")
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            tracker.stop_tracking()
            print("\nStopped distraction tracking")
        
    elif args.action == "stop":
        tracker.stop_tracking()
        print(f"Stopped distraction tracking for user {args.user}")
        
    elif args.action == "report":
        report = tracker.generate_weekly_report()
        
        # Save to file if output path provided
        if args.output:
            os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to {args.output}")
        else:
            # Print report summary
            print("\nWEEKLY DISTRACTION REPORT")
            print("=" * 50)
            
            print(f"\nUser: {report['user_id']}")
            print(f"Period: {report['start_date']} to {report['end_date']}")
            
            metrics = report["metrics"]
            print(f"\nTotal App Switches: {metrics['total_app_switches']}")
            print(f"Total Inactivity: {metrics['total_inactivity_minutes']:.1f} minutes")
            print(f"Average Switches Per Hour: {metrics['avg_switches_per_hour']:.1f}")
            
            print("\nMost Switched Apps:")
            for app in metrics.get("most_switched_apps", []):
                print(f"  - {app['app']}: {app['count']} switches")
            
            interventions = report["interventions"]
            print(f"\nTotal Interventions: {interventions['total_interventions']}")
            print(f"  - Frequent Switching: {interventions['by_type']['frequent_switching']}")
            print(f"  - Inactivity: {interventions['by_type']['inactivity']}")
            print(f"  - Regular: {interventions['by_type']['regular']}")
            
            print("\nRecommendations:")
            for recommendation in report.get("recommendations", []):
                print(f"  - {recommendation}")


if __name__ == "__main__":
    main()