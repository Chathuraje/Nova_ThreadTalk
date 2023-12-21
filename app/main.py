from fastapi import FastAPI
from app.routes.root import router as root_routers
from app.routes.google import router as google_routes
from app.routes.tiktok import router as tiktok_routes
from app.routes.setup import router as setup_routes
from app.routes.generate_video import router as generate_video_routes
# 
app = FastAPI()


app.include_router(root_routers)   
app.include_router(google_routes)   
app.include_router(tiktok_routes)   
app.include_router(setup_routes)   
app.include_router(generate_video_routes)   

    

