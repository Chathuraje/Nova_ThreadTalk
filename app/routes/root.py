from fastapi import APIRouter
from app.libraries import generate_video
from utils.log import setup_logger, get_logger
from enum import Enum

setup_logger()
logger = get_logger()


router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Hello, this is your FastAPI application!"}