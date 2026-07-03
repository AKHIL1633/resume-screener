from abc import ABC
from typing import Generic, Optional, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseService(ABC, Generic[ModelType]):
    """Generic async CRUD base — inherit and call super().__init__(ModelClass, db)."""

    def __init__(self, model: Type[ModelType], db: AsyncSession) -> None:
        self.model = model
        self.db = db

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, page: int = 1, page_size: int = 20) -> tuple[list[ModelType], int]:
        offset = (page - 1) * page_size

        count_result = await self.db.execute(select(func.count()).select_from(self.model))
        total: int = count_result.scalar_one()

        items_result = await self.db.execute(select(self.model).offset(offset).limit(page_size))
        return list(items_result.scalars().all()), total

    async def delete(self, id: int) -> bool:
        instance = await self.get_by_id(id)
        if not instance:
            return False
        await self.db.delete(instance)
        await self.db.commit()
        return True
