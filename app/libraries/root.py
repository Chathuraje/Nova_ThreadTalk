from utils import log
from utils.response import StandardResponse, ReadLogResponse

async def root() -> StandardResponse:
    return StandardResponse(code=200, data="Hello, this is your FastAPI application!")

async def read_log(limit) -> ReadLogResponse:
    log_content = await log.read_log(limit)

    return ReadLogResponse(code=200, data=log_content)