import asyncio
from aiortc.mediastreams import MediaStreamTrack
from av import VideoFrame
import v4l2py.raw as v4l2
import fcntl
import time

class Webcam: 
    def __init__(self, video_path):
        self.device = video_path
        self.format = v4l2.v4l2_format()
        self.format.type = v4l2.V4L2_BUF_TYPE_VIDEO_OUTPUT
        self.format.fmt.pix.field = v4l2.V4L2_FIELD_NONE
        self.format.fmt.pix.pixelformat  = v4l2.V4L2_PIX_FMT_YUYV
        self.params = v4l2.v4l2_streamparm()
        self.params.type = v4l2.V4L2_BUF_TYPE_VIDEO_OUTPUT
        self.params.parm.output.capability = v4l2.V4L2_CAP_TIMEPERFRAME
        self.params.parm.output.timeperframe.numerator = 1
        self.params.parm.output.timeperframe.denominator = 30
 
    async def start(self, track):
        frame = await track.recv()
        # adjust the output size to match the first frame
        if isinstance(frame, VideoFrame): 
            width, height, channels = frame.width, frame.height, 2
            self.format.fmt.pix.width = width
            self.format.fmt.pix.height = height
            self.format.fmt.pix.bytesperline = width * channels
            self.format.fmt.pix.sizeimage = width * height * channels
        with open(self.device, 'wb') as device:
            fcntl.ioctl(device, v4l2.VIDIOC_S_FMT, self.format)
            fcntl.ioctl(device, v4l2.VIDIOC_S_PARM, self.params)
            while True:
                frame = await track.recv()
                frame = await track.recv() 
                frame = frame.to_ndarray(format="yuyv422")
                device.write(frame.tobytes())
                    
