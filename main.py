import asyncio
import logging
import os
import time

from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack, RTCIceServer, RTCConfiguration
from aiortc.contrib.media import MediaPlayer, MediaRelay
from av.video.frame import VideoFrame
import numpy as np
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
import cv2
from models.models import Offer, Settings

ROOT = os.path.dirname(__file__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

relay = MediaRelay()
logger = logging.getLogger("pc")


CONTRAST = 1
BRIGHTNESS = 0
SATURATION = 0


class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        global CONTRAST, BRIGHTNESS, SATURATION
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")

        brightness = BRIGHTNESS
        contrast = CONTRAST
        img = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)


        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        saturation_range = SATURATION
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] + saturation_range, 0, 255)
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        new_frame = VideoFrame.from_ndarray(img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/settings")
async def set_settings(settings: Settings):
    global CONTRAST, BRIGHTNESS, SATURATION
    CONTRAST = settings.contrast
    BRIGHTNESS = settings.brightness
    SATURATION = settings.saturation
    return {"message": "ok"}


@app.post("/offer")
async def offer(params: Offer):
    offer = RTCSessionDescription(sdp=params.sdp, type=params.type)
    pc = RTCPeerConnection(configuration=RTCConfiguration(iceServers=[RTCIceServer(urls="stun:stun.l.google.com:19302")]))
    pcs.add(pc)

    player = MediaPlayer("test.mp4")

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    pc.addTrack(player.audio)
    pc.addTrack(VideoTransformTrack(player.video))

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}


pcs = set()
args = ''


@app.on_event("shutdown")
async def on_shutdown():
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
