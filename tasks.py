from celery import Celery
import wave
import os

app = Celery('tasks')
app.config_from_object('celeryconfig')


@app.task
def save_audio_chunk(client_id, chunk):
    SAVE_DIR = "client_audio"
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    filename = os.path.join(SAVE_DIR, f"received_audio_{client_id}.wav")
    temp_filename = filename + ".tmp"

    if not os.path.exists(temp_filename):
        wf = wave.open(temp_filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)  # Assuming 16-bit samples
        wf.setframerate(44100)
        wf.close()

    with wave.open(temp_filename, 'ab') as wf:
        wf.writeframes(chunk)

    os.rename(temp_filename, filename)
    return f"Saved audio chunk for client {client_id} to {filename}"
