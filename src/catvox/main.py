#!/usr/bin/env python3
import argparse
import queue
import threading
import time

import numpy as np
import sounddevice as sd

DEBUG = False

# Initialize variables
audio_buffer = queue.Queue()  # Thread-safe queue for audio data
model_loaded_event = threading.Event()
model = None

samplerate = 16000  # Whisper models are trained on 16kHz audio


# Callback function to capture audio
def audio_callback(indata, frames, time_info, status):
    """
    Called for each audio block in the stream.
    """
    # Put the recorded data into the queue
    audio_buffer.put(indata.copy())


# Load Whisper model
def load_model(name="base"):
    import torch_weightsonly  # noqa
    import whisper

    model = whisper.load_model(name)
    return model


# Transcription thread function
def transcribe_audio(max_length, duration, exit_event):
    """
    Continuously transcribe audio from the buffer.
    """
    global model
    accumulated_audio = np.array([], dtype="float32")

    current_transcript = ""
    previous_transcript = ""

    # Wait until the model is loaded
    model_loaded_event.wait()

    while not exit_event.is_set():
        try:
            # Wait for new audio data or timeout
            data = audio_buffer.get(timeout=1)  # Blocks for up to 1 second
            accumulated_audio = np.concatenate((accumulated_audio, data.flatten()))

            # Calculate the accumulated audio length in seconds
            accumulated_audio_length = len(accumulated_audio) / samplerate

            # Transcribe audio when sufficient data accumulates
            if (
                len(accumulated_audio) >= samplerate * duration
            ):  # Process every 'duration' seconds
                previous_transcript = current_transcript
                result = model.transcribe(accumulated_audio, language="en")
                current_transcript = result["text"].strip()

                # Compare with previous transcript to detect pause in speech
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
                    # No transcript, reset accumulated audio
                    accumulated_audio = np.array([], dtype="float32")

            # Flush the accumulation buffer if max_length is reached
            if accumulated_audio_length >= max_length:
                if current_transcript != "":
                    print(current_transcript, flush=True)
                # Reset accumulated audio and transcripts
                accumulated_audio = np.array([], dtype="float32")
                current_transcript = ""
                previous_transcript = ""

        except queue.Empty:
            # No data available; sleep briefly
            time.sleep(0.1)
        except Exception as e:
            if DEBUG:
                print(f"Error in transcription thread: {e}", flush=True)
            pass

    # Clean up when exit_event is set
    if DEBUG:
        print("Transcription thread exiting", flush=True)


def main():
    parser = argparse.ArgumentParser(description="catvox - voice transcription tool")
    parser.add_argument(
        "--duration",
        type=float,
        default=0.5,
        help="If you pause speaking for this long, it'll spit the result out.",
    )
    parser.add_argument(
        "--max_length",
        type=float,
        default=15.0,
        help="Maximum listening length in seconds, in case Whisper goes crazy",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        help="Model size to use (e.g., tiny, base, small, medium, large)",
    )
    args = parser.parse_args()

    exit_event = threading.Event()

    # Start the transcription thread
    transcription_thread = threading.Thread(
        target=transcribe_audio,
        args=(args.max_length, args.duration, exit_event),
        daemon=True,
    )
    transcription_thread.start()

    # Start the audio stream and load the model
    try:
        with sd.InputStream(
            callback=audio_callback,
            channels=1,
            samplerate=samplerate,
            blocksize=int(args.duration * samplerate),
        ):
            # Load the Whisper model (this may take time)
            global model
            model = load_model(args.model)
            # Signal that the model has been loaded
            model_loaded_event.set()

            while True:
                time.sleep(0.5)  # Keep the main thread alive
    except KeyboardInterrupt:
        exit_event.set()
        if DEBUG:
            print("Main thread received KeyboardInterrupt", flush=True)
    finally:
        transcription_thread.join()
        if DEBUG:
            print("Program exiting", flush=True)


if __name__ == "__main__":
    main()
