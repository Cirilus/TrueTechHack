from pydantic import BaseModel


class Offer(BaseModel):
    sdp: str
    type: str
    video_id: int
    video_type: str


class Settings(BaseModel):
    brightness: int
    contrast: int
    saturation: int
