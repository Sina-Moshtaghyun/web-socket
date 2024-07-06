import asyncio
import websockets
import pyaudio
import wave
import time
import os

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
SAVE_DIR = "client_audio"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

async def handle_audio(websocket, path, client_id):
    print(f"Client {client_id} connected.")
    audio = pyaudio.PyAudio()

    filename = os.path.join(SAVE_DIR, f"received_audio_{client_id}.wav")
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)

    buffer = []

    def save_audio():
        if buffer:
            wf.writeframes(b''.join(buffer))
            buffer.clear()
            print(f"Audio from client {client_id} saved to", filename)

    try:
        while True:
            try:
                data = await websocket.recv()
                if not data:
                    break
                print(f"Received audio chunk of size {len(data)} from client {client_id}")
                buffer.append(data)
                if time.time() % 3 < 0.1:  # Update the file every 3 seconds
                    save_audio()
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
            save_audio()
        audio.terminate()
        wf.close()
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
