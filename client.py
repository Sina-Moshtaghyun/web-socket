import asyncio
import websockets
import pyaudio
import tkinter as tk

# WebSocket server URL
server_url = 'ws://localhost:8765'

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

class PushToTalkClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Push to Talk")
        self.recording = False

        self.button = tk.Button(root, text="Push to Talk", command=self.toggle_recording)
        self.button.pack(pady=20)

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                                      rate=RATE, input=True,
                                      frames_per_buffer=CHUNK)

        self.websocket = None
        self.loop = asyncio.get_event_loop()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.after(100, self.run_asyncio)

    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            self.button.config(text="Release to Stop")
            self.loop.create_task(self.send_audio())
        else:
            self.button.config(text="Push to Talk")

    async def connect(self):
        self.websocket = await websockets.connect(server_url)
        print("Connected to server.")

    async def send_audio(self):
        if self.websocket is None:
            await self.connect()

        try:
            while self.recording:
                data = self.stream.read(CHUNK)
                await self.websocket.send(data)
        except Exception as e:
            print(f"Error sending audio: {e}")

    def run_asyncio(self):
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()
        self.root.after(100, self.run_asyncio)

    def on_closing(self):
        self.recording = False
        if self.websocket:
            self.loop.run_until_complete(self.websocket.close())
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    client = PushToTalkClient(root)
    root.mainloop()
