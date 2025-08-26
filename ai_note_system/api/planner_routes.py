"""
Study Planner API routes for AI Note System.
Handles study plan generation, retrieval, and updates.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Body, Path, Query

from ..database.oracle_db_manager import OracleDatabaseManager
from ..processing.study_plan_generator import generate_study_plan

# Setup logging
logger = logging.getLogger("ai_note_system.api.planner_routes")

# Create router
router = APIRouter(prefix="/planner", tags=["planner"])

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

# Models (using Pydantic models would be better in a real implementation)
class PlanGenerateRequest(dict):
    pass

class PlanUpdateRequest(dict):
    pass

# Routes
@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_plan(
    request: PlanGenerateRequest = Body(...),
    db: OracleDatabaseManager = Depends(get_db)
):
    """
    Generate a new study plan based on topic and deadline.
    Uses the SM-2 spaced repetition algorithm for optimal learning.
    
    Request body:
    - user_id: ID of the user
    - topic: Topic to study
    - deadline: Deadline for completing the study (ISO format)
    - hours_per_week: (optional) Target study hours per week
    - focus_areas: (optional) Specific areas to focus on
    """
    try:
        # Extract request data
        user_id = request.get("user_id")
        topic = request.get("topic")
        deadline_str = request.get("deadline")
        hours_per_week = request.get("hours_per_week")
        focus_areas = request.get("focus_areas")
        
        # Validate required fields
        if not user_id or not topic or not deadline_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: user_id, topic, deadline"
            )
        
        # Parse deadline
        try:
            deadline = datetime.fromisoformat(deadline_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )
        
        # Check if user exists
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate study plan using the study_plan_generator module
        plan_data = generate_study_plan(
            user_id=user_id,
            weeks=max(1, (deadline - datetime.now()).days // 7),
            hours_per_week=hours_per_week,
            focus_areas=focus_areas,
            db_manager=db
        )
        
        # Create study plan in database
        plan_id = db.create_study_plan({
            "user_id": user_id,
            "topic": topic,
            "deadline": deadline
        })
        
        # Create time blocks for the plan
        for week in plan_data.get("weekly_plan", []):
            for day in week.get("daily_plan", []):
                day_number = day.get("day")
                day_date = datetime.now() + timedelta(days=(week.get("week") - 1) * 7 + day_number - 1)
                
                for topic_block in day.get("topics", []):
                    # Calculate start and end times (simplified)
                    start_time = datetime.combine(day_date.date(), datetime.min.time().replace(hour=9))
                    end_time = start_time + timedelta(hours=topic_block.get("hours", 1))
                    
                    # Create time block
                    db.create_study_plan_block({
                        "plan_id": plan_id,
                        "start_time": start_time,
                        "end_time": end_time,
                        "title": topic_block.get("title"),
                        "description": f"Study session for {topic}",
                        "weight": 1.0  # Default weight
                    })
        
        # Create goals for the plan based on prioritized topics
        for i, topic_item in enumerate(plan_data.get("prioritized_topics", [])[:5]):  # Top 5 topics as goals
            goal_deadline = deadline - timedelta(days=i+1)  # Spread goals before the final deadline
            
            db.create_study_plan_goal({
                "plan_id": plan_id,
                "title": f"Master {topic_item.get('title')}",
                "description": f"Focus on: {', '.join([w.get('topic') for w in topic_item.get('weaknesses', [])[:3]])}",
                "deadline": goal_deadline,
                "priority": min(3, max(1, int(topic_item.get("priority_score", 0.5) * 3)))  # Priority 1-3 based on score
            })
        
        # Get the complete plan with blocks and goals
        complete_plan = db.get_study_plan(plan_id)
        
        # Record user activity
        try:
            db.execute_query("""
            INSERT INTO user_activity (id, user_id, type, value, timestamp)
            VALUES (:id, :user_id, :type, :value, CURRENT_TIMESTAMP)
            """, {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'type': 'plan_generated',
                'value': plan_id
            })
            db.conn.commit()
        except Exception as e:
            logger.error(f"Error recording user activity: {e}")
        
        return {
            "status": "success",
            "message": "Study plan generated successfully",
            "plan_id": plan_id,
            "plan": complete_plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating study plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating study plan: {str(e)}"
        )

@router.get("/{user_id}")
async def get_user_plans(
    user_id: str = Path(..., description="ID of the user"),
    db: OracleDatabaseManager = Depends(get_db)
):
    """
    Get all study plans for a user.
    """
    try:
        # Check if user exists
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get study plans for user
        plans = db.get_study_plans_by_user(user_id)
        
        # Record user activity
        try:
            db.execute_query("""
            INSERT INTO user_activity (id, user_id, type, value, timestamp)
            VALUES (:id, :user_id, :type, :value, CURRENT_TIMESTAMP)
            """, {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'type': 'plans_viewed',
                'value': str(len(plans))
            })
            db.conn.commit()
        except Exception as e:
            logger.error(f"Error recording user activity: {e}")
        
        return {
            "status": "success",
            "user_id": user_id,
            "plans": plans
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting study plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting study plans: {str(e)}"
        )

@router.put("/{plan_id}")
async def update_plan(
    plan_id: str = Path(..., description="ID of the study plan"),
    request: PlanUpdateRequest = Body(...),
    db: OracleDatabaseManager = Depends(get_db)
):
    """
    Update a study plan, including time blocks and goals.
    
    Request body can include:
    - topic: Updated topic
    - deadline: Updated deadline
    - time_blocks: List of time blocks to update
    - goals: List of goals to update
    """
    try:
        # Get the plan to ensure it exists
        plan = db.get_study_plan(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study plan not found"
            )
        
        # Extract request data
        topic = request.get("topic")
        deadline_str = request.get("deadline")
        time_blocks = request.get("time_blocks", [])
        goals = request.get("goals", [])
        
        # Parse deadline if provided
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                )
        
        # Update plan
        plan_updated = db.update_study_plan(plan_id, {
            "topic": topic,
            "deadline": deadline
        })
        
        # Update time blocks
        blocks_updated = []
        for block in time_blocks:
            block_id = block.get("id")
            if not block_id:
                continue
                
            result = db.update_study_plan_block(block_id, {
                "start_time": block.get("start_time"),
                "end_time": block.get("end_time"),
                "title": block.get("title"),
                "description": block.get("description"),
                "weight": block.get("weight"),
                "completed": block.get("completed")
            })
            
            if result:
                blocks_updated.append(block_id)
        
        # Update goals
        goals_updated = []
        for goal in goals:
            goal_id = goal.get("id")
            if not goal_id:
                continue
                
            result = db.update_study_plan_goal(goal_id, {
                "title": goal.get("title"),
                "description": goal.get("description"),
                "deadline": goal.get("deadline"),
                "priority": goal.get("priority"),
                "completed": goal.get("completed")
            })
            
            if result:
                goals_updated.append(goal_id)
        
        # Record user activity
        try:
            db.execute_query("""
            INSERT INTO user_activity (id, user_id, type, value, timestamp)
            VALUES (:id, :user_id, :type, :value, CURRENT_TIMESTAMP)
            """, {
                'id': str(uuid.uuid4()),
                'user_id': plan["user_id"],
                'type': 'plan_updated',
                'value': plan_id
            })
            db.conn.commit()
        except Exception as e:
            logger.error(f"Error recording user activity: {e}")
        
        # Get the updated plan
        updated_plan = db.get_study_plan(plan_id)
        
        return {
            "status": "success",
            "message": "Study plan updated successfully",
            "plan_id": plan_id,
            "blocks_updated": blocks_updated,
            "goals_updated": goals_updated,
            "plan": updated_plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating study plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating study plan: {str(e)}"
        )