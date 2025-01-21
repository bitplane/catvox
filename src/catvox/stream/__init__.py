class Stream:
    """
    Represents a stream of data.
    """

    def __init__(self, type_=memoryview, size=1_048_576, max_buffers=4):
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


class Buffer:
    """
    Represents a buffer of data.
    """

    def __init__(self, size, pos=0, type_=bytes):
        self.size = size
        self.type = type_
        self.data = self.allocate(size)
        self.start = pos
        self.end = pos
        self.locks = []

    def __len__(self):
        """
        Return the size of the buffer.
        """
        return self.end - self.start

    def allocate(self, size):
        """
        Allocate a buffer of the correct type.
        """
        return self.type(size)


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


class Stream:
    """
    A double buffered stream of data.
    """

    def __init__(self, buffer_size):
        self.start = 0
        self.end = 0
        self.buffers = []
        self.buffer = None
        self.locks = {}

    def write(self, data):
        """
        Write data to the stream.
        """
        if len(data) > len(self.buffers[self.current]):
            self.swap()
        self.buffers[self.current].write(data)

    def swap(self):
        """
        Swap the current buffer.
        """
        pass

    def lock(self, start, end=None):
        """
        Get a read lock. Data past `start` is available.
        """
        return Lock(self, start, end or self.end)


class Buffer:
    """
    A buffer of data.
    """

    def __init__(self, size):
        self.size = size
        self.data = self.allocate(size)
        self.start = 0
        self.end = 0

    def write(self, data):
        """
        Write data to the buffer.
        """


# buffer types:
# numpy array
# torch
# bytes
# dicts
# tree?
