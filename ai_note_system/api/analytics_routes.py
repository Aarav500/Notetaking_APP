"""
User Analytics API routes for AI Note System.
Handles analytics for user mastery and engagement.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Body, Path, Query

from ..database.oracle_db_manager import OracleDatabaseManager

# Setup logging
logger = logging.getLogger("ai_note_system.api.analytics_routes")

# Create router
router = APIRouter(prefix="/analytics", tags=["analytics"])

# Helper function to get database connection
def get_db():
    """
    Get database connection.
    """
    connection_string = os.environ.get("ORACLE_CONNECTION_STRING")
    username = os.environ.get("ORACLE_USERNAME")
    password = os.environ.get("ORACLE_PASSWORD")
    
    db = OracleDatabaseManager(connection_string, username, password)
    try:
        yield db
    finally:
        db.close()

# Routes
@router.get("/mastery")
async def get_mastery_analytics(
    user_id: str = Query(..., description="ID of the user"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    db: OracleDatabaseManager = Depends(get_db)
):
    """
    Get mastery analytics for a user.
    Returns a heatmap of flashcard and study activity.
    """
    try:
        # Check if user exists
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Parse dates
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                )
        else:
            # Default to 30 days ago
            start_datetime = datetime.now() - timedelta(days=30)
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                )
        else:
            # Default to now
            end_datetime = datetime.now()
        
        # Get flashcard activity
        flashcard_query = """
        SELECT COUNT(*) as count, TO_CHAR(timestamp, 'YYYY-MM-DD') as date
        FROM user_activity
        WHERE user_id = :user_id 
        AND type IN ('flashcard_created', 'flashcard_reviewed', 'quiz_completed')
        AND timestamp BETWEEN :start_date AND :end_date
        GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD')
        ORDER BY date
        """
        
        flashcard_params = {
            'user_id': user_id,
            'start_date': start_datetime,
            'end_date': end_datetime
        }
        
        flashcard_results = []
        try:
            cursor = db.execute_query(flashcard_query, flashcard_params)
            rows = cursor.fetchall()
            
            for row in rows:
                flashcard_results.append({
                    'date': row[1],
                    'count': row[0]
                })
        except Exception as e:
            logger.error(f"Error executing flashcard query: {e}")
        
        # Get study activity
        study_query = """
        SELECT COUNT(*) as count, TO_CHAR(timestamp, 'YYYY-MM-DD') as date
        FROM user_activity
        WHERE user_id = :user_id 
        AND type IN ('plan_generated', 'plan_updated', 'study_session_started', 'study_session_completed')
        AND timestamp BETWEEN :start_date AND :end_date
        GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD')
        ORDER BY date
        """
        
        study_params = {
            'user_id': user_id,
            'start_date': start_datetime,
            'end_date': end_datetime
        }
        
        study_results = []
        try:
            cursor = db.execute_query(study_query, study_params)
            rows = cursor.fetchall()
            
            for row in rows:
                study_results.append({
                    'date': row[1],
                    'count': row[0]
                })
        except Exception as e:
            logger.error(f"Error executing study query: {e}")
        
        # Get topic mastery
        topic_query = """
        SELECT n.tags, COUNT(ua.id) as activity_count
        FROM notes n
        JOIN user_activity ua ON ua.value = n.id
        WHERE n.user_id = :user_id
        AND ua.type IN ('note_viewed', 'flashcard_reviewed', 'quiz_completed')
        AND ua.timestamp BETWEEN :start_date AND :end_date
        GROUP BY n.tags
        ORDER BY activity_count DESC
        """
        
        topic_params = {
            'user_id': user_id,
            'start_date': start_datetime,
            'end_date': end_datetime
        }
        
        topic_results = []
        try:
            cursor = db.execute_query(topic_query, topic_params)
            rows = cursor.fetchall()
            
            for row in rows:
                tags = row[0].split(',') if row[0] else []
                activity_count = row[1]
                
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        # Find if tag already exists in results
                        existing = next((t for t in topic_results if t['topic'] == tag), None)
                        if existing:
                            existing['count'] += activity_count
                        else:
                            topic_results.append({
                                'topic': tag,
                                'count': activity_count
                            })
        except Exception as e:
            logger.error(f"Error executing topic query: {e}")
        
        # Sort topic results by count
        topic_results.sort(key=lambda x: x['count'], reverse=True)
        
        # Record user activity
        try:
            db.execute_query("""
            INSERT INTO user_activity (id, user_id, type, value, timestamp)
            VALUES (:id, :user_id, :type, :value, CURRENT_TIMESTAMP)
            """, {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'type': 'analytics_viewed',
                'value': 'mastery'
            })
            db.conn.commit()
        except Exception as e:
            logger.error(f"Error recording user activity: {e}")
        
        return {
            "status": "success",
            "user_id": user_id,
            "start_date": start_datetime.isoformat(),
            "end_date": end_datetime.isoformat(),
            "flashcard_activity": flashcard_results,
            "study_activity": study_results,
            "topic_mastery": topic_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mastery analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting mastery analytics: {str(e)}"
        )

@router.get("/engagement")
async def get_engagement_analytics(
    user_id: str = Query(..., description="ID of the user"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    db: OracleDatabaseManager = Depends(get_db)
):
    """
    Get engagement analytics for a user.
    Returns active sessions and spike detection.
    """
    try:
        # Check if user exists
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Parse dates
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                )
        else:
            # Default to 30 days ago
            start_datetime = datetime.now() - timedelta(days=30)
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                )
        else:
            # Default to now
            end_datetime = datetime.now()
        
        # Get active sessions
        session_query = """
        SELECT TO_CHAR(timestamp, 'YYYY-MM-DD') as date, 
               COUNT(DISTINCT TRUNC(timestamp, 'HH')) as session_count
        FROM user_activity
        WHERE user_id = :user_id 
        AND timestamp BETWEEN :start_date AND :end_date
        GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD')
        ORDER BY date
        """
        
        session_params = {
            'user_id': user_id,
            'start_date': start_datetime,
            'end_date': end_datetime
        }
        
        session_results = []
        try:
            cursor = db.execute_query(session_query, session_params)
            rows = cursor.fetchall()
            
            for row in rows:
                session_results.append({
                    'date': row[0],
                    'sessions': row[1]
                })
        except Exception as e:
            logger.error(f"Error executing session query: {e}")
        
        # Get activity by type
        activity_query = """
        SELECT type, COUNT(*) as count
        FROM user_activity
        WHERE user_id = :user_id 
        AND timestamp BETWEEN :start_date AND :end_date
        GROUP BY type
        ORDER BY count DESC
        """
        
        activity_params = {
            'user_id': user_id,
            'start_date': start_datetime,
            'end_date': end_datetime
        }
        
        activity_results = []
        try:
            cursor = db.execute_query(activity_query, activity_params)
            rows = cursor.fetchall()
            
            for row in rows:
                activity_results.append({
                    'type': row[0],
                    'count': row[1]
                })
        except Exception as e:
            logger.error(f"Error executing activity query: {e}")
        
        # Detect activity spikes
        # A spike is defined as a day with activity count > 2x the average
        
        # Calculate average daily activity
        avg_query = """
        SELECT AVG(daily_count) as avg_count
        FROM (
            SELECT TO_CHAR(timestamp, 'YYYY-MM-DD') as date, COUNT(*) as daily_count
            FROM user_activity
            WHERE user_id = :user_id 
            AND timestamp BETWEEN :start_date AND :end_date
            GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD')
        )
        """
        
        avg_params = {
            'user_id': user_id,
            'start_date': start_datetime,
            'end_date': end_datetime
        }
        
        avg_daily_activity = 0
        try:
            cursor = db.execute_query(avg_query, avg_params)
            row = cursor.fetchone()
            
            if row and row[0]:
                avg_daily_activity = float(row[0])
        except Exception as e:
            logger.error(f"Error executing average query: {e}")
        
        # Get daily activity counts
        daily_query = """
        SELECT TO_CHAR(timestamp, 'YYYY-MM-DD') as date, COUNT(*) as count
        FROM user_activity
        WHERE user_id = :user_id 
        AND timestamp BETWEEN :start_date AND :end_date
        GROUP BY TO_CHAR(timestamp, 'YYYY-MM-DD')
        ORDER BY date
        """
        
        daily_params = {
            'user_id': user_id,
            'start_date': start_datetime,
            'end_date': end_datetime
        }
        
        daily_results = []
        spikes = []
        try:
            cursor = db.execute_query(daily_query, daily_params)
            rows = cursor.fetchall()
            
            for row in rows:
                date = row[0]
                count = row[1]
                daily_results.append({
                    'date': date,
                    'count': count
                })
                
                # Check for spike
                if count > avg_daily_activity * 2 and avg_daily_activity > 0:
                    spikes.append({
                        'date': date,
                        'count': count,
                        'avg_ratio': round(count / avg_daily_activity, 2)
                    })
        except Exception as e:
            logger.error(f"Error executing daily query: {e}")
        
        # Record user activity
        try:
            db.execute_query("""
            INSERT INTO user_activity (id, user_id, type, value, timestamp)
            VALUES (:id, :user_id, :type, :value, CURRENT_TIMESTAMP)
            """, {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'type': 'analytics_viewed',
                'value': 'engagement'
            })
            db.conn.commit()
        except Exception as e:
            logger.error(f"Error recording user activity: {e}")
        
        return {
            "status": "success",
            "user_id": user_id,
            "start_date": start_datetime.isoformat(),
            "end_date": end_datetime.isoformat(),
            "active_sessions": session_results,
            "activity_by_type": activity_results,
            "daily_activity": daily_results,
            "avg_daily_activity": avg_daily_activity,
            "activity_spikes": spikes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting engagement analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting engagement analytics: {str(e)}"
        )