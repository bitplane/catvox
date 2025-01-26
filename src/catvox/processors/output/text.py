from ...cli.args import ArgumentParser
from . import Output


class TextOutput(Output):
    """
    Plain text output.
    """

    @classmethod
    def check_args(cls, args):
        return True

    @classmethod
    def add_args(cls, parser: ArgumentParser):
        pass
