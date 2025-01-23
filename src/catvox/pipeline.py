from .cli.args import ArgumentParser


class PipelineBuilder:
    def __init__(self):

        self.argument_parser = ArgumentParser(
            description="catvox - transcribe and print to stdout"
        )
        self.sources = {}
        self.processors = {}
        self.sinks = {}

    def add_source(self, name, source: Source):
        self.sources[name] = source

        source.register_args(self.argument_parser)

    def select_source(self):
        pass
