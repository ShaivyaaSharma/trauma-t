from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'tti_secret_key_2024')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Stripe Config
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', 'sk_test_emergent')

# Create the main app
app = FastAPI(title="Trauma Transformation Institute API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# ============ MODELS ============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    track: str  # "wellness" or "clinical"
    level: str  # "prerequisite", "level1", "level2", "advanced"
    description: str
    detailed_description: str = ""
    price: float
    equipment_fee: float = 0.0
    duration: str
    location: str
    schedule: str
    instructor: str = "ETT Certified Trainer"
    max_participants: int = 20
    features: List[str] = []
    is_coming_soon: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CourseCreate(BaseModel):
    title: str
    track: str
    level: str
    description: str
    detailed_description: str = ""
    price: float
    equipment_fee: float = 0.0
    duration: str
    location: str
    schedule: str
    start_date: Optional[str] = None  # User-selected start date
    instructor: str = "Sonia Siddhu"
    max_participants: int = 20
    features: List[str] = []
    is_coming_soon: bool = False

class Enrollment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    payment_status: str = "pending"
    session_id: Optional[str] = None
    enrolled_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    user_email: str
    course_id: str
    amount: float
    currency: str = "inr"
    payment_status: str = "initiated"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CheckoutRequest(BaseModel):
    course_id: str
    origin_url: str

# ============ LEARNING MODULE MODELS ============

class QuizQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    options: List[str]
    correct_answer: int  # index of correct option (0-3)
    explanation: str = ""

class ModuleAssessment(BaseModel):
    quiz_questions: List[QuizQuestion] = []
    passing_score: float = 0.8  # 80%

class Module(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    week: int
    module_number: int
    title: str
    description: str
    learning_objectives: List[str] = []
    topics_covered: List[str] = []
    concept_explanation: str = ""
    instructor_script: str = ""
    student_activities: List[str] = []
    exercises: List[Dict] = []
    expected_outcome: str = ""
    assessment: ModuleAssessment
    estimated_time: str = "3 hours"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ModuleProgress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    module_id: str
    is_unlocked: bool = False
    is_completed: bool = False
    quiz_attempts: int = 0
    best_score: float = 0.0
    last_attempt_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class QuizSubmission(BaseModel):
    module_id: str
    answers: List[int]  # indices of selected options

class QuizResult(BaseModel):
    score: float
    total_questions: int
    correct_answers: int
    passed: bool
    questions_review: List[Dict]  # detailed review of each question

class UserProgressSummary(BaseModel):
    course_id: str
    total_modules: int
    completed_modules: int
    current_module: int
    overall_progress: float

# ============ AUTH HELPERS ============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============ AUTH ROUTES ============

@api_router.post("/auth/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password_hash": hash_password(user_data.password),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    token = create_token(user_id, user_data.email)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            email=user_data.email,
            name=user_data.name,
            created_at=user_doc["created_at"]
        )
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token(user["id"], user["email"])
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            created_at=user["created_at"]
        )
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        created_at=user["created_at"]
    )

# ============ COURSE ROUTES ============

@api_router.get("/courses", response_model=List[Course])
async def get_courses(track: Optional[str] = None):
    query = {}
    if track:
        query["track"] = track
    courses = await db.courses.find(query, {"_id": 0}).to_list(100)
    return courses

@api_router.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str):
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@api_router.post("/courses", response_model=Course)
async def create_course(course_data: CourseCreate):
    course = Course(**course_data.model_dump())
    await db.courses.insert_one(course.model_dump())
    return course

# ============ ENROLLMENT & PAYMENT ROUTES ============

