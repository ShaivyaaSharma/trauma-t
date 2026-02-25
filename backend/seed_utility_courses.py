import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

async def seed_wellness_and_utility_modules():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['tti_db']

    # Data structure for modules
    course_modules_data = {
        "Trauma-Informed Hospitality Training": [
            {
                "module_number": 1,
                "title": "Introduction to Trauma Awareness",
                "description": "Understanding what trauma is and its visible/invisible markers.",
                "learning_objectives": ["Understand trauma and its impact on behavior", "Identify visible vs invisible distress"],
                "topics_covered": ["What is trauma?", "Visible vs invisible distress", "Impact on guest behavior"],
                "student_activities": ["Distress identification roleplay"],
                "estimated_time": "3 hours"
            },
            {
                "module_number": 2,
                "title": "Emotional Intelligence in Service",
                "description": "Techniques for empathy and active listening in hospitality.",
                "learning_objectives": ["Differentiate empathy vs sympathy", "Recognize signs of distress in guests"],
                "topics_covered": ["Empathy vs sympathy", "Active listening techniques", "Non-verbal communication"],
                "student_activities": ["Active listening drill"],
                "estimated_time": "3 hours"
            },
            {
                "module_number": 3,
                "title": "De-escalation Skills",
                "description": "Practical methods for handling angry or anxious guests.",
                "learning_objectives": ["Apply de-escalation techniques", "Resolve conflicts safely"],
                "topics_covered": ["Handling angry or anxious guests", "Conflict resolution methods", "Safety-first response strategies"],
                "student_activities": ["De-escalation simulation"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 4,
                "title": "Creating Safe Spaces",
                "description": "Designing trauma-sensitive environments and inclusive practices.",
                "learning_objectives": ["Build emotionally safe service environments", "Implement inclusive practices"],
                "topics_covered": ["Trauma-sensitive environments", "Staff coordination", "Inclusive practices"],
                "student_activities": ["Safe space design workshop"],
                "estimated_time": "3 hours"
            },
            {
                "module_number": 5,
                "title": "Staff Wellbeing",
                "description": "Preventing burnout and setting emotional boundaries.",
                "learning_objectives": ["Prevent burnout", "Establish emotional boundaries"],
                "topics_covered": ["Burnout prevention", "Emotional boundaries", "Self-care practices"],
                "student_activities": ["Self-care plan development"],
                "estimated_time": "2 hours"
            }
        ],
        "Wellness Retreat Program": [
            {
                "module_number": 1,
                "title": "Foundations of Wellness",
                "description": "Mind-body connection and nervous system basics.",
                "learning_objectives": ["Understand mind-body connection", "Learn nervous system basics"],
                "topics_covered": ["Mind-body connection", "Stress and nervous system basics"],
                "student_activities": ["Nervous system mapping"],
                "estimated_time": "3 hours"
            },
            {
                "module_number": 2,
                "title": "Retreat Design",
                "description": "Structuring multi-day retreats and transformation journeys.",
                "learning_objectives": ["Design structured retreat experiences", "Schedule activities effectively"],
                "topics_covered": ["Structuring multi-day retreats", "Scheduling activities", "Creating transformation journeys"],
                "student_activities": ["Retreat itinerary design"],
                "estimated_time": "5 hours"
            },
            {
                "module_number": 3,
                "title": "Facilitation Skills",
                "description": "Group engagement techniques and holding safe spaces.",
                "learning_objectives": ["Facilitate group wellness sessions", "Manage group dynamics"],
                "topics_covered": ["Group engagement techniques", "Holding safe spaces", "Communication skills"],
                "student_activities": ["Facilitation roleplay"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 4,
                "title": "Practices and Modalities",
                "description": "Integrating mindfulness, breathwork, and body-based practices.",
                "learning_objectives": ["Integrate mindfulness practices", "Facilitate breathwork and meditation"],
                "topics_covered": ["Breathwork", "Meditation", "Movement and relaxation"],
                "student_activities": ["Guided meditation workshop"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 5,
                "title": "Business and Operations",
                "description": "Pricing, marketing, and logistics for wellness retreats.",
                "learning_objectives": ["Price and market retreats", "Manage logistics and partnerships"],
                "topics_covered": ["Pricing and marketing", "Logistics and partnerships", "Client management"],
                "student_activities": ["Business plan drafting"],
                "estimated_time": "3 hours"
            }
        ],
        "CTSS (Certified Trauma Support Specialist)": [
            {
                "module_number": 1,
                "title": "Trauma Basics",
                "description": "Understanding basic trauma responses and types of trauma.",
                "learning_objectives": ["Understand basic trauma responses", "Identify types of trauma"],
                "topics_covered": ["Types of trauma", "Stress responses"],
                "student_activities": ["Trauma response identification"],
                "estimated_time": "3 hours"
            },
            {
                "module_number": 2,
                "title": "Psychological First Aid",
                "description": "Stabilization techniques and grounding exercises.",
                "learning_objectives": ["Provide immediate emotional support", "Apply stabilization techniques"],
                "topics_covered": ["Stabilization techniques", "Grounding exercises"],
                "student_activities": ["Grounding exercise practice"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 3,
                "title": "Communication Skills",
                "description": "Active listening and non-judgmental support in helping roles.",
                "learning_objectives": ["Apply active listening", "Maintain non-judgmental support"],
                "topics_covered": ["Active listening", "Non-judgmental support"],
                "student_activities": ["Listening skills drill"],
                "estimated_time": "3 hours"
            },
            {
                "module_number": 4,
                "title": "Referral Systems",
                "description": "Identifying when to refer to professionals and working with clinical teams.",
                "learning_objectives": ["Identify when to refer to professionals", "Understand referral protocols"],
                "topics_covered": ["When to escalate", "Working with professionals"],
                "student_activities": ["Referral scenario analysis"],
                "estimated_time": "2 hours"
            },
            {
                "module_number": 5,
                "title": "Ethics and Boundaries",
                "description": "Scope of practice and confidentiality in support roles.",
                "learning_objectives": ["Understand scope of practice", "Maintain confidentiality"],
                "topics_covered": ["Scope of practice", "Confidentiality"],
                "student_activities": ["Ethical dilemma workshop"],
                "estimated_time": "2 hours"
            }
        ],
        "CRP (Community Resilience Practitioner)": [
            {
                "module_number": 1,
                "title": "Community Psychology Basics",
                "description": "Understanding group dynamics and the social impact of trauma.",
                "learning_objectives": ["Understand group dynamics", "Recognize social impact of trauma"],
                "topics_covered": ["Understanding group dynamics", "Social impact of trauma"],
                "student_activities": ["Community mapping"],
                "estimated_time": "3 hours"
            },
            {
                "module_number": 2,
                "title": "Resilience Building",
                "description": "Promoting resilience and strength-based coping strategies.",
                "learning_objectives": ["Promote resilience strategies", "Apply strength-based approaches"],
                "topics_covered": ["Coping strategies", "Strength-based approaches"],
                "student_activities": ["Resilience workshop design"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 3,
                "title": "Program Design",
                "description": "Developing workshops and community engagement outreach.",
                "learning_objectives": ["Develop community-based support systems", "Plan outreach programs"],
                "topics_covered": ["Workshops and outreach", "Community engagement"],
                "student_activities": ["Engagement plan drafting"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 4,
                "title": "Crisis Response",
                "description": "Handling emergencies and coordination with local services.",
                "learning_objectives": ["Handle community emergencies", "Coordinate with local services"],
                "topics_covered": ["Handling emergencies", "Coordination with services"],
                "student_activities": ["Crisis coordination drill"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 5,
                "title": "Monitoring and Impact",
                "description": "Measuring community outcomes and implementing feedback systems.",
                "learning_objectives": ["Measure community outcomes", "Implement feedback systems"],
                "topics_covered": ["Measuring outcomes", "Feedback systems"],
                "student_activities": ["Impact assessment simulation"],
                "estimated_time": "3 hours"
            }
        ]
    }

    for course_title, modules in course_modules_data.items():
        course = await db.courses.find_one({"title": course_title})
        if not course:
            print(f"Skipping {course_title}: Course not found in database.")
            continue
        
        course_id = course['id']
        # Clear old modules for this course to ensure clean seed
        await db.modules.delete_many({"course_id": course_id})
        
        for mod in modules:
            mod["course_id"] = course_id
            mod["id"] = str(uuid.uuid4())
            mod["week"] = 1 # Default week or distributed
            mod["created_at"] = datetime.now(timezone.utc).isoformat()
            mod["assessment"] = {
                "quiz_questions": [],
                "passing_score": 0.8
            }
            await db.modules.insert_one(mod)
        
        print(f"Successfully seeded {len(modules)} modules for '{course_title}'")

if __name__ == "__main__":
    asyncio.run(seed_wellness_and_utility_modules())
