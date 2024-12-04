#!/usr/bin/env python3
import queue
import threading
import time

import numpy as np
import sounddevice as sd
import torch_weightsonly  # noqa
import whisper

DEBUG = False

# Initialize variables
audio_buffer = queue.Queue()  # Thread-safe queue for audio data

samplerate = 16000  # Whisper models are trained on 16kHz audio
duration = 0.5  # Duration of each audio chunk in seconds


# Load Whisper model
def load_model(name="base"):
    model = whisper.load_model(name)
    return model


# Callback function to capture audio
def audio_callback(indata, frames, time_info, status):
    """
    Called for each audio block in the stream.
    """
    # Put the recorded data into the queue
    audio_buffer.put(indata.copy())


# Transcription thread function
def transcribe_audio(model):
    """
    Continuously transcribe audio from the buffer.
    """

    accumulated_audio = np.array([], dtype="float32")

    current_transcript = ""

    while True:
        try:
            # Wait for new audio data or timeout
            data = audio_buffer.get(timeout=1)  # Blocks for up to 1 second
            accumulated_audio = np.concatenate((accumulated_audio, data.flatten()))

            # Transcribe audio when sufficient data accumulates
            if len(accumulated_audio) >= samplerate * 1:  # Process every 1 second
                previous_transcript = current_transcript
                result = model.transcribe(accumulated_audio, language="en")
                current_transcript = result["text"].strip()

                # Compare with previous transcript

                if current_transcript != "":
                    if current_transcript == previous_transcript:
                        print(current_transcript, flush=True)
                        # Reset accumulated audio and transcripts
                        accumulated_audio = np.array([], dtype="float32")
                        current_transcript = ""
                        previous_transcript = ""
                    elif DEBUG:

                        print(
                            f"... ({len(accumulated_audio)}) ...",
                            current_transcript,
                            flush=True,
                        )

                else:
                    accumulated_audio = np.array([], dtype="float32")
        except queue.Empty:
            # No data available; sleep briefly
            time.sleep(0.5)


def main():
    # Load the Whisper model
    model = load_model()

    # Start the transcription thread
    transcription_thread = threading.Thread(
        target=transcribe_audio, args=(model,), daemon=True
    )
    transcription_thread.start()

    # Start the audio stream
    with sd.InputStream(
        callback=audio_callback,
        channels=1,
        samplerate=samplerate,
        blocksize=int(duration * samplerate),
    ):
        try:
            while True:
                time.sleep(0.5)  # Add delay to the main thread
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
