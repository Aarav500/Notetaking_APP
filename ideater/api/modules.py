"""
Modules API router for the Ideater application.

This module handles module creation, retrieval, updating, and deletion
for the various ideation modules (idea expander, architecture bot, etc.).
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.models import (
    Module, ModuleStatus, Project, User,
    IdeaExpander, ArchitectureBot, FlowchartView, CodeBreakdown,
    MVPGenerator, TestPlanGenerator, RoadmapAssistant, WhiteboardCollaboration
)
from ..utils.db import get_db
from .auth import get_current_active_user

# Set up logging
logger = logging.getLogger("ideater.api.modules")

# Create router
router = APIRouter()

# Models
class ModuleBase(BaseModel):
    module_type: str
    data: Optional[Dict[str, Any]] = None

class ModuleCreate(ModuleBase):
    project_id: int

class ModuleUpdate(BaseModel):
    status: Optional[ModuleStatus] = None
    data: Optional[Dict[str, Any]] = None

class ModuleResponse(ModuleBase):
    id: int
    project_id: int
    status: ModuleStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Module type to model mapping
MODULE_TYPE_MAP = {
    "idea_expander": IdeaExpander,
    "architecture_bot": ArchitectureBot,
    "flowchart_view": FlowchartView,
    "code_breakdown": CodeBreakdown,
    "mvp_generator": MVPGenerator,
    "test_plan_generator": TestPlanGenerator,
    "roadmap_assistant": RoadmapAssistant,
    "whiteboard_collaboration": WhiteboardCollaboration
}

# Helper functions
def get_project(db: Session, project_id: int, user_id: int):
    """Get a project by ID and verify ownership."""
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

def get_module(db: Session, module_id: int, user_id: int):
    """Get a module by ID and verify ownership."""
    module = db.query(Module).join(Project).filter(
        Module.id == module_id,
        Project.owner_id == user_id
    ).first()
    
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return module

def create_module_specific_data(db: Session, module: Module, data: Dict[str, Any]):
    """Create module-specific data based on module type."""
    if module.module_type not in MODULE_TYPE_MAP:
        logger.warning(f"Unknown module type: {module.module_type}")
        return
    
    model_class = MODULE_TYPE_MAP[module.module_type]
    module_data = model_class(module_id=module.id, **data)
    
    db.add(module_data)
    db.commit()
    
    return module_data

def update_module_specific_data(db: Session, module: Module, data: Dict[str, Any]):
    """Update module-specific data based on module type."""
    if module.module_type not in MODULE_TYPE_MAP:
        logger.warning(f"Unknown module type: {module.module_type}")
        return
    
    model_class = MODULE_TYPE_MAP[module.module_type]
    module_data = db.query(model_class).filter(model_class.module_id == module.id).first()
    
    if module_data is None:
        return create_module_specific_data(db, module, data)
    
    for key, value in data.items():
        if hasattr(module_data, key):
            setattr(module_data, key, value)
    
    db.commit()
    
    return module_data

# Routes
@router.post("/", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    module_data: ModuleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new module for a project.
    """
    logger.info(f"Creating new module of type: {module_data.module_type}")
    
    # Verify project exists and user owns it
    project = get_project(db, module_data.project_id, current_user.id)
    
    # Verify module type is valid
    if module_data.module_type not in MODULE_TYPE_MAP:
        logger.warning(f"Invalid module type: {module_data.module_type}")
        raise HTTPException(status_code=400, detail=f"Invalid module type: {module_data.module_type}")
    
    # Create new module
    db_module = Module(
        project_id=module_data.project_id,
        module_type=module_data.module_type,
        status=ModuleStatus.NOT_STARTED,
        data=module_data.data or {},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    
    # Create module-specific data if provided
    if module_data.data:
        create_module_specific_data(db, db_module, module_data.data)
    
    logger.info(f"Module created with ID: {db_module.id}")
    return db_module

@router.get("/project/{project_id}", response_model=List[ModuleResponse])
async def get_modules_by_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all modules for a specific project.
    """
    logger.info(f"Getting modules for project: {project_id}")
    
    # Verify project exists and user owns it
    project = get_project(db, project_id, current_user.id)
    
    modules = db.query(Module).filter(Module.project_id == project_id).all()
    return modules

@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module_by_id(
    module_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific module by ID.
    """
    logger.info(f"Getting module with ID: {module_id}")
    module = get_module(db, module_id, current_user.id)
    return module

@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: int,
    module_data: ModuleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific module by ID.
    """
    logger.info(f"Updating module with ID: {module_id}")
    module = get_module(db, module_id, current_user.id)
    
    # Update module fields
    if module_data.status is not None:
        module.status = module_data.status
    
    if module_data.data is not None:
        module.data = module_data.data
        update_module_specific_data(db, module, module_data.data)
    
    module.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(module)
    
    logger.info(f"Module updated: {module.id}")
    return module

@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific module by ID.
    """
    logger.info(f"Deleting module with ID: {module_id}")
    module = get_module(db, module_id, current_user.id)
    
    db.delete(module)
    db.commit()
    
    logger.info(f"Module deleted: {module_id}")
    return None

@router.post("/{module_id}/process", response_model=ModuleResponse)
async def process_module(
    module_id: int,
    input_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Process a module with the given input data.
    This endpoint will trigger the appropriate module processor based on the module type.
    """
    logger.info(f"Processing module with ID: {module_id}")
    module = get_module(db, module_id, current_user.id)
    
    # Update module status to in progress
    module.status = ModuleStatus.IN_PROGRESS
    db.commit()
    
    try:
        # TODO: Implement module processing logic based on module type
        # This would involve calling the appropriate module processor
        # For now, we'll just update the module status to completed
        
        # Update module status to completed
        module.status = ModuleStatus.COMPLETED
        module.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(module)
        
        logger.info(f"Module processed successfully: {module.id}")
        return module
        
    except Exception as e:
        # Update module status to failed
        module.status = ModuleStatus.FAILED
        module.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.error(f"Error processing module {module.id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing module: {str(e)}")