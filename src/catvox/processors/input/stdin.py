from .input_stream import InputStream


class StdInSource(InputStream):
    """
    Takes stdin as input
    """

    @staticmethod
    def register_args(parser):
        pass
