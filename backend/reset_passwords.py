from pymongo import MongoClient
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Connect to MongoDB
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client['medischedule']

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def reset_all_passwords():
    """Reset all test account passwords to '123456'"""
    
    new_password = "123456"
    hashed_password = hash_password(new_password)
    
    # List of test accounts to reset
    test_accounts = [
        {"email": "admin@medischedule.com", "role": "Admin"},
        {"email": "departmenthead@test.com", "role": "Department Head"},
        {"email": "doctor1@test.com", "role": "Doctor"},
        {"email": "doctor2@test.com", "role": "Doctor"},
        {"email": "doctor3@test.com", "role": "Doctor"},
        {"email": "patient1@test.com", "role": "Patient"},
        {"email": "patient2@test.com", "role": "Patient"},
        {"email": "patient3@test.com", "role": "Patient"},
    ]
    
    print("🔄 Đang reset mật khẩu cho tất cả tài khoản test...\n")
    print(f"📝 Mật khẩu mới: {new_password}\n")
    print("=" * 60)
    
    updated_count = 0
    
    for account in test_accounts:
        email = account["email"]
        role = account["role"]
        
        # Update password in users collection
        result = db.users.update_one(
            {"email": email},
            {"$set": {"password": hashed_password}}
        )
        
        if result.matched_count > 0:
            status = "✅ Đã reset"
            updated_count += 1
        else:
            status = "❌ Không tìm thấy"
        
        print(f"{status} | {role:15} | {email}")
    
    print("=" * 60)
    print(f"\n✨ Hoàn thành! Đã reset {updated_count}/{len(test_accounts)} tài khoản")
    print(f"\n🔑 Tất cả tài khoản đã được đặt mật khẩu: {new_password}")
    print("\n📋 Danh sách tài khoản:")
    print("   • Admin:           admin@medischedule.com / 123456")
    print("   • Department Head: departmenthead@test.com / 123456")
    print("   • Doctor:          doctor1@test.com / 123456")
    print("   • Patient:         patient1@test.com / 123456")

if __name__ == "__main__":
    reset_all_passwords()
    client.close()
