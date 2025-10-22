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
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://node-html-database.preview.emergentagent.com')
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
            "email": f"patient_{test_id}@example.com",
            "password": "patient123",
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
            "email": f"doctor_{test_id}@example.com",
            "password": "doctor123",
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
        
        # 3. Register Admin (first admin - should work without auth)
        admin_data = {
            "email": f"admin_{test_id}@example.com",
            "password": "admin123",
            "full_name": "Quản trị viên Nguyễn",
            "role": "admin"
        }
        
        response = self.make_request("POST", "/auth/register", admin_data)
        if response and response.status_code == 200:
            data = response.json()
            self.admin_token = data.get("token")
            self.admin_id = data.get("user", {}).get("id")
            self.log_result("Admin Registration", True, "Admin registered successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Admin Registration", False, "Failed to register admin", error_msg)
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
        if response and response.status_code == 401:
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
        if response and response.status_code == 401:
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
        if response and response.status_code == 401:
            self.log_result("AI Chat History - Auth Check", True, 
                          "Correctly rejected unauthorized access")
        else:
            self.log_result("AI Chat History - Auth Check", False, 
                          "Should reject unauthorized access")
    
    def test_admin_create_admin(self):
        """Test Admin Create Admin Account"""
        print("\n=== ADMIN CREATE ADMIN TESTING ===")
        
        if not self.admin_token:
            self.log_result("Admin Create Admin", False, "No admin token available")
            return
        
        # Test 1: Valid admin creation
        new_admin_data = {
            "email": f"newadmin_{uuid.uuid4().hex[:8]}@medischedule.test",
            "password": "admin123",
            "full_name": "Quản trị viên mới"
        }
        
        response = self.make_request("POST", "/admin/create-admin", new_admin_data, token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("user"):
                self.log_result("Admin Create Admin", True, "Successfully created new admin account")
            else:
                self.log_result("Admin Create Admin", False, "Missing message or user in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Admin Create Admin", False, "Failed to create admin account", error_msg)
        
        # Test 2: Unauthorized access (patient trying to create admin)
        response = self.make_request("POST", "/admin/create-admin", new_admin_data, token=self.patient_token)
        if response and response.status_code == 403:
            self.log_result("Admin Create Admin - Auth Check", True, 
                          "Correctly rejected patient access")
        else:
            self.log_result("Admin Create Admin - Auth Check", False, 
                          "Should reject patient access")
        
        # Test 3: No token
        response = self.make_request("POST", "/admin/create-admin", new_admin_data)
        if response and response.status_code == 401:
            self.log_result("Admin Create Admin - No Token", True, 
                          "Correctly rejected unauthorized access")
        else:
            self.log_result("Admin Create Admin - No Token", False, 
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
        self.test_admin_create_admin()
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

if __name__ == "__main__":
    tester = MediScheduleAPITester()
    tester.run_all_tests()