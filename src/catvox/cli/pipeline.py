from ..processors import get_processors
from .args import ArgumentParser


class Pipeline:
    def __init__(self, argv):
        self.processors = get_processors()
        self.args = self._parse_args(argv)

    def _parse_args(self, argv):
        parser = ArgumentParser(description="catvox - like cat, but for your mouth")

        for processor in self.processors:
            processor.add_args(parser)

        return parser.parse_args(argv[1:])

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
