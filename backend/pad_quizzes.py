import asyncio
import os
import uuid
from motor.motor_asyncio import AsyncIOMotorClient

new_questions = {
    1: [
        {"question": "How does ETT distinguish itself from cognitive-behavioral therapy?", "options": ["It relies only on talking", "It integrates sensory stimulation directly into emotional processing", "It ignores the body entirely", "It requires no clinical training"], "correct_answer": 1, "explanation": "ETT actively uses sensory stimulation like light and eye movements alongside cognitive processing."},
        {"question": "Who can practice ETT professionally according to the guidelines?", "options": ["Anyone who buys the device", "Only licensed medical doctors", "Licensed mental health practitioners meeting the prerequisites", "Only physical therapists"], "correct_answer": 2, "explanation": "ETT requires a licensed mental health practitioner."},
        {"question": "What is the primary role of attachment focus in ETT?", "options": ["To blame parents for current issues", "To understand and process relational patterns impacting emotional regulation", "To diagnose personality disorders", "To replace medical interventions"], "correct_answer": 1, "explanation": "Attachment focus helps therapists understand relational patterns that shape a client's emotional regulation."},
        {"question": "Which of the following is NOT a core component of ETT?", "options": ["Light/Color devices", "Eye movement", "Attachment focus", "Acupuncture needles"], "correct_answer": 3, "explanation": "Acupuncture is not a core component of ETT."},
        {"question": "How many training levels does the standard ETT pathway typically include?", "options": ["1-3", "1-5", "1-10", "There are no structured levels"], "correct_answer": 1, "explanation": "The ETT curriculum typically progresses from Level I through V."}
    ],
    2: [
        {"question": "Which attachment style is typically characterized by a strong desire for closeness but a fear of rejection?", "options": ["Secure", "Anxious/Preoccupied", "Avoidant/Dismissive", "Disorganized"], "correct_answer": 1, "explanation": "Anxious attachment involves high emotional reactivity and fear of abandonment."},
        {"question": "According to constructivist emotion theory of ETT context, how are emotions perceived?", "options": ["As purely uncontrollable biological reflexes", "As constructed from physiological arousal and cognitive interpretation", "As illusions that don't exist in the brain", "They only exist in the digestive system"], "correct_answer": 1, "explanation": "Emotions involve both bodily sensations and the brain's sense-making processes."},
        {"question": "Which brain structure is primarily associated with initial emotional threat detection?", "options": ["Frontal lobe", "Amygdala", "Cerebellum", "Brainstem"], "correct_answer": 1, "explanation": "The amygdala acts as the brain's alarm system for threat detection."},
        {"question": "Interpersonal neurobiology suggests that:", "options": ["Relationships have no impact on brain structure", "Human brains grow independently of social interaction", "Our brains and nervous systems are shaped continuously by our relationships", "Only childhood relationships affect the brain"], "correct_answer": 2, "explanation": "Interpersonal neurobiology highlights that brains are deeply influenced by ongoing social connections."},
        {"question": "Mind-body connection in trauma implies that:", "options": ["Trauma is only 'in the head'", "Unprocessed trauma only affects muscle strength", "Trauma memories can be stored and reactivated somatically (in the body)", "Therapy should only involve physical exercise"], "correct_answer": 2, "explanation": "Trauma heavily impacts the autonomic nervous system and somatic experiences."}
    ],
    3: [
        {"question": "Which part of the brain acts as the primary visual processing center?", "options": ["Prefrontal cortex", "Visual cortex (Occipital lobe)", "Pons", "Medulla oblongata"], "correct_answer": 1, "explanation": "The visual cortex, located in the occipital lobe, processes visual information."},
        {"question": "What role does the retina play in light stimulation?", "options": ["It converts light into neural signals", "It controls eye movement", "It produces tears", "It changes the color of the iris"], "correct_answer": 0, "explanation": "The retina converts light waves into electrical neural impulses."},
        {"question": "Different color wavelengths can theoretically influence the brain because:", "options": ["They change the temperature of the brain significantly", "Distinct wavelengths stimulate specific retinal cells that project to unique neural pathways", "They magically heal cells", "They bypass the eye entirely"], "correct_answer": 1, "explanation": "Different wavelengths (colors) activate distinct photoreceptor patterns and neural tracks."},
        {"question": "Brainwave entrainment to an external stimulus occurs when:", "options": ["The brain stops functioning", "The brain's electrical rhythms synchronize with the frequency of that stimulus", "The patient falls into REM sleep", "Neurons spontaneously disconnect"], "correct_answer": 1, "explanation": "Entrainment means the brain matches the rhythm of external light or sound."},
        {"question": "Gamma brainwaves (30+ Hz) are generally associated with:", "options": ["Deep sleep", "Drowsiness", "High-level information processing and cognitive functioning", "Coma states"], "correct_answer": 2, "explanation": "Gamma waves are linked to high focus, learning, and peak concentration."}
    ],
    4: [
        {"question": "In the context of SRT, why is picking a color impactful?", "options": ["Because clients like art", "Color choice may unconciously signal underlying emotional states or resonances", "It determines the length of the session", "It replaces the need for verbal communication entirely"], "correct_answer": 1, "explanation": "Color choice acts as a somatic and psychological cue to inner states."},
        {"question": "What does 'resonance' mean in Spectral Resonance Technique?", "options": ["The sound the wand makes", "The matching of a specific color frequency to a specific emotional or physiological state", "The echo in the therapy room", "Singing during therapy"], "correct_answer": 1, "explanation": "Resonance refers to the alignment of an outer stimulus (color) with an inner state."},
        {"question": "Which of these is a theoretical step in SRT?", "options": ["Applying ice packs", "Scanning the color chart while tracking somatic reactions", "Closing eyes for the entire 60 minutes", "Writing a detailed autobiography"], "correct_answer": 1, "explanation": "SRT involves engaging with the color chart while noticing internal reactions."},
        {"question": "In generalized color psychology, yellow is most frequently linked to:", "options": ["Deep sadness and grief", "High energy, intellect, or anxiety depending on brightness", "Sleep and relaxation", "Hunger and eating"], "correct_answer": 1, "explanation": "Yellow is typically associated with mental stimulation, energy, and sometimes anxiety."},
        {"question": "If a client shows highly aversive reactions to all light during prescreening, a practitioner should:", "options": ["Ignore it", "Force them to look at the light", "Recognize it as a contraindication or sign of photosensitivity and proceed with caution or alternative methods", "Tell them they are resisting therapy"], "correct_answer": 2, "explanation": "Photosensitivity is a crucial safety screening metric."}
    ],
    5: [
        {"question": "What does multidimensional mean in MDEM?", "options": ["Using 3D glasses", "Involving variations in eye position angles, depths, and speeds rather than just basic side-to-side", "Practicing in different rooms", "Only moving eyes up and down"], "correct_answer": 1, "explanation": "MDEM uses diverse visual fields and angles for processing."},
        {"question": "Slower eye movements in MDEM are typically theorized to:", "options": ["Increase anxiety drastically", "Facilitate deep parasympathetic processing and emotional integration", "Cause hypnosis", "Make the client fall asleep immediately"], "correct_answer": 1, "explanation": "Slower, guided tracking often aids in calming the nervous system and integrating emotion."},
        {"question": "How might MDEM differ from a standard EMDR session physically?", "options": ["It doesn't use the eyes at all", "EMDR relies heavily on rapid horizontal saccades, while MDEM uses varied targeted positions and slow tracking", "EMDR uses a wand", "MDEM requires closed eyes"], "correct_answer": 1, "explanation": "MDEM integrates specific angled tracking rather than just horizontal rapid movement."},
        {"question": "The concept of an 'emotional target' refers to:", "options": ["A dartboard in the office", "The specific memory, belief, or bodily sensation the client focuses on during eye movement", "The therapist's goal for the day", "The duration of the session"], "correct_answer": 1, "explanation": "A target helps anchor the brain to the specific neural network being processed."},
        {"question": "A key theoretical component of successful MDEM is:", "options": ["The client feeling entirely detached", "Simultaneous dual awareness (anchored in present while processing the past)", "Forgetting the memory instantly", "Complete muscle paralysis"], "correct_answer": 1, "explanation": "Dual awareness prevents retraumatization and safety during processing."}
    ],
    6: [
        {"question": "Why is it important to integrate cognitive reframing with ETT?", "options": ["To make the session last longer", "Because sensory shifts often open windows for new cognitive insights that need to be actively solidified", "Because ETT doesn't work on its own", "To confuse the client"], "correct_answer": 1, "explanation": "Combining somatic shifts with cognitive meaning-making leads to lasting change."},
        {"question": "A typical debrief phase of an ETT session includes:", "options": ["Stopping abruptly", "Reviewing the shifts experienced, grounding the client, and planning next steps", "Only asking for payment", "Starting a new deep trauma target 5 minutes before the end"], "correct_answer": 1, "explanation": "Debriefing ensures safety and integration before the client leaves."},
        {"question": "Which of these is a valid goal-setting approach for ETT?", "options": ["Promising to cure everything in one session", "Focusing exclusively on physical fitness", "Setting specific, measurable emotional regulation or trauma-reduction targets", "Setting goals the client doesn't agree with"], "correct_answer": 2, "explanation": "Goals should be collaborative, targeted, and appropriate for the modality."},
        {"question": "Psychoeducation in ETT involves:", "options": ["Explaining to the client how their brain, body, and the light/eye techniques interact", "Lecturing the client on their faults", "Recommending books unrelated to therapy", "Remaining completely silent about the process"], "correct_answer": 0, "explanation": "Psychoeducation empowers the client by understanding the 'why' behind the methods."},
        {"question": "If a client becomes highly dysregulated during an ETT exercise, the integration plan should:", "options": ["Push harder into the trauma", "Pivot to immediate grounding and containment strategies", "End the session immediately", "Ignore the dysregulation"], "correct_answer": 1, "explanation": "Safety and regulation are the highest priority in trauma work."}
    ],
    7: [
        {"question": "Why is cultural competence vital regarding color symbolism?", "options": ["It's not vital; colors mean the same thing everywhere", "A color like white might mean purity in one culture but mourning in another, altering emotional resonance", "To pass a test only", "Because artists say so"], "correct_answer": 1, "explanation": "Cultural background deeply influences psychological associations with color."},
        {"question": "Regarding data protection, telehealth ETT sessions must:", "options": ["Be recorded and posted online", "Use HIPAA (or equivalent) compliant, secure video platforms", "Be done in public coffee shops", "Ignore privacy laws if the client agrees"], "correct_answer": 1, "explanation": "Confidentiality and secure tech are mandatory ethical standards."},
        {"question": "A therapist using ETT realizes a client is dealing with an issue outside their scope of practice. What is the ethical action?", "options": ["Try to fix it anyway using light therapy", "Refer the client to a qualified specialist or seek extensive supervision", "Pretend it's not an issue", "Discharge the client with no explanation"], "correct_answer": 1, "explanation": "Practicing within scope of competence is a core NBCC/ICF ethical mandate."},
        {"question": "Clinician self-care in trauma modalities like ETT is primarily meant to prevent:", "options": ["Boredom", "Vicarious trauma and professional burnout", "Earning too much money", "Losing their license randomly"], "correct_answer": 1, "explanation": "Working with intense emotion requires self-regulation to prevent vicarious trauma."},
        {"question": "Informed consent for ETT should explicitly include:", "options": ["A guarantee of complete symptom resolution", "Explanation of the novel sensory tools (lights, wands) and their potential psychological physical effects", "A demand for upfront payment of 10 sessions", "Nothing, it should be a surprise"], "correct_answer": 1, "explanation": "Clients must understand the specific tools and methods being used on them."}
    ],
    8: [
        {"question": "Which of these constitutes a standardized outcome measure?", "options": ["Asking the client 'do you feel better?'", "Using a validated scale like the PHQ-9 or PCL-5 before and after treatment loops", "The therapist's gut feeling", "Measuring the client's height"], "correct_answer": 1, "explanation": "Standardized measures provide objective tracking data."},
        {"question": "In evidence-based practice, 'clinical expertise' refers to:", "options": ["Ignoring research in favor of habit", "The practitioner's ability to use clinical skills to integrate research with client context", "Having the most advanced degrees", "Being the oldest therapist in the clinic"], "correct_answer": 1, "explanation": "Clinical expertise is the bridge between raw data and human application."},
        {"question": "Why are single-case study reports considered lower in the hierarchy of evidence than RCTs?", "options": ["They lack control groups to rule out placebo or confounding variables", "Because they are written by individuals", "Because they are too long", "They aren't actually lower"], "correct_answer": 0, "explanation": "RCTs control for variables that single cases cannot, providing stronger efficacy proof."},
        {"question": "If a research study states ETT had statistically significant results, it implies:", "options": ["The results are guaranteed for every client", "The results are likely not due to chance, but clinical significance must still be evaluated", "The treatment was 100% effective", "No further research is ever needed"], "correct_answer": 1, "explanation": "Statistical significance means the effect is mathematically reliable, though clinical impact may vary."},
        {"question": "Tracking client outcomes session-by-session is beneficial primarily because:", "options": ["It justifies higher fees", "It allows the therapist to dynamically adjust the treatment plan if the client is not improving", "It creates more paperwork", "It guarantees publication in a journal"], "correct_answer": 1, "explanation": "Regular outcome tracking prevents treatment failure by signaling when a pivot is needed."}
    ],
    9: [
        {"question": "What is the primary purpose of a case conceptualization?", "options": ["To judge the client", "To integrate client history, symptoms, and theory into a coherent roadmap for treatment", "To write a biography", "To show off to peers"], "correct_answer": 1, "explanation": "Conceptualization is the compass that guides clinical intervention."},
        {"question": "In the BIOLOGY model or biopsychosocial approach, a client's chronic pain is:", "options": ["Ignored entirely in psychological therapy", "Viewed as potentially interacting with their psychological trauma and emotional dysregulation", "Told to be 'all in their head'", "Only treated with ETT wands"], "correct_answer": 1, "explanation": "Somatic and psychological aspects are deeply interconnected in holistic conceptualizations."},
        {"question": "When formulating a treatment strategy, why is the sequence of interventions important?", "options": ["It doesn't matter", "Establishing safety and regulation must precede deep trauma processing", "You should do the hardest things first to get them over with", "insurance companies demand it"], "correct_answer": 1, "explanation": "Trauma processing without prior regulation skills can cause destabilization."},
        {"question": "A case note documenting an ETT session should primarily focus on:", "options": ["What the client was wearing", "Observable behaviors, specific interventions applied, client response, and progress toward goals", "The therapist's personal opinions about the client's family", "Complete transcripts of the conversation"], "correct_answer": 1, "explanation": "Clinical notes must be objective, focused on treatment, and track clinical progress."},
        {"question": "If a comprehensive case conceptualization involves multiple comorbid issues (e.g., trauma AND severe substance abuse), an ETT practitioner might:", "options": ["Treat them all simultaneously in 30 minutes", "Coordinate care with other specialists (e.g., addiction counselors) while targeting specific agreed-upon goals", "Refuse to treat the client", "Ignore the substance abuse"], "correct_answer": 1, "explanation": "Complex cases often require a coordinated care team and prioritized goal setting."}
    ],
    10: [
        {"question": "Review: The core distinct mechanism of ETT compared to traditional talk therapy is:", "options": ["It uses fewer words", "It actively integrates visual/photic sensory stimulation to alter neural processing states", "It happens only outdoors", "It requires no clinical assessment"], "correct_answer": 1, "explanation": "ETT's defining feature is the direct use of visual and sensory manipulation."},
        {"question": "Which system in the body is most directly targeted for regulation during ETT grounding exercises?", "options": ["The digestive system", "The autonomic nervous system", "The skeletal system", "The lymphatic system"], "correct_answer": 1, "explanation": "Grounding exercises primarily target the sympathetic and parasympathetic nervous system."},
        {"question": "To maintain ETT certification, practitioners typically must:", "options": ["Do nothing further", "Engage in continuing education and ethical practice guidelines", "Retake the foundational course every month", "Pay a daily fee"], "correct_answer": 1, "explanation": "Professional certifications require ongoing CEUs and adherence to ethics."},
        {"question": "A key takeaway regarding ETT and trauma processing is that:", "options": ["Trauma is permanently unchangeable", "Neural pathways related to trauma memory can be modified through targeted sensory and cognitive work (neuroplasticity)", "Only time heals trauma", "Trauma processing must always be painful"], "correct_answer": 1, "explanation": "Neuroplasticity allows for the transformation of traumatic memories via ETT."},
        {"question": "When approaching the final certification exam, a student should focus on:", "options": ["Only the colors of the wand", "Synthesizing attachments theory, neurobiology, and practical safety protocols of ETT", "Failing intentionally", "Memorizing textbook page numbers"], "correct_answer": 1, "explanation": "Certification requires holistic comprehension of the theory, science, and ethics of ETT."}
    ]
}

async def update_quizzes():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = AsyncIOMotorClient(mongo_url)
    db = client["tti_db"]
    
    course = await db.courses.find_one({"title": "ETT Foundational Course"})
    if not course:
        print("Course not found!")
        return
        
    modules = await db.modules.find({"course_id": course["id"]}).sort("module_number", 1).to_list(100)
    
    for module in modules:
        num = module["module_number"]
        if num in new_questions:
            current_assessment = module.get("assessment", {})
            current_questions = current_assessment.get("quiz_questions", [])
            
            # if we already have 10, skip (in case we run this multiple times)
            if len(current_questions) < 10:
                # Add unique IDs to the new questions
                for q in new_questions[num]:
                    q["id"] = str(uuid.uuid4())
                    
                updated_questions = current_questions + new_questions[num]
                # Slice to exactly 10 in case there are 11 or 12
                if len(updated_questions) > 10:
                    updated_questions = updated_questions[:10]
                    
                current_assessment["quiz_questions"] = updated_questions
                
                await db.modules.update_one(
                    {"_id": module["_id"]},
                    {"$set": {"assessment": current_assessment}}
                )
                print(f"Padded module {num} to {len(updated_questions)} questions.")

if __name__ == "__main__":
    asyncio.run(update_quizzes())
