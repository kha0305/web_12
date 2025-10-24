#!/usr/bin/env python3
"""
Focused Backend API Testing for Medical System
Tests only implemented endpoints
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

class FocusedAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.dept_head_token = None
        self.admin_token = None
        self.patient_token = None
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
        """Setup authentication tokens"""
        print("\n=== AUTHENTICATION SETUP ===")
        
        # 1. Login as Department Head
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
        
        # 2. Login as Admin
        admin_login = {
            "email": "admin@medischedule.com",
            "password": "admin123"
        }
        
        response = self.make_request("POST", "/auth/login", admin_login)
        if response and response.status_code == 200:
            data = response.json()
            self.admin_token = data.get("token")
            self.log_result("Admin Login", True, "Admin logged in successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Admin Login", False, "Failed to login as Admin", error_msg)
            return False
        
        # 3. Login as Patient
        patient_login = {
            "email": "patient1@test.com",
            "password": "patient123"
        }
        
        response = self.make_request("POST", "/auth/login", patient_login)
        if response and response.status_code == 200:
            data = response.json()
            self.patient_token = data.get("token")
            self.log_result("Patient Login", True, "Patient logged in successfully")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Patient Login", False, "Failed to login as Patient", error_msg)
        
        return True
    
    def test_department_head_endpoints(self):
        """Test Department Head endpoints"""
        print("\n=== DEPARTMENT HEAD ENDPOINTS TESTING ===")
        
        if not self.dept_head_token:
            self.log_result("Department Head Endpoints", False, "No Department Head token available")
            return
        
        # Test 1: GET /api/department-head/doctors
        response = self.make_request("GET", "/department-head/doctors", token=self.dept_head_token)
        if response and response.status_code == 200:
            data = response.json()
            self.log_result("GET /department-head/doctors", True, f"Successfully fetched {len(data)} doctors")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("GET /department-head/doctors", False, "Failed to fetch doctors", error_msg)
        
        # Test 2: GET /api/department-head/patients
        response = self.make_request("GET", "/department-head/patients", token=self.dept_head_token)
        if response and response.status_code == 200:
            data = response.json()
            self.log_result("GET /department-head/patients", True, f"Successfully fetched {len(data)} patients")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("GET /department-head/patients", False, "Failed to fetch patients", error_msg)
        
        # Test 3: GET /api/department-head/stats
        response = self.make_request("GET", "/department-head/stats", token=self.dept_head_token)
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ["total_doctors", "approved_doctors", "pending_doctors", "total_patients", "total_appointments", "completed_appointments"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                self.log_result("GET /department-head/stats", True, "Successfully fetched all required statistics")
                print(f"   Stats: {data}")
            else:
                self.log_result("GET /department-head/stats", False, f"Missing required fields: {', '.join(missing_fields)}")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("GET /department-head/stats", False, "Failed to fetch statistics", error_msg)
        
        # Test 4: POST /api/department-head/create-user (Test role validation)
        test_admin_data = {
            "email": f"testadmin_{str(uuid.uuid4())[:8]}@test.com",
            "password": "admin123",
            "full_name": "Test Admin",
            "role": "admin"
        }
        
        response = self.make_request("POST", "/department-head/create-user", test_admin_data, token=self.dept_head_token)
        if response and response.status_code == 403:
            self.log_result("POST /department-head/create-user (Admin Role Rejection)", True, "Correctly rejected admin role creation")
        else:
            self.log_result("POST /department-head/create-user (Admin Role Rejection)", False, "Should reject admin role creation")
        
        # Test 5: POST /api/department-head/create-user (Test department_head role validation)
        test_dept_head_data = {
            "email": f"testdepthead_{str(uuid.uuid4())[:8]}@test.com",
            "password": "dept123",
            "full_name": "Test Department Head",
            "role": "department_head"
        }
        
        response = self.make_request("POST", "/department-head/create-user", test_dept_head_data, token=self.dept_head_token)
        if response and response.status_code == 403:
            self.log_result("POST /department-head/create-user (Department Head Role Rejection)", True, "Correctly rejected department_head role creation")
        else:
            self.log_result("POST /department-head/create-user (Department Head Role Rejection)", False, "Should reject department_head role creation")
    
    def test_admin_endpoints(self):
        """Test Admin endpoints"""
        print("\n=== ADMIN ENDPOINTS TESTING ===")
        
        if not self.admin_token:
            self.log_result("Admin Endpoints", False, "No Admin token available")
            return
        
        # Test 1: GET /api/admin/admins
        response = self.make_request("GET", "/admin/admins", token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            self.log_result("GET /admin/admins", True, f"Successfully fetched {len(data)} admins")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("GET /admin/admins", False, "Failed to fetch admins", error_msg)
        
        # Test 2: POST /api/admin/create-user (Create patient)
        test_id = str(uuid.uuid4())[:8]
        patient_data = {
            "email": f"testpatient_{test_id}@test.com",
            "password": "patient123",
            "full_name": "Test Patient Admin Created",
            "role": "patient",
            "phone": "0123456789",
            "date_of_birth": "1990-01-01",
            "address": "123 Test Street"
        }
        
        response = self.make_request("POST", "/admin/create-user", patient_data, token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            self.log_result("POST /admin/create-user (Patient)", True, "Successfully created patient account")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("POST /admin/create-user (Patient)", False, "Failed to create patient account", error_msg)
    
    def test_ai_endpoints(self):
        """Test AI endpoints (should return 404 since not implemented)"""
        print("\n=== AI ENDPOINTS TESTING (Expected 404) ===")
        
        if not self.patient_token:
            self.log_result("AI Endpoints", False, "No Patient token available")
            return
        
        # Test 1: POST /api/ai/chat
        chat_data = {"message": "Test health question"}
        response = self.make_request("POST", "/ai/chat", chat_data, token=self.patient_token)
        if response and response.status_code == 404:
            self.log_result("POST /ai/chat", True, "Correctly returned 404 - AI endpoint not implemented")
        else:
            self.log_result("POST /ai/chat", False, "Expected 404 for unimplemented AI endpoint")
        
        # Test 2: POST /api/ai/recommend-doctor
        symptoms_data = {"symptoms": "Test symptoms"}
        response = self.make_request("POST", "/ai/recommend-doctor", symptoms_data, token=self.patient_token)
        if response and response.status_code == 404:
            self.log_result("POST /ai/recommend-doctor", True, "Correctly returned 404 - AI endpoint not implemented")
        else:
            self.log_result("POST /ai/recommend-doctor", False, "Expected 404 for unimplemented AI endpoint")
        
        # Test 3: GET /api/ai/chat-history
        response = self.make_request("GET", "/ai/chat-history", token=self.patient_token)
        if response and response.status_code == 404:
            self.log_result("GET /ai/chat-history", True, "Correctly returned 404 - AI endpoint not implemented")
        else:
            self.log_result("GET /ai/chat-history", False, "Expected 404 for unimplemented AI endpoint")
        
        # Test 4: POST /api/ai/summarize-conversation/{appointment_id}
        fake_appointment_id = str(uuid.uuid4())
        response = self.make_request("POST", f"/ai/summarize-conversation/{fake_appointment_id}", token=self.patient_token)
        if response and response.status_code == 404:
            self.log_result("POST /ai/summarize-conversation", True, "Correctly returned 404 - AI endpoint not implemented")
        else:
            self.log_result("POST /ai/summarize-conversation", False, "Expected 404 for unimplemented AI endpoint")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🏥 Medical System Backend API Testing")
        print("=" * 50)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue with tests.")
            return
        
        # Run tests
        self.test_department_head_endpoints()
        self.test_admin_endpoints()
        self.test_ai_endpoints()
        
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
    tester = FocusedAPITester()
    tester.run_all_tests()