#!/usr/bin/env python3
"""
Backend API Testing for MediSchedule AI Features
Tests all AI endpoints and admin functionality
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
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://web-file-manager.preview.emergentagent.com')
BASE_URL = f"{BACKEND_URL}/api"

class MediScheduleAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.patient_token = None
        self.doctor_token = None
        self.admin_token = None
        self.patient_id = None
        self.doctor_id = None
        self.admin_id = None
        self.appointment_id = None
        self.test_results = []
        
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
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"   Response status: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"   Request failed: {str(e)}")
            return None
    
    def test_auth_setup(self):
        """Test authentication setup - register and login users"""
        print("\n=== AUTHENTICATION SETUP ===")
        
        # Generate unique emails for this test run
        test_id = str(uuid.uuid4())[:8]
        
        # 1. Register Patient
        patient_data = {
            "email": f"patient_{test_id}@test.com",
            "password": "test123",
            "full_name": "Nguyễn Văn Bệnh Nhân",
            "role": "patient"
        }
        
        response = self.make_request("POST", "/auth/register", patient_data)
        if response is not None and response.status_code == 200:
            data = response.json()
            self.patient_token = data.get("token")
            self.patient_id = data.get("user", {}).get("id")
            self.log_result("Patient Registration", True, "Patient registered successfully")
        else:
            if response is not None:
                try:
                    error_detail = response.json()
                    error_msg = f"Status: {response.status_code}, Error: {error_detail}"
                except:
                    error_msg = f"Status: {response.status_code}, Body: {response.text}"
                print(f"   Registration error: {error_msg}")
            else:
                error_msg = "Connection failed - no response received"
            self.log_result("Patient Registration", False, "Failed to register patient", error_msg)
            return False
        
        # 2. Register Doctor
        doctor_data = {
            "email": f"doctor_{test_id}@test.com",
            "password": "test123",
            "full_name": "Bác sĩ Nguyễn Văn Y",
            "role": "doctor"
        }
        
        response = self.make_request("POST", "/auth/register", doctor_data)
        if response and response.status_code == 200:
            data = response.json()
            self.doctor_token = data.get("token")
            self.doctor_id = data.get("user", {}).get("id")
            self.log_result("Doctor Registration", True, "Doctor registered successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Doctor Registration", False, "Failed to register doctor", error_msg)
            return False
        
        # 3. Login as Root Admin (use existing root admin)
        admin_login_data = {
            "email": "admin@medischedule.com",
            "password": "admin123"
        }
        
        response = self.make_request("POST", "/auth/login", admin_login_data)
        if response and response.status_code == 200:
            data = response.json()
            self.admin_token = data.get("token")
            self.admin_id = data.get("user", {}).get("id")
            self.log_result("Root Admin Login", True, "Root admin logged in successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Root Admin Login", False, "Failed to login as root admin", error_msg)
            return False
        
        return True
    
    def test_ai_chatbot(self):
        """Test AI Chatbot - Health Consultation"""
        print("\n=== AI CHATBOT TESTING ===")
        
        if not self.patient_token:
            self.log_result("AI Chatbot", False, "No patient token available")
            return
        
        # Test 1: Valid health consultation
        chat_data = {
            "message": "Tôi bị đau đầu và sốt, tôi nên làm gì?"
        }
        
        response = self.make_request("POST", "/ai/chat", chat_data, token=self.patient_token)
        if response and response.status_code == 200:
            data = response.json()
            ai_response = data.get("response", "")
            session_id = data.get("session_id", "")
            
            if ai_response and session_id:
                self.log_result("AI Chatbot - Health Consultation", True, 
                              f"AI responded with {len(ai_response)} characters")
                print(f"   AI Response: {ai_response[:100]}...")
            else:
                self.log_result("AI Chatbot - Health Consultation", False, 
                              "Missing response or session_id in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("AI Chatbot - Health Consultation", False, 
                          "AI chat request failed", error_msg)
        
        # Test 2: Unauthorized access (no token)
        response = self.make_request("POST", "/ai/chat", chat_data)
        if response and response.status_code in [401, 403]:
            self.log_result("AI Chatbot - Auth Check", True, "Correctly rejected unauthorized access")
        else:
            self.log_result("AI Chatbot - Auth Check", False, "Should reject unauthorized access")
        
        # Test 3: Doctor trying to access (should fail)
        response = self.make_request("POST", "/ai/chat", chat_data, token=self.doctor_token)
        if response and response.status_code == 403:
            self.log_result("AI Chatbot - Role Check", True, "Correctly rejected doctor access")
        else:
            self.log_result("AI Chatbot - Role Check", False, "Should reject doctor access")
    
    def test_ai_doctor_recommendation(self):
        """Test AI Doctor Recommendation"""
        print("\n=== AI DOCTOR RECOMMENDATION TESTING ===")
        
        if not self.patient_token:
            self.log_result("AI Doctor Recommendation", False, "No patient token available")
            return
        
        # First, create some specialties and doctors for testing
        self.setup_test_data()
        
        # Test 1: Valid symptom analysis
        symptoms_data = {
            "symptoms": "Đau bụng, buồn nôn, tiêu chảy"
        }
        
        response = self.make_request("POST", "/ai/recommend-doctor", symptoms_data, token=self.patient_token)
        if response and response.status_code == 200:
            data = response.json()
            specialty = data.get("recommended_specialty", "")
            reasoning = data.get("reasoning", "")
            doctors = data.get("doctors", [])
            
            if specialty and reasoning:
                self.log_result("AI Doctor Recommendation", True, 
                              f"Recommended specialty: {specialty}")
                print(f"   Reasoning: {reasoning[:100]}...")
                print(f"   Found {len(doctors)} doctors")
            else:
                self.log_result("AI Doctor Recommendation", False, 
                              "Missing specialty or reasoning in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("AI Doctor Recommendation", False, 
                          "AI recommendation request failed", error_msg)
        
        # Test 2: Unauthorized access
        response = self.make_request("POST", "/ai/recommend-doctor", symptoms_data)
        if response and response.status_code in [401, 403]:
            self.log_result("AI Doctor Recommendation - Auth Check", True, 
                          "Correctly rejected unauthorized access")
        else:
            self.log_result("AI Doctor Recommendation - Auth Check", False, 
                          "Should reject unauthorized access")
    
    def test_ai_chat_history(self):
        """Test AI Chat History"""
        print("\n=== AI CHAT HISTORY TESTING ===")
        
        if not self.patient_token:
            self.log_result("AI Chat History", False, "No patient token available")
            return
        
        # Test 1: Get chat history (should work even if empty)
        response = self.make_request("GET", "/ai/chat-history", token=self.patient_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("AI Chat History", True, f"Retrieved {len(data)} chat records")
            else:
                self.log_result("AI Chat History", False, "Response should be a list")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("AI Chat History", False, "Failed to get chat history", error_msg)
        
        # Test 2: Unauthorized access
        response = self.make_request("GET", "/ai/chat-history")
        if response and response.status_code in [401, 403]:
            self.log_result("AI Chat History - Auth Check", True, 
                          "Correctly rejected unauthorized access")
        else:
            self.log_result("AI Chat History - Auth Check", False, 
                          "Should reject unauthorized access")
    
    def test_admin_permission_system(self):
        """Test Admin Permission System - Complete Flow"""
        print("\n=== ADMIN PERMISSION SYSTEM TESTING ===")
        
        if not self.admin_token:
            self.log_result("Admin Permission System", False, "No admin token available")
            return
        
        # Test 1: Create Admin with Limited Permissions
        limited_admin_data = {
            "email": "limited_admin@test.com",
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
        
        response = self.make_request("POST", "/admin/create-admin", limited_admin_data, token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("user"):
                self.limited_admin_id = data.get("user", {}).get("id")
                self.log_result("Create Admin with Limited Permissions", True, 
                              "Successfully created limited admin account")
            else:
                self.log_result("Create Admin with Limited Permissions", False, 
                              "Missing message or user in response")
                return
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Create Admin with Limited Permissions", False, 
                          "Failed to create admin account", error_msg)
            return
        
        # Test 2: Get All Admins
        response = self.make_request("GET", "/admin/admins", token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) >= 2:  # Root admin + new admin
                self.log_result("Get All Admins", True, f"Retrieved {len(data)} admin accounts")
            else:
                self.log_result("Get All Admins", False, "Should return at least 2 admins")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Get All Admins", False, "Failed to get admin list", error_msg)
        
        # Test 3: Update Admin Permissions
        if hasattr(self, 'limited_admin_id'):
            update_permissions_data = {
                "admin_id": self.limited_admin_id,
                "permissions": {
                    "can_manage_doctors": True,
                    "can_manage_patients": True,
                    "can_manage_appointments": False,
                    "can_view_stats": True,
                    "can_manage_specialties": True,  # Changed to True
                    "can_create_admins": False
                }
            }
            
            response = self.make_request("PUT", "/admin/update-permissions", update_permissions_data, token=self.admin_token)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("message") and data.get("admin"):
                    self.log_result("Update Admin Permissions", True, "Successfully updated permissions")
                else:
                    self.log_result("Update Admin Permissions", False, "Missing message or admin in response")
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result("Update Admin Permissions", False, "Failed to update permissions", error_msg)
        
        # Test 4: Test Permission Enforcement - Login as limited admin and try to create admin
        limited_admin_login = {
            "email": "limited_admin@test.com",
            "password": "admin123"
        }
        
        response = self.make_request("POST", "/auth/login", limited_admin_login)
        if response and response.status_code == 200:
            limited_admin_token = response.json().get("token")
            
            # Try to create another admin (should fail)
            test_admin_data = {
                "email": "test_admin@test.com",
                "password": "admin123",
                "full_name": "Test Admin"
            }
            
            response = self.make_request("POST", "/admin/create-admin", test_admin_data, token=limited_admin_token)
            if response and response.status_code == 403:
                self.log_result("Permission Enforcement Test", True, 
                              "Correctly rejected limited admin trying to create admin")
            else:
                self.log_result("Permission Enforcement Test", False, 
                              "Should reject limited admin creating admin")
        else:
            self.log_result("Limited Admin Login", False, "Failed to login as limited admin")
        
        # Test 5: Unauthorized access tests
        response = self.make_request("POST", "/admin/create-admin", limited_admin_data, token=self.patient_token)
        if response and response.status_code == 403:
            self.log_result("Admin Create - Patient Access Check", True, 
                          "Correctly rejected patient access")
        else:
            self.log_result("Admin Create - Patient Access Check", False, 
                          "Should reject patient access")
        
        response = self.make_request("POST", "/admin/create-admin", limited_admin_data)
        if response and response.status_code in [401, 403]:
            self.log_result("Admin Create - No Token Check", True, 
                          "Correctly rejected unauthorized access")
        else:
            self.log_result("Admin Create - No Token Check", False, 
                          "Should reject unauthorized access")
    
    def test_ai_conversation_summarization(self):
        """Test AI Conversation Summarization"""
        print("\n=== AI CONVERSATION SUMMARIZATION TESTING ===")
        
        if not self.patient_token or not self.doctor_token:
            self.log_result("AI Conversation Summarization", False, 
                          "Missing patient or doctor token")
            return
        
        # First create an appointment
        appointment_created = self.create_test_appointment()
        if not appointment_created:
            return
        
        # Send some test messages
        self.send_test_messages()
        
        # Test 1: Summarize conversation (as doctor)
        response = self.make_request("POST", f"/ai/summarize-conversation/{self.appointment_id}", 
                                   token=self.doctor_token)
        if response and response.status_code == 200:
            data = response.json()
            summary = data.get("summary", "")
            message_count = data.get("message_count", 0)
            
            if summary and message_count > 0:
                self.log_result("AI Conversation Summarization", True, 
                              f"Generated summary for {message_count} messages")
                print(f"   Summary: {summary[:100]}...")
            else:
                self.log_result("AI Conversation Summarization", False, 
                              "Missing summary or message count")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("AI Conversation Summarization", False, 
                          "Failed to summarize conversation", error_msg)
        
        # Test 2: Unauthorized access (different user)
        fake_appointment_id = str(uuid.uuid4())
        response = self.make_request("POST", f"/ai/summarize-conversation/{fake_appointment_id}", 
                                   token=self.patient_token)
        if response and response.status_code == 404:
            self.log_result("AI Conversation Summarization - Access Check", True, 
                          "Correctly rejected access to non-existent appointment")
        else:
            self.log_result("AI Conversation Summarization - Access Check", False, 
                          "Should reject access to non-existent appointment")
    
    def setup_test_data(self):
        """Setup test specialties and doctors"""
        if not self.admin_token:
            return
        
        # Create test specialty
        specialty_data = {
            "name": "Nội khoa",
            "description": "Chuyên khoa nội tổng quát"
        }
        
        response = self.make_request("POST", "/specialties", specialty_data, token=self.admin_token)
        if response and response.status_code == 200:
            print("   Created test specialty: Nội khoa")
    
    def create_test_appointment(self):
        """Create a test appointment for conversation testing"""
        if not self.patient_token or not self.doctor_id:
            return False
        
        appointment_data = {
            "doctor_id": self.doctor_id,
            "appointment_type": "online",
            "appointment_date": "2024-12-20",
            "appointment_time": "10:00",
            "symptoms": "Đau đầu và sốt"
        }
        
        response = self.make_request("POST", "/appointments", appointment_data, token=self.patient_token)
        if response and response.status_code == 200:
            data = response.json()
            self.appointment_id = data.get("id")
            print(f"   Created test appointment: {self.appointment_id}")
            return True
        else:
            self.log_result("Create Test Appointment", False, "Failed to create appointment")
            return False
    
    def send_test_messages(self):
        """Send test messages for conversation summarization"""
        if not self.appointment_id:
            return
        
        messages = [
            {"token": self.patient_token, "message": "Xin chào bác sĩ, tôi bị đau đầu và sốt từ 2 ngày nay"},
            {"token": self.doctor_token, "message": "Chào bạn, bạn có thể mô tả chi tiết hơn về triệu chứng không?"},
            {"token": self.patient_token, "message": "Đau đầu dữ dội, sốt 38.5 độ, và hơi buồn nôn"},
            {"token": self.doctor_token, "message": "Tôi khuyên bạn nên nghỉ ngơi và uống nhiều nước. Nếu không khỏi sau 2 ngày nữa thì đến khám trực tiếp."}
        ]
        
        for msg in messages:
            message_data = {
                "appointment_id": self.appointment_id,
                "message": msg["message"]
            }
            response = self.make_request("POST", "/chat/send", message_data, token=msg["token"])
            if response and response.status_code == 200:
                print(f"   Sent message: {msg['message'][:30]}...")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🏥 MediSchedule AI Features Backend Testing")
        print("=" * 50)
        
        # Setup authentication
        if not self.test_auth_setup():
            print("❌ Authentication setup failed. Cannot continue with tests.")
            return
        
        # Run AI feature tests
        self.test_ai_chatbot()
        self.test_ai_doctor_recommendation()
        self.test_ai_chat_history()
        self.test_admin_permission_system()
        self.test_ai_conversation_summarization()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        print("\n🎯 BACKEND URL USED:", self.base_url)

class DepartmentHeadAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.dept_head_token = None
        self.patient_token = None
        self.doctor_token = None
        self.dept_head_id = None
        self.test_patient_id = None
        self.test_doctor_id = None
        self.test_results = []
        
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
        """Setup authentication for Department Head testing"""
        print("\n=== DEPARTMENT HEAD AUTHENTICATION SETUP ===")
        
        # 1. Login as Department Head
        dept_head_login = {
            "email": "departmenthead@test.com",
            "password": "dept123"
        }
        
        response = self.make_request("POST", "/auth/login", dept_head_login)
        if response and response.status_code == 200:
            data = response.json()
            self.dept_head_token = data.get("token")
            self.dept_head_id = data.get("user", {}).get("id")
            self.log_result("Department Head Login", True, "Department Head logged in successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Department Head Login", False, "Failed to login as Department Head", error_msg)
            return False
        
        # 2. Create a test patient for access control testing
        test_id = str(uuid.uuid4())[:8]
        patient_data = {
            "email": f"testpatient_{test_id}@test.com",
            "password": "test123",
            "full_name": "Nguyễn Thị Bệnh Nhân Test",
            "role": "patient"
        }
        
        response = self.make_request("POST", "/auth/register", patient_data)
        if response and response.status_code == 200:
            data = response.json()
            self.patient_token = data.get("token")
            self.log_result("Test Patient Registration", True, "Test patient registered successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Test Patient Registration", False, "Failed to register test patient", error_msg)
            return False
        
        return True
    
    def test_create_user_endpoint(self):
        """Test POST /api/department-head/create-user"""
        print("\n=== TESTING DEPARTMENT HEAD CREATE USER ENDPOINT ===")
        
        if not self.dept_head_token:
            self.log_result("Create User Endpoint", False, "No Department Head token available")
            return
        
        # Get specialties first for doctor creation
        specialties_response = self.make_request("GET", "/specialties")
        specialty_id = None
        if specialties_response and specialties_response.status_code == 200:
            specialties = specialties_response.json()
            if specialties:
                specialty_id = specialties[0]["id"]
        
        test_id = str(uuid.uuid4())[:8]
        
        # Test 1: ✅ Create doctor account with valid data
        doctor_data = {
            "email": f"testdoctor_{test_id}@test.com",
            "password": "doctor123",
            "full_name": "Bác sĩ Nguyễn Văn Test",
            "role": "doctor",
            "phone": "0123456789",
            "specialty_id": specialty_id,
            "bio": "Bác sĩ có kinh nghiệm 10 năm",
            "experience_years": 10,
            "consultation_fee": 500000
        }
        
        response = self.make_request("POST", "/department-head/create-user", doctor_data, token=self.dept_head_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("user"):
                self.test_doctor_id = data.get("user", {}).get("id")
                self.log_result("Create Doctor Account", True, "Successfully created doctor account")
            else:
                self.log_result("Create Doctor Account", False, "Missing message or user in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Create Doctor Account", False, "Failed to create doctor account", error_msg)
        
        # Test 2: ✅ Create patient account with valid data
        patient_data = {
            "email": f"testpatient2_{test_id}@test.com",
            "password": "patient123",
            "full_name": "Nguyễn Thị Bệnh Nhân Test 2",
            "role": "patient",
            "phone": "0987654321",
            "date_of_birth": "1990-01-01",
            "address": "123 Đường Test, TP.HCM"
        }
        
        response = self.make_request("POST", "/department-head/create-user", patient_data, token=self.dept_head_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("user"):
                self.test_patient_id = data.get("user", {}).get("id")
                self.log_result("Create Patient Account", True, "Successfully created patient account")
            else:
                self.log_result("Create Patient Account", False, "Missing message or user in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Create Patient Account", False, "Failed to create patient account", error_msg)
        
        # Test 3: ❌ Try to create admin account (should be rejected with 403)
        admin_data = {
            "email": f"testadmin_{test_id}@test.com",
            "password": "admin123",
            "full_name": "Admin Test",
            "role": "admin"
        }
        
        response = self.make_request("POST", "/department-head/create-user", admin_data, token=self.dept_head_token)
        if response and response.status_code == 403:
            self.log_result("Create Admin Account - Rejection Test", True, "Correctly rejected admin account creation")
        else:
            self.log_result("Create Admin Account - Rejection Test", False, "Should reject admin account creation")
        
        # Test 4: ❌ Try to create department_head account (should be rejected with 403)
        dept_head_data = {
            "email": f"testdepthead_{test_id}@test.com",
            "password": "dept123",
            "full_name": "Department Head Test",
            "role": "department_head"
        }
        
        response = self.make_request("POST", "/department-head/create-user", dept_head_data, token=self.dept_head_token)
        if response and response.status_code == 403:
            self.log_result("Create Department Head Account - Rejection Test", True, "Correctly rejected department_head account creation")
        else:
            self.log_result("Create Department Head Account - Rejection Test", False, "Should reject department_head account creation")
        
        # Test 5: ❌ Try with existing email (should fail with 400)
        duplicate_data = {
            "email": "departmenthead@test.com",  # Existing email
            "password": "test123",
            "full_name": "Duplicate Test",
            "role": "patient"
        }
        
        response = self.make_request("POST", "/department-head/create-user", duplicate_data, token=self.dept_head_token)
        if response and response.status_code == 400:
            self.log_result("Duplicate Email Test", True, "Correctly rejected duplicate email")
        else:
            self.log_result("Duplicate Email Test", False, "Should reject duplicate email")
        
        # Test 6: ❌ Try without authentication (should fail with 401)
        response = self.make_request("POST", "/department-head/create-user", patient_data)
        if response and response.status_code == 401:
            self.log_result("No Authentication Test", True, "Correctly rejected request without authentication")
        else:
            self.log_result("No Authentication Test", False, "Should reject request without authentication")
        
        # Test 7: ❌ Try with non-department_head role (should fail with 403)
        response = self.make_request("POST", "/department-head/create-user", patient_data, token=self.patient_token)
        if response and response.status_code == 403:
            self.log_result("Non-Department Head Access Test", True, "Correctly rejected non-department_head access")
        else:
            self.log_result("Non-Department Head Access Test", False, "Should reject non-department_head access")
    
    def test_get_doctors_endpoint(self):
        """Test GET /api/department-head/doctors"""
        print("\n=== TESTING DEPARTMENT HEAD GET DOCTORS ENDPOINT ===")
        
        if not self.dept_head_token:
            self.log_result("Get Doctors Endpoint", False, "No Department Head token available")
            return
        
        # Test 1: ✅ Fetch all doctors list
        response = self.make_request("GET", "/department-head/doctors", token=self.dept_head_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("Fetch Doctors List", True, f"Successfully fetched {len(data)} doctors")
                
                # Test 2: ✅ Verify response includes user_info and specialty_name
                if data:
                    doctor = data[0]
                    has_user_info = "user_info" in doctor
                    has_specialty_name = "specialty_name" in doctor
                    
                    if has_user_info and has_specialty_name:
                        self.log_result("Doctor Response Format", True, "Response includes user_info and specialty_name")
                    else:
                        missing_fields = []
                        if not has_user_info:
                            missing_fields.append("user_info")
                        if not has_specialty_name:
                            missing_fields.append("specialty_name")
                        self.log_result("Doctor Response Format", False, f"Missing fields: {', '.join(missing_fields)}")
                else:
                    self.log_result("Doctor Response Format", True, "No doctors to verify format (empty list)")
            else:
                self.log_result("Fetch Doctors List", False, "Response should be a list")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Fetch Doctors List", False, "Failed to fetch doctors list", error_msg)
        
        # Test 3: ❌ Try without authentication (should fail with 401)
        response = self.make_request("GET", "/department-head/doctors")
        if response and response.status_code == 401:
            self.log_result("Get Doctors - No Authentication Test", True, "Correctly rejected request without authentication")
        else:
            self.log_result("Get Doctors - No Authentication Test", False, "Should reject request without authentication")
        
        # Test 4: ❌ Try with non-department_head role (should fail with 403)
        response = self.make_request("GET", "/department-head/doctors", token=self.patient_token)
        if response and response.status_code == 403:
            self.log_result("Get Doctors - Non-Department Head Access Test", True, "Correctly rejected non-department_head access")
        else:
            self.log_result("Get Doctors - Non-Department Head Access Test", False, "Should reject non-department_head access")
    
    def test_get_patients_endpoint(self):
        """Test GET /api/department-head/patients"""
        print("\n=== TESTING DEPARTMENT HEAD GET PATIENTS ENDPOINT ===")
        
        if not self.dept_head_token:
            self.log_result("Get Patients Endpoint", False, "No Department Head token available")
            return
        
        # Test 1: ✅ Fetch all patients list
        response = self.make_request("GET", "/department-head/patients", token=self.dept_head_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("Fetch Patients List", True, f"Successfully fetched {len(data)} patients")
                
                # Test 2: ✅ Verify response excludes password field
                if data:
                    patient = data[0]
                    has_password = "password" in patient
                    
                    if not has_password:
                        self.log_result("Patient Response Security", True, "Response correctly excludes password field")
                    else:
                        self.log_result("Patient Response Security", False, "Response should not include password field")
                else:
                    self.log_result("Patient Response Security", True, "No patients to verify format (empty list)")
            else:
                self.log_result("Fetch Patients List", False, "Response should be a list")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Fetch Patients List", False, "Failed to fetch patients list", error_msg)
        
        # Test 3: ❌ Try without authentication (should fail with 401)
        response = self.make_request("GET", "/department-head/patients")
        if response and response.status_code == 401:
            self.log_result("Get Patients - No Authentication Test", True, "Correctly rejected request without authentication")
        else:
            self.log_result("Get Patients - No Authentication Test", False, "Should reject request without authentication")
        
        # Test 4: ❌ Try with non-department_head role (should fail with 403)
        response = self.make_request("GET", "/department-head/patients", token=self.patient_token)
        if response and response.status_code == 403:
            self.log_result("Get Patients - Non-Department Head Access Test", True, "Correctly rejected non-department_head access")
        else:
            self.log_result("Get Patients - Non-Department Head Access Test", False, "Should reject non-department_head access")
    
    def test_remove_patient_endpoint(self):
        """Test DELETE /api/department-head/remove-patient/{patient_id}"""
        print("\n=== TESTING DEPARTMENT HEAD REMOVE PATIENT ENDPOINT ===")
        
        if not self.dept_head_token:
            self.log_result("Remove Patient Endpoint", False, "No Department Head token available")
            return
        
        # Test 1: ✅ Delete a patient successfully (use the test patient we created)
        if self.test_patient_id:
            response = self.make_request("DELETE", f"/department-head/remove-patient/{self.test_patient_id}", token=self.dept_head_token)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("message"):
                    self.log_result("Delete Patient Successfully", True, "Successfully deleted patient")
                else:
                    self.log_result("Delete Patient Successfully", False, "Missing message in response")
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result("Delete Patient Successfully", False, "Failed to delete patient", error_msg)
        else:
            self.log_result("Delete Patient Successfully", False, "No test patient ID available")
        
        # Test 2: ❌ Try to delete non-existent patient (should fail with 404)
        fake_patient_id = str(uuid.uuid4())
        response = self.make_request("DELETE", f"/department-head/remove-patient/{fake_patient_id}", token=self.dept_head_token)
        if response and response.status_code == 404:
            self.log_result("Delete Non-existent Patient Test", True, "Correctly returned 404 for non-existent patient")
        else:
            self.log_result("Delete Non-existent Patient Test", False, "Should return 404 for non-existent patient")
        
        # Test 3: ❌ Try without authentication (should fail with 401)
        response = self.make_request("DELETE", f"/department-head/remove-patient/{fake_patient_id}")
        if response and response.status_code == 401:
            self.log_result("Remove Patient - No Authentication Test", True, "Correctly rejected request without authentication")
        else:
            self.log_result("Remove Patient - No Authentication Test", False, "Should reject request without authentication")
        
        # Test 4: ❌ Try with non-department_head role (should fail with 403)
        response = self.make_request("DELETE", f"/department-head/remove-patient/{fake_patient_id}", token=self.patient_token)
        if response and response.status_code == 403:
            self.log_result("Remove Patient - Non-Department Head Access Test", True, "Correctly rejected non-department_head access")
        else:
            self.log_result("Remove Patient - Non-Department Head Access Test", False, "Should reject non-department_head access")
    
    def test_get_stats_endpoint(self):
        """Test GET /api/department-head/stats"""
        print("\n=== TESTING DEPARTMENT HEAD GET STATS ENDPOINT ===")
        
        if not self.dept_head_token:
            self.log_result("Get Stats Endpoint", False, "No Department Head token available")
            return
        
        # Test 1: ✅ Fetch statistics successfully
        response = self.make_request("GET", "/department-head/stats", token=self.dept_head_token)
        if response and response.status_code == 200:
            data = response.json()
            
            # Test 2: ✅ Verify stats include required fields
            required_fields = [
                "total_doctors", "approved_doctors", "pending_doctors",
                "total_patients", "total_appointments", "completed_appointments"
            ]
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                self.log_result("Fetch Statistics Successfully", True, "Successfully fetched all required statistics")
                print(f"   Stats: {data}")
            else:
                self.log_result("Fetch Statistics Successfully", False, f"Missing required fields: {', '.join(missing_fields)}")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Fetch Statistics Successfully", False, "Failed to fetch statistics", error_msg)
        
        # Test 3: ❌ Try without authentication (should fail with 401)
        response = self.make_request("GET", "/department-head/stats")
        if response and response.status_code == 401:
            self.log_result("Get Stats - No Authentication Test", True, "Correctly rejected request without authentication")
        else:
            self.log_result("Get Stats - No Authentication Test", False, "Should reject request without authentication")
        
        # Test 4: ❌ Try with non-department_head role (should fail with 403)
        response = self.make_request("GET", "/department-head/stats", token=self.patient_token)
        if response and response.status_code == 403:
            self.log_result("Get Stats - Non-Department Head Access Test", True, "Correctly rejected non-department_head access")
        else:
            self.log_result("Get Stats - Non-Department Head Access Test", False, "Should reject non-department_head access")
    
    def run_all_tests(self):
        """Run all Department Head tests"""
        print("🏥 Department Head Backend API Testing")
        print("=" * 50)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue with tests.")
            return
        
        # Run all Department Head tests
        self.test_create_user_endpoint()
        self.test_get_doctors_endpoint()
        self.test_get_patients_endpoint()
        self.test_remove_patient_endpoint()
        self.test_get_stats_endpoint()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 DEPARTMENT HEAD TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        print("\n🎯 BACKEND URL USED:", self.base_url)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "department-head":
        # Run only Department Head tests
        tester = DepartmentHeadAPITester()
        tester.run_all_tests()
    else:
        # Run original tests
        tester = MediScheduleAPITester()
        tester.run_all_tests()