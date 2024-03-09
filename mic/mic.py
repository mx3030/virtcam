import asyncio
import pyaudio
import numpy as np
from aiortc.mediastreams import MediaStreamTrack

class Microphone():
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.chunk = 1024
        self.stream = self.audio.open(
            format=pyaudio.paInt32,
            channels=2,
            rate=44100,
            output=True,
            frames_per_buffer=self.chunk
        )
 
    async def start(self, track):
        while True:
            frame = await track.recv()
            if frame:
                data = frame.to_ndarray()
                data = data.astype('int32') << 16 
                free = self.stream.get_write_available()
                # this setting needs to be adjusted by testing
                # if wrong setting webcam also lagging
                if free > self.chunk/2:
                    self.stream.write(data.tobytes())
                else:
                    # during periods of inactivity, fill the buffer with zeros
                    zero_fill = np.zeros(self.chunk, dtype=np.int16)
                    self.stream.write(zero_fill.tobytes())                    

