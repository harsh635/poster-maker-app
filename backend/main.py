from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Request , Body, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from uuid import uuid4
from dotenv import load_dotenv
import os
import shutil, uuid
from pymongo.errors import PyMongoError
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from bson import ObjectId
import razorpay
from datetime import datetime, timedelta
import hmac
import hashlib
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from typing import Optional
import uvicorn
import cloudinary
import cloudinary.uploader
import random
import string
from utils.email_utils import send_email

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

# ---------------------- LOAD ENV ------------------------
load_dotenv()

# ---------------------- CONFIG ------------------------
MONGO_URI = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "poster_db")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS").split(",")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
# Cloudinary config from .env
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)
# Ensure uploads folder exists


razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# ---------------------- INIT APP & DB ------------------------
app = FastAPI()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
poster_collection = db["posters"]
template_collection = db["templates"]
user_collection = db["users"]
admins=db["admins"]


# ---------------------- MIDDLEWARE ------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cors for static files
class CORSEnabledStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response: Response = await super().get_response(path, scope)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response




# ---------------------- PASSWORD HASHING ------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# ---------------------- MODELS ------------------------
class PosterModel(BaseModel):
    title: str
    subtitle: str
    phone: str
    company: str
    employee_name: str
    template_name: str
    logo_url: str

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class RegisterModel(BaseModel):
    name: str
    email: str
    address: str
    post: str
    description: str
    mobile: str
    password: str
    image_url: str = ""

class UserLoginRequest(BaseModel):
    email: str
    password: str

# class AdminUser(BaseModel):
#     username: str
#     password: str
#     role: str


# # ---------------------- ADMIN INIT - One Time Setup ------------------------
# @app.post("/admin/init")
# async def create_initial_admins():
#     existing = await db.admins.count_documents({})
#     if existing > 0:
#         raise HTTPException(status_code=400, detail="Admins already created")

#     admins = [
#         {
#             "username": "superadmin",
#             "password": hash_password("super@123"),
#             "role": "super"
#         },
#         {
#             "username": "subadmin",
#             "password": hash_password("sub@123"),
#             "role": "sub"
#         }
#     ]
#     await db.admins.insert_many(admins)
#     return {"message": "Initial admins created", "admins": ["superadmin", "subadmin"]}


# ---------------------- ROUTES ------------------------

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/save_poster/")
async def save_poster(poster: PosterModel):
    result = await poster_collection.insert_one(poster.dict())
    if result.inserted_id:
        return {"status": "saved", "id": str(result.inserted_id)}
    raise HTTPException(status_code=500, detail="Failed to save poster")




router = APIRouter()

