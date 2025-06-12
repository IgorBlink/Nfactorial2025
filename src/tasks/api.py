from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_active_user
from ..database import get_db
from ..redis_client import redis_client
from .crud import TaskCRUD
from .models import Task, TaskCreate, TaskUpdate, User
from .celery_tasks import export_user_tasks, process_task_statistics, send_task_reminder, bulk_update_tasks

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/create_task", response_model=Task)
async def create_task(
    task_data: TaskCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new task for the current user"""
    task = await TaskCRUD.create_task(db, task_data, current_user.id)
    
    # Clear user's task cache
    await redis_client.delete(f"user_tasks:{current_user.id}")
    
    # Schedule reminder if deadline is set
    if task.deadline:
        # Send reminder 1 day before deadline
        from datetime import datetime, timedelta
        reminder_time = task.deadline - timedelta(days=1)
        if reminder_time > datetime.utcnow():
            send_task_reminder.apply_async(
                args=[current_user.id, task.id, task.title],
                eta=reminder_time
            )
    
    # Update statistics in background
    background_tasks.add_task(lambda: process_task_statistics.delay())
    
    return task


@router.get("/get_tasks", response_model=List[Task])
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tasks for the current user with caching"""
    cache_key = f"user_tasks:{current_user.id}"
    
    # Try to get from cache first
    cached_tasks = await redis_client.get(cache_key)
    if cached_tasks:
        return cached_tasks
    
    # If not in cache, get from database
    tasks = await TaskCRUD.get_tasks_by_user(db, current_user.id)
    
    # Convert to dict for caching
    tasks_data = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "deadline": task.deadline.isoformat() if task.deadline else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "owner_id": task.owner_id
        }
        for task in tasks
    ]
    
    # Cache for 5 minutes
    await redis_client.set(cache_key, tasks_data, ttl=300)
    
    return tasks


@router.get("/statistics")
async def get_task_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """Get cached task statistics"""
    stats = await redis_client.get("task_statistics")
    
    if not stats:
        # Trigger statistics calculation
        process_task_statistics.delay()
        return {"message": "Statistics are being calculated. Please try again in a moment."}
    
    return stats


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific task by ID with caching"""
    cache_key = f"task_cache:{task_id}"
    
    # Try cache first
    cached_task = await redis_client.get(cache_key)
    if cached_task:
        # Verify task belongs to current user
        if cached_task.get("owner_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return cached_task
    
    # Get from database
    task = await TaskCRUD.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Cache the task
    task_data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),  
        "owner_id": task.owner_id
    }
    await redis_client.set(cache_key, task_data, ttl=300)
    
    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a specific task"""
    task = await TaskCRUD.update_task(db, task_id, current_user.id, task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Clear caches
    await redis_client.delete(f"task_cache:{task_id}")
    await redis_client.delete(f"user_tasks:{current_user.id}")
    
    # Update statistics in background
    background_tasks.add_task(lambda: process_task_statistics.delay())
    
    return task


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a specific task"""
    success = await TaskCRUD.delete_task(db, task_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Clear caches
    await redis_client.delete(f"task_cache:{task_id}")
    await redis_client.delete(f"user_tasks:{current_user.id}")
    
    # Update statistics in background
    background_tasks.add_task(lambda: process_task_statistics.delay())
    
    return {"message": "Task deleted successfully"}


@router.post("/export")
async def export_tasks(
    export_format: str = "json",
    current_user: User = Depends(get_current_active_user)
):
    """Export user tasks asynchronously"""
    task_result = export_user_tasks.delay(current_user.id, export_format)
    
    return {
        "message": "Export started",
        "task_id": task_result.id,
        "status_url": f"/tasks/export-status/{task_result.id}"
    }


@router.get("/export-status/{task_id}")
async def get_export_status(task_id: str):
    """Get export task status"""
    from ..celery_app import celery_app
    
    result = celery_app.AsyncResult(task_id)
    
    if result.ready():
        if result.successful():
            return {
                "status": "completed",
                "result": result.result
            }
        else:
            return {
                "status": "failed",
                "error": str(result.result)
            }
    else:
        return {
            "status": "pending"
        }


@router.post("/bulk-update")
async def bulk_update_tasks_endpoint(
    task_ids: List[int],
    update_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Bulk update multiple tasks"""
    # Verify all tasks belong to current user
    # (This is a simplified version - in production, add proper validation)
    
    task_result = bulk_update_tasks.delay(task_ids, update_data)
    
    # Clear user's task cache
    await redis_client.delete(f"user_tasks:{current_user.id}")
    
    return {
        "message": "Bulk update started",
        "task_id": task_result.id,
        "task_count": len(task_ids)
    }
