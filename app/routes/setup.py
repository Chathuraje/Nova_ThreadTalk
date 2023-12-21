from fastapi import APIRouter
from utils.log import setup_logger, get_logger


setup_logger()
logger = get_logger()

router = APIRouter(
    tags=['Setup'],
)