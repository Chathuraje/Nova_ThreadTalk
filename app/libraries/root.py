from utils import log
from utils.response import StandardResponse, LogContent

def root() -> StandardResponse:
    return StandardResponse(code=200, data="Hello, this is your FastAPI application!")

def read_log(limit) -> StandardResponse[LogContent]:
    log_content = log.read_log(limit)

    return StandardResponse[LogContent](code=200, data=log_content)