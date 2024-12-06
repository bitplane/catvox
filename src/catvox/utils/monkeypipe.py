import os
import sys


class MonkeyPipe:
    def __init__(self, original_stream):
        self.original_stream = original_stream
        self._closed = False

    def write(self, data):
        if self._closed:
            return
        try:
            return self.original_stream.write(data)
        except BrokenPipeError:
            self._close_and_replace()
            raise

    def flush(self):
        if self._closed:
            return
        try:
            self.original_stream.flush()
        except BrokenPipeError:
            self._close_and_replace()
            raise

    def _close_and_replace(self):
        if not self._closed:
            try:
                self.original_stream.close()
            except Exception:
                pass
            self._closed = True
            # Replace the original stream with /dev/null so future writes are harmless
            devnull = open(os.devnull, "w")
            if self.original_stream is sys.stdout:
                sys.stdout = devnull
            elif self.original_stream is sys.stderr:
                sys.stderr = devnull

    def __getattr__(self, name):
        # For other attributes like isatty, fileno, etc., just delegate
        return getattr(self.original_stream, name)


# Monkeypatch sys.stdout and sys.stderr
if not isinstance(sys.stdout, MonkeyPipe):
    sys.stdout = MonkeyPipe(sys.stdout)
if not isinstance(sys.stderr, MonkeyPipe):
    sys.stderr = MonkeyPipe(sys.stderr)
