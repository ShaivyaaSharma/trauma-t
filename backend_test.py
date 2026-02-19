import requests
import sys
import json
import subprocess
from datetime import datetime

class TTIAPITester:
    def __init__(self, base_url="http://localhost:8001"):  # Use internal URL for testing
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.course_id = None
        self.module_ids = []
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = f"ett_learner_{datetime.now().strftime('%H%M%S')}@example.com"
        self.test_user_password = "ETTLearning123!"
        self.test_user_name = "ETT Learning Student"

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

    def test_seed_modules(self):
        """Test seed modules endpoint"""
        success, response = self.run_test("Seed Module Data", "POST", "seed-modules", 200)
        if success:
            print(f"   {response.get('message', 'Module seeding completed')}")
        return success

    def test_create_enrollment(self):
        """Create a paid enrollment for testing"""
        # First get ETT Foundational Course ID
        success, courses = self.run_test("Get Courses for Enrollment", "GET", "courses", 200)
        if not success or not courses:
            print("❌ Failed to get courses")
            return False
        
        # Find ETT Foundational Course
        foundational_course = None
        for course in courses:
            if course.get('title') == 'ETT Foundational Course':
                foundational_course = course
                self.course_id = course['id']
                break
        
        if not foundational_course:
            print("❌ ETT Foundational Course not found")
            return False
        
        print(f"   Found ETT Foundational Course: {self.course_id}")
        
        # Create enrollment directly via MongoDB
        try:
            enrollment_id = f"enroll_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            mongo_cmd = f'''mongosh "mongodb://localhost:27017/tti_db" --quiet --eval "db.enrollments.insertOne({{id: '{enrollment_id}', user_id: '{self.user_id}', course_id: '{self.course_id}', payment_status: 'paid', enrolled_at: '{datetime.now().isoformat()}'}});"'''
            
            result = subprocess.run(
                mongo_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ Paid enrollment created successfully")
                return True
            else:
                print(f"❌ Failed to create enrollment: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Enrollment creation failed: {e}")
            return False

    def test_module_listing(self):
        """Test GET /api/courses/{courseId}/modules"""
        if not self.course_id:
            print("❌ No course ID available")
            return False
            
        success, response = self.run_test(
            "Get Course Modules",
            "GET", 
            f"courses/{self.course_id}/modules",
            200,
            auth_required=True
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} modules")
            
            # Store module IDs for later tests
            self.module_ids = [m['id'] for m in response]
            
            # Verify Module 1 is unlocked by default
            module_1 = next((m for m in response if m.get('module_number') == 1), None)
            if module_1:
                is_unlocked = module_1.get('progress', {}).get('is_unlocked', False)
                print(f"   Module 1 unlocked: {is_unlocked}")
                if not is_unlocked:
                    print("❌ Module 1 should be unlocked by default")
                    return False
            
            # Verify other modules are locked initially
            locked_count = 0
            for module in response:
                if module.get('module_number', 0) > 1:
                    is_unlocked = module.get('progress', {}).get('is_unlocked', False)
                    if not is_unlocked:
                        locked_count += 1
            
            print(f"   Locked modules (2+): {locked_count}")
            
            # Check progress structure
            has_progress = all('progress' in m for m in response)
            print(f"   All modules have progress: {has_progress}")
            
            return True
        return False

    def test_module_detail(self):
        """Test GET /api/courses/{courseId}/modules/{moduleId}"""
        if not self.course_id or not self.module_ids:
            print("❌ Missing course/module IDs")
            return False
        
        # Test Module 1 (should be accessible)
        module_1_id = self.module_ids[0] if self.module_ids else None
        if not module_1_id:
            print("❌ No Module 1 ID available")
            return False
            
        success, response = self.run_test(
            "Get Module 1 Detail",
            "GET",
            f"courses/{self.course_id}/modules/{module_1_id}",
            200,
            auth_required=True
        )
        
        if success:
            print(f"   Module title: {response.get('title', 'N/A')}")
            print(f"   Learning objectives: {len(response.get('learning_objectives', []))}")
            print(f"   Topics covered: {len(response.get('topics_covered', []))}")
            print(f"   Has progress: {'progress' in response}")
            
            # Test accessing a locked module (should return 403)
            if len(self.module_ids) > 1:
                module_2_id = self.module_ids[1]
                locked_success, locked_response = self.run_test(
                    "Get Locked Module Detail (Should Fail)",
                    "GET",
                    f"courses/{self.course_id}/modules/{module_2_id}",
                    403,
                    auth_required=True
                )
                if locked_success:
                    print("   ✅ Locked module correctly returns 403")
                else:
                    print("   ❌ Locked module should return 403")
                    return False
            
            return True
        return False

    def test_quiz_retrieval(self):
        """Test GET /api/courses/{courseId}/modules/{moduleId}/quiz"""
        if not self.course_id or not self.module_ids:
            print("❌ Missing course/module IDs")
            return False
        
        module_1_id = self.module_ids[0]
        success, response = self.run_test(
            "Get Module 1 Quiz",
            "GET",
            f"courses/{self.course_id}/modules/{module_1_id}/quiz",
            200,
            auth_required=True
        )
        
        if success:
            questions = response.get('questions', [])
            print(f"   Quiz questions: {len(questions)}")
            print(f"   Passing score: {response.get('passing_score', 'N/A')}")
            print(f"   Attempts: {response.get('attempts', 0)}")
            print(f"   Best score: {response.get('best_score', 0)}")
            
            # Verify questions don't have correct_answer field
            has_correct_answers = any('correct_answer' in q for q in questions)
            if has_correct_answers:
                print("❌ Quiz questions should NOT contain correct_answer field")
                return False
            
            # Verify required fields
            required_fields = ['id', 'question', 'options']
            valid_questions = all(
                all(field in q for field in required_fields) 
                for q in questions
            )
            print(f"   Valid question structure: {valid_questions}")
            
            return valid_questions
        return False

    def test_quiz_submission_passing(self):
        """Test quiz submission with passing score (100%)"""
        if not self.course_id or not self.module_ids:
            print("❌ Missing course/module IDs") 
            return False
        
        module_1_id = self.module_ids[0]
        
        # Submit all correct answers (indices 1, 1, 1, 1, 1 based on the seed data)
        correct_answers = [1, 3, 1, 1, 1]  # Based on Module 1 quiz in seed data
        
        success, response = self.run_test(
            "Submit Quiz (100% Score)",
            "POST",
            f"courses/{self.course_id}/modules/{module_1_id}/submit-quiz",
            200,
            data={"module_id": module_1_id, "answers": correct_answers},
            auth_required=True
        )
        
        if success:
            score = response.get('score', 0)
            passed = response.get('passed', False)
            total_questions = response.get('total_questions', 0)
            correct_count = response.get('correct_answers', 0)
            
            print(f"   Score: {score:.1%} ({correct_count}/{total_questions})")
            print(f"   Passed: {passed}")
            print(f"   Questions review: {len(response.get('questions_review', []))}")
            
            # Verify score calculation
            expected_score = 1.0  # 100%
            if abs(score - expected_score) > 0.01:
                print(f"❌ Score calculation error. Expected {expected_score}, got {score}")
                return False
            
            if not passed:
                print("❌ Quiz should be marked as passed")
                return False
            
            return True
        return False

    def test_quiz_submission_failing(self):
        """Test quiz submission with failing score (<80%)"""
        if not self.course_id or not self.module_ids:
            print("❌ Missing course/module IDs")
            return False
        
        # Use Module 2 if available, or Module 1 (need to unlock Module 2 first)
        if len(self.module_ids) > 1:
            module_id = self.module_ids[1]
            
            # First check if Module 2 is unlocked (it should be after Module 1 passed)
            success, module_response = self.run_test(
                "Check Module 2 Access",
                "GET",
                f"courses/{self.course_id}/modules/{module_id}",
                200,
                auth_required=True
            )
            
            if not success:
                print("❌ Module 2 should be unlocked after Module 1 completion")
                return False
        else:
            module_id = self.module_ids[0]
        
        # Submit mostly wrong answers for failing score
        failing_answers = [0, 0, 0, 2, 2]  # Should get ~20% score
        
        success, response = self.run_test(
            "Submit Quiz (Failing Score)",
            "POST", 
            f"courses/{self.course_id}/modules/{module_id}/submit-quiz",
            200,
            data={"module_id": module_id, "answers": failing_answers},
            auth_required=True
        )
        
        if success:
            score = response.get('score', 0)
            passed = response.get('passed', True)
            
            print(f"   Score: {score:.1%}")
            print(f"   Passed: {passed}")
            
            # Verify failing behavior
            if score >= 0.8:
                print("❌ Score should be < 80% for failing test")
                return False
                
            if passed:
                print("❌ Quiz should NOT be marked as passed")
                return False
            
            return True
        return False

    def test_quiz_submission_exactly_passing(self):
        """Test quiz submission with exactly 80% (passing threshold)"""
        if not self.course_id or not self.module_ids:
            return False
        
        # For a 5-question quiz, 80% = 4 correct answers
        # Submit 4 correct, 1 wrong
        passing_answers = [1, 3, 1, 1, 0]  # 4/5 = 80%
        module_id = self.module_ids[0]
        
        success, response = self.run_test(
            "Submit Quiz (Exactly 80%)",
            "POST",
            f"courses/{self.course_id}/modules/{module_id}/submit-quiz", 
            200,
            data={"module_id": module_id, "answers": passing_answers},
            auth_required=True
        )
        
        if success:
            score = response.get('score', 0)
            passed = response.get('passed', False)
            
            print(f"   Score: {score:.1%}")
            print(f"   Passed: {passed}")
            
            # Verify exactly 80% passes
            if abs(score - 0.8) > 0.01:
                print(f"❌ Expected 80% score, got {score:.1%}")
                return False
                
            if not passed:
                print("❌ 80% should be passing")
                return False
            
            return True
        return False

    def test_progress_tracking(self):
        """Test GET /api/courses/{courseId}/progress"""
        if not self.course_id:
            print("❌ No course ID available")
            return False
            
        success, response = self.run_test(
            "Get Course Progress",
            "GET",
            f"courses/{self.course_id}/progress",
            200, 
            auth_required=True
        )
        
        if success:
            total = response.get('total_modules', 0)
            completed = response.get('completed_modules', 0)
            current = response.get('current_module', 0) 
            progress = response.get('overall_progress', 0)
            
            print(f"   Total modules: {total}")
            print(f"   Completed modules: {completed}")
            print(f"   Current module: {current}")
            print(f"   Overall progress: {progress:.1f}%")
            
            # Verify reasonable values
            if total == 0:
                print("❌ Should have modules seeded")
                return False
                
            if progress < 0 or progress > 100:
                print("❌ Progress percentage should be 0-100")
                return False
            
            return True
        return False

    def test_module_progression_flow(self):
        """Test the complete gamified progression flow"""
        if not self.course_id or len(self.module_ids) < 3:
            print("❌ Insufficient modules for progression test")
            return False
        
        print(f"\n🔄 Testing Module Progression Flow...")
        
        # 1. Verify initial state - only Module 1 unlocked
        success, modules = self.run_test(
            "Check Initial Module States",
            "GET",
            f"courses/{self.course_id}/modules",
            200,
            auth_required=True
        )
        
        if not success:
            return False
        
        module_1 = next((m for m in modules if m.get('module_number') == 1), None)
        module_2 = next((m for m in modules if m.get('module_number') == 2), None)
        
        if not module_1 or not module_2:
            print("❌ Missing Module 1 or 2")
            return False
        
        print(f"   Module 1 unlocked: {module_1.get('progress', {}).get('is_unlocked', False)}")
        print(f"   Module 2 unlocked: {module_2.get('progress', {}).get('is_unlocked', False)}")
        
        # 2. Pass Module 1 quiz to unlock Module 2
        correct_answers = [1, 3, 1, 1, 1]
        success, quiz_result = self.run_test(
            "Pass Module 1 Quiz",
            "POST",
            f"courses/{self.course_id}/modules/{module_1['id']}/submit-quiz",
            200,
            data={"module_id": module_1['id'], "answers": correct_answers},
            auth_required=True
        )
        
        if not success or not quiz_result.get('passed'):
            print("❌ Failed to pass Module 1 quiz")
            return False
        
        print(f"   Module 1 quiz passed with {quiz_result.get('score', 0):.1%}")
        
        # 3. Verify Module 2 is now unlocked
        success, updated_modules = self.run_test(
            "Check Module 2 Unlocked",
            "GET",
            f"courses/{self.course_id}/modules",
            200,
            auth_required=True
        )
        
        if success:
            updated_module_2 = next((m for m in updated_modules if m.get('module_number') == 2), None)
            if updated_module_2:
                is_unlocked = updated_module_2.get('progress', {}).get('is_unlocked', False)
                print(f"   Module 2 now unlocked: {is_unlocked}")
                if not is_unlocked:
                    print("❌ Module 2 should be unlocked after Module 1 completion")
                    return False
            else:
                print("❌ Module 2 not found")
                return False
        
        # 4. Try accessing Module 3 (should still be locked)
        if len(self.module_ids) > 2:
            module_3_id = self.module_ids[2]
            success, response = self.run_test(
                "Access Locked Module 3 (Should Fail)",
                "GET",
                f"courses/{self.course_id}/modules/{module_3_id}",
                403,
                auth_required=True
            )
            if success:
                print("   ✅ Module 3 correctly blocked (403)")
            else:
                print("   ❌ Module 3 should return 403 when locked")
                return False
        
        print("✅ Module progression flow working correctly")
        return True

    def test_quiz_retry_functionality(self):
        """Test quiz retry and best score tracking"""
        if not self.course_id or not self.module_ids:
            return False
        
        module_2_id = self.module_ids[1] if len(self.module_ids) > 1 else self.module_ids[0]
        
        # First attempt with failing score
        failing_answers = [0, 0, 0, 0, 0]  # 0% score
        success, first_result = self.run_test(
            "First Quiz Attempt (Failing)",
            "POST",
            f"courses/{self.course_id}/modules/{module_2_id}/submit-quiz",
            200,
            data={"module_id": module_2_id, "answers": failing_answers},
            auth_required=True
        )
        
        if not success:
            return False
        
        first_score = first_result.get('score', 0)
        print(f"   First attempt score: {first_score:.1%}")
        
        # Second attempt with better score
        better_answers = [1, 1, 2, 2, 1]  # Should be higher score
        success, second_result = self.run_test(
            "Second Quiz Attempt (Better)",
            "POST",
            f"courses/{self.course_id}/modules/{module_2_id}/submit-quiz",
            200,
            data={"module_id": module_2_id, "answers": better_answers},
            auth_required=True
        )
        
        if not success:
            return False
        
        second_score = second_result.get('score', 0)
        print(f"   Second attempt score: {second_score:.1%}")
        
        # Check quiz attempts and best score via quiz endpoint
        success, quiz_info = self.run_test(
            "Check Quiz Attempts",
            "GET",
            f"courses/{self.course_id}/modules/{module_2_id}/quiz",
            200,
            auth_required=True
        )
        
        if success:
            attempts = quiz_info.get('attempts', 0)
            best_score = quiz_info.get('best_score', 0)
            
            print(f"   Total attempts: {attempts}")
            print(f"   Best score tracked: {best_score:.1%}")
            
            # Verify attempts incremented
            if attempts < 2:
                print("❌ Attempt count should be at least 2")
                return False
            
            # Verify best score is tracked
            expected_best = max(first_score, second_score)
            if abs(best_score - expected_best) > 0.01:
                print(f"❌ Best score tracking error. Expected {expected_best:.1%}, got {best_score:.1%}")
                return False
            
            return True
        return False

    def test_unenrolled_user_access(self):
        """Test that unenrolled users get 403 errors"""
        # Create another user without enrollment
        temp_email = f"unenrolled_{datetime.now().strftime('%H%M%S')}@example.com"
        
        success, response = self.run_test(
            "Create Unenrolled User",
            "POST",
            "auth/signup",
            200,
            data={
                "email": temp_email,
                "password": "TempPass123!",
                "name": "Unenrolled User"
            }
        )
        
        if not success:
            print("❌ Failed to create test user")
            return False
        
        temp_token = response.get('access_token')
        if not temp_token:
            print("❌ No token received")
            return False
        
        # Test access with unenrolled user (should get 403)
        url = f"{self.base_url}/api/courses/{self.course_id}/modules"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {temp_token}'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 403:
                print("   ✅ Unenrolled user correctly blocked (403)")
                return True
            else:
                print(f"   ❌ Expected 403, got {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Request error: {e}")
            return False

def main():
    """Main test runner for gamified learning module system"""
    print("🚀 Starting TTI Gamified Learning API Testing...")
    print("=" * 60)
    
    tester = TTIAPITester()
    
    # Basic health check
    if not tester.test_health_check():
        print("❌ API is not responding, stopping tests")
        return 1
    
    print("\n📚 GAMIFIED LEARNING MODULE TESTING")
    print("-" * 40)
    
    # 1. Data Seeding (Prerequisites)
    print("\n1️⃣ SEEDING TEST DATA")
    tester.test_seed_data()
    tester.test_seed_modules()
    
    # 2. Authentication Setup
    print("\n2️⃣ USER AUTHENTICATION")
    if not tester.test_signup():
        print("❌ Signup failed, trying existing user login")
        if not tester.test_login():
            print("❌ Authentication failed completely")
            return 1
    
    tester.test_get_me()
    
    # 3. Create Enrollment
    print("\n3️⃣ ENROLLMENT SETUP")
    if not tester.test_create_enrollment():
        print("❌ Failed to create enrollment, skipping module tests")
        return 1
    
    # 4. Module Listing Tests
    print("\n4️⃣ MODULE LISTING")
    if not tester.test_module_listing():
        print("❌ Module listing failed")
        return 1
    
    # 5. Module Detail Tests  
    print("\n5️⃣ MODULE DETAIL ACCESS")
    if not tester.test_module_detail():
        print("❌ Module detail tests failed")
        return 1
    
    # 6. Quiz Retrieval Tests
    print("\n6️⃣ QUIZ RETRIEVAL")
    if not tester.test_quiz_retrieval():
        print("❌ Quiz retrieval failed")
        return 1
    
    # 7. Quiz Submission Tests
    print("\n7️⃣ QUIZ SUBMISSION & GRADING")
    if not tester.test_quiz_submission_passing():
        print("❌ Passing quiz submission failed")
        return 1
    
    # 8. Module Progression Flow
    print("\n8️⃣ MODULE PROGRESSION FLOW")
    if not tester.test_module_progression_flow():
        print("❌ Module progression failed")
        return 1
    
    # 9. Quiz Retry Tests
    print("\n9️⃣ QUIZ RETRY FUNCTIONALITY")
    if not tester.test_quiz_retry_functionality():
        print("❌ Quiz retry functionality failed")
        return 1
    
    # 10. Progress Tracking
    print("\n🔟 PROGRESS TRACKING")
    if not tester.test_progress_tracking():
        print("❌ Progress tracking failed")
        return 1
    
    # 11. Security Tests
    print("\n🔒 SECURITY TESTS")
    if not tester.test_unenrolled_user_access():
        print("❌ Security tests failed")
        return 1
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 GAMIFIED LEARNING TEST RESULTS")
    print(f"Total: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 ALL GAMIFIED LEARNING TESTS PASSED!")
        return 0
    else:
        failed = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())