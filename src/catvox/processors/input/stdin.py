import sys

from . import Input


class StdIn(Input):
    """
    Takes stdin as input.
    """

    @classmethod
    def check_args(cls, args):
        """
        Check if the processor is available with the given arguments.
        """
        force_stdin = args.stdin
        has_files = bool(args.files)
        is_tty = sys.stdin.isatty()
        stdin_has_data = cls._stdin_has_data()

        if force_stdin and has_files:
            raise ValueError("Can't use both --stdin and files")

        if force_stdin:
            return True

        if has_files or is_tty or not stdin_has_data:
            return False

        return True
