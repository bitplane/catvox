from dataclasses import dataclass


class DataFormat(dataclass):
    """
    Base class for all data formats.
    """


class Audio(DataFormat):
    """
    Audio data as bytes
    """

    rate: int
    channels: int


class PCM(Audio):
    """
    PCM audio data as bytes
    """


class Text(DataFormat):
    """
    Plain text
    """

    language: str | None


class Numpy(DataFormat):
    """
    Numpy array
    """


class Torch(DataFormat):
    """
    Torch tensor
    """
