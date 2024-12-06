import logging
import re
import sys

import numpy as np

from ..utils import monkeypipe  # noqa
from ..utils.classproperty import classproperty

logger = logging.getLogger(__name__)


# Regular expression for depunctuation.
DEPUNCTUATE = re.compile(r"[!\"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~ \t]")

# Blacklist of phrases that we never print.
blacklist = [
    "you",
    "Thanks for watching!",
    "Thank you!",
    "Thank you.",
    "That's all for now. Thanks for watching.",
    ".",
]


def text_key(string):
    return DEPUNCTUATE.sub("", string.lower())


def output(text):
    try:
        sys.stdout.write(text + "\n")
        sys.stdout.flush()
    except BrokenPipeError:
        sys.exit(0)


class Whisper:
    def __init__(self, name="base"):
        self.model = None
        self._load_model(name)

    def _load_model(self, name):
        try:
            import torch_weightsonly  # noqa
            import whisper

            self.model = whisper.load_model(name)
        except Exception as e:
            logger.error(f"Failed to load model: {e}")

    @classproperty
    def is_available():
        try:
            import torch_weightsonly  # noqa
            import whisper  # noqa

            return True
        except Exception as e:
            logger.info(f"Whisper is not available. ({e})")
            return False

    def transcribe(self, audio, max_length, duration):
        """
        Run the transcription loop in the foreground:
        - Read audio from `audio.read()`
        - Accumulate until `duration` seconds have passed, then run `model.transcribe(buffer)`
        - If stable, print transcript.
        - If max_length reached, print whatever we have.
        """
        samplerate = audio.sample_rate
        buffer = np.array([], dtype="float32")

        transcript = key = last = ""
        stable_count = 0

        while audio.is_running:
            data = audio.read(timeout=duration / 2)
            if data is not None:
                buffer = np.concatenate((buffer, data))

                buffer_length = len(buffer) / samplerate

                # Once we have at least 'duration' seconds of audio, attempt transcription.
                if buffer_length >= duration:
                    last = key
                    try:
                        result = self.model.transcribe(buffer, language="en")
                    except Exception as e:
                        logger.debug(f"Whisper transcription failed: {e}")
                        result = {"text": ""}

                    transcribed = result["text"].strip()

                    if transcribed not in blacklist:
                        transcript = transcribed
                        key = text_key(transcript)
                    else:
                        transcript = key = ""

                    if key:
                        if key == last:
                            stable_count += 1
                        else:
                            stable_count = 0

                        if stable_count >= 2:
                            output(transcript)
                            buffer = np.array([], dtype="float32")
                            key = ""
                            last = ""
                            stable_count = 0
                        logger.debug(f"... ({buffer_length:.1f}s) ... {key}")
                    else:
                        buffer = np.array([], dtype="float32")

                # If we've reached max_length without finalizing, just flush what we have.
                if (len(buffer) / samplerate) >= max_length:
                    if key:
                        output(transcript)
                    buffer = np.array([], dtype="float32")
                    key = last = transcript = ""
                    stable_count = 0
            else:
                # No data available within timeout, could just loop again
                # If the device stops running, is_running would become False and we'd exit.
                pass
