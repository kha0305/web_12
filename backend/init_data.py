import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def init_specialties():
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Check if specialties already exist
    count = await db.specialties.count_documents({})
    if count > 0:
        print(f"Specialties already exist ({count} specialties). Skipping...")
        return
    
    specialties = [
        {"id": str(uuid.uuid4()), "name": "Nội khoa", "description": "Chuyên khoa nội tổng quát"},
        {"id": str(uuid.uuid4()), "name": "Ngoại khoa", "description": "Chuyên khoa ngoại tổng quát"},
        {"id": str(uuid.uuid4()), "name": "Tim mạch", "description": "Chuyên khoa tim mạch"},
        {"id": str(uuid.uuid4()), "name": "Da liễu", "description": "Chuyên khoa da liễu"},
        {"id": str(uuid.uuid4()), "name": "Tai mũi họng", "description": "Chuyên khoa tai mũi họng"},
        {"id": str(uuid.uuid4()), "name": "Mắt", "description": "Chuyên khoa mắt"},
        {"id": str(uuid.uuid4()), "name": "Nhi khoa", "description": "Chuyên khoa nhi"},
        {"id": str(uuid.uuid4()), "name": "Sản phụ khoa", "description": "Chuyên khoa sản phụ"},
    ]
    
    await db.specialties.insert_many(specialties)
    print(f"Successfully inserted {len(specialties)} specialties")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(init_specialties())
