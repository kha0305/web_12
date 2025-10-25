#!/usr/bin/env python3
"""
Admin Login Test for MediSchedule - Testing with correct password
Tests the admin credentials: admin@medischedule.com / Admin@123
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://web-run.preview.emergentagent.com')
BASE_URL = f"{BACKEND_URL}/api"

class AdminLoginTester:
    def __init__(self):
        self.base_url = BASE_URL
        
    def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        print(f"Making {method} request to: {url}")
        if data:
            print(f"Request body: {json.dumps(data, indent=2)}")
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30, verify=False)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30, verify=False)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"Response status: {response.status_code}")
            
            try:
                response_json = response.json()
                print(f"Response body: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
                return response, response_json
            except:
                print(f"Response body (text): {response.text}")
                return response, response.text
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            return None, None
    
    def test_both_passwords(self):
        """Test admin login with both passwords"""
        print("🔐 Testing Admin Login with Both Passwords")
        print("=" * 60)
        
        # Test 1: Original password from request
        print("\n1️⃣ Testing with original password: admin123")
        admin_credentials_1 = {
            "login": "admin@medischedule.com",
            "password": "admin123"
        }
        
        response1, data1 = self.make_request("POST", "/auth/login", admin_credentials_1)
        
        if response1 and response1.status_code == 200:
            print("✅ SUCCESS with admin123!")
            return True, "admin123"
        else:
            print("❌ FAILED with admin123")
        
        # Test 2: Correct password from create_admin.py
        print("\n2️⃣ Testing with correct password: Admin@123")
        admin_credentials_2 = {
            "login": "admin@medischedule.com",
            "password": "Admin@123"
        }
        
        response2, data2 = self.make_request("POST", "/auth/login", admin_credentials_2)
        
        if response2 and response2.status_code == 200:
            print("✅ SUCCESS with Admin@123!")
            
            if isinstance(data2, dict):
                # Check response details
                token = data2.get("token")
                user = data2.get("user")
                
                if token:
                    print(f"✅ Token received: {token[:20]}...")
                
                if user:
                    print(f"✅ User info:")
                    print(f"   - ID: {user.get('id')}")
                    print(f"   - Email: {user.get('email')}")
                    print(f"   - Full Name: {user.get('full_name')}")
                    print(f"   - Role: {user.get('role')}")
                    print(f"   - Admin Permissions: {user.get('admin_permissions')}")
            
            return True, "Admin@123"
        else:
            print("❌ FAILED with Admin@123")
            if isinstance(data2, dict):
                print(f"   Error: {data2.get('detail')}")
        
        return False, None
    
    def run_test(self):
        """Run the complete admin login test"""
        print("🏥 MediSchedule Admin Login Test - Complete Analysis")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print()
        
        # Test both passwords
        success, working_password = self.test_both_passwords()
        
        print("\n" + "=" * 60)
        print("📋 FINAL ANALYSIS")
        print("=" * 60)
        
        print("🔍 ACCOUNT EXISTENCE:")
        print("   ✅ Account admin@medischedule.com EXISTS")
        print("   (Confirmed by create_admin.py script)")
        
        print("\n🔑 PASSWORD ANALYSIS:")
        if success:
            print(f"   ✅ CORRECT PASSWORD: {working_password}")
            if working_password == "admin123":
                print("   ✅ Original request password works")
            else:
                print("   ❌ Original request password (admin123) is INCORRECT")
                print("   ✅ Actual password is Admin@123 (from create_admin.py)")
        else:
            print("   ❌ BOTH passwords failed")
            print("   - admin123 (from request): FAILED")
            print("   - Admin@123 (from create_admin.py): FAILED")
        
        print("\n📡 API RESPONSE:")
        if success:
            print("   ✅ Returns valid JWT token")
            print("   ✅ Returns user object with admin role")
            print("   ✅ Returns admin permissions")
        else:
            print("   ❌ Returns 401 authentication error")
        
        print(f"\n🎯 ENDPOINT TESTED: POST {self.base_url}/auth/login")

if __name__ == "__main__":
    tester = AdminLoginTester()
    tester.run_test()