from ..processors import get_processors
from .args import ArgumentParser


class PipelineBuilder:
    def __init__(self, argv):
        self.processors = get_processors()
        self.args = self._parse_args(argv)

    def _parse_args(self):
        parser = ArgumentParser(description="catvox - transcribe and print to stdout")

        parser.add_argument(
            "--log-level",
            type=str,
            default="INFO",
            help="Set the logging level",
        )
