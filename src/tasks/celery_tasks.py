import asyncio
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from ..celery_app import celery_app
from ..database import async_session_maker
from ..models import TaskDB, User
from ..redis_client import redis_client


@celery_app.task
def send_task_reminder(user_id: int, task_id: int, task_title: str):
    """Send reminder about upcoming task deadline"""
    # Here you can integrate with email service, push notifications, etc.
    print(f"📧 Reminder: Task '{task_title}' is due soon for user {user_id}")
    
    # Example: You could send email here
    # send_email(
    #     to=user_email,
    #     subject=f"Task Reminder: {task_title}",
    #     body=f"Your task '{task_title}' is due soon!"
    # )
    
    return f"Reminder sent for task {task_id}"


@celery_app.task
def process_task_statistics():
    """Process and cache task statistics"""
    async def _process_stats():
        async with async_session_maker() as session:
            # Get total tasks count
            total_tasks = await session.execute(select(TaskDB))
            total_count = len(total_tasks.scalars().all())
            
            # Get completed tasks count
            completed_tasks = await session.execute(
                select(TaskDB).where(TaskDB.completed == True)
            )
            completed_count = len(completed_tasks.scalars().all())
            
            # Get overdue tasks count
            now = datetime.utcnow()
            overdue_tasks = await session.execute(
                select(TaskDB).where(
                    and_(
                        TaskDB.deadline < now,
                        TaskDB.completed == False
                    )
                )
            )
            overdue_count = len(overdue_tasks.scalars().all())
            
            stats = {
                "total_tasks": total_count,
                "completed_tasks": completed_count,
                "overdue_tasks": overdue_count,
                "completion_rate": (completed_count / total_count * 100) if total_count > 0 else 0,
                "updated_at": now.isoformat()
            }
            
            # Cache statistics for 1 hour
            await redis_client.set("task_statistics", stats, ttl=3600)
            
            return stats
    
    return asyncio.run(_process_stats())


@celery_app.task
def check_overdue_tasks():
    """Check for overdue tasks and send notifications"""
    async def _check_overdue():
        async with async_session_maker() as session:
            now = datetime.utcnow()
            
            # Find overdue tasks
            result = await session.execute(
                select(TaskDB, User).join(User).where(
                    and_(
                        TaskDB.deadline < now,
                        TaskDB.completed == False
                    )
                )
            )
            
            overdue_tasks = result.all()
            notifications_sent = 0
            
            for task, user in overdue_tasks:
                # Send notification for each overdue task
                send_task_reminder.delay(
                    user_id=user.id,
                    task_id=task.id,
                    task_title=task.title
                )
                notifications_sent += 1
            
            return f"Checked overdue tasks: {notifications_sent} notifications sent"
    
    return asyncio.run(_check_overdue())


@celery_app.task
def daily_cleanup():
    """Daily cleanup tasks"""
    async def _cleanup():
        # Clear old cached data
        await redis_client.clear_pattern("task_cache:*")
        
        # You can add more cleanup tasks here
        # - Delete old logs
        # - Archive completed tasks older than X days
        # - Clean up temporary files
        
        return "Daily cleanup completed"
    
    return asyncio.run(_cleanup())


@celery_app.task
def export_user_tasks(user_id: int, export_format: str = "json"):
    """Export user tasks to specified format"""
    async def _export_tasks():
        async with async_session_maker() as session:
            result = await session.execute(
                select(TaskDB).where(TaskDB.owner_id == user_id)
            )
            tasks = result.scalars().all()
            
            if export_format.lower() == "json":
                task_data = []
                for task in tasks:
                    task_data.append({
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed,
                        "deadline": task.deadline.isoformat() if task.deadline else None,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat()
                    })
                
                # Save to Redis temporarily (for download)
                export_key = f"export:{user_id}:{datetime.utcnow().timestamp()}"
                await redis_client.set(export_key, task_data, ttl=3600)  # 1 hour
                
                return {
                    "export_key": export_key,
                    "task_count": len(task_data),
                    "format": export_format
                }
    
    return asyncio.run(_export_tasks())


@celery_app.task
def bulk_update_tasks(task_ids: List[int], update_data: dict):
    """Bulk update multiple tasks"""
    async def _bulk_update():
        async with async_session_maker() as session:
            updated_count = 0
            
            for task_id in task_ids:
                result = await session.execute(
                    select(TaskDB).where(TaskDB.id == task_id)
                )
                task = result.scalar_one_or_none()
                
                if task:
                    for field, value in update_data.items():
                        if hasattr(task, field):
                            setattr(task, field, value)
                    updated_count += 1
            
            await session.commit()
            
            # Clear cache for updated tasks
            for task_id in task_ids:
                await redis_client.delete(f"task_cache:{task_id}")
            
            return f"Updated {updated_count} tasks"
    
    return asyncio.run(_bulk_update()) 