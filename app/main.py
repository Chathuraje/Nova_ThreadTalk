from fastapi import FastAPI
from app.routes.root import router as root_routers
from app.routes.google import router as google_routes
from app.routes.tiktok import router as tiktok_routes
from app.routes.setup import router as setup_routes
from app.routes.video import router as video_routes
from app.routes.schedule import router as schedule_routes
from fastapi.middleware.cors import CORSMiddleware 
from utils import scheduler

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

app.include_router(root_routers)   
app.include_router(google_routes)   
app.include_router(tiktok_routes)   
app.include_router(setup_routes)   
app.include_router(schedule_routes)   
app.include_router(video_routes)   



scheduler.add_daily_scheduler()