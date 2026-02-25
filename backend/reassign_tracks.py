import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

async def sync_courses():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['tti_db']
    
    # 1. Foundational Course should be in both
    foundational = await db.courses.find_one({'title': 'ETT Foundational Course'})
    if foundational:
        await db.courses.update_one({'_id': foundational['_id']}, {'$set': {'track': 'both'}})
        print("Updated Foundational Course to 'both'")
    
    # 2. Definitive list of professional courses mapped to Clinical or Wellness
    # (CTSS and CRP are now mapped to Wellness as per user feedback to hide Support)
    courses_to_add = [
        {
            'title': 'CCTSI (Certified Clinical Trauma Specialist - Individual)',
            'track': 'clinical',
            'level': 'level2',
            'description': 'Clinical trauma treatment for individual adults.',
            'detailed_description': 'Advanced training for clinical professionals focusing on individual trauma interventions.',
            'price': 32000,
            'duration': '8 weeks',
            'location': 'Online',
            'schedule': 'Tuesdays & Thursdays',
            'instructor': 'Senior Clinical Trainer',
            'features': ['Clinical formulation', 'Individual processing', 'Certification'],
            'is_coming_soon': False
        },
        {
            'title': 'CCTSF (Certified Clinical Trauma Specialist - Family)',
            'track': 'clinical',
            'level': 'level2',
            'description': 'Family systems and intergenerational trauma diagnosis.',
            'detailed_description': 'Integrating family systems theory with trauma transformation.',
            'price': 32000,
            'duration': '8 weeks',
            'location': 'Online',
            'schedule': 'Sat & Sun',
            'instructor': 'Family Systems Expert',
            'features': ['Systemic assessment', 'Cycle breaking', 'Family protocols'],
            'is_coming_soon': False
        },
        {
            'title': 'CCTSA (Certified Clinical Trauma Specialist - Addiction)',
            'track': 'clinical',
            'level': 'advanced',
            'description': 'Neurobiology of addiction and complex trauma treatment.',
            'detailed_description': 'Handling the trauma-addiction loop with advanced ETT protocols.',
            'price': 35000,
            'duration': '10 weeks',
            'location': 'Online',
            'schedule': 'Weekly Intensive',
            'instructor': 'Addiction Specialist',
            'features': ['Craving management', 'Root cause healing', 'Supervision'],
            'is_coming_soon': False
        },
        {
            'title': 'CTSS (Certified Trauma Support Specialist)',
            'track': 'wellness', # Moved from support
            'level': 'level1',
            'description': 'Trauma awareness and psychological first aid.',
            'detailed_description': 'Designed for teachers, first responders, and community helpers.',
            'price': 15000,
            'duration': '4 weeks',
            'location': 'Online',
            'schedule': 'Flexi-learning',
            'instructor': 'Support Lead',
            'features': ['Psychological first aid', 'Active listening', 'Referral mapping'],
            'is_coming_soon': False
        },
        {
            'title': 'CRP (Community Resilience Practitioner)',
            'track': 'wellness', # Moved from support
            'level': 'level2',
            'description': 'Community healing and referral systems.',
            'detailed_description': 'Focus on building resilient community networks and structured support.',
            'price': 20000,
            'duration': '6 weeks',
            'location': 'Hybrid',
            'schedule': 'Bi-weekly',
            'instructor': 'Community Lead',
            'features': ['Group facilitateion', 'Resource mapping', 'Crisis support'],
            'is_coming_soon': False
        },
        {
            'title': 'ACCTS (Advanced Certified Clinical Trauma Specialist)',
            'track': 'clinical',
            'level': 'advanced',
            'description': 'Complexity, supervision, and advanced diagnostic frameworks.',
            'detailed_description': 'The peak of clinical ETT training.',
            'price': 45000,
            'duration': '12 weeks',
            'location': 'Online',
            'schedule': 'Custom',
            'instructor': 'Institute Director',
            'features': ['Mastery', 'Supervision', 'Fellowship'],
            'is_coming_soon': False
        },
        {
            'title': 'CCTS-P (Certified Clinical Trauma Specialist - Prenatal/Pediatric)',
            'track': 'clinical',
            'level': 'level2',
            'description': 'Early developmental trauma and pediatric mental health.',
            'detailed_description': 'Specialized training for working with children and early developmental stages.',
            'price': 32000,
            'duration': '8 weeks',
            'location': 'Online',
            'schedule': 'Mondays',
            'instructor': 'Pediatric Expert',
            'features': ['Child-friendly ETT', 'Family integration', 'Early years focus'],
            'is_coming_soon': False
        }
    ]
    
    for c_data in courses_to_add:
        # We will update existing by title to ensure tracks are correct
        exists = await db.courses.find_one({'title': c_data['title']})
        if exists:
            await db.courses.update_one({'_id': exists['_id']}, {'$set': {'track': c_data['track']}})
            print(f"Updated Track for: {c_data['title']} -> {c_data['track']}")
        else:
            c_data['id'] = str(uuid.uuid4())
            c_data['created_at'] = datetime.now(timezone.utc).isoformat()
            await db.courses.insert_one(c_data)
            print(f"Created and assigned: {c_data['title']} to {c_data['track']}")

if __name__ == "__main__":
    asyncio.run(sync_courses())
