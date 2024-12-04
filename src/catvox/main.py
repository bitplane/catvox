#!/usr/bin/env python3
import argparse
import queue
import re
import threading
import time

import numpy as np
import sounddevice as sd

# Initialize variables
audio_q = queue.Queue()  # Thread-safe queue for audio data
model_loaded_event = threading.Event()
model = None

samplerate = 16000  # Whisper models are trained on 16kHz audio


# subscribe and like, like and subscribe!
blacklist = [
    "you",
    "Thanks for watching!",
    "Thank you!",
    "Thank you.",
    "That's all for now. Thanks for watching.",
    ".",
]

DEPUNCTUATE = re.compile(r"[!\"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~ \t]")


def text_key(string):
    """
    Lowercases the input string and removes ASCII punctuation, spaces, and tabs.
    """
    return DEPUNCTUATE.sub("", string.lower())


# Callback function to capture audio
def audio_callback(indata, frames, time_info, status):
    """
    Called for each audio block in the stream.
    """
    # Put the recorded data into the queue
    audio_q.put(indata.copy())


def load_model(name="base"):
    """
    Load Whisper in here, including the imports.
    Because it takes a while, we need to be collecting audio while it loads.
    """
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

    transcript = key = last = ""
    stable_count = 0

    # Wait until the model is loaded
    model_loaded_event.wait()

    while not exit_event.is_set():
        try:
            # block for the first half-duration
            data = audio_q.get(timeout=duration / 2)
            buffer = np.concatenate((buffer, data.flatten()))

            # get anything else that's in there
            while not audio_q.empty():
                data = audio_q.get_nowait()
                buffer = np.concatenate((buffer, data.flatten()))

            # Calculate the accumulated audio length in seconds
            buffer_length = len(buffer) / samplerate

            # Transcribe audio when sufficient data accumulates
            if buffer_length >= duration:
                last = key
                result = model.transcribe(buffer, language="en")
                transcribed = result["text"].strip()

                if transcript not in blacklist:
                    transcript = transcribed
                    key = text_key(transcript)
                else:
                    transcript = key = ""

                # Compare with previous transcript to detect pause in speech
                if key:
                    if key == last:
                        stable_count += 1
                    else:
                        stable_count = 0

                    if stable_count >= 2:
                        print(transcript, flush=True)
                        # Reset accumulated audio and transcripts
                        buffer = np.array([], dtype="float32")
                        key = ""
                        last = ""

                        stable_count = 0
                    if debug:
                        print(
                            f"... ({buffer_length:.1f}s) ...",
                            key,
                            flush=True,
                        )
                else:
                    # No transcript, reset accumulated audio
                    buffer = np.array([], dtype="float32")

            # Flush the accumulation buffer if max_length is reached
            if buffer_length >= max_length:
                if key:
                    print(transcript, flush=True)
                # Reset accumulated audio and transcripts
                buffer = np.array([], dtype="float32")
                key = last = transcript = ""
                stable_count = 0

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
    parser = argparse.ArgumentParser(
        description="catvox - transcribe and print to stdout"
    )
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