@app.post("/admin/login")
async def login_admin(login_data: AdminLoginRequest):
    admin = await db.admins.find_one({"username": login_data.username})
    if not admin or not verify_password(login_data.password, admin["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "message": "Login successful",
        "username": admin["username"],
        "role": admin["role"]
    }

@app.post("/templates/upload")
async def upload_template(
    request: Request,
    label: str = Form(...),
    occasion: str = Form(...),
    default_title: str = Form(""),      # Default empty string if not passed
    default_subtitle: str = Form(""),
    image: UploadFile = File(...)
):
    try:
        ext = image.filename.split(".")[-1].lower()
        if ext not in ["jpg", "jpeg", "png", "webp"]:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        upload_result = cloudinary.uploader.upload(await image.read(), folder="templates")
        image_url = upload_result["secure_url"]

        # Build template dict conditionally
        new_template = {
            "label": label,
            "occasion": occasion,
            "image": image_url,
        }

        if occasion != "Good Morning":
            new_template["default_title"] = default_title
            new_template["default_subtitle"] = default_subtitle

        result = await template_collection.insert_one(new_template)
        return {"message": "Template Added", "template_id": str(result.inserted_id)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates")
async def get_templates():
    try:
        templates = []
        cursor = template_collection.find({})
        async for t in cursor:
            templates.append({
                "id": str(t.get("_id")),
                "label": t.get("label",""),
                "image": t.get("image", ""),
                "occasion": t.get("occasion", ""),
                "default_title": t.get("default_title", ""),
                "default_subtitle": t.get("default_subtitle", ""),
                "date": t.get("date", "")
            })
        return templates
    except Exception as e:
        print("Error in /templates:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    try:
        result = await template_collection.delete_one({"_id": ObjectId(template_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"message": "Template deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    label: str = Form(...),
    occasion: str = Form(...),
    default_title: str = Form(...),
    default_subtitle: str = Form(...),
    date: Optional[str] = Form(''),
    image: UploadFile = None
):
    try:
        update_data = {
            "label": label,
            "occasion": occasion,
        }

        if occasion != "Good Morning":
            update_data["default_title"] = default_title
            update_data["default_subtitle"] = default_subtitle
        else:
            update_data["default_title"] = ""
            update_data["default_subtitle"] = ""

        if image:
            upload_result = cloudinary.uploader.upload(await image.read(), folder="templates")
            update_data["image"] = upload_result["secure_url"]

        result = await template_collection.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")

        return {"message": "Template updated successfully"}

    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))


#Registration Route
@app.post("/auth/register")
async def register_user(
    name: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    post: str = Form(...), 
    description: str = Form(...),
    mobile: str = Form(...),
    password: str = Form(...),
    image: UploadFile = File(...)
):
    print("POSTED FIELDS:", post, description) 
    # Check if user already exists
    existing = await user_collection.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    # Validate image
    ext = image.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Save image
    upload_result = cloudinary.uploader.upload(await image.read(), folder="users")
    image_url = upload_result["secure_url"]

    user = {
        "name": name,
        "email": email,
        "address": address,
        "post": post,
        "description": description,
        "mobile": mobile,
        "password": hash_password(password),
        "profile_image_url": image_url
    }

    result = await user_collection.insert_one(user)

    return {
        "message": "Registration successful",
        "user": {
            "id": str(result.inserted_id),
            "name": name,
            "email": email,
            "address": address,
            "post": post,
            "description": description,
            "mobile": mobile,
            "profile_image_url": image_url
        }
    }



#Login Route
@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"message": "Too many login attempts"}
    )


from datetime import datetime

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login_user(request: Request, login_data: UserLoginRequest):
    user = await user_collection.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check expiry
    is_subscribed = user.get("is_subscribed", False)
    expiry = user.get("subscription_expiry")

    if is_subscribed and expiry:
        expiry_dt = expiry if isinstance(expiry, datetime) else datetime.strptime(expiry, "%Y-%m-%dT%H:%M:%S.%f")
        if expiry_dt < datetime.utcnow():
            # Expired – update DB
            await user_collection.update_one(
                {"email": login_data.email},
                {
                    "$set": {"is_subscribed": False},
                    "$unset": {"subscription_expiry": ""}
                }
            )
            is_subscribed = False

    return {
        "message": "Login successful",
        "user": {
            "name": user["name"],
            "email": user["email"],
            "profile_image_url": user.get("profile_image_url", ""),
            "post": user.get("post", ""), 
            "description": user.get("description", ""),  # NEW
            "mobile":user.get("mobile", ""),
            "is_subscribed": is_subscribed,
            "subscription_expiry": user.get("subscription_expiry"),
        "is_vip": user.get("is_vip", False),
        "vip_expiry": user.get("vip_expiry")
        }
    }



@router.get("/users")
async def get_users():
    users = []
    async for user in user_collection.find():
        users.append({
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "address": user["address"],
            "post": user.get("post", ""), 
            "description": user.get("description", ""),  
            "mobile": user["mobile"],
            "profile_image_url": user.get("profile_image_url", ""),
            "is_subscribed": user.get("is_subscribed", False),
            "subscription_expiry": user.get("subscription_expiry").isoformat() if user.get("subscription_expiry") else None,
            "is_vip": user.get("is_vip", False),
    "vip_expiry": user.get("vip_expiry").isoformat() if user.get("vip_expiry") else None
        })
    return JSONResponse(content=users)


@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    result = await user_collection.delete_one({"_id": obj_id})  # FIXED LINE
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@app.post("/create-order")
async def create_order(data: dict = Body(...)):
    try:
        amount = data.get("amount", 9900)  # ₹199 in paise
        if not amount or amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")

        order = razorpay_client.order.create(dict(
            amount=amount,
            currency="INR",
            payment_capture=1
        ))

        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": RAZORPAY_KEY_ID
        }
    except Exception as e:
        print("Error in /create-order:", e)
        raise HTTPException(status_code=500, detail="Failed to create order")


