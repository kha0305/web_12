import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
from passlib.context import CryptContext
import uuid
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def create_admin():
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Check if admin exists
    admin = await db.users.find_one({"email": "admin@medischedule.com"})
    if admin:
        print("Admin already exists")
        return
    
    # Create root admin with full permissions
    admin_data = {
        "id": str(uuid.uuid4()),
        "email": "admin@medischedule.com",
        "username": "admin",
        "password": pwd_context.hash("Admin@123"),
        "full_name": "Root Admin",
        "phone": "0123456789",
        "date_of_birth": "1990-01-01",
        "address": "Admin Office",
        "role": "admin",
        "admin_permissions": {
            "can_manage_doctors": True,
            "can_manage_patients": True,
            "can_manage_appointments": True,
            "can_view_stats": True,
            "can_manage_specialties": True,
            "can_create_admins": True  # Root admin can create other admins
        },
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(admin_data)
    print("Admin created successfully!")
    print("Email: admin@medischedule.com")
    print("Username: admin")
    print("Password: Admin@123")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin())
