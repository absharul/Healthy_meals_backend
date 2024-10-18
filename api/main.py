from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.future import select

# Use asyncpg for async connections to PostgreSQL
DATABASE_URL = "postgresql+asyncpg://default:vfE8dZ0UmJab@ep-frosty-meadow-a4gj8903-pooler.us-east-1.aws.neon.tech:5432/verceldb"

# Create async engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Item(Base):
    __tablename__ = "food_nutrition"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    image_url = Column(String)
    calories = Column(String)
    protein = Column(String)
    total_fat = Column(String)
    saturated_fat = Column(String)
    monounsaturated_fat = Column(String)
    polyunsaturated_fat = Column(String)
    cholesterol = Column(String)
    sodium = Column(String)
    potassium = Column(String)
    carbohydrates = Column(String)
    dietary_fiber = Column(String)
    sugars = Column(String)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/items/")
async def create_item(name: str, db: AsyncSession = Depends(get_db)):
    item = Item(name=name)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@app.get("/items/{item_id}")
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()  # Returns None if not found

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item

@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).offset(skip).limit(limit))
    items = result.scalars().all()
    return items

@app.get("/items/veg/")
async def read_veg_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.category == "Veg"))
    veg_items = result.scalars().all()
    return veg_items

@app.get("/items/non-veg/")
async def read_nonveg_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.category == "Non-Veg"))
    nonveg_items = result.scalars().all()
    return nonveg_items
