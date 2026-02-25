import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

async def seed_clinical_curriculum():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client['tti_db']

    clinical_modules_data = {
        "CCTSI (Certified Clinical Trauma Specialist - Individual)": [
            {
                "module_number": 1,
                "title": "Foundations of Trauma Therapy",
                "description": "Trauma definitions, neurobiology, and stress response systems.",
                "learning_objectives": ["Understand neurobiology of trauma", "Define trauma classifications"],
                "topics_covered": ["Trauma definitions", "Neurobiology of trauma", "Stress response systems"],
                "student_activities": ["Neurobiology case study review"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 2,
                "title": "Clinical Assessment",
                "description": "Intake, risk assessment, and screening tools.",
                "learning_objectives": ["Conduct trauma-informed assessments", "Use screening tools effectively"],
                "topics_covered": ["Intake and case history", "Risk assessment", "Screening tools and frameworks"],
                "student_activities": ["Assessment simulation"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 3,
                "title": "Treatment Modalities",
                "description": "Cognitive, somatic, and stabilization approaches.",
                "learning_objectives": ["Apply evidence-based interventions", "Implement stabilization techniques"],
                "topics_covered": ["Cognitive and somatic approaches", "Stabilization techniques", "Emotional regulation protocols"],
                "student_activities": ["Intervention planning"],
                "estimated_time": "5 hours"
            },
            {
                "module_number": 4,
                "title": "Session Structuring",
                "description": "Therapeutic alliance and progress tracking.",
                "learning_objectives": ["Build therapeutic alliance", "Track clinical progress"],
                "topics_covered": ["Therapeutic alliance", "Session planning", "Progress tracking"],
                "student_activities": ["Session structure design"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 5,
                "title": "Ethics and Supervision",
                "description": "Clinical boundaries and supervision models.",
                "learning_objectives": ["Maintain clinical boundaries", "Understand supervision models"],
                "topics_covered": ["Clinical boundaries", "Documentation", "Supervision models"],
                "student_activities": ["Ethical scenario analysis"],
                "estimated_time": "3 hours"
            }
        ],
        "CCTSF (Certified Clinical Trauma Specialist - Family)": [
            {
                "module_number": 1,
                "title": "Family Systems Theory",
                "description": "Structure, roles, and communication in family units.",
                "learning_objectives": ["Understand family systems theory", "Identify communication patterns"],
                "topics_covered": ["Structure and roles", "Communication patterns"],
                "student_activities": ["Genogram creation"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 2,
                "title": "Intergenerational Trauma",
                "description": "Patterns of transmission and attachment styles.",
                "learning_objectives": ["Identify intergenerational patterns", "Understand attachment styles"],
                "topics_covered": ["Transmission patterns", "Attachment styles"],
                "student_activities": ["Intergenerational mapping"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 3,
                "title": "Family Assessment",
                "description": "Mapping family systems and identifying conflicts.",
                "learning_objectives": ["Map family systems", "Identify systemic conflicts"],
                "topics_covered": ["Mapping family systems", "Conflict identification"],
                "student_activities": ["Family assessment workshop"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 4,
                "title": "Intervention Strategies",
                "description": "Family therapy techniques and conflict resolution.",
                "learning_objectives": ["Facilitate family-based interventions", "Apply conflict resolution"],
                "topics_covered": ["Family therapy techniques", "Conflict resolution"],
                "student_activities": ["Intervention roleplay"],
                "estimated_time": "5 hours"
            },
            {
                "module_number": 5,
                "title": "Ethical Practice",
                "description": "Confidentiality and cultural sensitivity in family work.",
                "learning_objectives": ["Maintain confidentiality in systems work", "Apply cultural sensitivity"],
                "topics_covered": ["Confidentiality in family work", "Cultural sensitivity"],
                "student_activities": ["Cultural competence exercise"],
                "estimated_time": "3 hours"
            }
        ],
        "CCTSA (Certified Clinical Trauma Specialist - Addiction)": [
            {
                "module_number": 1,
                "title": "Neurobiology of Addiction",
                "description": "Brain reward systems and dependency cycles.",
                "learning_objectives": ["Understand addiction neurobiology", "Define dependency cycles"],
                "topics_covered": ["Brain reward systems", "Dependency cycles"],
                "student_activities": ["Addiction pathway mapping"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 2,
                "title": "Trauma-Addiction Link",
                "description": "Co-occurring disorders and behavioral patterns.",
                "learning_objectives": ["Integrate trauma-informed addiction treatment", "Identify co-occurring patterns"],
                "topics_covered": ["Co-occurring disorders", "Behavioral patterns"],
                "student_activities": ["Case formulation"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 3,
                "title": "Clinical Interventions",
                "description": "Behavioral and somatic approaches to recovery.",
                "learning_objectives": ["Apply addiction recovery techniques", "Integrate somatic tools"],
                "topics_covered": ["Behavioral therapies", "Somatic approaches"],
                "student_activities": ["Treatment planning exercise"],
                "estimated_time": "5 hours"
            },
            {
                "module_number": 4,
                "title": "Recovery Models",
                "description": "Rehabilitation frameworks and support systems.",
                "learning_objectives": ["Implement rehabilitation frameworks", "Build support systems"],
                "topics_covered": ["Rehabilitation frameworks", "Support systems"],
                "student_activities": ["Support network design"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 5,
                "title": "Relapse Prevention",
                "description": "Triggers and long-term care planning.",
                "learning_objectives": ["Apply relapse prevention strategies", "Develop care plans"],
                "topics_covered": ["Triggers and coping strategies", "Long-term care planning"],
                "student_activities": ["Relapse prevention plan design"],
                "estimated_time": "4 hours"
            }
        ],
        "ACCTS (Advanced Certified Clinical Trauma Specialist)": [
            {
                "module_number": 1,
                "title": "Complex Trauma",
                "description": "Chronic trauma patterns and dissociation.",
                "learning_objectives": ["Work with complex trauma cases", "Understand dissociation"],
                "topics_covered": ["Chronic trauma patterns", "Dissociation"],
                "student_activities": ["Complex case analysis"],
                "estimated_time": "5 hours"
            },
            {
                "module_number": 2,
                "title": "Advanced Diagnostics",
                "description": "Differential diagnosis and multi-layered assessment.",
                "learning_objectives": ["Apply advanced diagnostic frameworks", "Perform layered assessments"],
                "topics_covered": ["Differential diagnosis", "Multi-layered assessment"],
                "student_activities": ["Advanced diagnostic workshop"],
                "estimated_time": "5 hours"
            },
            {
                "module_number": 3,
                "title": "Intervention Integration",
                "description": "Multi-modal therapies and custom treatment design.",
                "learning_objectives": ["Integrate multi-modal therapies", "Design custom treatments"],
                "topics_covered": ["Multi-modal therapies", "Custom treatment design"],
                "student_activities": ["Integrated treatment blueprint"],
                "estimated_time": "6 hours"
            },
            {
                "module_number": 4,
                "title": "Supervision",
                "description": "Supervisory models and feedback frameworks.",
                "learning_objectives": ["Provide clinical supervision", "Use feedback frameworks"],
                "topics_covered": ["Supervisory models", "Feedback frameworks"],
                "student_activities": ["Supervision roleplay"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 5,
                "title": "Professional Practice",
                "description": "Ethical leadership and advanced documentation.",
                "learning_objectives": ["Demonstrate ethical leadership", "Apply advanced documentation"],
                "topics_covered": ["Ethical leadership", "Advanced documentation"],
                "student_activities": ["Leadership project"],
                "estimated_time": "4 hours"
            }
        ],
        "CCTS-P (Certified Clinical Trauma Specialist - Prenatal/Pediatric)": [
            {
                "module_number": 1,
                "title": "Developmental Foundations",
                "description": "Prenatal influences and early brain development.",
                "learning_objectives": ["Understand prenatal influences", "Learn developmental brain basics"],
                "topics_covered": ["Prenatal influences", "Early brain development"],
                "student_activities": ["Devleopmental timeline mapping"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 2,
                "title": "Pediatric Trauma",
                "description": "Childhood stress responses and behavioral indicators.",
                "learning_objectives": ["Understand developmental trauma", "Identify pediatric indicators"],
                "topics_covered": ["Childhood stress responses", "Behavioral indicators"],
                "student_activities": ["Indicator identification workshop"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 3,
                "title": "Assessment Techniques",
                "description": "Child-friendly tools and parent interviews.",
                "learning_objectives": ["Assess pediatric mental health", "Conduct parent interviews"],
                "topics_covered": ["Child-friendly tools", "Parent interviews"],
                "student_activities": ["Interview simulation"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 4,
                "title": "Interventions",
                "description": "Play therapy principles and family involvement.",
                "learning_objectives": ["Apply age-appropriate interventions", "Engage families in therapy"],
                "topics_covered": ["Play therapy principles", "Family involvement"],
                "student_activities": ["Play therapy technique practice"],
                "estimated_time": "5 hours"
            },
            {
                "module_number": 5,
                "title": "Safeguarding",
                "description": "Ethical care and reporting protocols.",
                "learning_objectives": ["Maintain ethical pediatric care", "Follow reporting protocols"],
                "topics_covered": ["Ethical care", "Reporting protocols"],
                "student_activities": ["Safeguarding protocol review"],
                "estimated_time": "3 hours"
            }
        ],
        "Rehabilitation Support Program": [
            {
                "module_number": 1,
                "title": "Rehabilitation Frameworks",
                "description": "Foundational models for rehabilitation and support.",
                "learning_objectives": ["Understand rehab frameworks"],
                "topics_covered": ["Rehabilitation frameworks"],
                "student_activities": ["Framework analysis"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 2,
                "title": "Behavioral Reintegration",
                "description": "Strategies for community and behavioral reintegration.",
                "learning_objectives": ["Apply reintegration strategies"],
                "topics_covered": ["Behavioral reintegration"],
                "student_activities": ["Reintegration planning"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 3,
                "title": "Trauma-Informed Correctional Care",
                "description": "Applying trauma-informed principles in correctional settings.",
                "learning_objectives": ["Learn trauma-informed correctional care"],
                "topics_covered": ["Correctional care principles"],
                "student_activities": ["Scenario roleplay"],
                "estimated_time": "4 hours"
            },
            {
                "module_number": 4,
                "title": "Community Support Systems",
                "description": "Building sustainable community support structures.",
                "learning_objectives": ["Build community support"],
                "topics_covered": ["Community support systems"],
                "student_activities": ["System design"],
                "estimated_time": "4 hours"
            }
        ]
    }

    for course_title, modules in clinical_modules_data.items():
        course = await db.courses.find_one({"title": course_title})
        if not course:
            print(f"Skipping {course_title}: Course not found.")
            continue
        
        course_id = course['id']
        await db.modules.delete_many({"course_id": course_id})
        
        for mod in modules:
            mod["course_id"] = course_id
            mod["id"] = str(uuid.uuid4())
            mod["week"] = mod["module_number"] # Using module number as week for now
            mod["created_at"] = datetime.now(timezone.utc).isoformat()
            mod["assessment"] = {
                "quiz_questions": [],
                "passing_score": 0.8
            }
            await db.modules.insert_one(mod)
        
        print(f"Successfully seeded {len(modules)} clinical modules for '{course_title}'")

if __name__ == "__main__":
    asyncio.run(seed_clinical_curriculum())
