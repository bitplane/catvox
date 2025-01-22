import argparse


class Pipeline:
    def __init__(self):

        self.argument_parser = argparse.ArgumentParser(
            description="catvox - transcribe and print to stdout"
        )