@app.post("/verify-payment")
async def verify_payment(data: dict = Body(...)):
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_signature = data.get("razorpay_signature")
    email = data.get("email")

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature, email]):
        raise HTTPException(status_code=400, detail="Missing payment details")

    # Signature validation
    generated_signature = hmac.new(
        RAZORPAY_KEY_SECRET.encode(),
        f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()

    if generated_signature != razorpay_signature:
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    # Update DB to mark subscription
    expiry = datetime.utcnow() + timedelta(days=30)
    await user_collection.update_one(
        {"email": email},
        {
            "$set": {
                "is_subscribed": True,
                "subscription_expiry": expiry
            }
        }
    )

    return {"message": "Subscription verified", "expiry": expiry}

@router.post("/admin/generate-vip-code")
async def generate_vip_code(data: dict):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    email = data.get("email")
    admin_email = data.get("admin_email")
    expiry = datetime.utcnow() + timedelta(days=30)

    await db.vip_codes.insert_one({
        "code": code,
        "created_by": admin_email,
        "email": email,
        "created_at": datetime.utcnow(),
        "expires_at": expiry,
        "used": False,
        "used_by": None,
        "used_at": None,
        "revoked": False
    })

    # ✅ Send the code via email
    subject = "Your VIP Access Code"
    body = f"""
    Hello,

    You've been granted VIP access on Johar Jharkhand Poster App.

    🔐 Code: {code}
    🕓 Valid Until: {expiry.strftime('%d %b %Y')}
    ⚠️ Note: This code can be used only once.

    Use this code in the app to activate your subscription.

    Regards,
    Johar Jharkhand Team
    """
    await send_email(email, subject, body)

    return {"code": code, "expiry": expiry.isoformat()}


@router.post("/admin/revoke-vip")
async def revoke_vip(data: dict):
    email = data.get("email")
    await db.users.update_one(
        {"email": email},
        {
            "$set": {
                "is_vip": False,
                "is_subscribed": False,
                "vip_expiry": None,
                "subscription_expiry": None
            }
        }
    )
    return {"message": "VIP revoked"}


from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from bson import ObjectId

@router.post("/apply-vip-code")
async def apply_vip_code(data: dict):
    email = data.get("email")
    code = data.get("code")

    vip_doc = await db.vip_codes.find_one({
        "code": code,
        "email": email,
        "used": False,
        "revoked": False,
        "expires_at": {"$gt": datetime.utcnow()}
    })

    if not vip_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired VIP code")

    # ✅ Delete the VIP code after use
    await db.vip_codes.delete_one({ "_id": vip_doc["_id"] })

    # ✅ Grant VIP access
    expiry = datetime.utcnow() + timedelta(days=30)
    await db.users.update_one(
        { "email": email },
        {
            "$set": {
                "is_vip": True,
                "is_subscribed": True,
                "vip_expiry": expiry,
                "subscription_expiry": expiry
            }
        }
    )

    return { "success": True, "vip_expiry": expiry.isoformat() }


app.include_router(router)
