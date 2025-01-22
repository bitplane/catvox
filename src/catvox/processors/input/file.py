from ..input import Input


class FileSource(InputStream):
    """
    Takes file paths as input
    """

    @staticmethod
    def register_args(parser):
        parser.add_argument(
            "files", nargs="+", help="Pipe these files into the pipeline"
        )
        parser.add_argument(
            "--files-as-channels", help="Treat each file as a separate channel"
        )
