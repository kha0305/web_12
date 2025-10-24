#!/usr/bin/env python3
"""
Comprehensive Hospital Management System Backend Testing
Tests all modules: Admin, Doctor, Patient, Department Head, AI Features
"""

import requests
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://dual-file-recorder.preview.emergentagent.com')
BASE_URL = f"{BACKEND_URL}/api"

class HospitalSystemTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.tokens = {}
        self.user_ids = {}
        self.test_results = []
        self.specialty_id = None
        self.appointment_id = None
        
    def log_result(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def make_request(self, method, endpoint, data=None, headers=None, token=None):
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        print(f"   Making {method} request to: {url}")
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30, verify=False)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30, verify=False)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=30, verify=False)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30, verify=False)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"   Response status: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"   Request failed: {str(e)}")
            return None
    
    def setup_authentication(self):
        """Setup authentication for all user types"""
        print("\n=== AUTHENTICATION SETUP ===")
        
        test_id = str(uuid.uuid4())[:8]
        
        # 1. Login as Root Admin
        admin_login = {
            "email": "admin@medischedule.com",
            "password": "admin123"
        }
        
        response = self.make_request("POST", "/auth/login", admin_login)
        if response and response.status_code == 200:
            data = response.json()
            self.tokens["admin"] = data.get("token")
            self.user_ids["admin"] = data.get("user", {}).get("id")
            self.log_result("Admin Login", True, "Admin logged in successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Admin Login", False, "Failed to login as admin", error_msg)
            return False
        
        # 2. Login as Department Head
        dept_head_login = {
            "email": "departmenthead@test.com",
            "password": "dept123"
        }
        
        response = self.make_request("POST", "/auth/login", dept_head_login)
        if response and response.status_code == 200:
            data = response.json()
            self.tokens["department_head"] = data.get("token")
            self.user_ids["department_head"] = data.get("user", {}).get("id")
            self.log_result("Department Head Login", True, "Department Head logged in successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Department Head Login", False, "Failed to login as Department Head", error_msg)
        
        # 3. Register Patient
        patient_data = {
            "email": f"patient_{test_id}@test.com",
            "password": "patient123",
            "full_name": "Nguyễn Văn Bệnh Nhân",
            "role": "patient"
        }
        
        response = self.make_request("POST", "/auth/register", patient_data)
        if response and response.status_code == 200:
            data = response.json()
            self.tokens["patient"] = data.get("token")
            self.user_ids["patient"] = data.get("user", {}).get("id")
            self.log_result("Patient Registration", True, "Patient registered successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Patient Registration", False, "Failed to register patient", error_msg)
        
        # 4. Register Doctor
        doctor_data = {
            "email": f"doctor_{test_id}@test.com",
            "password": "doctor123",
            "full_name": "Bác sĩ Nguyễn Văn Y",
            "role": "doctor"
        }
        
        response = self.make_request("POST", "/auth/register", doctor_data)
        if response and response.status_code == 200:
            data = response.json()
            self.tokens["doctor"] = data.get("token")
            self.user_ids["doctor"] = data.get("user", {}).get("id")
            self.log_result("Doctor Registration", True, "Doctor registered successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Doctor Registration", False, "Failed to register doctor", error_msg)
        
        return True
    
    def test_admin_module(self):
        """Test Admin Module functionality"""
        print("\n=== ADMIN MODULE TESTING ===")
        
        if not self.tokens.get("admin"):
            self.log_result("Admin Module", False, "No admin token available")
            return
        
        admin_token = self.tokens["admin"]
        
        # Test 1: Admin Create User Accounts
        test_id = str(uuid.uuid4())[:8]
        
        # Create patient via admin
        patient_data = {
            "email": f"admin_patient_{test_id}@test.com",
            "password": "test123",
            "full_name": "Admin Created Patient",
            "role": "patient",
            "phone": "0123456789",
            "date_of_birth": "1990-01-01",
            "address": "123 Test Street"
        }
        
        response = self.make_request("POST", "/admin/create-user", patient_data, token=admin_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("user"):
                self.log_result("Admin Create Patient", True, "Successfully created patient account")
            else:
                self.log_result("Admin Create Patient", False, "Missing message or user in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Admin Create Patient", False, "Failed to create patient", error_msg)
        
        # Test 2: Admin Get Doctors
        response = self.make_request("GET", "/admin/doctors", token=admin_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("Admin Get Doctors", True, f"Retrieved {len(data)} doctors")
            else:
                self.log_result("Admin Get Doctors", False, "Response should be a list")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Admin Get Doctors", False, "Failed to get doctors", error_msg)
        
        # Test 3: Admin Get Patients
        response = self.make_request("GET", "/admin/patients", token=admin_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("Admin Get Patients", True, f"Retrieved {len(data)} patients")
            else:
                self.log_result("Admin Get Patients", False, "Response should be a list")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Admin Get Patients", False, "Failed to get patients", error_msg)
        
        # Test 4: Admin Get Stats
        response = self.make_request("GET", "/admin/stats", token=admin_token)
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ["total_patients", "total_doctors", "total_appointments"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                self.log_result("Admin Get Stats", True, "Successfully retrieved statistics")
            else:
                self.log_result("Admin Get Stats", False, f"Missing fields: {', '.join(missing_fields)}")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Admin Get Stats", False, "Failed to get statistics", error_msg)
        
        # Test 5: Admin Permission Management
        # Create admin with limited permissions
        limited_admin_data = {
            "email": f"limited_admin_{test_id}@test.com",
            "password": "admin123",
            "full_name": "Limited Admin",
            "admin_permissions": {
                "can_manage_doctors": True,
                "can_manage_patients": True,
                "can_manage_appointments": False,
                "can_view_stats": True,
                "can_manage_specialties": False,
                "can_create_admins": False
            }
        }
        
        response = self.make_request("POST", "/admin/create-admin", limited_admin_data, token=admin_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("user"):
                limited_admin_id = data.get("user", {}).get("id")
                self.log_result("Admin Create Admin", True, "Successfully created admin with permissions")
                
                # Test get all admins
                response = self.make_request("GET", "/admin/admins", token=admin_token)
                if response and response.status_code == 200:
                    admins = response.json()
                    if isinstance(admins, list) and len(admins) >= 2:
                        self.log_result("Admin Get Admins", True, f"Retrieved {len(admins)} admin accounts")
                    else:
                        self.log_result("Admin Get Admins", False, "Should return at least 2 admins")
                else:
                    self.log_result("Admin Get Admins", False, "Failed to get admin list")
            else:
                self.log_result("Admin Create Admin", False, "Missing message or user in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Admin Create Admin", False, "Failed to create admin", error_msg)
    
    def test_department_head_module(self):
        """Test Department Head Module functionality"""
        print("\n=== DEPARTMENT HEAD MODULE TESTING ===")
        
        if not self.tokens.get("department_head"):
            self.log_result("Department Head Module", False, "No department head token available")
            return
        
        dept_token = self.tokens["department_head"]
        test_id = str(uuid.uuid4())[:8]
        
        # Get specialties for doctor creation
        specialties_response = self.make_request("GET", "/specialties")
        specialty_id = None
        if specialties_response and specialties_response.status_code == 200:
            specialties = specialties_response.json()
            if specialties:
                specialty_id = specialties[0]["id"]
        
        # Test 1: Department Head Create User (Doctor)
        doctor_data = {
            "email": f"dept_doctor_{test_id}@test.com",
            "password": "doctor123",
            "full_name": "Department Created Doctor",
            "role": "doctor",
            "specialty_id": specialty_id,
            "bio": "Experienced doctor",
            "experience_years": 5,
            "consultation_fee": 300000
        }
        
        response = self.make_request("POST", "/department-head/create-user", doctor_data, token=dept_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("user"):
                self.log_result("Department Head Create Doctor", True, "Successfully created doctor")
            else:
                self.log_result("Department Head Create Doctor", False, "Missing message or user in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Department Head Create Doctor", False, "Failed to create doctor", error_msg)
        
        # Test 2: Department Head Create User (Patient)
        patient_data = {
            "email": f"dept_patient_{test_id}@test.com",
            "password": "patient123",
            "full_name": "Department Created Patient",
            "role": "patient",
            "phone": "0987654321"
        }
        
        response = self.make_request("POST", "/department-head/create-user", patient_data, token=dept_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("user"):
                self.log_result("Department Head Create Patient", True, "Successfully created patient")
            else:
                self.log_result("Department Head Create Patient", False, "Missing message or user in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Department Head Create Patient", False, "Failed to create patient", error_msg)
        
        # Test 3: Department Head Get Doctors
        response = self.make_request("GET", "/department-head/doctors", token=dept_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("Department Head Get Doctors", True, f"Retrieved {len(data)} doctors")
            else:
                self.log_result("Department Head Get Doctors", False, "Response should be a list")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Department Head Get Doctors", False, "Failed to get doctors", error_msg)
        
        # Test 4: Department Head Get Patients
        response = self.make_request("GET", "/department-head/patients", token=dept_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("Department Head Get Patients", True, f"Retrieved {len(data)} patients")
            else:
                self.log_result("Department Head Get Patients", False, "Response should be a list")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Department Head Get Patients", False, "Failed to get patients", error_msg)
        
        # Test 5: Department Head Get Stats
        response = self.make_request("GET", "/department-head/stats", token=dept_token)
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ["total_doctors", "approved_doctors", "pending_doctors", 
                             "total_patients", "total_appointments", "completed_appointments"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                self.log_result("Department Head Get Stats", True, "Successfully retrieved all statistics")
            else:
                self.log_result("Department Head Get Stats", False, f"Missing fields: {', '.join(missing_fields)}")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Department Head Get Stats", False, "Failed to get statistics", error_msg)
        
        # Test 6: Role validation - try to create admin (should fail)
        admin_data = {
            "email": f"dept_admin_{test_id}@test.com",
            "password": "admin123",
            "full_name": "Should Fail Admin",
            "role": "admin"
        }
        
        response = self.make_request("POST", "/department-head/create-user", admin_data, token=dept_token)
        if response and response.status_code == 403:
            self.log_result("Department Head Role Validation", True, "Correctly rejected admin creation")
        else:
            self.log_result("Department Head Role Validation", False, "Should reject admin creation")
    
    def test_doctor_module(self):
        """Test Doctor Module functionality"""
        print("\n=== DOCTOR MODULE TESTING ===")
        
        if not self.tokens.get("doctor"):
            self.log_result("Doctor Module", False, "No doctor token available")
            return
        
        doctor_token = self.tokens["doctor"]
        
        # Test 1: Doctor Get Appointments
        response = self.make_request("GET", "/appointments/my", token=doctor_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("Doctor Get Appointments", True, f"Retrieved {len(data)} appointments")
            else:
                self.log_result("Doctor Get Appointments", False, "Response should be a list")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Doctor Get Appointments", False, "Failed to get appointments", error_msg)
        
        # Test 2: Doctor Update Profile
        profile_data = {
            "bio": "Updated doctor bio",
            "experience_years": 10,
            "consultation_fee": 500000
        }
        
        response = self.make_request("PUT", "/doctors/profile", profile_data, token=doctor_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                self.log_result("Doctor Update Profile", True, "Successfully updated profile")
            else:
                self.log_result("Doctor Update Profile", False, "Invalid response format")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Doctor Update Profile", False, "Failed to update profile", error_msg)
    
    def test_patient_module(self):
        """Test Patient Module functionality"""
        print("\n=== PATIENT MODULE TESTING ===")
        
        if not self.tokens.get("patient") or not self.user_ids.get("doctor"):
            self.log_result("Patient Module", False, "Missing patient token or doctor ID")
            return
        
        patient_token = self.tokens["patient"]
        doctor_id = self.user_ids["doctor"]
        
        # Test 1: Patient Create Appointment
        appointment_data = {
            "doctor_id": doctor_id,
            "appointment_type": "online",
            "appointment_date": "2024-12-25",
            "appointment_time": "10:00",
            "symptoms": "Đau đầu và sốt nhẹ"
        }
        
        response = self.make_request("POST", "/appointments", appointment_data, token=patient_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("id"):
                self.appointment_id = data.get("id")
                self.log_result("Patient Create Appointment", True, "Successfully created appointment")
            else:
                self.log_result("Patient Create Appointment", False, "Missing appointment ID in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Patient Create Appointment", False, "Failed to create appointment", error_msg)
        
        # Test 2: Patient Get Appointments
        response = self.make_request("GET", "/appointments/my", token=patient_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("Patient Get Appointments", True, f"Retrieved {len(data)} appointments")
            else:
                self.log_result("Patient Get Appointments", False, "Response should be a list")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Patient Get Appointments", False, "Failed to get appointments", error_msg)
        
        # Test 3: Patient Chat with Doctor (if appointment exists)
        if self.appointment_id:
            chat_data = {
                "appointment_id": self.appointment_id,
                "message": "Xin chào bác sĩ, tôi cần tư vấn về triệu chứng của mình"
            }
            
            response = self.make_request("POST", "/chat/send", chat_data, token=patient_token)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("id"):
                    self.log_result("Patient Send Chat Message", True, "Successfully sent chat message")
                else:
                    self.log_result("Patient Send Chat Message", False, "Missing message ID in response")
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result("Patient Send Chat Message", False, "Failed to send chat message", error_msg)
    
    def test_ai_features(self):
        """Test AI Features"""
        print("\n=== AI FEATURES TESTING ===")
        
        if not self.tokens.get("patient"):
            self.log_result("AI Features", False, "No patient token available")
            return
        
        patient_token = self.tokens["patient"]
        
        # Test 1: AI Health Consultation Chatbot
        chat_data = {
            "message": "Tôi bị đau đầu và sốt, tôi nên làm gì?"
        }
        
        response = self.make_request("POST", "/ai/chat", chat_data, token=patient_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("response") and data.get("session_id"):
                self.log_result("AI Health Consultation", True, "AI chatbot responded successfully")
            else:
                self.log_result("AI Health Consultation", False, "Missing response or session_id")
        elif response and response.status_code == 429:
            self.log_result("AI Health Consultation", False, "OpenAI API quota exceeded", "Error 429 - Rate limit")
        elif response and response.status_code == 503:
            self.log_result("AI Health Consultation", False, "AI service not configured", "Service unavailable")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("AI Health Consultation", False, "AI chat request failed", error_msg)
        
        # Test 2: AI Doctor Recommendation
        symptoms_data = {
            "symptoms": "Đau bụng, buồn nôn, tiêu chảy từ 2 ngày nay"
        }
        
        response = self.make_request("POST", "/ai/recommend-doctor", symptoms_data, token=patient_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("recommended_specialty"):
                self.log_result("AI Doctor Recommendation", True, "AI recommended doctor successfully")
            else:
                self.log_result("AI Doctor Recommendation", False, "Missing recommended specialty")
        elif response and response.status_code == 429:
            self.log_result("AI Doctor Recommendation", False, "OpenAI API quota exceeded", "Error 429 - Rate limit")
        elif response and response.status_code == 503:
            self.log_result("AI Doctor Recommendation", False, "AI service not configured", "Service unavailable")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("AI Doctor Recommendation", False, "AI recommendation failed", error_msg)
        
        # Test 3: AI Chat History
        response = self.make_request("GET", "/ai/chat-history", token=patient_token)
        if response and response.status_code == 200:
            data = response.json()
            if "sessions" in data and "total_messages" in data:
                self.log_result("AI Chat History", True, f"Retrieved chat history with {data.get('total_messages', 0)} messages")
            else:
                self.log_result("AI Chat History", False, "Invalid chat history format")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("AI Chat History", False, "Failed to get chat history", error_msg)
        
        # Test 4: AI Conversation Summarization (if appointment exists)
        if self.appointment_id:
            response = self.make_request("POST", f"/ai/summarize-conversation/{self.appointment_id}", token=patient_token)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("summary"):
                    self.log_result("AI Conversation Summarization", True, "AI summarized conversation successfully")
                else:
                    self.log_result("AI Conversation Summarization", False, "Missing summary in response")
            elif response and response.status_code == 429:
                self.log_result("AI Conversation Summarization", False, "OpenAI API quota exceeded", "Error 429 - Rate limit")
            elif response and response.status_code == 503:
                self.log_result("AI Conversation Summarization", False, "AI service not configured", "Service unavailable")
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result("AI Conversation Summarization", False, "AI summarization failed", error_msg)
    
    def test_email_validation_fix(self):
        """Test Email Validation Fix"""
        print("\n=== EMAIL VALIDATION FIX TESTING ===")
        
        # Test with test domain emails
        test_emails = [
            "user@test.com",
            "user@example.org", 
            "user@domain.test",
            "user@localhost.local"
        ]
        
        for email in test_emails:
            user_data = {
                "email": email,
                "password": "test123",
                "full_name": "Test User",
                "role": "patient"
            }
            
            response = self.make_request("POST", "/auth/register", user_data)
            if response and response.status_code == 200:
                self.log_result(f"Email Validation - {email}", True, "Test domain email accepted")
            elif response and response.status_code == 400:
                error_data = response.json() if response.text else {}
                if "already registered" in error_data.get("detail", ""):
                    self.log_result(f"Email Validation - {email}", True, "Email already exists (validation working)")
                else:
                    self.log_result(f"Email Validation - {email}", False, "Email validation rejected test domain")
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result(f"Email Validation - {email}", False, "Unexpected response", error_msg)
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🏥 Hospital Management System - Comprehensive Backend Testing")
        print("=" * 70)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue with tests.")
            return
        
        # Run all module tests
        self.test_admin_module()
        self.test_department_head_module()
        self.test_doctor_module()
        self.test_patient_module()
        self.test_ai_features()
        self.test_email_validation_fix()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group results by module
        modules = {
            "Admin": [r for r in self.test_results if "Admin" in r["test"]],
            "Department Head": [r for r in self.test_results if "Department Head" in r["test"]],
            "Doctor": [r for r in self.test_results if "Doctor" in r["test"]],
            "Patient": [r for r in self.test_results if "Patient" in r["test"]],
            "AI Features": [r for r in self.test_results if "AI" in r["test"]],
            "Email Validation": [r for r in self.test_results if "Email Validation" in r["test"]],
            "Authentication": [r for r in self.test_results if "Login" in r["test"] or "Registration" in r["test"]]
        }
        
        print("\n📋 MODULE BREAKDOWN:")
        for module, results in modules.items():
            if results:
                module_passed = len([r for r in results if r["success"]])
                module_total = len(results)
                print(f"   {module}: {module_passed}/{module_total} passed")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
                    if result.get("details"):
                        print(f"      Details: {result['details']}")
        
        print(f"\n🎯 BACKEND URL USED: {self.base_url}")

if __name__ == "__main__":
    tester = HospitalSystemTester()
    tester.run_all_tests()