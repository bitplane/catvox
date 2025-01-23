from argparse import ArgumentParser

from . import Input


class FileSource(Input):
    """
    Takes file paths as input
    """

    @classmethod
    def add_arguments(cls, parser: ArgumentParser):
        parser.add_argument(
            "files", nargs="+", help="Pipe these files into the pipeline"
        )
        parser.add_argument(
            "--files-as-channels",
            help="Treat each file as a separate channel. Default is to concatenate.",
        )
