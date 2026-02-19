import requests
import sys
import json
from datetime import datetime

class TTIAPITester:
    def __init__(self, base_url="https://ett-india.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = f"test_user_{datetime.now().strftime('%H%M%S')}@example.com"
        self.test_user_password = "TestPass123!"
        self.test_user_name = "Test User"

    def run_test(self, name, method, endpoint, expected_status, data=None, auth_required=False):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}" if endpoint else f"{self.base_url}/api"
        headers = {'Content-Type': 'application/json'}
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {"message": "success"}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_body = response.text[:500]
                    print(f"   Response: {error_body}")
                except:
                    pass
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout")
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic API health"""
        success, response = self.run_test("API Health Check", "GET", "", 200)
        if success:
            print(f"   Message: {response.get('message', 'No message')}")
        return success

    def test_signup(self):
        """Test user signup"""
        success, response = self.run_test(
            "User Signup",
            "POST",
            "auth/signup",
            200,
            data={
                "email": self.test_user_email,
                "password": self.test_user_password,
                "name": self.test_user_name
            }
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response.get('user', {}).get('id')
            print(f"   Token acquired for user: {response.get('user', {}).get('name')}")
            return True
        return False

    def test_login(self):
        """Test user login"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": self.test_user_email,
                "password": self.test_user_password
            }
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response.get('user', {}).get('id')
            print(f"   Login successful for: {response.get('user', {}).get('name')}")
            return True
        return False

    def test_get_me(self):
        """Test get current user"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200,
            auth_required=True
        )
        if success:
            print(f"   User: {response.get('name')} ({response.get('email')})")
        return success

    def test_get_courses(self):
        """Test get all courses"""
        success, response = self.run_test("Get All Courses", "GET", "courses", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} courses")
            # Check for Coming Soon courses
            coming_soon = [c for c in response if c.get('is_coming_soon', False)]
            print(f"   Coming Soon courses: {len(coming_soon)}")
            return True
        return False

    def test_get_wellness_courses(self):
        """Test get wellness track courses"""
        success, response = self.run_test("Get Wellness Courses", "GET", "courses?track=wellness", 200)
        if success and isinstance(response, list):
            wellness_courses = [c for c in response if c.get('track') == 'wellness']
            print(f"   Found {len(wellness_courses)} wellness courses")
            coming_soon = [c for c in wellness_courses if c.get('is_coming_soon', False)]
            print(f"   Coming Soon wellness courses: {len(coming_soon)}")
            return True
        return False

    def test_get_clinical_courses(self):
        """Test get clinical track courses"""
        success, response = self.run_test("Get Clinical Courses", "GET", "courses?track=clinical", 200)
        if success and isinstance(response, list):
            clinical_courses = [c for c in response if c.get('track') == 'clinical']
            print(f"   Found {len(clinical_courses)} clinical courses")
            return True
        return False

    def test_get_single_course(self):
        """Test get single course details"""
        # First get a course ID
        success, courses = self.run_test("Get Courses for ID", "GET", "courses", 200)
        if not success or not courses:
            return False
        
        course_id = courses[0].get('id')
        if not course_id:
            return False
            
        success, response = self.run_test(
            f"Get Course Details",
            "GET",
            f"courses/{course_id}",
            200
        )
        if success:
            print(f"   Course: {response.get('title')} - {response.get('track')} track")
            print(f"   Price: ₹{response.get('price', 0)}")
            print(f"   Coming Soon: {response.get('is_coming_soon', False)}")
        return success

    def test_get_my_enrollments(self):
        """Test get user enrollments"""
        success, response = self.run_test(
            "Get My Enrollments",
            "GET",
            "enrollments/my",
            200,
            auth_required=True
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} enrollments")
            return True
        return False

    def test_seed_data(self):
        """Test seed data endpoint"""
        success, response = self.run_test("Seed Course Data", "POST", "seed", 200)
        if success:
            print(f"   {response.get('message', 'Seeding completed')}")
        return success

def main():
    """Main test runner"""
    print("🚀 Starting TTI API Testing...")
    print("=" * 60)
    
    tester = TTIAPITester()
    
    # Basic health check
    if not tester.test_health_check():
        print("❌ API is not responding, stopping tests")
        return 1
    
    # Seed data first
    tester.test_seed_data()
    
    # Test courses endpoints (no auth required)
    tester.test_get_courses()
    tester.test_get_wellness_courses()
    tester.test_get_clinical_courses()
    tester.test_get_single_course()
    
    # Test authentication flow
    if not tester.test_signup():
        print("❌ Signup failed, trying existing user login")
        if not tester.test_login():
            print("❌ Both signup and login failed, skipping auth tests")
        else:
            # Test authenticated endpoints
            tester.test_get_me()
            tester.test_get_my_enrollments()
    else:
        # Test authenticated endpoints after successful signup
        tester.test_get_me()
        tester.test_get_my_enrollments()
        
        # Test login with same credentials
        tester.test_login()
    
    # Print results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        failed = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())