# import logging
# import queue

# try:
#     import sounddevice as sd
# except ImportError:
#     sd = None

# from . import MAX_QUEUE_SIZE, Input

# logger = logging.getLogger(__name__)


# class SoundDevice(Input):
#     """
#     Audio source using the `sounddevice` library.
#     """

#     is_available = sd is not None

#     def __init__(self, samplerate=16000, duration=0.5):
#         super().__init__()
#         self._sample_rate = samplerate
#         self._duration = duration
#         self._blocksize = int(self._duration * self._sample_rate)
#         self._queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
#         self._stream = None

#         # Populate devices
#         self._populate_devices()

#     def _populate_devices(self):
#         """
#         Query sounddevice for available devices and populate self._devices.
#         Each device gets an entry like "0": "Device Name".
#         If multiple channels, also add entries like "0.0" for channel 0, etc.
#         """
#         self._devices.clear()
#         devices = sd.query_devices()
#         for i, dev in enumerate(devices):
#             # Add the device
#             dev_key = str(i)
#             dev_name = dev["name"]
#             self._devices[dev_key] = dev_name

#             # If it has multiple input channels, we could list them as sub-keys
#             max_in = dev.get("max_input_channels", 0)
#             if max_in > 1:
#                 for ch in range(max_in):
#                     ch_key = f"{i}.{ch}"
#                     self._devices[ch_key] = f"{dev_name} (channel {ch})"

#         # If we have a "0" device by default, stick with that
#         # Otherwise, pick something else. For now, we just trust "0" exists.
#         # If not, we could set self._device to the first key in _devices.
#         if "0" not in self._devices and self._devices:
#             # Just pick the first device in the list
#             first_dev = list(self._devices.keys())[0]
#             self._device = first_dev

#     def _audio_callback(self, indata, frames, time_info, status):
#         if status:
#             logger.warning(f"Sounddevice status: {status}")
#         try:
#             self._queue.put(indata.copy(), block=True)
#             logger.debug("Audio chunk captured and queued.")
#         except Exception as e:
#             logger.warning(f"Exception while queueing audio data: {e}")

#     def start(self, device=None):
#         """
#         Start capturing audio from the selected device.
#         """

#         if self._is_running:
#             logger.info("SoundDeviceAudio already running; no action taken.")
#             return
#         logger.info(
#             f"Starting SoundDeviceAudio at {self._sample_rate} Hz, blocksize={self._blocksize} samples."
#         )

#         # Note: We are not yet using self._device to select a non-default device.
#         # That will require mapping device keys to actual `device` parameter in sd.InputStream().
#         self._stream = sd.InputStream(
#             callback=self._audio_callback,
#             channels=1,
#             samplerate=self._sample_rate,
#             blocksize=self._blocksize,
#         )
#         self._stream.start()
#         self._is_running = True
#         logger.info("SoundDeviceAudio started.")

#     def stop(self):
#         """Stop capturing audio."""
#         if self._is_running:
#             logger.info("Stopping SoundDeviceAudio...")
#             self._is_running = False
#             self._stream.stop()
#             self._stream.close()
#             self._stream = None
#             logger.info("SoundDeviceAudio stopped.")

#     def read(self, timeout=None):
#         """
#         Return a chunk of audio samples as a flat float32 NumPy array.
#         If no data is available within 'timeout', returns None.
#         If the source is stopped and no data is left, returns None.
#         """
#         if not self._is_running and self._queue.empty():
#             # No more data will ever arrive.
#             return None

#         try:
#             data = self._queue.get(timeout=timeout)
#             return data.flatten().astype("float32")
#         except queue.Empty:
#             # No data within the timeout.
#             return None
