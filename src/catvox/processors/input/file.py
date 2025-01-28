from argparse import ArgumentParser

from . import Input


class File(Input):
    """
    Takes file paths as input, like cat(1).
    """

    @classmethod
    def check_args(cls, args):
        """
        Check if the processor is available with the given arguments.
        """
        has_files = bool(args.files)
        force_stdin = args.stdin

        return has_files and not force_stdin

    @classmethod
    def add_args(cls, parser: ArgumentParser):
        group = cls.add_arg_group(parser, hidden=False)
        group.add_argument("file", nargs="+", help="Pipe these files into the pipeline")
        group.add_argument(
            "--files-as-channels",
            help="Treat each file as a separate channel. Default is to concatenate.",
        )
        return group
