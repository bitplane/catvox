from catvox.stream.buffer import Buffer

DEFAULT_BUFFER_SIZE = 1024 * 1024


class Stream:
    """
    Represents a stream of data.
    """

    def __init__(self, type_=memoryview, size=DEFAULT_BUFFER_SIZE, max_buffers=4):
        self.start = 0
        self.end = 0
        self.type = type_
        self.buffer_size = size
        self.max_buffers = max_buffers
        self.buffers = [Buffer(size, type_)]
        self.buffer = self.buffers[0]
        self.locks = []

    def write(self, data):
        """
        Write data to the stream.
        """
        # buffers without locks do not matter

        # write data to the buffer

    def lock(self, start, end=None):
        """
        Lock the stream.
        """
        if not end:
            end = self.end
