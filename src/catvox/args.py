import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="catvox - transcribe and print to stdout"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=0.5,
        help="If you pause speaking for this long, it'll spit the result out.",
    )
    parser.add_argument(
        "--max_length",
        type=float,
        default=15.0,
        help="Maximum listening length in seconds, in case Whisper goes crazy",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        help="Model size to use (e.g., tiny, base, small, medium, large)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Spit debug stuff out to the console",
    )

    return parser.parse_args()
