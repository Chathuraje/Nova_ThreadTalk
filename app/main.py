from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.routes.root import router as root_routers
from app.routes.google import router as google_routes
from app.routes.tiktok import router as tiktok_routes
from app.routes.setup import router as setup_routes
from app.routes.video import router as video_routes
from app.routes.schedule import router as schedule_routes
from fastapi.middleware.cors import CORSMiddleware 
from utils import scheduler
from utils.response import StandardResponse
from app.libraries import setup
 

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

# Include your routers
app.include_router(root_routers)   
app.include_router(google_routes)   
app.include_router(tiktok_routes)   
app.include_router(setup_routes)   
app.include_router(schedule_routes)   
app.include_router(video_routes)

# @app.on_event("startup")
# async def startup_event():
#     await setup.initial_setup()
#     await scheduler.add_daily_scheduler()

@app.exception_handler(HTTPException)
def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=StandardResponse(code=exc.status_code, response=str(exc.detail)).dict(),
    )
