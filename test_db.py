import asyncio
from app.db.postgressconnection import engine, Base
from app.models.user import UserORM  # must import so Base sees the table

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully")

asyncio.run(create_tables())