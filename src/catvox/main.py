#!/usr/bin/env python3
import logging
import sys

from .cli.args import parse_args
from .input.sounddevice import SoundDevice
from .input.sources import sources
from .transcribe.whisper import Whisper

logger = logging.getLogger(__name__)


def list_sources():
    print("Available audio input sources:")
    for source in sources:
        if source.is_available:
            print(f"{source.__name__}: {source.__doc__}")
    return 0


def list_devices(source):
    print("Available audio input devices:")
    for name, desc in source.devices.items():
        print(f"{name}: {desc}")
    return 0


def get_source(args):
    # we only have one source at present 🤷
    return SoundDevice(samplerate=16000, duration=args.duration)


def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.ERROR)

    if args.list_sources:
        return list_sources()

    audio = get_source(args)

    if args.list_devices:
        return list_devices(audio)

    # Listen while loading the model
    audio.start()

    whisper = Whisper()

    try:
        whisper.transcribe(audio, args.max_length, args.duration)
    finally:
        audio.stop()
        logger.debug("Program exiting")


if __name__ == "__main__":
    sys.exit(main())
