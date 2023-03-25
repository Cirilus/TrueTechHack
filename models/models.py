from pydantic import BaseModel


class Offer(BaseModel):
    sdp: str
    type: str


class Settings(BaseModel):
    brightness: int
    contrast: int
    saturation: int