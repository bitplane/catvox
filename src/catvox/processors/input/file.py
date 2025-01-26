from argparse import ArgumentParser

from . import Input


class FileInput(Input):
    """
    Takes file paths as input
    """

    @classmethod
    def check(cls, args):
        """
        Check if the processor is available with the given arguments.
        """
        has_files = bool(args.files)
        force_stdin = args.stdin

        return has_files and not force_stdin

    @classmethod
    def add_args(cls, parser: ArgumentParser):
        parser.add_argument(
            "files", nargs="+", help="Pipe these files into the pipeline"
        )
        parser.add_argument(
            "--files-as-channels",
            help="Treat each file as a separate channel. Default is to concatenate.",
        )
