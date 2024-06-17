
from injector import inject
from sqlalchemy import select

from src.model.corporation import Corporations
from src.database.database import DatabaseConnection


class CorporationRepository:
    @inject
    def __init__(
        self,
        db: DatabaseConnection,
    ) -> None:
        self.db = db
        
    # uuidからcorporation取得
    async def get_corporation_by_uuid(self, uuid: str) -> Corporations:
        async with self.db.get_db() as session:
            query = (
                select(Corporations)
                .where(Corporations.uuid == uuid)
            )
            result = await session.exec(query)
            return result.scalars().first()