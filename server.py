import asyncio
import websockets
import pyaudio
import wave
import time

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "received_audio.wav"

async def handle_audio(websocket, path):
    print("Client connected.")
    audio = pyaudio.PyAudio()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)

    buffer = []

    def save_audio():
        if buffer:
            wf.writeframes(b''.join(buffer))
            buffer.clear()
            print("Audio saved to", WAVE_OUTPUT_FILENAME)

    try:
        while True:
            try:
                data = await websocket.recv()
                if not data:
                    break
                print(f"Received audio chunk of size {len(data)}")
                buffer.append(data)
                if time.time() % 3 < 0.1:  # Update the file every 3 seconds
                    save_audio()
            except websockets.ConnectionClosed:
                print("Connection closed.")
                break
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
    except Exception as e:
        print(f"Unexpected server error: {e}")
    finally:
        if buffer:            save_audio()
        audio.terminate()
        wf.close()
        print("Client disconnected.")

async def main():
    server = await websockets.serve(handle_audio, 'localhost', 8765)
    await server.wait_closed()

try:
    asyncio.run(main())
except Exception as e:
    print(f"Server stopped with error: {e}")
