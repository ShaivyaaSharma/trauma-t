import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

latex_data = [
    {
        "module_number": 1,
        "title": "Introduction to Emotional Transformation Therapy",
        "description": "This module introduces the history, purpose, and theoretical basis of ETT. Students learn how ETT integrates psychotherapy with light and color modalities to rapidly transform emotional states. The module clarifies key concepts and distinguishes ETT from related approaches, setting the foundation for later technique-specific modules.",
        "learning_objectives": [
            "Define Emotional Transformation Therapy (ETT) and its foundational principles.",
            "Summarize the historical development of ETT and its founding theorists.",
            "Describe how ETT combines cognitive-emotional theory with sensory stimulation.",
            "Differentiate ETT from other modalities (e.g., EMDR, cognitive-behavioral therapy).",
            "Recognize the certification pathway and professional standards (ICF, NBCC, CEUs)."
        ],
        "topics_covered": [
            "Origins and evolution of ETT; role of the ETT Institute.",
            "Core components: light/color devices, eye movement, attachment focus.",
            "Theoretical foundations: mind-body connection, introduction to attachment.",
            "Scope of ETT practice and prerequisites (licensed practitioner requirement).",
            "Overview of training levels (ETT I–V) for context."
        ],
        "student_activities": [
            "Quiz on ETT key terms and historical milestones.",
            "Short reflection essay: comparing ETT with familiar therapies.",
            "Scenario analysis: selecting therapy approaches for given case vignettes."
        ],
        "estimated_time": "3 hours"
    },
    {
        "module_number": 2,
        "title": "Theoretical Foundations of Emotion and Attachment",
        "description": "This module covers psychological theories of emotion and attachment relevant to ETT. Students explore how emotions are generated and processed in the brain and body, and how early attachment patterns influence emotional regulation. The content provides frameworks for understanding client emotional responses and the rationale for rapid, targeted interventions.",
        "learning_objectives": [
            "Describe major theories of emotion (e.g., physiological, cognitive).",
            "Explain the role of attachment styles in emotional development and trauma.",
            "Identify common attachment patterns (secure, anxious, avoidant, disorganized).",
            "Discuss interpersonal neurobiology: how relationships shape the brain.",
            "Understand mind-body connections in stress and healing."
        ],
        "topics_covered": [
            "Overview of emotion models (James-Lange, Schachter-Singer, constructivist theories).",
            "Neurobiological components: amygdala, limbic system, stress response.",
            "Attachment theory basics: Bowlby, Ainsworth; secure vs. insecure attachments.",
            "Interpersonal neurobiology principles: emotional regulation and memory.",
            "Impact of trauma and early experiences on emotional patterns."
        ],
        "student_activities": [
            "Quiz on emotion theories and attachment concepts.",
            "Reflective exercise on personal emotion regulation strategies.",
            "Case conceptualization: identify a client's attachment style from a vignette."
        ],
        "estimated_time": "4 hours"
    },
    {
        "module_number": 3,
        "title": "Neuroscience of Visual Stimulation",
        "description": "This module examines how visual stimuli (light and color) affect brain function and emotion. Students learn basic neuroanatomy of vision and emotion, including how light cues influence neural pathways and brainwave states. Theoretical knowledge of sensory processing and neuroplasticity is presented to explain the rapid shifts observed in ETT practice.",
        "learning_objectives": [
            "Explain how photic (light) stimulation can influence neural activity and brainwave patterns.",
            "Identify brain regions involved in visual processing and emotional response (e.g., retina, visual cortex, thalamus, amygdala).",
            "Describe neuroplasticity and its relevance to emotional change.",
            "Understand the role of brainwave entrainment in emotion regulation."
        ],
        "topics_covered": [
            "Anatomy of the human visual system: retina, optic nerve, visual pathways.",
            "Brain regions for emotion processing: limbic system, visual cortex, thalamus.",
            "Color perception and wavelengths: how different colors are processed neurologically.",
            "Brainwave frequencies (alpha, beta, theta) and entrainment principles.",
            "Theoretical models of how light therapy may alter neural circuits (no device demonstration)."
        ],
        "student_activities": [
            "Quiz on neuroanatomy of vision and emotion.",
            "Diagram exercise: trace a visual stimulus from eye to brain regions.",
            "Scenario analysis: evaluate a hypothetical response to specific light frequencies."
        ],
        "estimated_time": "3 hours"
    },
    {
        "module_number": 4,
        "title": "Spectral Resonance Technique (SRT) and Color Psychology",
        "description": "This module presents the theory behind the Spectral Resonance Technique. Students explore how color associations relate to emotional states and learn the conceptual steps of SRT. The focus is on understanding how the color chart and wand are used to identify core emotions; practical device use is not performed.",
        "learning_objectives": [
            "Describe the SRT procedure and its key components (color chart, wand).",
            "Explain the psychological significance of different colors in ETT.",
            "Analyze how color selection can signal underlying emotional themes.",
            "Outline the theoretical steps of an SRT session."
        ],
        "topics_covered": [
            "The spectral resonance color chart: structure and color-emotion correspondences.",
            "Psychological and cultural meanings of basic colors (e.g., red = energy/anger, blue = calm).",
            "SRT protocol: screening for photosensitivity, color selection, verbal processing.",
            "Case examples (conceptual) of using SRT to target core emotions.",
            "Comparisons to other color/light therapies."
        ],
        "student_activities": [
            "Quiz on color-emotion associations and SRT terminology.",
            "Case study: interpret a client's color choice and propose a reflective intervention.",
            "Reflection essay on the theoretical benefits and limitations of color-based techniques."
        ],
        "estimated_time": "3 hours"
    },
    {
        "module_number": 5,
        "title": "Multidimensional Eye Movement (MDEM) Theory",
        "description": "This module delves into the theory of Multidimensional Eye Movement (MDEM), an advanced ETT technique. Students study how guided eye positions and movements are theorized to access and transform emotional memories. The focus is cognitive: understanding MDEM steps and comparing it to other eye movement therapies (e.g., EMDR) without practical enactment.",
        "learning_objectives": [
            "Explain the core principles of MDEM and its intended therapeutic effects.",
            "Differentiate MDEM from EMDR and other eye movement-based therapies.",
            "Describe the typical theoretical sequence of an MDEM session.",
            "Understand how specific eye movement patterns may facilitate emotional processing."
        ],
        "topics_covered": [
            "Overview of MDEM steps: targets, eye positions, bilateral movement.",
            "Neuroscientific rationale for eye movement in trauma processing.",
            "Comparisons: MDEM vs EMDR (speed, structure, applications).",
            "Role of therapist cues and client focus during MDEM.",
            "Review of conceptual clinical examples demonstrating MDEM effects."
        ],
        "student_activities": [
            "Quiz on MDEM vs EMDR principles.",
            "Scenario analysis: plan an MDEM-based intervention for a case study.",
            "Reflective journal entry: articulate understanding of MDEM's theoretical basis."
        ],
        "estimated_time": "4 hours"
    },
    {
        "module_number": 6,
        "title": "Integrating ETT Techniques into Practice",
        "description": "This module covers how to synthesize ETT techniques in a counseling context. Students learn how to plan an ETT-informed session and how ETT complements traditional psychotherapy. Concepts include client assessment, setting goals, and monitoring progress. Emphasis is on case conceptualization and session structure (conceptual, not practical).",
        "learning_objectives": [
            "Identify assessment methods appropriate for ETT (e.g., photosensitivity screening, emotional inventory).",
            "Develop a treatment plan integrating ETT methods with clinical goals.",
            "Plan session structure combining talk therapy and ETT procedures.",
            "Explain how to adapt techniques to client needs while ensuring safety."
        ],
        "topics_covered": [
            "Client intake and screening: contraindications (e.g., seizure risk).",
            "Goal setting and outcome expectations in an ETT context.",
            "Structuring an ETT session: orientation, technique application, debrief.",
            "Integrating cognitive reframing and psychoeducation with ETT tools.",
            "Professional practice issues: informed consent, documentation, referral."
        ],
        "student_activities": [
            "Case study: write an ETT treatment plan for a sample client profile.",
            "Quiz on client safety, screening, and contraindications.",
            "Discussion (theoretical): adapting ETT in diverse clinical scenarios."
        ],
        "estimated_time": "4 hours"
    },
    {
        "module_number": 7,
        "title": "Ethical, Cultural, and Professional Standards",
        "description": "This module addresses ethical and multicultural considerations for ETT practitioners. Students review professional codes (NBCC, ICF) and discuss their application to ETT. Topics include client safety, confidentiality, and therapist boundaries. Cultural competence is emphasized, exploring how color and emotional expression vary across populations.",
        "learning_objectives": [
            "Summarize key ethical principles from NBCC and ICF relevant to ETT practice.",
            "Identify cultural factors affecting perceptions of color, light, and emotion.",
            "Discuss confidentiality, boundaries, and informed consent in light-based therapy.",
            "Recognize the role of clinician self-care and professional development."
        ],
        "topics_covered": [
            "Ethical standards: autonomy, non-maleficence, informed consent.",
            "Cultural considerations: symbolic meanings of colors, cultural attitudes toward therapy.",
            "Legal and professional guidelines: scope of practice, mandated reporting.",
            "Client privacy and data protection (especially in tele-therapy contexts).",
            "Continuing competency: supervision, peer consultation, ongoing education."
        ],
        "student_activities": [
            "Reflection essay on an ethical dilemma in ETT therapy.",
            "Quiz on ethical codes, legal issues, and multicultural competence.",
            "Case discussion (theoretical): adapting ETT for culturally diverse clients."
        ],
        "estimated_time": "3 hours"
    },
    {
        "module_number": 8,
        "title": "Research, Evidence, and Outcomes",
        "description": "This module reviews research evidence and outcome evaluation methods related to ETT and similar therapies. Students learn about evidence-based practice and basic research literacy. Topics include reviewing key study findings, measuring therapy outcomes, and understanding the limits of current evidence. Emphasis is on critical thinking rather than statistical computation.",
        "learning_objectives": [
            "Summarize major research findings on ETT efficacy and related methods.",
            "Understand the principles of evidence-based practice in therapy.",
            "Identify common outcome measures for emotional and psychological change.",
            "Critically evaluate a brief research scenario or claim."
        ],
        "topics_covered": [
            "Overview of research on light therapy, SRT, MDEM (levels of evidence).",
            "Basics of evidence-based practice and clinical decision-making.",
            "Outcome measurement: symptom rating scales (depression, anxiety, trauma inventories).",
            "Program evaluation essentials: tracking client progress and response.",
            "Research limitations and current gaps in ETT literature."
        ],
        "student_activities": [
            "Quiz on research methodology terms and evidence-based concepts.",
            "Critique of a hypothetical research abstract on ETT outcomes.",
            "Discussion: designing a basic outcome tracking form for a case study."
        ],
        "estimated_time": "3 hours"
    },
    {
        "module_number": 9,
        "title": "Case Conceptualization and Synthesis",
        "description": "This module integrates knowledge by having students work through case studies in a conceptual manner. Learners apply ETT theory to hypothetical client cases, planning assessments and interventions without practical enactment. The module emphasizes synthesizing material from all previous topics to build a coherent treatment approach.",
        "learning_objectives": [
            "Apply ETT principles to analyze a client's emotional presentation.",
            "Develop a comprehensive treatment approach using ETT and supportive techniques.",
            "Synthesize learning from previous modules to justify chosen interventions.",
            "Articulate a case formulation in structured written form."
        ],
        "topics_covered": [
            "Case conceptualization methods: e.g., BIOLOGY model, biopsychosocial factors.",
            "Holistic perspective: integrating cognitive, emotional, and somatic elements.",
            "Designing an ETT-informed session plan step by step.",
            "Professional documentation: writing case notes and treatment rationale.",
            "Common clinical issues addressed by ETT (trauma, anxiety, chronic pain)."
        ],
        "student_activities": [
            "Case study report: detailed conceptualization and intervention plan.",
            "Quiz matching client presentations to ETT techniques.",
            "Peer review (discussion): provide feedback on a sample case formulation."
        ],
        "estimated_time": "4 hours"
    },
    {
        "module_number": 10,
        "title": "Final Review and Certification Preparation",
        "description": "The final module reviews key concepts and ensures readiness for certification. Students engage in synthesis activities, including comprehensive quizzes and self-assessment. The focus is on reinforcing understanding of ETT theory and preparing for the certificate exam, rather than introducing new material.",
        "learning_objectives": [
            "Review and consolidate learning objectives from all modules.",
            "Demonstrate mastery through a comprehensive final assessment.",
            "Identify remaining knowledge gaps and create a personal study plan.",
            "Understand the steps to obtain ETT certification and continuing education opportunities."
        ],
        "topics_covered": [
            "Recap of ETT core concepts, techniques, and ethical guidelines.",
            "Sample certification exam questions and case vignettes.",
            "Study strategies for continued professional development.",
            "Administrative steps: certificate issuance and next-level training options."
        ],
        "student_activities": [
            "Final comprehensive quiz covering all course modules.",
            "Self-reflection report on achieved competencies and future goals.",
            "Capstone scenario analysis integrating multiple ETT techniques."
        ],
        "estimated_time": "3 hours"
    }
]

async def update_db():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client["tti_db"]
    
    course = await db.courses.find_one({"title": "ETT Foundational Course"})
    if not course:
        print("Course not found!")
        return
        
    for module in latex_data:
        await db.modules.update_one(
            {"course_id": course["id"], "module_number": module["module_number"]},
            {"$set": {
                "title": module["title"],
                "description": module["description"],
                "learning_objectives": module["learning_objectives"],
                "topics_covered": module["topics_covered"],
                "student_activities": module["student_activities"],
                "estimated_time": module["estimated_time"]
            }}
        )
    print("Successfully updated database with LaTeX course outline.")

if __name__ == "__main__":
    asyncio.run(update_db())
