from .sounddevice import SoundDevice

sources = [SoundDevice]

sources = [source for source in sources if source.is_available]
