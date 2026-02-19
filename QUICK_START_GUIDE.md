# TTI Gamified Learning System - Quick Start Guide

## 🚀 Ready-to-Use Demo Account

I've created a demo account for you to test the learning system immediately:

### Login Credentials:
- **Email:** `demo@tti.com`
- **Password:** `demo123`

This account is already enrolled in the **ETT Foundational Course** with payment completed, so you can start learning right away!

---

## 📚 How to Access the Learning System

### Option 1: Use Demo Account (Recommended)
1. Go to http://localhost:3000/login
2. Enter the credentials above
3. You'll be redirected to Dashboard
4. Click **"Start Learning"** button on the ETT Foundational Course card
5. Start with Module 1!

### Option 2: Create New Account
If signup is failing in the browser, here's how to create and enroll a user manually:

#### Step 1: Create User via API
```bash
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email":"your.email@example.com",
    "password":"yourpassword",
    "name":"Your Name"
  }'
```

Save the `user_id` from the response.

#### Step 2: Enroll in Course
```python
# Run this Python script
import pymongo
from datetime import datetime, timezone

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["tti_db"]

enrollment = {
    "id": "your-enrollment-id",
    "user_id": "YOUR_USER_ID_HERE",  # from Step 1
    "course_id": "7db7fc27-00bd-4102-99b7-e81f23900770",  # ETT Foundational Course
    "payment_status": "paid",
    "session_id": None,
    "enrolled_at": datetime.now(timezone.utc).isoformat()
}

db.enrollments.insert_one(enrollment)
print("✅ Enrolled successfully!")
```

#### Step 3: Login
Now you can login at http://localhost:3000/login with your credentials.

---

## 🎮 Testing the Gamification Flow

### 1. **Module 1 (Unlocked by Default)**
   - Click "Start Learning" from Dashboard
   - Module 1 will be unlocked and ready
   - Read the learning objectives and topics
   - Click "Assessment" tab
   - Take the quiz (5 questions)

### 2. **Pass the Quiz (Need 80%+)**
   - Answer at least 4 out of 5 questions correctly
   - Submit the quiz
   - You'll see:
     - ✅ Your score
     - ✅ Pass/Fail status
     - ✅ Detailed review with explanations
     - ✅ Module 2 unlocks automatically

### 3. **Failed Quiz (< 80%)**
   - If you score less than 80%:
     - Module stays incomplete
     - Next module stays locked
     - You can retry unlimited times
     - Best score is tracked

### 4. **Progress Through All 10 Modules**
   - Complete Module 1 → unlocks Module 2
   - Complete Module 2 → unlocks Module 3
   - Continue through all 6 weeks
   - Watch your progress percentage increase

---

## 📊 Key Features to Test

### Progress Tracking
- Overall course progress percentage
- Completed modules count
- Current module indicator
- Stats dashboard

### Quiz Features
- Multiple choice questions
- Instant grading
- Detailed explanations
- Attempt tracking
- Best score tracking
- Retry functionality

### Module Locking
- Only Module 1 unlocked initially
- Must pass to unlock next
- Visual lock/unlock indicators
- Completion badges

### UI Elements
- Week-based grouping (Week 1-6)
- Lock 🔒, Unlock ▶️, Completed ✅ icons
- Progress bars
- Color-coded status (green=complete, blue=unlocked, gray=locked)

---

## 🔍 Troubleshooting

### If Signup in Browser Fails:
1. Open browser console (F12) and check for errors
2. Use the demo account provided above
3. Or create account via API as shown in Option 2

### If "Start Learning" Button Doesn't Appear:
- Make sure you're enrolled in "ETT Foundational Course"
- The button only appears for this specific course
- Check Dashboard shows "Enrolled" badge

### If Module Won't Unlock:
- You must score >= 80% on previous module's quiz
- Check your quiz score in the results
- Retry the quiz if needed

### Check Backend API:
```bash
# Test if backend is running
curl http://localhost:8001/api/health

# Get courses
curl http://localhost:8001/api/courses

# Check if modules are seeded
curl http://localhost:8001/api/courses | grep -i foundational
```

---

## 📝 Course Content Overview

**ETT Foundational Course - 10 Modules:**

**Week 1:**
- Module 1: Introduction to Emotional Transformation Therapy
- Module 2: Theoretical Foundations of Emotion and Attachment

**Week 2:**
- Module 3: Neuroscience of Visual Stimulation
- Module 4: Spectral Resonance Technique (SRT) and Color Psychology

**Week 3:**
- Module 5: Multidimensional Eye Movement (MDEM) Theory
- Module 6: Integrating ETT Techniques into Practice

**Week 4:**
- Module 7: Ethical, Cultural, and Professional Standards
- Module 8: Research, Evidence, and Outcomes

**Week 5:**
- Module 9: Case Conceptualization and Synthesis

**Week 6:**
- Module 10: Final Review and Certification Preparation

Each module includes:
- Learning objectives (4-5 points)
- Topics covered (4-5 points)
- Auto-graded quiz (5-6 questions)
- Estimated time: 3-4 hours

---

## 🎯 Success Criteria

You'll know everything is working when:
1. ✅ Can login with demo account
2. ✅ See "Start Learning" button on Dashboard
3. ✅ Module 1 is unlocked, others locked
4. ✅ Can take quiz and see results
5. ✅ Passing quiz (80%+) unlocks next module
6. ✅ Progress percentage updates
7. ✅ Can navigate through all 10 modules sequentially

---

## 🆘 Need Help?

If you encounter any issues:
1. Check browser console for frontend errors (F12)
2. Check backend logs: `tail -f /var/log/supervisor/backend.*.log`
3. Verify MongoDB is running: `sudo supervisorctl status mongodb`
4. Restart services: `sudo supervisorctl restart all`

**Happy Learning! 🎓**
