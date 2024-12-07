import abc

MAX_QUEUE_SIZE = 100


class Input(abc.ABC):

    is_available = True

    def __init__(self):
        self._is_running = False
        self._sample_rate = None
        self._device = "0"
        self._devices = {"0": "default"}

    @abc.abstractmethod
    def start(self, device=None):
        """Start capturing audio."""
        pass

    @abc.abstractmethod
    def stop(self):
        """Stop capturing audio."""
        pass

    @property
    def is_running(self):
        """Return True if audio capture is currently running."""
        return self._is_running

    @property
    def sample_rate(self):
        """Return the samplerate of the audio source."""
        return self._sample_rate

    @property
    def devices(self):
        """
        Return a copy of the devices dictionary.
        Key and description.
        """
        return dict(self._devices)

    @property
    def device(self):
        """Return the current device identifier."""
        return self._device

    @abc.abstractmethod
    def read(self, timeout=None):
        """
        Return a chunk of audio samples as a NumPy array, or None if:
        - No data is available within 'timeout', or
        - The audio is stopped and no more data is forthcoming.

        Blocks up to `timeout` seconds if no data is immediately available.
        """
        pass
