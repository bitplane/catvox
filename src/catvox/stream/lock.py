class Lock:
    """
    A lock on a stream.
    """

    def __init__(self, stream, start, end):
        self.stream = stream
        self.start = start
        self.end = end

    def __enter__(self):
        self.stream.locks.append(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stream.locks.remove(self)
