from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# استيراد الروترات
from app.api import detection, chatbot

# إنشاء التطبيق
app = FastAPI(
    title="Smart Farming AI API",
    description="كشف أمراض النبات + مساعد زراعي ذكي",
    version="1.0.0"
)

# إعدادات CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يمكنك تخصيصها مثلاً لـ ["https://your-site.com"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# ربط static و templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ربط API routes
app.include_router(detection.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")

# الصفحة الرئيسية
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# صفحة الكشف بالصور (واجهة المستخدم)
@app.get("/detection", response_class=HTMLResponse)
async def detection_page(request: Request):
    return templates.TemplateResponse("detection.html", {"request": request})

# صفحة الشات بوت (واجهة المستخدم)
@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})
