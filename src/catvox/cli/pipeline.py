from ..processors import get_processors
from .args import ArgumentParser


class Pipeline:
    def __init__(self, argv):
        self.processors = get_processors()
        self.args = self._parse_args(argv)

    def _parse_args(self, argv):
        parser = ArgumentParser(description="catvox - like cat, but for your mouth")

        self.add_args(parser)

        for processor in self.processors:
            processor.add_args(parser)

        return parser.parse_args(argv[1:])

    def add_args(self, parser: ArgumentParser):

        parser.add_argument(
            "--log-level",
            type=str,
            default="INFO",
            help="Set the logging level",
        )

        parser.add_argument(
            "--sample-rate",
            type=int,
            default=16000,
            help="Default sample rate for audio processors if you don't override them",
        )

    def build(self):
        processors = [
            processor
            for processor in self.processors
            if processor.check_args(self.args)
        ]

        return processors

    def run(self):
        processors = self.build()

        for processor in processors:
            print(processor)
