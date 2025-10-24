#!/usr/bin/env python3
"""
Focused Backend API Testing for Medical System
Tests previously failing endpoints and newly implemented AI features
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

class FocusedMedicalAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.dept_head_token = None
        self.patient_token = None
        self.doctor_token = None
        self.test_results = []
        self.session_id = None
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
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    print(f"   Error response: {error_data}")
                except:
                    print(f"   Error response: {response.text}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"   Request failed: {str(e)}")
            return None
    
    def setup_authentication(self):
        """Setup authentication for all user types"""
        print("\n=== AUTHENTICATION SETUP ===")
        
        # 1. Login as Root Admin
        admin_login = {
            "email": "admin@medischedule.com",
            "password": "admin123"
        }
        
        response = self.make_request("POST", "/auth/login", admin_login)
        if response and response.status_code == 200:
            data = response.json()
            self.admin_token = data.get("token")
            self.log_result("Root Admin Login", True, "Root admin logged in successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Root Admin Login", False, "Failed to login as root admin", error_msg)
            return False
        
        # 2. Login as Department Head
        dept_head_login = {
            "email": "departmenthead@test.com",
            "password": "dept123"
        }
        
        response = self.make_request("POST", "/auth/login", dept_head_login)
        if response and response.status_code == 200:
            data = response.json()
            self.dept_head_token = data.get("token")
            self.log_result("Department Head Login", True, "Department Head logged in successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Department Head Login", False, "Failed to login as Department Head", error_msg)
            return False
        
        # 3. Create and login as Patient
        test_id = str(uuid.uuid4())[:8]
        patient_data = {
            "email": f"testpatient_{test_id}@test.com",
            "password": "patient123",
            "full_name": "Nguyễn Văn Bệnh Nhân",
            "role": "patient"
        }
        
        response = self.make_request("POST", "/auth/register", patient_data)
        if response and response.status_code == 200:
            data = response.json()
            self.patient_token = data.get("token")
            self.log_result("Patient Registration", True, "Patient registered successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Patient Registration", False, "Failed to register patient", error_msg)
            return False
        
        # 4. Create and login as Doctor
        doctor_data = {
            "email": f"testdoctor_{test_id}@test.com",
            "password": "doctor123",
            "full_name": "Bác sĩ Nguyễn Văn Y",
            "role": "doctor"
        }
        
        response = self.make_request("POST", "/auth/register", doctor_data)
        if response and response.status_code == 200:
            data = response.json()
            self.doctor_token = data.get("token")
            self.log_result("Doctor Registration", True, "Doctor registered successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Doctor Registration", False, "Failed to register doctor", error_msg)
            return False
        
        return True
    
    def test_priority1_previously_failing_endpoints(self):
        """Test Priority 1: Previously Failing Endpoints (Now Fixed)"""
        print("\n=== PRIORITY 1: PREVIOUSLY FAILING ENDPOINTS ===")
        
        # Get specialties for doctor creation
        specialties_response = self.make_request("GET", "/specialties")
        specialty_id = None
        if specialties_response and specialties_response.status_code == 200:
            specialties = specialties_response.json()
            if specialties:
                specialty_id = specialties[0]["id"]
        
        test_id = str(uuid.uuid4())[:8]
        
        # Test 1: POST /api/department-head/create-user - Patient creation
        patient_data = {
            "email": f"deptpatient_{test_id}@test.com",
            "password": "patient123",
            "full_name": "Bệnh nhân từ Trưởng khoa",
            "role": "patient",
            "phone": "0123456789",
            "date_of_birth": "1990-05-15",
            "address": "123 Đường ABC, TP.HCM"
        }
        
        response = self.make_request("POST", "/department-head/create-user", patient_data, token=self.dept_head_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("user"):
                self.log_result("Department Head Create Patient", True, "Successfully created patient account")
            else:
                self.log_result("Department Head Create Patient", False, "Missing message or user in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Department Head Create Patient", False, "Failed to create patient account", error_msg)
        
        # Test 2: POST /api/department-head/create-user - Doctor creation
        if specialty_id:
            doctor_data = {
                "email": f"deptdoctor_{test_id}@test.com",
                "password": "doctor123",
                "full_name": "Bác sĩ từ Trưởng khoa",
                "role": "doctor",
                "phone": "0987654321",
                "specialty_id": specialty_id,
                "bio": "Bác sĩ có kinh nghiệm 5 năm",
                "experience_years": 5,
                "consultation_fee": 300000
            }
            
            response = self.make_request("POST", "/department-head/create-user", doctor_data, token=self.dept_head_token)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("message") and data.get("user"):
                    self.log_result("Department Head Create Doctor", True, "Successfully created doctor account")
                else:
                    self.log_result("Department Head Create Doctor", False, "Missing message or user in response")
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result("Department Head Create Doctor", False, "Failed to create doctor account", error_msg)
        else:
            self.log_result("Department Head Create Doctor", False, "No specialty available for doctor creation")
        
        # Test 3: POST /api/admin/create-admin - Admin creation
        admin_data = {
            "email": f"newadmin_{test_id}@test.com",
            "password": "admin123",
            "full_name": "Admin Mới",
            "admin_permissions": {
                "can_manage_doctors": True,
                "can_manage_patients": True,
                "can_manage_appointments": True,
                "can_view_stats": True,
                "can_manage_specialties": False,
                "can_create_admins": False
            }
        }
        
        response = self.make_request("POST", "/admin/create-admin", admin_data, token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("user"):
                self.log_result("Admin Create Admin", True, "Successfully created admin account")
            else:
                self.log_result("Admin Create Admin", False, "Missing message or user in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Admin Create Admin", False, "Failed to create admin account", error_msg)
        
        # Test 4: POST /api/admin/create-user - Creating all roles
        # Patient
        admin_patient_data = {
            "email": f"adminpatient_{test_id}@test.com",
            "password": "patient123",
            "full_name": "Bệnh nhân từ Admin",
            "role": "patient",
            "phone": "0111222333",
            "date_of_birth": "1985-03-20",
            "address": "456 Đường XYZ, Hà Nội"
        }
        
        response = self.make_request("POST", "/admin/create-user", admin_patient_data, token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("user"):
                self.log_result("Admin Create Patient", True, "Successfully created patient account")
            else:
                self.log_result("Admin Create Patient", False, "Missing message or user in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Admin Create Patient", False, "Failed to create patient account", error_msg)
        
        # Doctor
        if specialty_id:
            admin_doctor_data = {
                "email": f"admindoctor_{test_id}@test.com",
                "password": "doctor123",
                "full_name": "Bác sĩ từ Admin",
                "role": "doctor",
                "phone": "0444555666",
                "specialty_id": specialty_id,
                "bio": "Bác sĩ chuyên khoa",
                "experience_years": 8,
                "consultation_fee": 500000
            }
            
            response = self.make_request("POST", "/admin/create-user", admin_doctor_data, token=self.admin_token)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("message") and data.get("user"):
                    self.log_result("Admin Create Doctor", True, "Successfully created doctor account")
                else:
                    self.log_result("Admin Create Doctor", False, "Missing message or user in response")
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result("Admin Create Doctor", False, "Failed to create doctor account", error_msg)
        
        # Department Head
        admin_dept_head_data = {
            "email": f"admindepthead_{test_id}@test.com",
            "password": "dept123",
            "full_name": "Trưởng khoa từ Admin",
            "role": "department_head",
            "phone": "0777888999"
        }
        
        response = self.make_request("POST", "/admin/create-user", admin_dept_head_data, token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("message") and data.get("user"):
                self.log_result("Admin Create Department Head", True, "Successfully created department head account")
            else:
                self.log_result("Admin Create Department Head", False, "Missing message or user in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Admin Create Department Head", False, "Failed to create department head account", error_msg)
    
    def test_priority2_ai_features(self):
        """Test Priority 2: Newly Implemented AI Features"""
        print("\n=== PRIORITY 2: AI FEATURES ===")
        
        # Test 1: POST /api/ai/chat - Health consultation chatbot
        chat_data = {
            "message": "Tôi bị đau đầu và sốt từ 3 ngày nay, tôi nên làm gì?"
        }
        
        response = self.make_request("POST", "/ai/chat", chat_data, token=self.patient_token)
        if response and response.status_code == 200:
            data = response.json()
            ai_response = data.get("response", "")
            session_id = data.get("session_id", "")
            
            if ai_response and session_id:
                self.session_id = session_id
                self.log_result("AI Health Consultation", True, f"AI responded with {len(ai_response)} characters")
                print(f"   AI Response: {ai_response[:150]}...")
                print(f"   Session ID: {session_id}")
            else:
                self.log_result("AI Health Consultation", False, "Missing response or session_id")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("AI Health Consultation", False, "AI chat request failed", error_msg)
        
        # Test 2: Continue conversation with session_id
        if self.session_id:
            follow_up_data = {
                "message": "Tôi cũng bị buồn nôn nữa, điều này có nghiêm trọng không?",
                "session_id": self.session_id
            }
            
            response = self.make_request("POST", "/ai/chat", follow_up_data, token=self.patient_token)
            if response and response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "")
                returned_session_id = data.get("session_id", "")
                
                if ai_response and returned_session_id == self.session_id:
                    self.log_result("AI Chat Session Continuity", True, "Successfully continued conversation with same session")
                else:
                    self.log_result("AI Chat Session Continuity", False, "Session continuity failed")
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result("AI Chat Session Continuity", False, "Follow-up chat failed", error_msg)
        
        # Test 3: POST /api/ai/recommend-doctor - Doctor recommendation
        symptoms_data = {
            "symptoms": "Tôi bị đau bụng dữ dội, buồn nôn và tiêu chảy từ 3 ngày nay"
        }
        
        response = self.make_request("POST", "/ai/recommend-doctor", symptoms_data, token=self.patient_token)
        if response and response.status_code == 200:
            data = response.json()
            specialty = data.get("recommended_specialty", "")
            doctors = data.get("recommended_doctors", [])
            explanation = data.get("explanation", "")
            urgency = data.get("urgency_level", "")
            
            if specialty and explanation:
                self.log_result("AI Doctor Recommendation", True, f"Recommended specialty: {specialty}")
                print(f"   Explanation: {explanation[:100]}...")
                print(f"   Urgency Level: {urgency}")
                print(f"   Recommended Doctors: {len(doctors)}")
            else:
                self.log_result("AI Doctor Recommendation", False, "Missing specialty or explanation")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("AI Doctor Recommendation", False, "AI recommendation failed", error_msg)
        
        # Test 4: GET /api/ai/chat-history - Chat history retrieval
        response = self.make_request("GET", "/ai/chat-history", token=self.patient_token)
        if response and response.status_code == 200:
            data = response.json()
            sessions = data.get("sessions", {})
            total_messages = data.get("total_messages", 0)
            
            if isinstance(sessions, dict) and total_messages >= 0:
                self.log_result("AI Chat History - All Sessions", True, f"Retrieved {len(sessions)} sessions with {total_messages} total messages")
            else:
                self.log_result("AI Chat History - All Sessions", False, "Invalid response format")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("AI Chat History - All Sessions", False, "Failed to get chat history", error_msg)
        
        # Test 5: GET /api/ai/chat-history with session_id filter
        if self.session_id:
            response = self.make_request("GET", f"/ai/chat-history?session_id={self.session_id}", token=self.patient_token)
            if response and response.status_code == 200:
                data = response.json()
                sessions = data.get("sessions", {})
                
                if self.session_id in sessions:
                    session_messages = sessions[self.session_id]
                    self.log_result("AI Chat History - Specific Session", True, f"Retrieved {len(session_messages)} messages for session")
                else:
                    self.log_result("AI Chat History - Specific Session", False, "Session not found in response")
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result("AI Chat History - Specific Session", False, "Failed to get session history", error_msg)
        
        # Test 6: POST /api/ai/summarize-conversation/{appointment_id} - Conversation summary
        # First create an appointment and some chat messages
        appointment_created = self.create_test_appointment_and_messages()
        
        if appointment_created and self.appointment_id:
            response = self.make_request("POST", f"/ai/summarize-conversation/{self.appointment_id}", token=self.doctor_token)
            if response and response.status_code == 200:
                data = response.json()
                summary = data.get("summary", "")
                key_points = data.get("key_points", [])
                symptoms = data.get("symptoms_mentioned", [])
                recommendations = data.get("recommendations", [])
                
                if summary:
                    self.log_result("AI Conversation Summary", True, "Successfully generated conversation summary")
                    print(f"   Summary: {summary[:100]}...")
                    print(f"   Key Points: {len(key_points)}")
                    print(f"   Symptoms: {len(symptoms)}")
                    print(f"   Recommendations: {len(recommendations)}")
                else:
                    self.log_result("AI Conversation Summary", False, "Missing summary in response")
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result("AI Conversation Summary", False, "Failed to summarize conversation", error_msg)
        else:
            self.log_result("AI Conversation Summary", False, "Could not create test appointment for summary")
    
    def create_test_appointment_and_messages(self):
        """Create a test appointment and send some messages for conversation summary testing"""
        # Get doctor ID from doctor token
        response = self.make_request("GET", "/auth/me", token=self.doctor_token)
        if not response or response.status_code != 200:
            return False
        
        doctor_data = response.json()
        doctor_id = doctor_data.get("id")
        
        if not doctor_id:
            return False
        
        # Create appointment
        appointment_data = {
            "doctor_id": doctor_id,
            "appointment_type": "online",
            "appointment_date": "2024-12-25",
            "appointment_time": "14:00",
            "symptoms": "Đau bụng và buồn nôn"
        }
        
        response = self.make_request("POST", "/appointments", appointment_data, token=self.patient_token)
        if not response or response.status_code != 200:
            return False
        
        appointment = response.json()
        self.appointment_id = appointment.get("id")
        
        if not self.appointment_id:
            return False
        
        # Send test messages
        messages = [
            {"token": self.patient_token, "message": "Xin chào bác sĩ, tôi bị đau bụng và buồn nôn từ sáng nay"},
            {"token": self.doctor_token, "message": "Chào bạn, bạn có ăn gì lạ không? Đau bụng ở vị trí nào?"},
            {"token": self.patient_token, "message": "Tôi ăn hải sản tối qua, đau ở vùng bụng dưới"},
            {"token": self.doctor_token, "message": "Có thể là ngộ độc thực phẩm nhẹ. Bạn nên uống nhiều nước và nghỉ ngơi. Nếu không khỏi sau 24h thì đến bệnh viện."}
        ]
        
        for msg in messages:
            message_data = {
                "appointment_id": self.appointment_id,
                "message": msg["message"]
            }
            response = self.make_request("POST", "/chat/send", message_data, token=msg["token"])
            if not response or response.status_code != 200:
                return False
        
        return True
    
    def test_authentication_and_authorization(self):
        """Test authentication and authorization for AI endpoints"""
        print("\n=== AI ENDPOINTS AUTHENTICATION TESTS ===")
        
        # Test unauthorized access to AI endpoints
        test_data = {"message": "Test message"}
        
        # Test without token
        response = self.make_request("POST", "/ai/chat", test_data)
        if response and response.status_code == 401:
            self.log_result("AI Chat - No Auth", True, "Correctly rejected unauthorized access")
        else:
            self.log_result("AI Chat - No Auth", False, "Should reject unauthorized access")
        
        # Test with wrong role (admin trying to use patient endpoint)
        response = self.make_request("POST", "/ai/chat", test_data, token=self.admin_token)
        if response and response.status_code in [403, 401]:
            self.log_result("AI Chat - Wrong Role", True, "Correctly rejected admin access to patient endpoint")
        else:
            self.log_result("AI Chat - Wrong Role", False, "Should reject admin access to patient endpoint")
        
        # Test doctor recommendation without auth
        symptoms_data = {"symptoms": "Test symptoms"}
        response = self.make_request("POST", "/ai/recommend-doctor", symptoms_data)
        if response and response.status_code == 401:
            self.log_result("AI Recommend - No Auth", True, "Correctly rejected unauthorized access")
        else:
            self.log_result("AI Recommend - No Auth", False, "Should reject unauthorized access")
        
        # Test chat history without auth
        response = self.make_request("GET", "/ai/chat-history")
        if response and response.status_code == 401:
            self.log_result("AI History - No Auth", True, "Correctly rejected unauthorized access")
        else:
            self.log_result("AI History - No Auth", False, "Should reject unauthorized access")
    
    def run_all_tests(self):
        """Run all focused tests"""
        print("🏥 Medical System Backend API - Focused Testing")
        print("Testing Previously Failing Endpoints & New AI Features")
        print("=" * 60)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue with tests.")
            return
        
        # Run focused tests
        self.test_priority1_previously_failing_endpoints()
        self.test_priority2_ai_features()
        self.test_authentication_and_authorization()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 FOCUSED TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group results by category
        priority1_tests = [r for r in self.test_results if "Department Head" in r["test"] or "Admin Create" in r["test"]]
        ai_tests = [r for r in self.test_results if "AI" in r["test"]]
        auth_tests = [r for r in self.test_results if "Auth" in r["test"] or "No Auth" in r["test"] or "Wrong Role" in r["test"]]
        
        print(f"\n📋 CATEGORY BREAKDOWN:")
        print(f"Priority 1 (Previously Failing): {len([r for r in priority1_tests if r['success']])}/{len(priority1_tests)} passed")
        print(f"Priority 2 (AI Features): {len([r for r in ai_tests if r['success']])}/{len(ai_tests)} passed")
        print(f"Authentication Tests: {len([r for r in auth_tests if r['success']])}/{len(auth_tests)} passed")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
                    if result.get("details"):
                        print(f"      Details: {result['details']}")
        
        print(f"\n🎯 BACKEND URL USED: {self.base_url}")
        
        # Summary for main agent
        print(f"\n🤖 SUMMARY FOR MAIN AGENT:")
        if failed_tests == 0:
            print("✅ ALL TESTS PASSED - Previously failing endpoints are now working and AI features are fully functional!")
        else:
            print(f"⚠️  {failed_tests} tests failed - Review the failed tests above for issues that need fixing")

if __name__ == "__main__":
    tester = FocusedMedicalAPITester()
    tester.run_all_tests()