@api_router.post("/enrollments/checkout")
async def create_checkout(request: Request, checkout_data: CheckoutRequest, user: dict = Depends(get_current_user)):
    # Get course details
    course = await db.courses.find_one({"id": checkout_data.course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.get("is_coming_soon"):
        raise HTTPException(status_code=400, detail="This course is not yet available for enrollment")
    
    # Check if already enrolled
    existing = await db.enrollments.find_one({
        "user_id": user["id"],
        "course_id": checkout_data.course_id,
        "payment_status": "paid"
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
    
    # Calculate total amount (course price + equipment fee)
    total_amount = float(course["price"]) + float(course.get("equipment_fee", 0))
    
    # Build URLs from frontend origin
    success_url = f"{checkout_data.origin_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{checkout_data.origin_url}/courses/{checkout_data.course_id}"
    
    # Create Stripe checkout
    host_url = str(request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    checkout_request = CheckoutSessionRequest(
        amount=total_amount,
        currency="inr",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user["id"],
            "user_email": user["email"],
            "course_id": checkout_data.course_id,
            "course_title": course["title"]
        }
    )
    
    session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Create payment transaction record
    transaction = PaymentTransaction(
        session_id=session.session_id,
        user_id=user["id"],
        user_email=user["email"],
        course_id=checkout_data.course_id,
        amount=total_amount,
        currency="inr",
        payment_status="initiated"
    )
    await db.payment_transactions.insert_one(transaction.model_dump())
    
    # Create pending enrollment
    enrollment = Enrollment(
        user_id=user["id"],
        course_id=checkout_data.course_id,
        payment_status="pending",
        session_id=session.session_id
    )
    await db.enrollments.insert_one(enrollment.model_dump())
    
    return {"checkout_url": session.url, "session_id": session.session_id}

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(request: Request, session_id: str, user: dict = Depends(get_current_user)):
    # Get transaction
    transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # If already processed as paid, return immediately
    if transaction["payment_status"] == "paid":
        return {"status": "complete", "payment_status": "paid"}
    
    # Check with Stripe
    host_url = str(request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction and enrollment based on status
        if status.payment_status == "paid" and transaction["payment_status"] != "paid":
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {
                    "payment_status": "paid",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            await db.enrollments.update_one(
                {"session_id": session_id},
                {"$set": {"payment_status": "paid"}}
            )
        elif status.status == "expired":
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {
                    "payment_status": "expired",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            await db.enrollments.update_one(
                {"session_id": session_id},
                {"$set": {"payment_status": "expired"}}
            )
        
        return {
            "status": status.status,
            "payment_status": status.payment_status,
            "amount_total": status.amount_total,
            "currency": status.currency
        }
    except Exception as e:
        logger.error(f"Error checking payment status: {e}")
        return {"status": "pending", "payment_status": transaction["payment_status"]}

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    
    host_url = str(request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.payment_status == "paid":
            # Update transaction
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": {
                    "payment_status": "paid",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            # Update enrollment
            await db.enrollments.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": {"payment_status": "paid"}}
            )
        
        return {"received": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"received": True}

# ============ USER DASHBOARD ROUTES ============

@api_router.get("/enrollments/my")
async def get_my_enrollments(user: dict = Depends(get_current_user)):
    enrollments = await db.enrollments.find(
        {"user_id": user["id"], "payment_status": "paid"},
        {"_id": 0}
    ).to_list(100)
    
    # Get course details for each enrollment
    result = []
    for enrollment in enrollments:
        course = await db.courses.find_one({"id": enrollment["course_id"]}, {"_id": 0})
        if course:
            result.append({
                "enrollment": enrollment,
                "course": course
            })
    
    return result

# ============ LEARNING MODULE ROUTES ============

@api_router.get("/courses/{course_id}/modules")
async def get_course_modules(course_id: str, user: dict = Depends(get_current_user)):
    """Get all modules for a course with user's progress"""
    # Check if user is enrolled
    enrollment = await db.enrollments.find_one({
        "user_id": user["id"],
        "course_id": course_id,
        "payment_status": "paid"
    })
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")
    
    # Get all modules for the course
    modules = await db.modules.find({"course_id": course_id}, {"_id": 0}).sort("module_number", 1).to_list(100)
    
    # Get user's progress for all modules
    progress_records = await db.module_progress.find({
        "user_id": user["id"],
        "course_id": course_id
    }, {"_id": 0}).to_list(100)
    
    # Create a map of module_id -> progress
    progress_map = {p["module_id"]: p for p in progress_records}
    
    # Combine modules with progress
    result = []
    for module in modules:
        progress = progress_map.get(module["id"], {
            "is_unlocked": module["module_number"] == 1,  # First module is unlocked by default
            "is_completed": False,
            "quiz_attempts": 0,
            "best_score": 0.0
        })
        result.append({
            **module,
            "progress": progress
        })
    
    return result

@api_router.get("/courses/{course_id}/modules/{module_id}")
async def get_module_detail(course_id: str, module_id: str, user: dict = Depends(get_current_user)):
    """Get detailed module content"""
    # Check enrollment
    enrollment = await db.enrollments.find_one({
        "user_id": user["id"],
        "course_id": course_id,
        "payment_status": "paid"
    })
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")
    
    # Get module
    module = await db.modules.find_one({"id": module_id, "course_id": course_id}, {"_id": 0})
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Get or create progress
    progress = await db.module_progress.find_one({
        "user_id": user["id"],
        "module_id": module_id
    }, {"_id": 0})
    
    if not progress:
        # Check if this is the first module or if previous module is completed
        if module["module_number"] == 1:
            is_unlocked = True
        else:
            # Get previous module
            prev_module = await db.modules.find_one({
                "course_id": course_id,
                "module_number": module["module_number"] - 1
            }, {"_id": 0})
            
            if prev_module:
                prev_progress = await db.module_progress.find_one({
                    "user_id": user["id"],
                    "module_id": prev_module["id"],
                    "is_completed": True
                }, {"_id": 0})
                is_unlocked = prev_progress is not None
            else:
                is_unlocked = False
        
        # Create progress record
        progress = ModuleProgress(
            user_id=user["id"],
            course_id=course_id,
            module_id=module_id,
            is_unlocked=is_unlocked
        ).model_dump()
        await db.module_progress.insert_one(progress)
        progress.pop("_id", None)
    
    # Check if module is unlocked
    if not progress["is_unlocked"]:
        raise HTTPException(status_code=403, detail="Module is locked. Complete previous module first.")
    
    return {
        **module,
        "progress": progress
    }

@api_router.get("/courses/{course_id}/modules/{module_id}/quiz")
async def get_module_quiz(course_id: str, module_id: str, user: dict = Depends(get_current_user)):
    """Get quiz questions for a module (without correct answers)"""
    # Check enrollment
    enrollment = await db.enrollments.find_one({
        "user_id": user["id"],
        "course_id": course_id,
        "payment_status": "paid"
    })
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")
    
    # Get module
    module = await db.modules.find_one({"id": module_id, "course_id": course_id}, {"_id": 0})
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Check if module is unlocked
    progress = await db.module_progress.find_one({
        "user_id": user["id"],
        "module_id": module_id
    }, {"_id": 0})
    
    if not progress or not progress.get("is_unlocked"):
        raise HTTPException(status_code=403, detail="Module is locked")
    
    # Return quiz questions without correct answers
    quiz_questions = []
    for q in module["assessment"]["quiz_questions"]:
        quiz_questions.append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"]
        })
    
    return {
        "module_id": module_id,
        "module_title": module["title"],
        "questions": quiz_questions,
        "passing_score": module["assessment"]["passing_score"],
        "attempts": progress.get("quiz_attempts", 0),
        "best_score": progress.get("best_score", 0.0)
    }

@api_router.post("/courses/{course_id}/modules/{module_id}/submit-quiz")
async def submit_quiz(
    course_id: str,
    module_id: str,
    submission: QuizSubmission,
    user: dict = Depends(get_current_user)
):
    """Submit quiz answers and get results"""
    # Check enrollment
    enrollment = await db.enrollments.find_one({
        "user_id": user["id"],
        "course_id": course_id,
        "payment_status": "paid"
    })
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")
    
    # Get module
    module = await db.modules.find_one({"id": module_id, "course_id": course_id}, {"_id": 0})
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Get progress
    progress = await db.module_progress.find_one({
        "user_id": user["id"],
        "module_id": module_id
    }, {"_id": 0})
    
    if not progress or not progress.get("is_unlocked"):
        raise HTTPException(status_code=403, detail="Module is locked")
    
    # Grade the quiz
    questions = module["assessment"]["quiz_questions"]
    if len(submission.answers) != len(questions):
        raise HTTPException(status_code=400, detail="Invalid number of answers")
    
    correct_count = 0
    questions_review = []
    
    for i, (user_answer, question) in enumerate(zip(submission.answers, questions)):
        is_correct = user_answer == question["correct_answer"]
        if is_correct:
            correct_count += 1
        
        questions_review.append({
            "question_number": i + 1,
            "question": question["question"],
            "user_answer": question["options"][user_answer] if 0 <= user_answer < len(question["options"]) else "No answer",
            "correct_answer": question["options"][question["correct_answer"]],
            "is_correct": is_correct,
            "explanation": question.get("explanation", "")
        })
    
    score = correct_count / len(questions)
    passed = score >= module["assessment"]["passing_score"]
    
    # Update progress
    update_data = {
        "quiz_attempts": progress.get("quiz_attempts", 0) + 1,
        "last_attempt_at": datetime.now(timezone.utc).isoformat()
    }
    
    if score > progress.get("best_score", 0):
        update_data["best_score"] = score
    
    if passed and not progress.get("is_completed"):
        update_data["is_completed"] = True
        update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        # Unlock next module
        next_module = await db.modules.find_one({
            "course_id": course_id,
            "module_number": module["module_number"] + 1
        }, {"_id": 0})
        
        if next_module:
            # Check if progress exists for next module
            next_progress = await db.module_progress.find_one({
                "user_id": user["id"],
                "module_id": next_module["id"]
            })
            
            if next_progress:
                await db.module_progress.update_one(
                    {"user_id": user["id"], "module_id": next_module["id"]},
                    {"$set": {"is_unlocked": True}}
                )
            else:
                next_progress_doc = ModuleProgress(
                    user_id=user["id"],
                    course_id=course_id,
                    module_id=next_module["id"],
                    is_unlocked=True
                ).model_dump()
                await db.module_progress.insert_one(next_progress_doc)
    
    await db.module_progress.update_one(
        {"user_id": user["id"], "module_id": module_id},
        {"$set": update_data}
    )
    
    return QuizResult(
        score=score,
        total_questions=len(questions),
        correct_answers=correct_count,
        passed=passed,
        questions_review=questions_review
    )

@api_router.get("/courses/{course_id}/progress")
async def get_course_progress(course_id: str, user: dict = Depends(get_current_user)):
    """Get user's overall progress in a course"""
    # Check enrollment
    enrollment = await db.enrollments.find_one({
        "user_id": user["id"],
        "course_id": course_id,
        "payment_status": "paid"
    })
    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")
    
    # Get total modules
    total_modules = await db.modules.count_documents({"course_id": course_id})
    
    # Get completed modules
    completed_count = await db.module_progress.count_documents({
        "user_id": user["id"],
        "course_id": course_id,
        "is_completed": True
    })
    
    # Find current module (first unlocked, not completed)
    current_progress = await db.module_progress.find_one({
        "user_id": user["id"],
        "course_id": course_id,
        "is_unlocked": True,
        "is_completed": False
    }, {"_id": 0})
    
    if current_progress:
        current_module_doc = await db.modules.find_one(
            {"id": current_progress["module_id"]},
            {"_id": 0}
        )
        current_module = current_module_doc["module_number"] if current_module_doc else 1
    else:
        # If all completed or none started
        current_module = completed_count + 1 if completed_count < total_modules else total_modules
    
    overall_progress = (completed_count / total_modules * 100) if total_modules > 0 else 0
    
    return UserProgressSummary(
        course_id=course_id,
        total_modules=total_modules,
        completed_modules=completed_count,
        current_module=current_module,
        overall_progress=overall_progress
    )

# ============ SEED DATA ============

@api_router.post("/seed")
async def seed_data():
    # Clear existing courses
    await db.courses.delete_many({})
    
    courses = [
        # Wellness Track
        Course(
            title="ETT Foundational Course",
            track="wellness",
            level="prerequisite",
            description="Essential foundation for all ETT training tracks",
            detailed_description="This comprehensive foundational course introduces the core principles of Emotional Transformation Therapy. You'll learn the theoretical framework, basic techniques, and prepare for advanced training in either the Wellness or Clinical track.",
            price=25000.00,
            equipment_fee=0.0,
            duration="2 days",
            location="Online (Google Meet/Zoom)",
            schedule="To be scheduled",
            instructor="Sonia Siddhu",
            max_participants=25,
            features=[
                "Introduction to ETT principles",
                "Understanding emotional patterns",
                "Basic intervention techniques",
                "Certificate of completion",
                "Access to online resources"
            ]
        ),
        Course(
            title="ETT Wellness Level 1",
            track="wellness",
            level="level1",
            description="Emotional regulation & stress reduction with SRT chart and wands (MDEM)",
            detailed_description="Level 1 Wellness training introduces the SRT (Spectral Resonance Therapy) chart and wands using the MDEM (Multi-Dimensional Energy Method). Learn to facilitate emotional regulation and stress reduction for personal and professional wellness applications.",
            price=28000.00,
            equipment_fee=0.0,
            duration="3-4 days",
            location="Online (Google Meet/Zoom)",
            schedule="To be scheduled",
            instructor="Sonia Siddhu",
            max_participants=20,
            features=[
                "SRT chart fundamentals",
                "MDEM wand techniques",
                "Emotional regulation protocols",
                "Stress reduction methods",
                "Practice sessions",
                "Equipment included"
            ]
        ),
        Course(
            title="ETT Wellness Level 2",
            track="wellness",
            level="level2",
            description="Brain wave light stimulation and Google-PES protocols",
            detailed_description="Advanced wellness training covering brain wave light stimulation techniques and Google-PES (Peripheral Energy Stimulation) protocols. Master sophisticated approaches to somatic healing and spiritual wellness pathways.",
            price=30000.00,
            equipment_fee=0.0,
            duration="3-4 days",
            location="Online (Google Meet/Zoom)",
            schedule="To be scheduled",
            instructor="Sonia Siddhu",
            max_participants=15,
            features=[
                "Brain wave stimulation",
                "Google-PES protocols",
                "Somatic healing techniques",
                "Spiritual wellness integration",
                "Advanced practice sessions",
                "Specialized equipment"
            ]
        ),
        # Clinical Track
        Course(
            title="ETT Clinical Level 1",
            track="clinical",
            level="level1",
            description="Core ETT techniques & attachment work for mental health professionals",
            detailed_description="Comprehensive clinical training covering all wellness content plus advanced clinical protocols. Learn core ETT techniques, attachment work methodologies, and evidence-based approaches for licensed mental health practitioners.",
            price=29000.00,
            equipment_fee=0.0,
            duration="4 days",
            location="Online (Google Meet/Zoom)",
            schedule="To be scheduled",
            instructor="Sonia Siddhu",
            max_participants=18,
            features=[
                "All Wellness Level 1 content",
                "Clinical assessment protocols",
                "Attachment-based interventions",
                "Case conceptualization",
                "Supervised practice",
                "Clinical documentation"
            ]
        ),
        Course(
            title="ETT Clinical Level 2",
            track="clinical",
            level="level2",
            description="Addiction, trauma, spirituality, and DSM-5 diagnostic integration",
            detailed_description="Advanced clinical certification covering complex presentations including addiction, somatic conditions, trauma, spirituality/religion integration, and DSM-5 diagnostic frameworks. Includes monthly consultation calls and certification requirements.",
            price=30000.00,
            equipment_fee=0.0,
            duration="4 days",
            location="Online (Google Meet/Zoom)",
            schedule="To be scheduled",
            instructor="Sonia Siddhu",
            max_participants=15,
            features=[
                "Addiction treatment protocols",
                "Trauma-informed interventions",
                "Somatic condition management",
                "Spiritual integration approaches",
                "DSM-5 diagnostic integration",
                "Monthly consultation calls",
                "Certification pathway"
            ]
        ),
        # Coming Soon Programs
        Course(
            title="Trauma-Informed Hospitality Training",
            track="wellness",
            level="advanced",
            description="Specialized training for hospitality staff and corporate teams",
            detailed_description="Coming soon: A specialized program designed for hospitality industry professionals and corporate teams to understand and respond to trauma-informed practices in workplace settings.",
            price=22000.00,
            duration="2 days",
            location="Online (Google Meet/Zoom)",
            schedule="Coming Soon",
            is_coming_soon=True,
            instructor="Sonia Siddhu",
            features=[
                "Understanding workplace trauma",
                "De-escalation techniques",
                "Self-care strategies",
                "Team support protocols"
            ]
        ),
        Course(
            title="Wellness Retreat Program",
            track="wellness",
            level="advanced",
            description="Immersive wellness retreat experience at holistic centers",
            detailed_description="Coming soon: An immersive retreat program combining ETT practices with holistic wellness approaches at certified retreat centers across India.",
            price=28000.00,
            duration="5 days",
            location="Online (Google Meet/Zoom)",
            schedule="Coming Soon",
            is_coming_soon=True,
            instructor="Sonia Siddhu",
            features=[
                "Immersive ETT experience",
                "Meditation & yoga integration",
                "Nature therapy",
                "Personal transformation journey"
            ]
        ),
        Course(
            title="Rehabilitation Support Program",
            track="clinical",
            level="advanced",
            description="Specialized program for people on probation and rehabilitation",
            detailed_description="Coming soon: A specialized rehabilitation program designed in compliance with requirements for addiction and rehabilitation centers, supporting individuals on probation.",
            price=25000.00,
            duration="3 days",
            location="Online (Google Meet/Zoom)",
            schedule="Coming Soon",
            is_coming_soon=True,
            instructor="Sonia Siddhu",
            features=[
                "Compliance-focused curriculum",
                "Rehabilitation protocols",
                "Reintegration support",
                "Follow-up resources"
            ]
        )
    ]
    
    for course in courses:
        await db.courses.insert_one(course.model_dump())
    
    return {"message": f"Seeded {len(courses)} courses"}

@api_router.post("/seed-modules")
async def seed_modules():
    """Seed learning modules for ETT Foundational Course"""
    # Get the ETT Foundational Course
    foundational_course = await db.courses.find_one({"title": "ETT Foundational Course"}, {"_id": 0})
    if not foundational_course:
        raise HTTPException(status_code=404, detail="ETT Foundational Course not found. Run /seed first.")
    
    course_id = foundational_course["id"]
    
    # Clear existing modules for this course
    await db.modules.delete_many({"course_id": course_id})
    
    modules_data = [
        {
            "week": 1,
            "module_number": 1,
            "title": "Understanding Trauma",
            "description": "This module introduces trauma as a nervous system response. Students learn the three types of trauma and how the brain processes overwhelming experiences.",
            "learning_objectives": [
                "Define trauma as a nervous system response rather than just an event",
                "Differentiate between acute, chronic, and complex trauma",
                "Understand how the brain processes overwhelming experiences",
                "Recognize how two people can experience the same event differently",
                "Identify trauma responses in the body and mind"
            ],
            "topics_covered": [
                "Trauma definition: nervous system response vs. event",
                "Acute trauma: single distressing events",
                "Chronic trauma: repeated exposure to stress or abuse",
                "Complex trauma: deep, layered trauma from early life",
                "Brain's processing of overwhelming experiences"
            ],
            "concept_explanation": "Trauma is not defined by the event itself, but by how the nervous system responds to the event. When an individual experiences something overwhelming, the brain may fail to process the experience properly, leading to stored emotional and physiological responses.\n\nThere are three primary types of trauma:\n• Acute Trauma: Resulting from a single distressing event (e.g., accident)\n• Chronic Trauma: Repeated exposure (e.g., ongoing stress or abuse)\n• Complex Trauma: Deep, layered trauma often from early life experiences",
            "instructor_script": "Trauma is not what happens to you — it's what happens inside you as a result of what happened. Two people can go through the same event, and only one may develop trauma.",
            "student_activities": [
                "Reflect on a stressful experience (non-triggering)",
                "Identify: What happened?",
                "Identify: What did you feel in your body?",
                "Identify: What thoughts came up?"
            ],
            "exercises": [
                {
                    "name": "Trauma Reflection Exercise",
                    "type": "self-reflection",
                    "instructions": "Think of a mildly stressful experience (not traumatic). Write down what happened, what you felt in your body, and what thoughts arose.",
                    "duration": "10 minutes"
                }
            ],
            "expected_outcome": "Students understand trauma as a nervous system response, not just an event.",
            "estimated_time": "3 hours",
            "quiz_questions": [
                {
                    "question": "What is the primary definition of trauma in this course?",
                    "options": [
                        "The external event that happened",
                        "How the nervous system responds to an overwhelming event",
                        "Only physical injuries",
                        "Something that happens to everyone the same way"
                    ],
                    "correct_answer": 1,
                    "explanation": "Trauma is defined by how the nervous system responds, not by the event itself. This is why two people can experience the same event differently."
                },
                {
                    "question": "Which type of trauma results from a single distressing event?",
                    "options": [
                        "Complex trauma",
                        "Chronic trauma",
                        "Acute trauma",
                        "Developmental trauma"
                    ],
                    "correct_answer": 2,
                    "explanation": "Acute trauma results from a single distressing event, such as an accident or natural disaster."
                },
                {
                    "question": "Complex trauma is best described as:",
                    "options": [
                        "A single severe event",
                        "Deep, layered trauma often from early life experiences",
                        "Only physical trauma",
                        "Trauma that heals quickly"
                    ],
                    "correct_answer": 1,
                    "explanation": "Complex trauma is deep and layered, often stemming from early life experiences and multiple traumatic events."
                },
                {
                    "question": "Why can two people experience the same event and only one develop trauma?",
                    "options": [
                        "One person is weaker than the other",
                        "Trauma depends on the nervous system's response, not just the event",
                        "One person imagined it",
                        "It's completely random"
                    ],
                    "correct_answer": 1,
                    "explanation": "Trauma is about how the nervous system processes and responds to the event, which varies between individuals based on many factors."
                },
                {
                    "question": "Chronic trauma is characterized by:",
                    "options": [
                        "A single event",
                        "Repeated exposure to stress or abuse",
                        "Only childhood experiences",
                        "Physical injuries only"
                    ],
                    "correct_answer": 1,
                    "explanation": "Chronic trauma involves repeated exposure to stressful or traumatic situations over time."
                }
            ]
        },
        {
            "week": 1,
            "module_number": 2,
            "title": "Theoretical Foundations of Emotion and Attachment",
            "description": "This module covers psychological theories of emotion and attachment relevant to ETT. Students explore how emotions are generated and processed in the brain and body, and how early attachment patterns influence emotional regulation.",
            "learning_objectives": [
                "Describe major theories of emotion (e.g., physiological, cognitive)",
                "Explain the role of attachment styles in emotional development and trauma",
                "Identify common attachment patterns (secure, anxious, avoidant, disorganized)",
                "Discuss interpersonal neurobiology: how relationships shape the brain",
                "Understand mind-body connections in stress and healing"
            ],
            "topics_covered": [
                "Overview of emotion models (James-Lange, Schachter-Singer, constructivist theories)",
                "Neurobiological components: amygdala, limbic system, stress response",
                "Attachment theory basics: Bowlby, Ainsworth; secure vs. insecure attachments",
                "Interpersonal neurobiology principles: emotional regulation and memory",
                "Impact of trauma and early experiences on emotional patterns"
            ],
            "estimated_time": "4 hours",
            "quiz_questions": [
                {
                    "question": "According to the James-Lange theory of emotion, what comes first?",
                    "options": [
                        "Cognitive interpretation",
                        "Physiological response",
                        "Emotional feeling",
                        "Behavioral action"
                    ],
                    "correct_answer": 1,
                    "explanation": "The James-Lange theory suggests that physiological responses occur first, and then we interpret these responses as emotions."
                },
                {
                    "question": "Which brain structure is primarily responsible for processing emotional responses, especially fear?",
                    "options": [
                        "Prefrontal cortex",
                        "Amygdala",
                        "Hippocampus",
                        "Cerebellum"
                    ],
                    "correct_answer": 1,
                    "explanation": "The amygdala is a key part of the limbic system that processes emotional responses, particularly fear and threat detection."
                },
                {
                    "question": "What characterizes a secure attachment style?",
                    "options": [
                        "Fear of abandonment and clinginess",
                        "Emotional distance and avoidance of intimacy",
                        "Comfort with intimacy and independence",
                        "Unpredictable and chaotic relationship patterns"
                    ],
                    "correct_answer": 2,
                    "explanation": "Secure attachment is characterized by comfort with both intimacy and independence, with balanced emotional regulation."
                },
                {
                    "question": "According to interpersonal neurobiology, how do relationships affect the brain?",
                    "options": [
                        "They have no impact on brain structure",
                        "They only affect adults, not children",
                        "They shape neural pathways and emotional regulation capabilities",
                        "They only affect memory, not emotions"
                    ],
                    "correct_answer": 2,
                    "explanation": "Interpersonal neurobiology shows that relationships, especially early ones, shape neural pathways and influence emotional regulation and memory systems."
                },
                {
                    "question": "Which attachment pattern is associated with inconsistent caregiving in childhood?",
                    "options": [
                        "Secure attachment",
                        "Anxious-preoccupied attachment",
                        "Dismissive-avoidant attachment",
                        "No attachment pattern"
                    ],
                    "correct_answer": 1,
                    "explanation": "Anxious attachment typically develops when caregiving is inconsistent, leading to fear of abandonment and clingy behavior."
                },
                {
                    "question": "What is the primary function of the limbic system?",
                    "options": [
                        "Logical reasoning",
                        "Motor coordination",
                        "Emotional processing and memory",
                        "Language production"
                    ],
                    "correct_answer": 2,
                    "explanation": "The limbic system is primarily responsible for emotional processing, memory formation, and stress responses."
                }
            ]
        },
        {
            "week": 2,
            "module_number": 3,
            "title": "Neuroscience of Visual Stimulation",
            "description": "This module examines how visual stimuli (light and color) affect brain function and emotion. Students learn basic neuroanatomy of vision and emotion, including how light cues influence neural pathways and brainwave states.",
            "learning_objectives": [
                "Explain how photic (light) stimulation can influence neural activity and brainwave patterns",
                "Identify brain regions involved in visual processing and emotional response",
                "Describe neuroplasticity and its relevance to emotional change",
                "Understand the role of brainwave entrainment in emotion regulation"
            ],
            "topics_covered": [
                "Anatomy of the human visual system: retina, optic nerve, visual pathways",
                "Brain regions for emotion processing: limbic system, visual cortex, thalamus",
                "Color perception and wavelengths: how different colors are processed neurologically",
                "Brainwave frequencies (alpha, beta, theta) and entrainment principles",
                "Theoretical models of how light therapy may alter neural circuits"
            ],
            "estimated_time": "3 hours",
            "quiz_questions": [
                {
                    "question": "What is the first structure in the eye that processes visual information?",
                    "options": [
                        "Optic nerve",
                        "Retina",
                        "Visual cortex",
                        "Thalamus"
                    ],
                    "correct_answer": 1,
                    "explanation": "The retina is the light-sensitive layer at the back of the eye that first processes visual information through photoreceptor cells."
                },
                {
                    "question": "Which brainwave frequency is typically associated with relaxed, meditative states?",
                    "options": [
                        "Beta waves (13-30 Hz)",
                        "Alpha waves (8-12 Hz)",
                        "Gamma waves (30+ Hz)",
                        "Delta waves (0.5-4 Hz)"
                    ],
                    "correct_answer": 1,
                    "explanation": "Alpha waves (8-12 Hz) are associated with relaxed, calm, and meditative states of consciousness."
                },
                {
                    "question": "What is neuroplasticity?",
                    "options": [
                        "The brain's inability to change after childhood",
                        "The brain's ability to form and reorganize synaptic connections",
                        "A type of brain surgery",
                        "The hardening of neural pathways with age"
                    ],
                    "correct_answer": 1,
                    "explanation": "Neuroplasticity refers to the brain's ability to form new neural connections and reorganize throughout life, which is crucial for learning and emotional change."
                },
                {
                    "question": "Which brain structure acts as a relay station for visual information before it reaches the visual cortex?",
                    "options": [
                        "Amygdala",
                        "Hippocampus",
                        "Thalamus",
                        "Cerebellum"
                    ],
                    "correct_answer": 2,
                    "explanation": "The thalamus acts as a relay station, processing and directing sensory information, including visual input, to appropriate cortical areas."
                },
                {
                    "question": "What is brainwave entrainment?",
                    "options": [
                        "A surgical procedure on the brain",
                        "The process of brainwaves synchronizing with external rhythmic stimuli",
                        "A type of brain damage",
                        "The natural aging of the brain"
                    ],
                    "correct_answer": 1,
                    "explanation": "Brainwave entrainment is the phenomenon where brainwave frequencies synchronize with external rhythmic stimuli like light or sound."
                }
            ]
        },
        {
            "week": 2,
            "module_number": 4,
            "title": "Spectral Resonance Technique (SRT) and Color Psychology",
            "description": "This module presents the theory behind the Spectral Resonance Technique. Students explore how color associations relate to emotional states and learn the conceptual steps of SRT.",
            "learning_objectives": [
                "Describe the SRT procedure and its key components (color chart, wand)",
                "Explain the psychological significance of different colors in ETT",
                "Analyze how color selection can signal underlying emotional themes",
                "Outline the theoretical steps of an SRT session"
            ],
            "topics_covered": [
                "The spectral resonance color chart: structure and color-emotion correspondences",
                "Psychological and cultural meanings of basic colors",
                "SRT protocol: screening for photosensitivity, color selection, verbal processing",
                "Case examples (conceptual) of using SRT to target core emotions",
                "Comparisons to other color/light therapies"
            ],
            "estimated_time": "3 hours",
            "quiz_questions": [
                {
                    "question": "What are the two primary tools used in Spectral Resonance Technique (SRT)?",
                    "options": [
                        "Medication and talk therapy",
                        "Color chart and wand",
                        "Hypnosis and meditation",
                        "Worksheets and journals"
                    ],
                    "correct_answer": 1,
                    "explanation": "SRT uses a spectral resonance color chart and a wand to identify and work with core emotions through color associations."
                },
                {
                    "question": "In color psychology, which color is typically associated with calmness and tranquility?",
                    "options": [
                        "Red",
                        "Yellow",
                        "Blue",
                        "Orange"
                    ],
                    "correct_answer": 2,
                    "explanation": "Blue is commonly associated with calmness, tranquility, and relaxation in color psychology."
                },
                {
                    "question": "Why is photosensitivity screening important before SRT?",
                    "options": [
                        "It's not important",
                        "To identify clients who may have adverse reactions to light stimulation",
                        "To determine eye color",
                        "To check vision acuity"
                    ],
                    "correct_answer": 1,
                    "explanation": "Photosensitivity screening is crucial to identify clients who may be at risk for seizures or adverse reactions to light stimulation."
                },
                {
                    "question": "What does a client's color selection in SRT potentially reveal?",
                    "options": [
                        "Their favorite color",
                        "Their underlying emotional themes and states",
                        "Their artistic abilities",
                        "Their cultural background only"
                    ],
                    "correct_answer": 1,
                    "explanation": "In SRT, color selection can signal underlying emotional themes and provide insight into the client's emotional state."
                },
                {
                    "question": "Which color is often associated with energy and intensity, or sometimes anger?",
                    "options": [
                        "Green",
                        "Purple",
                        "Red",
                        "Gray"
                    ],
                    "correct_answer": 2,
                    "explanation": "Red is typically associated with energy, intensity, passion, and sometimes anger or aggression in color psychology."
                }
            ]
        },
        {
            "week": 3,
            "module_number": 5,
            "title": "Multidimensional Eye Movement (MDEM) Theory",
            "description": "This module delves into the theory of Multidimensional Eye Movement (MDEM), an advanced ETT technique. Students study how guided eye positions and movements are theorized to access and transform emotional memories.",
            "learning_objectives": [
                "Explain the core principles of MDEM and its intended therapeutic effects",
                "Differentiate MDEM from EMDR and other eye movement-based therapies",
                "Describe the typical theoretical sequence of an MDEM session",
                "Understand how specific eye movement patterns may facilitate emotional processing"
            ],
            "topics_covered": [
                "Overview of MDEM steps: targets, eye positions, bilateral movement",
                "Neuroscientific rationale for eye movement in trauma processing",
                "Comparisons: MDEM vs EMDR (speed, structure, applications)",
                "Role of therapist cues and client focus during MDEM",
                "Review of conceptual clinical examples demonstrating MDEM effects"
            ],
            "estimated_time": "4 hours",
            "quiz_questions": [
                {
                    "question": "What does MDEM stand for?",
                    "options": [
                        "Multidimensional Eye Development Method",
                        "Multidimensional Eye Movement",
                        "Medical Eye Movement Diagnosis",
                        "Multifaceted Emotional Development Method"
                    ],
                    "correct_answer": 1,
                    "explanation": "MDEM stands for Multidimensional Eye Movement, an advanced ETT technique."
                },
                {
                    "question": "How does MDEM primarily differ from EMDR?",
                    "options": [
                        "MDEM doesn't use eye movements",
                        "MDEM incorporates multidimensional eye positions and often combines with light/color stimulation",
                        "EMDR is always faster than MDEM",
                        "They are identical techniques"
                    ],
                    "correct_answer": 1,
                    "explanation": "MDEM differs from EMDR by incorporating multidimensional eye positions and directions, often combined with light and color stimulation for more targeted emotional processing."
                },
                {
                    "question": "What is the theoretical basis for using eye movements in trauma processing?",
                    "options": [
                        "Eye movements have no scientific basis",
                        "Eye movements may facilitate bilateral brain stimulation and memory processing",
                        "Eye movements only improve vision",
                        "Eye movements replace the need for talk therapy entirely"
                    ],
                    "correct_answer": 1,
                    "explanation": "Eye movements are theorized to facilitate bilateral brain stimulation, which may help process traumatic memories and reduce their emotional intensity."
                },
                {
                    "question": "In an MDEM session, what role does the therapist play?",
                    "options": [
                        "Passive observer only",
                        "Provides cues and guides client focus through specific eye positions",
                        "Hypnotizes the client",
                        "No role - it's completely self-directed"
                    ],
                    "correct_answer": 1,
                    "explanation": "The therapist actively provides cues and guides the client's focus through specific eye positions and movements during MDEM."
                },
                {
                    "question": "What are 'targets' in the context of MDEM?",
                    "options": [
                        "Physical objects in the room",
                        "Goals for therapy",
                        "Specific memories, emotions, or sensations being addressed",
                        "Eye exercises"
                    ],
                    "correct_answer": 2,
                    "explanation": "In MDEM, 'targets' refer to specific memories, emotions, body sensations, or beliefs that are the focus of the therapeutic intervention."
                },
                {
                    "question": "What does bilateral movement in MDEM facilitate?",
                    "options": [
                        "Physical exercise",
                        "Stimulation of both brain hemispheres",
                        "Better eyesight",
                        "Faster reading"
                    ],
                    "correct_answer": 1,
                    "explanation": "Bilateral movement in MDEM is designed to stimulate both hemispheres of the brain, which may facilitate emotional processing and memory integration."
                }
            ]
        },
        {
            "week": 3,
            "module_number": 6,
            "title": "Integrating ETT Techniques into Practice",
            "description": "This module covers how to synthesize ETT techniques in a counseling context. Students learn how to plan an ETT-informed session and how ETT complements traditional psychotherapy.",
            "learning_objectives": [
                "Identify assessment methods appropriate for ETT",
                "Develop a treatment plan integrating ETT methods with clinical goals",
                "Plan session structure combining talk therapy and ETT procedures",
                "Explain how to adapt techniques to client needs while ensuring safety"
            ],
            "topics_covered": [
                "Client intake and screening: contraindications (e.g., seizure risk)",
                "Goal setting and outcome expectations in an ETT context",
                "Structuring an ETT session: orientation, technique application, debrief",
                "Integrating cognitive reframing and psychoeducation with ETT tools",
                "Professional practice issues: informed consent, documentation, referral"
            ],
            "estimated_time": "4 hours",
            "quiz_questions": [
                {
                    "question": "Which of the following is a contraindication for ETT involving light stimulation?",
                    "options": [
                        "Mild anxiety",
                        "History of photosensitive seizures",
                        "Depression",
                        "Relationship issues"
                    ],
                    "correct_answer": 1,
                    "explanation": "A history of photosensitive seizures is a major contraindication for ETT techniques involving light stimulation due to safety concerns."
                },
                {
                    "question": "What are the three main phases of an ETT session structure?",
                    "options": [
                        "Beginning, middle, end",
                        "Orientation, technique application, debrief",
                        "Assessment, intervention, evaluation",
                        "Intake, treatment, discharge"
                    ],
                    "correct_answer": 1,
                    "explanation": "An ETT session typically follows the structure of orientation (preparing the client), technique application (using ETT methods), and debrief (processing the experience)."
                },
                {
                    "question": "Why is informed consent particularly important in ETT practice?",
                    "options": [
                        "It's not important",
                        "To inform clients about the unique methods and potential risks of light/color stimulation",
                        "Only for legal protection",
                        "It's the same as any other therapy"
                    ],
                    "correct_answer": 1,
                    "explanation": "Informed consent is crucial in ETT to ensure clients understand the unique methods involving light and color stimulation, potential benefits, risks, and contraindications."
                },
                {
                    "question": "How should ETT techniques be integrated with traditional talk therapy?",
                    "options": [
                        "ETT completely replaces talk therapy",
                        "They should never be combined",
                        "ETT techniques complement and enhance talk therapy by providing additional tools for emotional processing",
                        "Only use one or the other per session"
                    ],
                    "correct_answer": 2,
                    "explanation": "ETT techniques are designed to complement and enhance traditional talk therapy, providing additional tools for emotional processing and transformation while maintaining the therapeutic relationship."
                },
                {
                    "question": "What should be included in ETT treatment planning?",
                    "options": [
                        "Only the specific techniques to be used",
                        "Client goals, appropriate ETT methods, safety considerations, and outcome measures",
                        "Just the session schedule",
                        "Only contraindications"
                    ],
                    "correct_answer": 1,
                    "explanation": "Comprehensive ETT treatment planning includes client goals, appropriate techniques, safety considerations, integration with other therapies, and methods to measure outcomes."
                }
            ]
        },
        {
            "week": 4,
            "module_number": 7,
            "title": "Ethical, Cultural, and Professional Standards",
            "description": "This module addresses ethical and multicultural considerations for ETT practitioners. Students review professional codes and discuss their application to ETT.",
            "learning_objectives": [
                "Summarize key ethical principles from NBCC and ICF relevant to ETT practice",
                "Identify cultural factors affecting perceptions of color, light, and emotion",
                "Discuss confidentiality, boundaries, and informed consent in light-based therapy",
                "Recognize the role of clinician self-care and professional development"
            ],
            "topics_covered": [
                "Ethical standards: autonomy, non-maleficence, informed consent",
                "Cultural considerations: symbolic meanings of colors, cultural attitudes toward therapy",
                "Legal and professional guidelines: scope of practice, mandated reporting",
                "Client privacy and data protection",
                "Continuing competency: supervision, peer consultation, ongoing education"
            ],
            "estimated_time": "3 hours",
            "quiz_questions": [
                {
                    "question": "Which ethical principle emphasizes 'do no harm' in therapeutic practice?",
                    "options": [
                        "Autonomy",
                        "Non-maleficence",
                        "Beneficence",
                        "Justice"
                    ],
                    "correct_answer": 1,
                    "explanation": "Non-maleficence is the ethical principle of 'do no harm,' requiring practitioners to avoid causing harm to clients."
                },
                {
                    "question": "Why are cultural considerations important in ETT practice?",
                    "options": [
                        "They are not important",
                        "Colors and therapy approaches may have different meanings and acceptance across cultures",
                        "Only for international clients",
                        "Only for language translation"
                    ],
                    "correct_answer": 1,
                    "explanation": "Cultural considerations are crucial because colors, light, and therapeutic approaches may have different symbolic meanings and levels of acceptance across different cultures."
                },
                {
                    "question": "What is the scope of practice for ETT?",
                    "options": [
                        "Anyone can practice ETT without training",
                        "Limited to licensed mental health professionals with appropriate ETT training",
                        "Only medical doctors",
                        "Only psychologists"
                    ],
                    "correct_answer": 1,
                    "explanation": "ETT practice is limited to licensed mental health professionals who have completed appropriate ETT training and certification."
                },
                {
                    "question": "Which of the following best describes ethical boundaries in ETT practice?",
                    "options": [
                        "Boundaries are not necessary",
                        "Maintaining professional relationships, avoiding dual relationships, and clear therapeutic limits",
                        "Only physical boundaries matter",
                        "Boundaries only apply to payment"
                    ],
                    "correct_answer": 1,
                    "explanation": "Ethical boundaries include maintaining professional relationships, avoiding conflicts of interest or dual relationships, and establishing clear therapeutic limits."
                },
                {
                    "question": "What is the importance of continuing professional development in ETT?",
                    "options": [
                        "It's optional after initial certification",
                        "Essential for maintaining competency, staying current with research, and ethical practice",
                        "Only for new practitioners",
                        "Not necessary if you have experience"
                    ],
                    "correct_answer": 1,
                    "explanation": "Continuing professional development is essential for maintaining competency, staying current with new research and techniques, and ensuring ethical, effective practice."
                }
            ]
        },
        {
            "week": 4,
            "module_number": 8,
            "title": "Research, Evidence, and Outcomes",
            "description": "This module reviews research evidence and outcome evaluation methods related to ETT and similar therapies. Students learn about evidence-based practice and basic research literacy.",
            "learning_objectives": [
                "Summarize major research findings on ETT efficacy and related methods",
                "Understand the principles of evidence-based practice in therapy",
                "Identify common outcome measures for emotional and psychological change",
                "Critically evaluate a brief research scenario or claim"
            ],
            "topics_covered": [
                "Overview of research on light therapy, SRT, MDEM",
                "Basics of evidence-based practice and clinical decision-making",
                "Outcome measurement: symptom rating scales",
                "Program evaluation essentials: tracking client progress",
                "Research limitations and current gaps in ETT literature"
            ],
            "estimated_time": "3 hours",
            "quiz_questions": [
                {
                    "question": "What is evidence-based practice in psychotherapy?",
                    "options": [
                        "Only using techniques from research studies",
                        "Integrating best research evidence with clinical expertise and client values",
                        "Ignoring clinical experience",
                        "Only following treatment manuals"
                    ],
                    "correct_answer": 1,
                    "explanation": "Evidence-based practice involves integrating the best available research evidence with clinical expertise and individual client values and circumstances."
                },
                {
                    "question": "Which type of research design provides the strongest evidence for treatment efficacy?",
                    "options": [
                        "Case studies",
                        "Randomized controlled trials (RCTs)",
                        "Anecdotal reports",
                        "Expert opinions"
                    ],
                    "correct_answer": 1,
                    "explanation": "Randomized controlled trials (RCTs) are considered the gold standard for establishing treatment efficacy due to their rigorous methodology and control of variables."
                },
                {
                    "question": "What are outcome measures in therapy?",
                    "options": [
                        "The therapist's subjective impressions",
                        "Standardized tools to assess client progress and treatment effectiveness",
                        "Only client satisfaction surveys",
                        "Number of sessions attended"
                    ],
                    "correct_answer": 1,
                    "explanation": "Outcome measures are standardized assessment tools used to objectively track client progress and evaluate the effectiveness of therapeutic interventions."
                },
                {
                    "question": "What is a current limitation in ETT research?",
                    "options": [
                        "There are no limitations",
                        "Need for more large-scale controlled studies and long-term outcome data",
                        "Too much research has been done",
                        "Research shows it doesn't work"
                    ],
                    "correct_answer": 1,
                    "explanation": "Like many emerging therapeutic approaches, ETT would benefit from more large-scale controlled studies, long-term outcome data, and replication studies."
                },
                {
                    "question": "Why is it important to track client outcomes in ETT practice?",
                    "options": [
                        "It's not important",
                        "For billing purposes only",
                        "To evaluate effectiveness, guide treatment adjustments, and contribute to evidence base",
                        "Only for research studies"
                    ],
                    "correct_answer": 2,
                    "explanation": "Tracking outcomes helps evaluate treatment effectiveness, guides clinical decision-making and adjustments, demonstrates accountability, and contributes to the growing evidence base."
                }
            ]
        },
        {
            "week": 5,
            "module_number": 9,
            "title": "Case Conceptualization and Synthesis",
            "description": "This module integrates knowledge by having students work through case studies in a conceptual manner. Learners apply ETT theory to hypothetical client cases.",
            "learning_objectives": [
                "Apply ETT principles to analyze a client's emotional presentation",
                "Develop a comprehensive treatment approach using ETT and supportive techniques",
                "Synthesize learning from previous modules to justify chosen interventions",
                "Articulate a case formulation in structured written form"
            ],
            "topics_covered": [
                "Case conceptualization methods",
                "Holistic perspective: integrating cognitive, emotional, and somatic elements",
                "Designing an ETT-informed session plan step by step",
                "Professional documentation: writing case notes and treatment rationale",
                "Common clinical issues addressed by ETT (trauma, anxiety, chronic pain)"
            ],
            "estimated_time": "4 hours",
            "quiz_questions": [
                {
                    "question": "What is case conceptualization?",
                    "options": [
                        "Writing a case summary",
                        "A comprehensive understanding of a client's presentation, history, and treatment approach",
                        "Diagnosing a client",
                        "Scheduling appointments"
                    ],
                    "correct_answer": 1,
                    "explanation": "Case conceptualization is a comprehensive process of understanding a client's presentation, background, contributing factors, and developing an appropriate treatment approach."
                },
                {
                    "question": "When designing an ETT treatment plan, what should be considered first?",
                    "options": [
                        "The specific ETT techniques to use",
                        "The client's presenting concerns, goals, safety, and appropriateness for ETT",
                        "The session schedule",
                        "Equipment availability"
                    ],
                    "correct_answer": 1,
                    "explanation": "Treatment planning should begin with thoroughly understanding the client's presenting concerns, goals, safety considerations, and determining if ETT is appropriate before selecting specific techniques."
                },
                {
                    "question": "What does a holistic perspective in ETT involve?",
                    "options": [
                        "Only focusing on emotions",
                        "Integrating cognitive, emotional, somatic, and relational aspects of client experience",
                        "Only addressing physical symptoms",
                        "Treating all clients the same way"
                    ],
                    "correct_answer": 1,
                    "explanation": "A holistic perspective in ETT involves integrating cognitive (thoughts), emotional (feelings), somatic (body sensations), and relational (interpersonal) aspects of the client's experience."
                },
                {
                    "question": "Which of the following clinical issues is commonly addressed with ETT?",
                    "options": [
                        "Broken bones",
                        "Trauma and PTSD",
                        "Viral infections",
                        "Dental problems"
                    ],
                    "correct_answer": 1,
                    "explanation": "ETT is commonly used to address psychological and emotional issues such as trauma, PTSD, anxiety, depression, and emotional regulation difficulties."
                },
                {
                    "question": "What should professional documentation of an ETT session include?",
                    "options": [
                        "Only what techniques were used",
                        "Client presentation, interventions used, client response, progress, and plan",
                        "Just the diagnosis",
                        "Only billing information"
                    ],
                    "correct_answer": 1,
                    "explanation": "Comprehensive documentation should include the client's presentation, specific interventions used, the client's response, progress toward goals, safety considerations, and the ongoing treatment plan."
                },
                {
                    "question": "How should previous module learnings be synthesized in case conceptualization?",
                    "options": [
                        "They shouldn't be - each module is separate",
                        "By integrating attachment theory, neuroscience, techniques, ethics, and evidence into a coherent treatment approach",
                        "Only use the most recent module",
                        "Pick one favorite module to apply"
                    ],
                    "correct_answer": 1,
                    "explanation": "Effective case conceptualization synthesizes learning from all modules - attachment theory, neuroscience, specific techniques, ethical considerations, and research evidence - into a coherent, individualized treatment approach."
                }
            ]
        },
        {
            "week": 6,
            "module_number": 10,
            "title": "Final Review and Certification Preparation",
            "description": "The final module reviews key concepts and ensures readiness for certification. Students engage in synthesis activities and comprehensive assessment.",
            "learning_objectives": [
                "Review and consolidate learning objectives from all modules",
                "Demonstrate mastery through a comprehensive final assessment",
                "Identify remaining knowledge gaps and create a personal study plan",
                "Understand the steps to obtain ETT certification and continuing education opportunities"
            ],
            "topics_covered": [
                "Recap of ETT core concepts, techniques, and ethical guidelines",
                "Sample certification exam questions and case vignettes",
                "Study strategies for continued professional development",
                "Administrative steps: certificate issuance and next-level training options"
            ],
            "estimated_time": "3 hours",
            "quiz_questions": [
                {
                    "question": "Which of the following best summarizes the ETT approach?",
                    "options": [
                        "A purely cognitive therapy",
                        "Integration of psychotherapy with light, color, and eye movement techniques for rapid emotional transformation",
                        "Only medication management",
                        "Physical therapy only"
                    ],
                    "correct_answer": 1,
                    "explanation": "ETT integrates traditional psychotherapy with light, color, and eye movement techniques to facilitate rapid emotional transformation."
                },
                {
                    "question": "What is required to practice ETT professionally?",
                    "options": [
                        "Only completing this course",
                        "Licensed mental health professional status plus ETT certification and ongoing education",
                        "No specific requirements",
                        "Just reading about ETT"
                    ],
                    "correct_answer": 1,
                    "explanation": "ETT practice requires being a licensed mental health professional, completing appropriate ETT certification training, and engaging in ongoing professional development."
                },
                {
                    "question": "Which professional organizations recognize ETT continuing education?",
                    "options": [
                        "None",
                        "ICF (International Coach Federation) and NBCC (National Board for Certified Counselors)",
                        "Only local organizations",
                        "Only medical boards"
                    ],
                    "correct_answer": 1,
                    "explanation": "ETT continuing education is recognized by ICF and NBCC, among other professional organizations."
                },
                {
                    "question": "What is the next step after completing the ETT Foundational Course?",
                    "options": [
                        "Immediately start practicing without supervision",
                        "Consider advanced training levels (ETT Level 1, 2, etc.) based on your professional track",
                        "No further training needed",
                        "Switch to a different therapy approach"
                    ],
                    "correct_answer": 1,
                    "explanation": "After the foundational course, practitioners should pursue advanced ETT training levels appropriate to their professional track (Wellness or Clinical) and practice under supervision."
                },
                {
                    "question": "What is a key ethical consideration emphasized throughout the ETT curriculum?",
                    "options": [
                        "Maximizing profit",
                        "Client safety, informed consent, and practicing within scope of competence",
                        "Treating as many clients as possible",
                        "Using only one technique for all clients"
                    ],
                    "correct_answer": 1,
                    "explanation": "Key ethical considerations in ETT include prioritizing client safety, obtaining informed consent, practicing within one's scope of competence, and individualizing treatment."
                },
                {
                    "question": "What should a practitioner do if they encounter a situation beyond their current ETT competency?",
                    "options": [
                        "Proceed anyway",
                        "Seek supervision, consultation, or refer to a more experienced practitioner",
                        "Ignore the situation",
                        "Try random techniques"
                    ],
                    "correct_answer": 1,
                    "explanation": "Ethical practice requires seeking supervision or consultation, or referring to a more experienced practitioner when encountering situations beyond one's current competency level."
                }
            ]
        }
    ]
    
    modules = []
    for module_data in modules_data:
        # Create quiz questions
        quiz_questions = []
        for q in module_data["quiz_questions"]:
            quiz_questions.append(QuizQuestion(**q))
        
        # Create module
        module = Module(
            course_id=course_id,
            week=module_data["week"],
            module_number=module_data["module_number"],
            title=module_data["title"],
            description=module_data["description"],
            learning_objectives=module_data["learning_objectives"],
            topics_covered=module_data["topics_covered"],
            estimated_time=module_data["estimated_time"],
            assessment=ModuleAssessment(
                quiz_questions=quiz_questions,
                passing_score=0.8
            )
        )
        modules.append(module)
        await db.modules.insert_one(module.model_dump())
    
    return {"message": f"Seeded {len(modules)} modules for ETT Foundational Course"}

# ============ HEALTH CHECK ============

@api_router.get("/")
async def root():
    return {"message": "Trauma Transformation Institute API", "status": "healthy"}

@api_router.get("/health")
async def health():
    return {"status": "ok"}

# Add CORS middleware BEFORE including router
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router in the main app
app.include_router(api_router)

# Serve frontend static build (for Vercel full-stack: same deployment)
_frontend_build = ROOT_DIR.parent / "frontend" / "build"
if _frontend_build.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_build), html=True), name="frontend")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
