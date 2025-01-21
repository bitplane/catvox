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


# buffer types:
# numpy array
# torch
# bytes
# dicts
