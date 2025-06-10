from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from ..models import TaskDB, User
from .models import TaskCreate, TaskUpdate


class TaskCRUD:
    @staticmethod
    async def create_task(db: AsyncSession, task_data: TaskCreate, user_id: int) -> TaskDB:
        db_task = TaskDB(
            title=task_data.title,
            description=task_data.description,
            deadline=task_data.deadline,
            owner_id=user_id
        )
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task

    @staticmethod
    async def get_tasks_by_user(db: AsyncSession, user_id: int) -> List[TaskDB]:
        result = await db.execute(
            select(TaskDB).where(TaskDB.owner_id == user_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_task_by_id(db: AsyncSession, task_id: int, user_id: int) -> Optional[TaskDB]:
        result = await db.execute(
            select(TaskDB).where(
                and_(TaskDB.id == task_id, TaskDB.owner_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_task(db: AsyncSession, task_id: int, user_id: int, task_update: TaskUpdate) -> Optional[TaskDB]:
        db_task = await TaskCRUD.get_task_by_id(db, task_id, user_id)
        if not db_task:
            return None
        
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        await db.commit()
        await db.refresh(db_task)
        return db_task

    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int, user_id: int) -> bool:
        db_task = await TaskCRUD.get_task_by_id(db, task_id, user_id)
        if not db_task:
            return False
        
        await db.delete(db_task)
        await db.commit()
        return True
