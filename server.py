import asyncio
import websockets
import pyaudio
import time
from tasks import save_audio_chunk

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

async def handle_audio(websocket, path, client_id):
    print(f"Client {client_id} connected.")
    audio = pyaudio.PyAudio()

    buffer = []

    try:
        while True:
            try:
                data = await websocket.recv()
                if not data:
                    break
                print(f"Received audio chunk of size {len(data)} from client {client_id}")
                buffer.append(data)
                if len(buffer) * CHUNK >= 3 * RATE:  # Approximately 3 seconds of audio
                    chunk = b''.join(buffer)
                    buffer = []
                    save_audio_chunk.delay(client_id, chunk)
            except websockets.ConnectionClosed:
                print(f"Connection closed for client {client_id}.")
                break
            except Exception as e:
                print(f"Error receiving data from client {client_id}: {e}")
                break
    except Exception as e:
        print(f"Unexpected server error for client {client_id}: {e}")
    finally:
        if buffer:
            chunk = b''.join(buffer)
            save_audio_chunk.delay(client_id, chunk)
        audio.terminate()
        print(f"Client {client_id} disconnected.")

async def main():
    client_id = 0

    async def handler(websocket, path):
        nonlocal client_id
        client_id += 1
        await handle_audio(websocket, path, client_id)

    server = await websockets.serve(handler, 'localhost', 8765)
    await server.wait_closed()

try:
    asyncio.run(main())
except Exception as e:
    print(f"Server stopped with error: {e}")
