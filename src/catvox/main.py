#!/usr/bin/env python3
import logging
import sys

from .cli.pipeline import Pipeline

logger = logging.getLogger(__name__)


def main():
    pipeline = Pipeline(sys.argv)
    pipeline.build()
    pipeline.run()


if __name__ == "__main__":
    sys.exit(main())
