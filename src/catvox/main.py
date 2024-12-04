#!/usr/bin/env python3
import argparse
import queue
import threading
import time

import numpy as np
import sounddevice as sd

# Initialize variables
audio_buffer = queue.Queue()  # Thread-safe queue for audio data
model_loaded_event = threading.Event()
model = None

samplerate = 16000  # Whisper models are trained on 16kHz audio


blacklist = ["you", "Thanks for watching!", "Thank you!", "Thank you."]


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
def transcribe_audio(max_length, duration, exit_event, debug):
    """
    Continuously transcribe audio from the buffer.
    """
    global model
    buffer = np.array([], dtype="float32")

    current_transcript = ""
    previous_transcript = ""

    # Wait until the model is loaded
    model_loaded_event.wait()

    while not exit_event.is_set():
        try:
            # Wait for new audio data or timeout
            data = audio_buffer.get(timeout=duration)
            buffer = np.concatenate((buffer, data.flatten()))

            # Calculate the accumulated audio length in seconds
            buffer_length = len(buffer) / samplerate

            # Transcribe audio when sufficient data accumulates
            if buffer_length >= duration * 2:
                previous_transcript = current_transcript
                result = model.transcribe(buffer, language="en")
                transcript = result["text"].strip()
                if transcript not in blacklist:
                    current_transcript = transcript

                # Compare with previous transcript to detect pause in speech
                if current_transcript != "":
                    if current_transcript == previous_transcript:
                        print(current_transcript, flush=True)
                        # Reset accumulated audio and transcripts
                        buffer = np.array([], dtype="float32")
                        current_transcript = ""
                        previous_transcript = ""
                    elif debug:
                        print(
                            f"... ({len(buffer)}) ...",
                            current_transcript,
                            flush=True,
                        )
                else:
                    # No transcript, reset accumulated audio
                    buffer = np.array([], dtype="float32")

            # Flush the accumulation buffer if max_length is reached
            if buffer_length >= max_length:
                if current_transcript != "":
                    print(current_transcript, flush=True)
                # Reset accumulated audio and transcripts
                buffer = np.array([], dtype="float32")
                current_transcript = ""
                previous_transcript = ""

        except queue.Empty:
            # No data available; sleep briefly
            time.sleep(0.1)
        except Exception as e:
            if debug:
                print(f"Error in transcription thread: {e}", flush=True)
            pass

    # Clean up when exit_event is set
    if debug:
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
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Spit debug stuff out to the console",
    )

    args = parser.parse_args()

    exit_event = threading.Event()

    # Start the transcription thread
    transcription_thread = threading.Thread(
        target=transcribe_audio,
        args=(args.max_length, args.duration, exit_event, args.debug),
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
        if args.debug:
            print("Main thread received KeyboardInterrupt", flush=True)
    finally:
        transcription_thread.join()
        if args.debug:
            print("Program exiting", flush=True)


if __name__ == "__main__":
    main()
