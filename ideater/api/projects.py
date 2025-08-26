"""
Projects API router for the Ideater application.

This module handles project creation, retrieval, updating, and deletion.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.models import Project, ProjectStatus, User
from ..utils.db import get_db
from .auth import get_current_active_user

# Set up logging
logger = logging.getLogger("ideater.api.projects")

# Create router
router = APIRouter()

# Models
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    original_idea: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None

class ProjectResponse(ProjectBase):
    id: int
    status: ProjectStatus
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Routes
@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project.
    """
    logger.info(f"Creating new project: {project_data.title}")
    
    # Create new project
    db_project = Project(
        title=project_data.title,
        description=project_data.description,
        original_idea=project_data.original_idea,
        status=ProjectStatus.DRAFT,
        owner_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    logger.info(f"Project created with ID: {db_project.id}")
    return db_project

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects for the current user.
    """
    logger.info(f"Getting projects for user: {current_user.username}")
    projects = db.query(Project).filter(Project.owner_id == current_user.id).offset(skip).limit(limit).all()
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific project by ID.
    """
    logger.info(f"Getting project with ID: {project_id}")
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    
    if project is None:
        logger.warning(f"Project with ID {project_id} not found")
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific project by ID.
    """
    logger.info(f"Updating project with ID: {project_id}")
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    
    if project is None:
        logger.warning(f"Project with ID {project_id} not found")
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update project fields
    if project_data.title is not None:
        project.title = project_data.title
    
    if project_data.description is not None:
        project.description = project_data.description
    
    if project_data.status is not None:
        project.status = project_data.status
    
    project.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(project)
    
    logger.info(f"Project updated: {project.id}")
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific project by ID.
    """
    logger.info(f"Deleting project with ID: {project_id}")
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    
    if project is None:
        logger.warning(f"Project with ID {project_id} not found")
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    
    logger.info(f"Project deleted: {project_id}")
    return None