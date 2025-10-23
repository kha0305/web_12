#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Medical System
Tests all implemented endpoints with proper validation
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
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://continue-project-7.preview.emergentagent.com')
BASE_URL = f"{BACKEND_URL}/api"

class ComprehensiveAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.dept_head_token = None
        self.admin_token = None
        self.patient_token = None
        self.test_patient_id = None
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
    
    def test_department_head_create_user(self):
        """Test Department Head Create User endpoint with proper validation"""
        print("\n=== DEPARTMENT HEAD CREATE USER TESTING ===")
        
        if not self.dept_head_token:
            self.log_result("Department Head Create User", False, "No Department Head token available")
            return
        
        # Get specialties for doctor creation
        specialties_response = self.make_request("GET", "/specialties")
        specialty_id = None
        if specialties_response and specialties_response.status_code == 200:
            specialties = specialties_response.json()
            if specialties:
                specialty_id = specialties[0]["id"]
        
        test_id = str(uuid.uuid4())[:8]
        
        # Test 1: Create patient account (should work)
        patient_data = {
            "email": f"testpatient_{test_id}@test.com",
            "password": "patient123",
            "full_name": "Test Patient Created by Dept Head",
            "role": "patient",
            "phone": "0123456789",
            "date_of_birth": "1990-01-01",
            "address": "123 Test Street"
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
        
        # Test 2: Create doctor account (should work)
        if specialty_id:
            doctor_data = {
                "email": f"testdoctor_{test_id}@test.com",
                "password": "doctor123",
                "full_name": "Test Doctor Created by Dept Head",
                "role": "doctor",
                "phone": "0987654321",
                "specialty_id": specialty_id,
                "bio": "Test doctor bio",
                "experience_years": 5,
                "consultation_fee": 300000
            }
            
            response = self.make_request("POST", "/department-head/create-user", doctor_data, token=self.dept_head_token)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("message") and data.get("user"):
                    self.log_result("Create Doctor Account", True, "Successfully created doctor account")
                else:
                    self.log_result("Create Doctor Account", False, "Missing message or user in response")
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result("Create Doctor Account", False, "Failed to create doctor account", error_msg)
        
        # Test 3: Try to create admin account (should be rejected)
        admin_data = {
            "email": f"testadmin_{test_id}@test.com",
            "password": "admin123",
            "full_name": "Test Admin",
            "role": "admin"
        }
        
        response = self.make_request("POST", "/department-head/create-user", admin_data, token=self.dept_head_token)
        if response and response.status_code == 403:
            self.log_result("Reject Admin Creation", True, "Correctly rejected admin account creation")
        else:
            self.log_result("Reject Admin Creation", False, "Should reject admin account creation")
        
        # Test 4: Try to create department_head account (should be rejected)
        dept_head_data = {
            "email": f"testdepthead_{test_id}@test.com",
            "password": "dept123",
            "full_name": "Test Department Head",
            "role": "department_head"
        }
        
        response = self.make_request("POST", "/department-head/create-user", dept_head_data, token=self.dept_head_token)
        if response and response.status_code == 403:
            self.log_result("Reject Department Head Creation", True, "Correctly rejected department_head account creation")
        else:
            self.log_result("Reject Department Head Creation", False, "Should reject department_head account creation")
    
    def test_department_head_get_endpoints(self):
        """Test Department Head GET endpoints"""
        print("\n=== DEPARTMENT HEAD GET ENDPOINTS TESTING ===")
        
        if not self.dept_head_token:
            self.log_result("Department Head GET Endpoints", False, "No Department Head token available")
            return
        
        # Test 1: GET /api/department-head/doctors
        response = self.make_request("GET", "/department-head/doctors", token=self.dept_head_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("GET Doctors List", True, f"Successfully fetched {len(data)} doctors")
                
                # Verify response format
                if data:
                    doctor = data[0]
                    has_user_info = "user_info" in doctor
                    has_specialty_name = "specialty_name" in doctor
                    
                    if has_user_info and has_specialty_name:
                        self.log_result("Doctors Response Format", True, "Response includes user_info and specialty_name")
                    else:
                        missing_fields = []
                        if not has_user_info:
                            missing_fields.append("user_info")
                        if not has_specialty_name:
                            missing_fields.append("specialty_name")
                        self.log_result("Doctors Response Format", False, f"Missing fields: {', '.join(missing_fields)}")
            else:
                self.log_result("GET Doctors List", False, "Response should be a list")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("GET Doctors List", False, "Failed to fetch doctors", error_msg)
        
        # Test 2: GET /api/department-head/patients
        response = self.make_request("GET", "/department-head/patients", token=self.dept_head_token)
        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                self.log_result("GET Patients List", True, f"Successfully fetched {len(data)} patients")
                
                # Verify password is excluded
                if data:
                    patient = data[0]
                    has_password = "password" in patient
                    
                    if not has_password:
                        self.log_result("Patients Security Check", True, "Response correctly excludes password field")
                    else:
                        self.log_result("Patients Security Check", False, "Response should not include password field")
            else:
                self.log_result("GET Patients List", False, "Response should be a list")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("GET Patients List", False, "Failed to fetch patients", error_msg)
        
        # Test 3: GET /api/department-head/stats
        response = self.make_request("GET", "/department-head/stats", token=self.dept_head_token)
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ["total_doctors", "approved_doctors", "pending_doctors", "total_patients", "total_appointments", "completed_appointments"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                self.log_result("GET Statistics", True, "Successfully fetched all required statistics")
                print(f"   Stats: {data}")
            else:
                self.log_result("GET Statistics", False, f"Missing required fields: {', '.join(missing_fields)}")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("GET Statistics", False, "Failed to fetch statistics", error_msg)
    
    def test_department_head_remove_patient(self):
        """Test Department Head Remove Patient endpoint"""
        print("\n=== DEPARTMENT HEAD REMOVE PATIENT TESTING ===")
        
        if not self.dept_head_token:
            self.log_result("Department Head Remove Patient", False, "No Department Head token available")
            return
        
        # Test 1: Remove the test patient we created
        if self.test_patient_id:
            response = self.make_request("DELETE", f"/department-head/remove-patient/{self.test_patient_id}", token=self.dept_head_token)
            if response and response.status_code == 200:
                data = response.json()
                if data.get("message"):
                    self.log_result("Remove Patient Successfully", True, "Successfully removed patient")
                else:
                    self.log_result("Remove Patient Successfully", False, "Missing message in response")
            else:
                error_msg = response.text if response else "Connection failed"
                self.log_result("Remove Patient Successfully", False, "Failed to remove patient", error_msg)
        else:
            self.log_result("Remove Patient Successfully", False, "No test patient ID available")
        
        # Test 2: Try to remove non-existent patient
        fake_patient_id = str(uuid.uuid4())
        response = self.make_request("DELETE", f"/department-head/remove-patient/{fake_patient_id}", token=self.dept_head_token)
        if response and response.status_code == 404:
            self.log_result("Remove Non-existent Patient", True, "Correctly returned 404 for non-existent patient")
        else:
            self.log_result("Remove Non-existent Patient", False, "Should return 404 for non-existent patient")
    
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
            if isinstance(data, list):
                self.log_result("GET Admin List", True, f"Successfully fetched {len(data)} admins")
            else:
                self.log_result("GET Admin List", False, "Response should be a list")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("GET Admin List", False, "Failed to fetch admins", error_msg)
        
        # Test 2: POST /api/admin/create-admin (Create limited admin)
        test_id = str(uuid.uuid4())[:8]
        limited_admin_data = {
            "email": f"limitedadmin_{test_id}@test.com",
            "password": "admin123",
            "full_name": "Limited Admin Test",
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
                self.log_result("Create Limited Admin", True, "Successfully created limited admin account")
            else:
                self.log_result("Create Limited Admin", False, "Missing message or user in response")
        else:
            error_msg = response.text if response else "Connection failed"
            self.log_result("Create Limited Admin", False, "Failed to create limited admin account", error_msg)
    
    def test_ai_endpoints_status(self):
        """Test AI endpoints status (should return 404 since not implemented)"""
        print("\n=== AI ENDPOINTS STATUS CHECK ===")
        
        if not self.patient_token:
            self.log_result("AI Endpoints Status", False, "No Patient token available")
            return
        
        ai_endpoints = [
            ("POST", "/ai/chat", {"message": "Test health question"}),
            ("POST", "/ai/recommend-doctor", {"symptoms": "Test symptoms"}),
            ("GET", "/ai/chat-history", None),
            ("POST", f"/ai/summarize-conversation/{str(uuid.uuid4())}", None)
        ]
        
        for method, endpoint, data in ai_endpoints:
            response = self.make_request(method, endpoint, data, token=self.patient_token)
            if response and response.status_code == 404:
                self.log_result(f"AI Endpoint {method} {endpoint}", True, "Correctly returned 404 - Not implemented")
            else:
                self.log_result(f"AI Endpoint {method} {endpoint}", False, f"Expected 404, got {response.status_code if response else 'No response'}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🏥 Medical System Comprehensive Backend API Testing")
        print("=" * 60)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue with tests.")
            return
        
        # Run tests in order
        self.test_department_head_create_user()
        self.test_department_head_get_endpoints()
        self.test_department_head_remove_patient()
        self.test_admin_endpoints()
        self.test_ai_endpoints_status()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Categorize results
        dept_head_tests = [r for r in self.test_results if "Department Head" in r["test"] or "GET" in r["test"] or "Remove" in r["test"] or "Create" in r["test"] or "Reject" in r["test"]]
        admin_tests = [r for r in self.test_results if "Admin" in r["test"] and "Department Head" not in r["test"]]
        ai_tests = [r for r in self.test_results if "AI Endpoint" in r["test"]]
        auth_tests = [r for r in self.test_results if "Login" in r["test"]]
        
        print(f"\n📋 RESULTS BY CATEGORY:")
        print(f"🔐 Authentication: {len([r for r in auth_tests if r['success']])}/{len(auth_tests)} passed")
        print(f"👔 Department Head: {len([r for r in dept_head_tests if r['success']])}/{len(dept_head_tests)} passed")
        print(f"👑 Admin: {len([r for r in admin_tests if r['success']])}/{len(admin_tests)} passed")
        print(f"🤖 AI Endpoints: {len([r for r in ai_tests if r['success']])}/{len(ai_tests)} passed")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        print("\n🎯 BACKEND URL USED:", self.base_url)

if __name__ == "__main__":
    tester = ComprehensiveAPITester()
    tester.run_all_tests()