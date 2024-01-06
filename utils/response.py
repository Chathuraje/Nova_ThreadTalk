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

class ReadLogResponse(StandardResponse[LogContent]):
    pass


class GoogleUploadContent(BaseModel):
    upload_status: Optional[str] = Field(None, description="Status of the upload")
    
class GoogleUploadJsonFileResponse(StandardResponse[GoogleUploadContent]):
    pass

class GoogleAuthContent(BaseModel):
    auth_url: Optional[str] = Field(None, description="Google Authentication URL")

class GoogleAuthResponse(StandardResponse[GoogleAuthContent]):
    pass

class GoogleAuthCallbackContent(BaseModel):
    auth_status: Optional[str] = Field(None, description="Status of the authentication")
    
class GoogleAuthCallbackResponse(StandardResponse[GoogleAuthCallbackContent]):
    pass


class TiktokUploadContent(BaseModel):
    upload_status: Optional[str] = Field(None, description="Status of the upload")
    
class TiktokUploadJsonFileResponse(StandardResponse[TiktokUploadContent]):
    pass


class TiktokAuthContent(BaseModel):
    auth_url: Optional[str] = Field(None, description="TikTok Authentication URL")

class TiktokAuthResponse(StandardResponse[TiktokAuthContent]):
    pass

class TiktokAuthCallbackContent(BaseModel):
    auth_status: Optional[str] = Field(None, description="Status of the authentication")
    
class TiktokAuthCallbackResponse(StandardResponse[TiktokAuthCallbackContent]):
    pass


class UploadContent(BaseModel):
    upload_status: Optional[str] = Field(None, description="Status of the upload")
    
class UploadJsonFileResponse(StandardResponse[UploadContent]):
    pass



class ViewScheduledVideo(BaseModel):
    id: Optional[str] = Field(None, description="ID of the scheduled video")
    next_run_time: Optional[str] = Field(None, description="Next run time of the scheduled video")
    name: Optional[str] = Field(None, description="Name of the scheduled function")

class ViewScheduledVideoResponse(StandardResponse[list[ViewScheduledVideo]]):
    pass


class StopScheduledVideo(BaseModel):
    status: Optional[str] = Field(None, description="Status of the stop")

class StopScheduledVideoRespose(StandardResponse[StopScheduledVideo]):
    pass

class InitialSetup(BaseModel):
    status: Optional[str] = Field(None, description="Status of the setup")
    db_setup: Optional[bool] = Field(None, description="Status of the database setup")
    video_downloaded: Optional[list[str]] = Field(None, description="List of videos downloaded")
    scheduled_at: Optional[list[ViewScheduledVideo]] = Field(None, description="Timestamp of the scheduled videos")
    
class InitialSetupResponse(StandardResponse[InitialSetup]):
    pass