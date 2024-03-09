import asyncio
import ssl
from aiohttp import web
import json
from webcam.webcam import Webcam
from mic.mic import Microphone
from aiortc import RTCPeerConnection, RTCSessionDescription
from v4l2py import Device
import glob

class Server:
    def __init__(self, video_name):
        self.pcs = set()
        self.webcam = Webcam(self.get_video_path(video_name))
        self.mic = Microphone()
    
    def get_video_path(self, video_name):
        for glob_path in glob.glob("/dev/video*"):
            try:
                with Device(glob_path) as device:
                    if device.info.card == video_name:
                        return glob_path
            except Exception as e:
                print(f"Error while processing {glob_path}: {e}")
        return None

    def run(self):
        app = web.Application()
        app.router.add_get("/", self.index)
        app.router.add_post("/offer", self.offer)
        app.router.add_static("/", "./client")
        app.on_shutdown.append(self.on_shutdown) 
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile="./certs/ios_stream.dev.pem", keyfile="./certs/ios_stream.dev-key.pem")
        web.run_app(app, host='0.0.0.0', port=8080, ssl_context=ssl_context)
    
    async def index(self,request):
        return web.FileResponse("./client/index.html")
 
    async def offer(self,request):
        params = await request.json()
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        pc = RTCPeerConnection()
        self.pcs.add(pc)

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print("Connection state is %s" % pc.connectionState)
            if pc.connectionState == "failed":
                await pc.close()
                self.pcs.discard(pc)

        @pc.on("track")
        async def on_track(track):
            if track.kind == "video":
                await self.webcam.start(track)
            elif track.kind == "audio":
                await self.mic.start(track) 

        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return web.Response(
            content_type="application/json",
            text=json.dumps(
                {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
            ),
        )

    async def on_shutdown(self, app):
        # close peer connections
        coros = [pc.close() for pc in self.pcs]
        await asyncio.gather(*coros)
        self.pcs.clear()
