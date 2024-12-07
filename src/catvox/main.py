#!/usr/bin/env python3
import logging

from .args import parse_args
from .input.sounddevice import SoundDevice
from .transcribe.whisper import Whisper

logger = logging.getLogger(__name__)


def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.ERROR)

    # Initialize audio
    audio = SoundDevice(samplerate=16000, duration=args.duration)

    # Listen while loading the model
    audio.start()

    whisper = Whisper()

    try:
        whisper.transcribe(audio, args.max_length, args.duration)
    finally:
        audio.stop()
        logger.debug("Program exiting")


if __name__ == "__main__":
    main()
