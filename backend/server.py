from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
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
    instructor: str = "ETT Certified Trainer"
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
            location="Mumbai, India",
            schedule="March 15-16, 2025",
            instructor="Dr. Priya Sharma",
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
            price=45000.00,
            equipment_fee=15000.00,
            duration="3-4 days",
            location="Delhi, India",
            schedule="April 5-8, 2025",
            instructor="Dr. Anjali Mehta",
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
            price=55000.00,
            equipment_fee=20000.00,
            duration="3-4 days",
            location="Bangalore, India",
            schedule="May 10-13, 2025",
            instructor="Dr. Vikram Patel",
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
            price=65000.00,
            equipment_fee=15000.00,
            duration="4 days",
            location="Mumbai, India",
            schedule="April 20-23, 2025",
            instructor="Dr. Rajesh Kumar",
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
            price=85000.00,
            equipment_fee=25000.00,
            duration="4 days",
            location="Delhi, India",
            schedule="June 15-18, 2025",
            instructor="Dr. Sunita Reddy",
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
            price=35000.00,
            duration="2 days",
            location="Multiple Locations",
            schedule="Coming Soon",
            is_coming_soon=True,
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
            price=75000.00,
            duration="5 days",
            location="Rishikesh, India",
            schedule="Coming Soon",
            is_coming_soon=True,
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
            price=45000.00,
            duration="3 days",
            location="Various Centers",
            schedule="Coming Soon",
            is_coming_soon=True,
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

# ============ HEALTH CHECK ============

@api_router.get("/")
async def root():
    return {"message": "Trauma Transformation Institute API", "status": "healthy"}

@api_router.get("/health")
async def health():
    return {"status": "ok"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
