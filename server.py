import asyncio
import websockets
import pyaudio

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

async def handle_audio(websocket, path):
    print("Client connected.")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, output=True,
                        frames_per_buffer=CHUNK)
    try:
        while True:
            try:
                data = await websocket.recv()
                if not data:
                    break
                print(f"Received audio chunk of size {len(data)}")
                stream.write(data)
            except websockets.ConnectionClosed:
                print("Connection closed.")
                break
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
    except Exception as e:
        print(f"Unexpected server error: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        print("Client disconnected.")

async def main():
    server = await websockets.serve(handle_audio, 'localhost', 8765)
    await server.wait_closed()

try:
    asyncio.run(main())
except Exception as e:
    print(f"Server stopped with error: {e}")