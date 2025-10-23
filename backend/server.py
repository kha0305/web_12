from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
from bson import ObjectId
# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection settings
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'healthcare')
MONGO_CONNECT_TIMEOUT = int(os.environ.get('MONGO_CONNECT_TIMEOUT', 5000))  # 5 seconds
MONGO_SERVER_SELECTION_TIMEOUT = int(os.environ.get('MONGO_SERVER_SELECTION_TIMEOUT', 5000))  # 5 seconds

# Application Settings
API_PREFIX = "/api"

# Create the main app with metadata
app = FastAPI(
    title="Healthcare API",
    description="Backend API for the Healthcare Management System",
    version="1.0.0",
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json"
)

# Create a router with versioned API prefix
api_router = APIRouter()

# Configure CORS
origins = os.environ.get("CORS_ORIGINS", "*").split(",")
if "*" in origins:
    origins = ["*"]
else:
    origins.extend([
        "http://localhost:3000",  # React development server
        "http://localhost:8000",  # FastAPI development server
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
client: Optional[AsyncIOMotorClient] = None
db: Any = None

async def get_database() -> Any:
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not established"
        )
    return db

@app.on_event("startup")
async def startup_db_client():
    global client, db
    try:
        logger.info(f"Connecting to MongoDB at {MONGO_URL}...")
        # Configure MongoDB client with timeouts
        client = AsyncIOMotorClient(
            MONGO_URL,
            serverSelectionTimeoutMS=MONGO_SERVER_SELECTION_TIMEOUT,
            connectTimeoutMS=MONGO_CONNECT_TIMEOUT
        )
        db = client[DB_NAME]
        # Verify the connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes if they don't exist
        await db.users.create_index("email", unique=True)
        await db.users.create_index("id", unique=True)
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # In development, we might want to continue without MongoDB
        if os.environ.get("ENVIRONMENT", "development") == "production":
            raise
        logger.warning("Running in development mode without MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    global client
    if client:
        logger.info("Closing MongoDB connection...")
        client.close()
        logger.info("MongoDB connection closed")

# Security settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
if SECRET_KEY == "your-secret-key-change-in-production":
    logger.warning("Using development JWT_SECRET_KEY. Change this in production!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))  # 7 days default

# Response Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class HTTPError(BaseModel):
    detail: str

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token"
        )

# Middleware for error handling
@app.middleware("http")
async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

# Authentication middleware
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_database)
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except jwt.ExpiredSignatureError:
        logger.warning(f"Expired token attempt for user ID: {user_id if 'user_id' in locals() else 'unknown'}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token attempt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )

# Router will be included at the end of file after all routes are defined

# Models
class UserRole:
    PATIENT = "patient"
    DOCTOR = "doctor"
    DEPARTMENT_HEAD = "department_head"
    ADMIN = "admin"

    @classmethod
    def is_valid(cls, role: str) -> bool:
        return role in {cls.PATIENT, cls.DOCTOR, cls.DEPARTMENT_HEAD, cls.ADMIN}

class AdminPermissions(BaseModel):
    can_manage_doctors: bool = True
    can_manage_patients: bool = True
    can_manage_appointments: bool = True
    can_view_stats: bool = True
    can_manage_specialties: bool = True
    can_create_admins: bool = False  # Only root admin should have this

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    full_name: str
    role: str = UserRole.PATIENT
    admin_permissions: Optional[dict] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = UserRole.PATIENT
    admin_permissions: Optional[dict] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Invalid email format')
        return v.lower()

class UserLogin(BaseModel):
    email: str
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Invalid email format')
        return v.lower()

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
    is_department_head: bool = False  # Trưởng khoa flag
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
    
    # If doctor or department_head, create profile
    if user_data.role in [UserRole.DOCTOR, UserRole.DEPARTMENT_HEAD]:
        doctor_profile = {
            "user_id": user.id,
            "specialty_id": "",
            "bio": "",
            "experience_years": 0,
            "consultation_fee": 0,
            "available_slots": [],
            "status": "pending",
            "is_department_head": user_data.role == UserRole.DEPARTMENT_HEAD,
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

class ForgotPasswordRequest(BaseModel):
    email: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Invalid email format')
        return v.lower()

@api_router.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    user = await db.users.find_one({"email": request.email})
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

# Admin - Create Admin Account with Permissions
@api_router.post("/admin/create-admin")
async def create_admin_account(user_data: UserCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if current admin has permission to create admins
    current_permissions = current_user.get("admin_permissions") or {}
    if not current_permissions.get("can_create_admins", False):
        raise HTTPException(status_code=403, detail="You don't have permission to create admin accounts")
    
    # Force role to be admin
    user_data.role = UserRole.ADMIN
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Set default permissions if not provided
    if not user_data.admin_permissions:
        user_data.admin_permissions = {
            "can_manage_doctors": True,
            "can_manage_patients": True,
            "can_manage_appointments": True,
            "can_view_stats": True,
            "can_manage_specialties": True,
            "can_create_admins": False
        }
    
    # Create admin user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        role=UserRole.ADMIN,
        admin_permissions=user_data.admin_permissions
    )
    
    user_dict = user.model_dump()
    user_dict["password"] = hashed_password
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    
    await db.users.insert_one(user_dict)
    
    user_dict.pop("password")
    return {"message": "Admin account created successfully", "user": user_dict}

# Admin - Get All Admins
@api_router.get("/admin/admins")
async def get_all_admins(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    admins = await db.users.find({"role": UserRole.ADMIN}, {"_id": 0, "password": 0}).to_list(1000)
    return admins

# Admin - Update Admin Permissions
class UpdatePermissionsRequest(BaseModel):
    admin_id: str
    permissions: dict

@api_router.put("/admin/update-permissions")
async def update_admin_permissions(request: UpdatePermissionsRequest, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if current admin has permission to create admins (implies managing admins)
    current_permissions = current_user.get("admin_permissions") or {}
    if not current_permissions.get("can_create_admins", False):
        raise HTTPException(status_code=403, detail="You don't have permission to manage admin accounts")
    
    # Prevent admin from modifying their own permissions
    if request.admin_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot modify your own permissions")
    
    # Update permissions
    result = await db.users.update_one(
        {"id": request.admin_id, "role": UserRole.ADMIN},
        {"$set": {"admin_permissions": request.permissions}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    updated_admin = await db.users.find_one({"id": request.admin_id}, {"_id": 0, "password": 0})
    return {"message": "Permissions updated successfully", "admin": updated_admin}

# Admin - Delete Admin Account
@api_router.delete("/admin/delete-admin/{admin_id}")
async def delete_admin_account(admin_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check permission
    current_permissions = current_user.get("admin_permissions") or {}
    if not current_permissions.get("can_create_admins", False):
        raise HTTPException(status_code=403, detail="You don't have permission to delete admin accounts")
    
    # Prevent self-deletion
    if admin_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Check if target is admin
    target_admin = await db.users.find_one({"id": admin_id, "role": UserRole.ADMIN})
    if not target_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # Delete
    await db.users.delete_one({"id": admin_id})
    
    return {"message": "Admin account deleted successfully"}

# Admin - Delete Any User Account (Patient, Doctor, Department Head)
@api_router.delete("/admin/delete-user/{user_id}")
async def admin_delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Prevent self-deletion
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Get user info
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If doctor, also delete doctor profile
    if user["role"] == UserRole.DOCTOR:
        await db.doctor_profiles.delete_one({"user_id": user_id})
        # Also delete related appointments if needed
        await db.appointments.delete_many({"doctor_id": user_id})
    
    # If patient, delete related appointments
    if user["role"] == UserRole.PATIENT:
        await db.appointments.delete_many({"patient_id": user_id})
    
    # Delete user
    await db.users.delete_one({"id": user_id})
    
    return {"message": f"{user['role'].capitalize()} account deleted successfully"}

# Admin - Create User Accounts (Patient, Doctor, Department Head)
class CreateUserAccountRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str  # patient, doctor, department_head
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    # For doctor role
    specialty_id: Optional[str] = None
    bio: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    # For department_head role
    admin_permissions: Optional[dict] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Invalid email format')
        return v.lower()

@api_router.post("/admin/create-user")
async def admin_create_user(user_data: CreateUserAccountRequest, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validate role
    if not UserRole.is_valid(user_data.role):
        raise HTTPException(status_code=400, detail="Invalid role")
    
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
        role=user_data.role,
        admin_permissions=user_data.admin_permissions if user_data.role == UserRole.DEPARTMENT_HEAD else None
    )
    
    user_dict = user.model_dump()
    user_dict["password"] = hashed_password
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    
    # Add optional fields
    if user_data.phone:
        user_dict["phone"] = user_data.phone
    if user_data.date_of_birth:
        user_dict["date_of_birth"] = user_data.date_of_birth
    if user_data.address:
        user_dict["address"] = user_data.address
    
    # Set default permissions for department_head
    if user_data.role == UserRole.DEPARTMENT_HEAD:
        if not user_data.admin_permissions:
            user_dict["admin_permissions"] = {
                "can_manage_doctors": True,
                "can_manage_patients": True,
                "can_manage_appointments": True,
                "can_view_stats": True,
                "can_manage_specialties": False,
                "can_create_admins": False
            }
    
    await db.users.insert_one(user_dict)
    
    # If doctor, create doctor profile
    if user_data.role == UserRole.DOCTOR and user_data.specialty_id:
        doctor_profile = {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "specialty_id": user_data.specialty_id,
            "bio": user_data.bio or "",
            "experience_years": user_data.experience_years or 0,
            "consultation_fee": user_data.consultation_fee or 0,
            "status": "approved",  # Admin creates approved doctors
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.doctor_profiles.insert_one(doctor_profile)
    
    user_dict.pop("password")
    return {"message": f"{user_data.role.capitalize()} account created successfully", "user": user_dict}

# Department Head Models
class PromoteToDepartmentHeadRequest(BaseModel):
    doctor_id: str

class AddDoctorRequest(BaseModel):
    email: str
    password: str
    full_name: str
    specialty_id: str
    bio: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None

# API Health Check
@api_router.get("/health")
async def health_check():
    """Check API health status"""
    try:
        # Check database connection
        await client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )

# Department Head Routes
@api_router.post("/department-head/promote")
async def promote_to_department_head(request: PromoteToDepartmentHeadRequest, current_user: dict = Depends(get_current_user)):
    """Admin hoặc Trưởng khoa hiện tại có thể chỉ định Trưởng khoa mới"""
    if current_user["role"] not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]:
        raise HTTPException(status_code=403, detail="Admin or Department Head access required")
    
    # Get doctor profile
    doctor = await db.doctor_profiles.find_one({"user_id": request.doctor_id}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # If current user is department head, they can only promote doctors in their specialty
    if current_user["role"] == UserRole.DEPARTMENT_HEAD:
        current_doctor = await db.doctor_profiles.find_one({"user_id": current_user["id"]}, {"_id": 0})
        if current_doctor["specialty_id"] != doctor["specialty_id"]:
            raise HTTPException(status_code=403, detail="You can only manage doctors in your specialty")
    
    # Set as department head
    await db.doctor_profiles.update_one(
        {"user_id": request.doctor_id},
        {"$set": {"is_department_head": True}}
    )
    
    # Update user role
    await db.users.update_one(
        {"id": request.doctor_id},
        {"$set": {"role": UserRole.DEPARTMENT_HEAD}}
    )
    
    return {"message": "Doctor promoted to Department Head successfully"}

@api_router.post("/department-head/demote/{doctor_id}")
async def demote_department_head(doctor_id: str, current_user: dict = Depends(get_current_user)):
    """Admin có thể hạ chức Trưởng khoa"""
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Demote from department head
    await db.doctor_profiles.update_one(
        {"user_id": doctor_id},
        {"$set": {"is_department_head": False}}
    )
    
    # Update user role back to doctor
    await db.users.update_one(
        {"id": doctor_id},
        {"$set": {"role": UserRole.DOCTOR}}
    )
    
    return {"message": "Department Head demoted to Doctor successfully"}

@api_router.post("/department-head/add-doctor")
async def add_doctor_by_department_head(doctor_data: AddDoctorRequest, current_user: dict = Depends(get_current_user)):
    """Trưởng khoa thêm bác sĩ vào chuyên khoa của mình"""
    if current_user["role"] not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]:
        raise HTTPException(status_code=403, detail="Admin or Department Head access required")
    
    # If department head, verify they're adding to their own specialty
    if current_user["role"] == UserRole.DEPARTMENT_HEAD:
        current_doctor = await db.doctor_profiles.find_one({"user_id": current_user["id"]}, {"_id": 0})
        if current_doctor["specialty_id"] != doctor_data.specialty_id:
            raise HTTPException(status_code=403, detail="You can only add doctors to your specialty")
    
    # Validate email
    if '@' not in doctor_data.email or '.' not in doctor_data.email.split('@')[1]:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": doctor_data.email.lower()})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(doctor_data.password)
    
    # Create doctor user
    user = User(
        email=doctor_data.email.lower(),
        full_name=doctor_data.full_name,
        role=UserRole.DOCTOR
    )
    
    user_dict = user.model_dump()
    user_dict["password"] = hashed_password
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    
    await db.users.insert_one(user_dict)
    
    # Create doctor profile - auto-approved since added by department head
    doctor_profile = {
        "user_id": user.id,
        "specialty_id": doctor_data.specialty_id,
        "bio": doctor_data.bio or "",
        "experience_years": doctor_data.experience_years or 0,
        "consultation_fee": doctor_data.consultation_fee or 0,
        "available_slots": [],
        "status": "approved",  # Auto-approved
        "is_department_head": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.doctor_profiles.insert_one(doctor_profile)
    
    return {"message": "Doctor added successfully", "doctor_id": user.id}

@api_router.get("/department-head/my-doctors")
async def get_my_department_doctors(current_user: dict = Depends(get_current_user)):
    """Trưởng khoa xem danh sách bác sĩ trong chuyên khoa của mình"""
    if current_user["role"] != UserRole.DEPARTMENT_HEAD:
        raise HTTPException(status_code=403, detail="Department Head access required")
    
    # Get department head's specialty
    dept_head_profile = await db.doctor_profiles.find_one({"user_id": current_user["id"]}, {"_id": 0})
    if not dept_head_profile:
        raise HTTPException(status_code=404, detail="Department Head profile not found")
    
    # Get all doctors in same specialty
    doctors = await db.doctor_profiles.find({
        "specialty_id": dept_head_profile["specialty_id"]
    }, {"_id": 0}).to_list(1000)
    
    # Enrich with user info
    for doctor in doctors:
        user = await db.users.find_one({"id": doctor["user_id"]}, {"_id": 0, "password": 0})
        if user:
            doctor["full_name"] = user["full_name"]
            doctor["email"] = user["email"]
            doctor["role"] = user["role"]
        
        # Get specialty name
        specialty = await db.specialties.find_one({"id": doctor["specialty_id"]}, {"_id": 0})
        if specialty:
            doctor["specialty_name"] = specialty["name"]
    
    return doctors

@api_router.put("/department-head/approve-doctor/{doctor_id}")
async def department_head_approve_doctor(doctor_id: str, status: str, current_user: dict = Depends(get_current_user)):
    """Trưởng khoa duyệt/từ chối bác sĩ trong chuyên khoa"""
    if current_user["role"] not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]:
        raise HTTPException(status_code=403, detail="Admin or Department Head access required")
    
    # Get doctor
    doctor = await db.doctor_profiles.find_one({"user_id": doctor_id}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # If department head, verify same specialty
    if current_user["role"] == UserRole.DEPARTMENT_HEAD:
        current_doctor = await db.doctor_profiles.find_one({"user_id": current_user["id"]}, {"_id": 0})
        if current_doctor["specialty_id"] != doctor["specialty_id"]:
            raise HTTPException(status_code=403, detail="You can only manage doctors in your specialty")
    
    # Update status
    await db.doctor_profiles.update_one(
        {"user_id": doctor_id},
        {"$set": {"status": status}}
    )
    
    updated_doctor = await db.doctor_profiles.find_one({"user_id": doctor_id}, {"_id": 0})
    return updated_doctor

@api_router.delete("/department-head/remove-doctor/{doctor_id}")
async def department_head_remove_doctor(doctor_id: str, current_user: dict = Depends(get_current_user)):
    """Trưởng khoa xóa bác sĩ khỏi chuyên khoa"""
    if current_user["role"] not in [UserRole.ADMIN, UserRole.DEPARTMENT_HEAD]:
        raise HTTPException(status_code=403, detail="Admin or Department Head access required")
    
    # Get doctor
    doctor = await db.doctor_profiles.find_one({"user_id": doctor_id}, {"_id": 0})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Cannot remove self
    if doctor_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")
    
    # Cannot remove other department heads
    if doctor.get("is_department_head", False):
        raise HTTPException(status_code=400, detail="Cannot remove another Department Head")
    
    # If department head, verify same specialty
    if current_user["role"] == UserRole.DEPARTMENT_HEAD:
        current_doctor = await db.doctor_profiles.find_one({"user_id": current_user["id"]}, {"_id": 0})
        if current_doctor["specialty_id"] != doctor["specialty_id"]:
            raise HTTPException(status_code=403, detail="You can only manage doctors in your specialty")
    
    # Delete doctor profile and user account
    await db.doctor_profiles.delete_one({"user_id": doctor_id})
    await db.users.delete_one({"id": doctor_id})
    
    return {"message": "Doctor removed successfully"}

# Department Head - Create User (Doctor and Patient only)
class DepartmentHeadCreateUserRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str  # 'doctor' or 'patient' only
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    
    # Doctor specific
    specialty_id: Optional[str] = None
    bio: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Invalid email format')
        return v.lower()

@api_router.post("/department-head/create-user")
async def department_head_create_user(user_data: DepartmentHeadCreateUserRequest, current_user: dict = Depends(get_current_user)):
    """Department Head creates doctor or patient accounts"""
    if current_user["role"] != UserRole.DEPARTMENT_HEAD:
        raise HTTPException(status_code=403, detail="Department Head access required")
    
    # Only allow doctor and patient roles
    if user_data.role not in ['doctor', 'patient']:
        raise HTTPException(status_code=403, detail="Department Head can only create doctor or patient accounts")
    
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
    
    # Add optional fields
    if user_data.phone:
        user_dict["phone"] = user_data.phone
    if user_data.date_of_birth:
        user_dict["date_of_birth"] = user_data.date_of_birth
    if user_data.address:
        user_dict["address"] = user_data.address
    
    await db.users.insert_one(user_dict)
    
    # If doctor, create doctor profile
    if user_data.role == 'doctor' and user_data.specialty_id:
        doctor_profile = {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "specialty_id": user_data.specialty_id,
            "bio": user_data.bio or "",
            "experience_years": user_data.experience_years or 0,
            "consultation_fee": user_data.consultation_fee or 0,
            "status": "approved",  # Department Head creates approved doctors
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.doctor_profiles.insert_one(doctor_profile)
    
    user_dict.pop("password")
    return {"message": f"{user_data.role.capitalize()} account created successfully", "user": user_dict}

@api_router.get("/department-head/doctors")
async def department_head_get_doctors(current_user: dict = Depends(get_current_user)):
    """Department Head views all doctors"""
    if current_user["role"] != UserRole.DEPARTMENT_HEAD:
        raise HTTPException(status_code=403, detail="Department Head access required")
    
    doctors = await db.doctor_profiles.find({}, {"_id": 0}).to_list(1000)
    
    # Get user info for each doctor
    for doctor in doctors:
        user = await db.users.find_one({"id": doctor["user_id"]}, {"_id": 0, "password": 0})
        if user:
            doctor["user_info"] = user
        
        # Get specialty info
        if doctor.get("specialty_id"):
            specialty = await db.specialties.find_one({"id": doctor["specialty_id"]}, {"_id": 0})
            if specialty:
                doctor["specialty_name"] = specialty["name"]
    
    return doctors

@api_router.get("/department-head/patients")
async def department_head_get_patients(current_user: dict = Depends(get_current_user)):
    """Department Head views all patients"""
    if current_user["role"] != UserRole.DEPARTMENT_HEAD:
        raise HTTPException(status_code=403, detail="Department Head access required")
    
    patients = await db.users.find({"role": UserRole.PATIENT}, {"_id": 0, "password": 0}).to_list(1000)
    return patients

@api_router.delete("/department-head/remove-patient/{patient_id}")
async def department_head_remove_patient(patient_id: str, current_user: dict = Depends(get_current_user)):
    """Department Head removes a patient"""
    if current_user["role"] != UserRole.DEPARTMENT_HEAD:
        raise HTTPException(status_code=403, detail="Department Head access required")
    
    # Get patient
    patient = await db.users.find_one({"id": patient_id, "role": UserRole.PATIENT}, {"_id": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Delete patient and related data
    await db.users.delete_one({"id": patient_id})
    await db.appointments.delete_many({"patient_id": patient_id})
    await db.chat_messages.delete_many({"$or": [{"sender_id": patient_id}, {"receiver_id": patient_id}]})
    
    return {"message": "Patient removed successfully"}

@api_router.get("/department-head/stats")
async def department_head_get_stats(current_user: dict = Depends(get_current_user)):
    """Department Head views statistics"""
    if current_user["role"] != UserRole.DEPARTMENT_HEAD:
        raise HTTPException(status_code=403, detail="Department Head access required")
    
    # Get counts
    total_doctors = await db.doctor_profiles.count_documents({})
    approved_doctors = await db.doctor_profiles.count_documents({"status": "approved"})
    pending_doctors = await db.doctor_profiles.count_documents({"status": "pending"})
    total_patients = await db.users.count_documents({"role": UserRole.PATIENT})
    total_appointments = await db.appointments.count_documents({})
    completed_appointments = await db.appointments.count_documents({"status": "completed"})
    
    return {
        "total_doctors": total_doctors,
        "approved_doctors": approved_doctors,
        "pending_doctors": pending_doctors,
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments
    }


# Include router in the main app after all routes are defined
app.include_router(api_router, prefix=API_PREFIX)

