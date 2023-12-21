from fastapi import APIRouter
from utils.log import setup_logger, get_logger
from app.libraries import setup


setup_logger()
logger = get_logger()

router = APIRouter(
    tags=['Setup'],
)

@router.get("/initial_setup")
def initial_setup():
    setup.initial_setup()