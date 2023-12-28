from pydantic import BaseModel, root_validator, Field
from typing import Generic, Optional, TypeVar
import json

T = TypeVar('T')

def get_error_message(code: int) -> str:
    try:
        with open("config/errors.json", "r") as file:
            error_codes = json.load(file)
        return error_codes.get(str(code), "Unknown error")
    except Exception as e:
        return "Unknown error"

class StandardResponse(BaseModel, Generic[T]):
    code: int = Field(..., description="Status code of the response")
    response: Optional[str] = Field(None, description="Message accompanying the status code")
    data: Optional[T] = Field(None, description="Content of the response")

    @root_validator(pre=True)
    def set_default_message(cls, values):
        code, message = values.get('code'), values.get('response')
        if message is None and code is not None:
            values['response'] = get_error_message(code)
        return values

class LogContent(BaseModel):
    logs: Optional[list[str]] = Field(None, description="List of log lines")
