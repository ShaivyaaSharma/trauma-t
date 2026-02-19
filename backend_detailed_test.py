import requests
import sys
import json
import subprocess
from datetime import datetime

class TTIDetailedTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.course_id = None
        self.module_ids = []
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = f"detailed_test_{datetime.now().strftime('%H%M%S')}@example.com"
        self.test_user_password = "DetailedTest123!"
        self.test_user_name = "Detailed Test User"

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

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_test_user_and_enrollment(self):
        """Setup test user and enrollment"""
        # Signup
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
        if not success:
            return False
            
        self.token = response['access_token']
        self.user_id = response.get('user', {}).get('id')
        
        # Get course ID
        success, courses = self.run_test("Get Courses", "GET", "courses", 200)
        if not success:
            return False
            
        for course in courses:
            if course.get('title') == 'ETT Foundational Course':
                self.course_id = course['id']
                break
                
        if not self.course_id:
            print("❌ ETT Foundational Course not found")
            return False
        
        # Create enrollment
        try:
            enrollment_id = f"detailed_enroll_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            mongo_cmd = f'''mongosh "mongodb://localhost:27017/tti_db" --quiet --eval "db.enrollments.insertOne({{id: '{enrollment_id}', user_id: '{self.user_id}', course_id: '{self.course_id}', payment_status: 'paid', enrolled_at: '{datetime.now().isoformat()}'}});"'''
            
            result = subprocess.run(mongo_cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"❌ Enrollment creation failed")
                return False
                
            # Get module IDs and complete Module 1 to unlock others
            success, modules = self.run_test("Get Modules", "GET", f"courses/{self.course_id}/modules", 200, auth_required=True)
            if success:
                self.module_ids = [m['id'] for m in modules]
                
                # Access Module 1 detail to create progress record
                success, module_1_detail = self.run_test(
                    "Access Module 1 Detail", "GET", f"courses/{self.course_id}/modules/{self.module_ids[0]}", 200, auth_required=True
                )
                
                if not success:
                    print("   ❌ Failed to access Module 1")
                    return False
                
                # Complete Module 1 to unlock Module 2
                module_1_correct_answers = [1, 3, 1, 1, 1]  # Based on seed data
                success, result = self.run_test(
                    "Complete Module 1", "POST", f"courses/{self.course_id}/modules/{self.module_ids[0]}/submit-quiz",
                    200, data={"module_id": self.module_ids[0], "answers": module_1_correct_answers}, auth_required=True
                )
                
                if success and result.get('passed'):
                    print("   ✅ Module 1 completed, Module 2 should be unlocked")
                    return True
                else:
                    print("   ❌ Failed to complete Module 1")
                    return False
                
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
            
        return False

    def test_exactly_80_percent_passing(self):
        """Test exact 80% threshold passing"""
        if not self.module_ids or len(self.module_ids) < 3:
            return False
            
        # Use Module 3 for this test
        module_3_id = self.module_ids[2]
        
        # First unlock Module 3 by completing Module 2
        # Get Module 2 quiz structure
        success, module_2_quiz = self.run_test(
            "Get Module 2 Quiz", "GET", f"courses/{self.course_id}/modules/{self.module_ids[1]}/quiz", 200, auth_required=True
        )
        if not success:
            return False
            
        num_q2 = len(module_2_quiz.get('questions', []))
        # Pass Module 2 with correct answers (assuming [1,1,2,2,1,1] works)
        pass_answers_2 = [1] * num_q2  # All answer index 1
        
        success, result = self.run_test(
            "Complete Module 2", "POST", f"courses/{self.course_id}/modules/{self.module_ids[1]}/submit-quiz",
            200, data={"module_id": self.module_ids[1], "answers": pass_answers_2}, auth_required=True
        )
        
        if not success or not result.get('passed'):
            print(f"❌ Failed to unlock Module 3 (Module 2 score: {result.get('score', 0):.1%})")
            return False
        
        # Now test Module 3 with exactly 80%
        success, module_3_quiz = self.run_test(
            "Get Module 3 Quiz", "GET", f"courses/{self.course_id}/modules/{module_3_id}/quiz", 200, auth_required=True
        )
        if not success:
            return False
            
        num_questions = len(module_3_quiz.get('questions', []))
        correct_answers_needed = int(num_questions * 0.8)  # Exactly 80%
        
        print(f"   Module 3 has {num_questions} questions, need {correct_answers_needed} correct for 80%")
        
        # Create answer pattern for exactly 80%
        exact_80_answers = [1] * correct_answers_needed + [0] * (num_questions - correct_answers_needed)
        
        success, result = self.run_test(
            "Submit Quiz (Exactly 80%)",
            "POST",
            f"courses/{self.course_id}/modules/{module_3_id}/submit-quiz",
            200,
            data={"module_id": module_3_id, "answers": exact_80_answers},
            auth_required=True
        )
        
        if success:
            score = result.get('score', 0)
            passed = result.get('passed', False)
            
            print(f"   Score: {score:.1%} ({result.get('correct_answers')}/{result.get('total_questions')})")
            print(f"   Passed: {passed}")
            
            expected_score = correct_answers_needed / num_questions
            if abs(score - expected_score) > 0.01:
                print(f"❌ Score calculation error. Expected {expected_score:.1%}, got {score:.1%}")
                return False
                
            # Should pass if exactly 80% or above
            if expected_score >= 0.8 and not passed:
                print("❌ Should pass with 80%")
                return False
            elif expected_score < 0.8 and passed:
                print("❌ Should not pass with <80%")
                return False
            
            return True
        return False

    def test_failing_quiz_locks_next_module(self):
        """Test that failing quiz doesn't unlock next module"""
        if len(self.module_ids) < 4:
            return False
        
        # Use a fresh module for this test - Module 4
        module_4_id = self.module_ids[3]
        
        # First make sure Module 4 is accessible by completing Module 3
        success, module_3_quiz = self.run_test(
            "Get Module 3 Quiz Info", "GET", f"courses/{self.course_id}/modules/{self.module_ids[2]}/quiz", 200, auth_required=True
        )
        if not success:
            return False
            
        num_q3 = len(module_3_quiz.get('questions', []))
        pass_answers_3 = [1] * num_q3
        
        success, result = self.run_test(
            "Complete Module 3", "POST", f"courses/{self.course_id}/modules/{self.module_ids[2]}/submit-quiz",
            200, data={"module_id": self.module_ids[2], "answers": pass_answers_3}, auth_required=True
        )
        
        if not success:
            return False
        
        # Now Module 4 should be accessible
        # Get Module 4 quiz
        success, module_4_quiz = self.run_test(
            "Get Module 4 Quiz", "GET", f"courses/{self.course_id}/modules/{module_4_id}/quiz", 200, auth_required=True
        )
        if not success:
            return False
            
        num_q4 = len(module_4_quiz.get('questions', []))
        
        # Submit failing score (all wrong)
        failing_answers = [0] * num_q4
        
        success, result = self.run_test(
            "Submit Failing Quiz",
            "POST",
            f"courses/{self.course_id}/modules/{module_4_id}/submit-quiz",
            200,
            data={"module_id": module_4_id, "answers": failing_answers},
            auth_required=True
        )
        
        if success:
            score = result.get('score', 1)  # Default to 1 if missing
            passed = result.get('passed', True)  # Default to True if missing
            
            print(f"   Failing score: {score:.1%}")
            print(f"   Passed: {passed}")
            
            if score >= 0.8:
                print("❌ This should be a failing score")
                return False
                
            if passed:
                print("❌ Should not pass with failing score")
                return False
            
            # Verify Module 5 is still locked
            if len(self.module_ids) > 4:
                module_5_id = self.module_ids[4]
                success, response = self.run_test(
                    "Check Module 5 Still Locked", "GET", f"courses/{self.course_id}/modules/{module_5_id}", 403, auth_required=True
                )
                if success:
                    print("   ✅ Module 5 correctly remains locked after failing Module 4")
                else:
                    print("   ❌ Module 5 should remain locked")
                    return False
            
            return True
        return False

def main():
    """Detailed edge case testing"""
    print("🔬 Starting TTI Detailed Edge Case Testing...")
    print("=" * 60)
    
    tester = TTIDetailedTester()
    
    # Setup
    print("\n📋 SETUP")
    if not tester.setup_test_user_and_enrollment():
        print("❌ Setup failed")
        return 1
    
    # Test edge cases
    print("\n🎯 EDGE CASE TESTING")
    
    if not tester.test_exactly_80_percent_passing():
        print("❌ 80% threshold test failed")
        return 1
    
    if not tester.test_failing_quiz_locks_next_module():
        print("❌ Failing quiz lock test failed") 
        return 1
    
    # Print results
    print("\n" + "=" * 60)
    print(f"📊 DETAILED TEST RESULTS")
    print(f"Total: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 ALL DETAILED TESTS PASSED!")
        return 0
    else:
        failed = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())