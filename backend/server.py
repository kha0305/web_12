from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
from bson import ObjectId

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

security = HTTPBearer()

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Models
class UserRole:
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    role: str = UserRole.PATIENT
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = UserRole.PATIENT

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Specialty(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None

class SpecialtyCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DoctorProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    specialty_id: str
    specialty_name: Optional[str] = None
    bio: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    available_slots: List[dict] = []  # [{"day": "monday", "start_time": "09:00", "end_time": "17:00"}]
    status: str = "pending"  # pending, approved, rejected
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DoctorProfileUpdate(BaseModel):
    specialty_id: Optional[str] = None
    bio: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None

class DoctorScheduleUpdate(BaseModel):
    available_slots: List[dict]

class AppointmentType:
    IN_PERSON = "in_person"
    ONLINE = "online"

class AppointmentStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Appointment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    patient_name: Optional[str] = None
    doctor_id: str
    doctor_name: Optional[str] = None
    appointment_type: str
    appointment_date: str  # YYYY-MM-DD
    appointment_time: str  # HH:MM
    symptoms: Optional[str] = None
    status: str = AppointmentStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AppointmentCreate(BaseModel):
    doctor_id: str
    appointment_type: str
    appointment_date: str
    appointment_time: str
    symptoms: Optional[str] = None

class AppointmentStatusUpdate(BaseModel):
    status: str

class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    appointment_id: str
    sender_id: str
    sender_name: Optional[str] = None
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessageCreate(BaseModel):
    appointment_id: str
    message: str

# Auth Routes
@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role
    )
    
    user_dict = user.model_dump()
    user_dict["password"] = hashed_password
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    
    await db.users.insert_one(user_dict)
    
    # If doctor, create profile
    if user_data.role == UserRole.DOCTOR:
        doctor_profile = {
            "user_id": user.id,
            "specialty_id": "",
            "bio": "",
            "experience_years": 0,
            "consultation_fee": 0,
            "available_slots": [],
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.doctor_profiles.insert_one(doctor_profile)
    
    # Create token
    token = create_access_token({"sub": user.id, "role": user.role})
    
    return {
        "token": token,
        "user": user.model_dump()
    }

@api_router.post("/auth/login")
async def login(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub": user["id"], "role": user["role"]})
    
    user.pop("password")
    
    return {
        "token": token,
        "user": user
    }

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@api_router.post("/auth/forgot-password")
async def forgot_password(email: EmailStr):
    user = await db.users.find_one({"email": email})
    if not user:
        # Don't reveal if email exists
        return {"message": "If email exists, reset link will be sent"}
    
    # In production, send email with reset link
    # For now, just return success
    return {"message": "If email exists, reset link will be sent"}

# Specialty Routes
@api_router.get("/specialties", response_model=List[Specialty])
async def get_specialties():
    specialties = await db.specialties.find({}, {"_id": 0}).to_list(1000)
    return specialties

@api_router.post("/specialties", response_model=Specialty)
async def create_specialty(specialty_data: SpecialtyCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    specialty = Specialty(**specialty_data.model_dump())
    await db.specialties.insert_one(specialty.model_dump())
    return specialty

# Doctor Routes
@api_router.get("/doctors")
async def get_doctors(specialty_id: Optional[str] = None):
    query = {"status": "approved"}
    
    if specialty_id:
        query["specialty_id"] = specialty_id
    
    doctors = await db.doctor_profiles.find(query, {"_id": 0}).to_list(1000)
    
    # Get user info for each doctor
    for doctor in doctors:
        user = await db.users.find_one({"id": doctor["user_id"]}, {"_id": 0, "password": 0})
        if user:
            doctor["full_name"] = user["full_name"]
            doctor["email"] = user["email"]
        
        # Get specialty name
        if doctor.get("specialty_id"):
            specialty = await db.specialties.find_one({"id": doctor["specialty_id"]}, {"_id": 0})
            if specialty:
                doctor["specialty_name"] = specialty["name"]
    
    return doctors

@api_router.get("/doctors/{doctor_id}")
async def get_doctor(doctor_id: str):
    doctor = await db.doctor_profiles.find_one({"user_id": doctor_id}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    user = await db.users.find_one({"id": doctor_id}, {"_id": 0, "password": 0})
    if user:
        doctor["full_name"] = user["full_name"]
        doctor["email"] = user["email"]
    
    # Get specialty name
    if doctor.get("specialty_id"):
        specialty = await db.specialties.find_one({"id": doctor["specialty_id"]}, {"_id": 0})
        if specialty:
            doctor["specialty_name"] = specialty["name"]
    
    return doctor

@api_router.put("/doctors/profile")
async def update_doctor_profile(profile_data: DoctorProfileUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Doctor access required")
    
    update_data = {k: v for k, v in profile_data.model_dump().items() if v is not None}
    
    if update_data:
        await db.doctor_profiles.update_one(
            {"user_id": current_user["id"]},
            {"$set": update_data}
        )
    
    doctor = await db.doctor_profiles.find_one({"user_id": current_user["id"]}, {"_id": 0})
    return doctor

@api_router.put("/doctors/schedule")
async def update_doctor_schedule(schedule_data: DoctorScheduleUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Doctor access required")
    
    await db.doctor_profiles.update_one(
        {"user_id": current_user["id"]},
        {"$set": {"available_slots": schedule_data.available_slots}}
    )
    
    doctor = await db.doctor_profiles.find_one({"user_id": current_user["id"]}, {"_id": 0})
    return doctor

# Appointment Routes
@api_router.post("/appointments", response_model=Appointment)
async def create_appointment(appointment_data: AppointmentCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Patient access required")
    
    appointment = Appointment(
        patient_id=current_user["id"],
        patient_name=current_user["full_name"],
        **appointment_data.model_dump()
    )
    
    # Get doctor name
    doctor = await db.users.find_one({"id": appointment_data.doctor_id}, {"_id": 0})
    if doctor:
        appointment.doctor_name = doctor["full_name"]
    
    doc = appointment.model_dump()
    doc["created_at"] = doc["created_at"].isoformat()
    
    await db.appointments.insert_one(doc)
    return appointment

@api_router.get("/appointments/my")
async def get_my_appointments(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == UserRole.PATIENT:
        appointments = await db.appointments.find({"patient_id": current_user["id"]}, {"_id": 0}).to_list(1000)
    elif current_user["role"] == UserRole.DOCTOR:
        appointments = await db.appointments.find({"doctor_id": current_user["id"]}, {"_id": 0}).to_list(1000)
    else:
        raise HTTPException(status_code=403, detail="Invalid role")
    
    # Sort by date and time (newest first)
    appointments.sort(key=lambda x: (x.get("appointment_date", ""), x.get("appointment_time", "")), reverse=True)
    
    return appointments

@api_router.put("/appointments/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: str,
    status_data: AppointmentStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Doctor access required")
    
    appointment = await db.appointments.find_one({"id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment["doctor_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not your appointment")
    
    await db.appointments.update_one(
        {"id": appointment_id},
        {"$set": {"status": status_data.status}}
    )
    
    updated = await db.appointments.find_one({"id": appointment_id}, {"_id": 0})
    return updated

# Chat Routes
@api_router.post("/chat/send")
async def send_message(message_data: ChatMessageCreate, current_user: dict = Depends(get_current_user)):
    # Verify appointment exists and user is part of it
    appointment = await db.appointments.find_one({"id": message_data.appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if current_user["id"] not in [appointment["patient_id"], appointment["doctor_id"]]:
        raise HTTPException(status_code=403, detail="Not your appointment")
    
    message = ChatMessage(
        appointment_id=message_data.appointment_id,
        sender_id=current_user["id"],
        sender_name=current_user["full_name"],
        message=message_data.message
    )
    
    doc = message.model_dump()
    doc["created_at"] = doc["created_at"].isoformat()
    
    await db.chat_messages.insert_one(doc)
    return message

@api_router.get("/chat/{appointment_id}")
async def get_chat_messages(appointment_id: str, current_user: dict = Depends(get_current_user)):
    # Verify appointment exists and user is part of it
    appointment = await db.appointments.find_one({"id": appointment_id}, {"_id": 0})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if current_user["id"] not in [appointment["patient_id"], appointment["doctor_id"]]:
        raise HTTPException(status_code=403, detail="Not your appointment")
    
    messages = await db.chat_messages.find({"appointment_id": appointment_id}, {"_id": 0}).to_list(1000)
    
    # Sort by created_at
    messages.sort(key=lambda x: x.get("created_at", ""))
    
    return messages

# Admin Routes
@api_router.get("/admin/doctors")
async def admin_get_doctors(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    doctors = await db.doctor_profiles.find({}, {"_id": 0}).to_list(1000)
    
    # Get user info for each doctor
    for doctor in doctors:
        user = await db.users.find_one({"id": doctor["user_id"]}, {"_id": 0, "password": 0})
        if user:
            doctor["full_name"] = user["full_name"]
            doctor["email"] = user["email"]
        
        # Get specialty name
        if doctor.get("specialty_id"):
            specialty = await db.specialties.find_one({"id": doctor["specialty_id"]}, {"_id": 0})
            if specialty:
                doctor["specialty_name"] = specialty["name"]
    
    return doctors

@api_router.put("/admin/doctors/{doctor_id}/approve")
async def admin_approve_doctor(doctor_id: str, status: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await db.doctor_profiles.update_one(
        {"user_id": doctor_id},
        {"$set": {"status": status}}
    )
    
    doctor = await db.doctor_profiles.find_one({"user_id": doctor_id}, {"_id": 0})
    return doctor

@api_router.get("/admin/patients")
async def admin_get_patients(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    patients = await db.users.find({"role": UserRole.PATIENT}, {"_id": 0, "password": 0}).to_list(1000)
    return patients

@api_router.get("/admin/stats")
async def admin_get_stats(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_patients = await db.users.count_documents({"role": UserRole.PATIENT})
    total_doctors = await db.users.count_documents({"role": UserRole.DOCTOR})
    total_appointments = await db.appointments.count_documents({})
    
    pending_appointments = await db.appointments.count_documents({"status": AppointmentStatus.PENDING})
    confirmed_appointments = await db.appointments.count_documents({"status": AppointmentStatus.CONFIRMED})
    completed_appointments = await db.appointments.count_documents({"status": AppointmentStatus.COMPLETED})
    cancelled_appointments = await db.appointments.count_documents({"status": AppointmentStatus.CANCELLED})
    
    online_consultations = await db.appointments.count_documents({"appointment_type": AppointmentType.ONLINE})
    in_person_consultations = await db.appointments.count_documents({"appointment_type": AppointmentType.IN_PERSON})
    
    pending_doctors = await db.doctor_profiles.count_documents({"status": "pending"})
    approved_doctors = await db.doctor_profiles.count_documents({"status": "approved"})
    
    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "confirmed_appointments": confirmed_appointments,
        "completed_appointments": completed_appointments,
        "cancelled_appointments": cancelled_appointments,
        "online_consultations": online_consultations,
        "in_person_consultations": in_person_consultations,
        "pending_doctors": pending_doctors,
        "approved_doctors": approved_doctors
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
