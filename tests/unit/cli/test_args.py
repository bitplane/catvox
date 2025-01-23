from catvox.cli.args import ArgumentParser, other


def test_copy_other():
    parser = ArgumentParser()

    parser.add_argument("--source", type=int, default=42)
    parser.add_argument("--dest", default=other("source"))

    args = parser.parse_args([])

    assert args.source == 42
    assert args.dest == 42


def test_override_default():
    parser = ArgumentParser()

    parser.add_argument("--source", type=int, default=42)
    parser.add_argument("--dest", type=int, default=other("source"))

    args = parser.parse_args(["--dest", "10"])

    assert args.source == 42
    assert args.dest == 10


def test_cascade():
    parser = ArgumentParser()

    parser.add_argument("--source", default="yay")
    parser.add_argument("--copied", default=other("source"))
    parser.add_argument("--cascade", default=other("copied"))

    args = parser.parse_args([])

    assert args.cascade == "yay"
    assert args.copied == "yay"
    assert args.source == "yay"


def test_strange_order():
    parser = ArgumentParser()

    parser.add_argument("--cascade", default=other("copied"))
    parser.add_argument("--copied", default=other("source"))
    parser.add_argument("--source", default="yay")

    args = parser.parse_args([])

    assert args.cascade == "yay"
    assert args.copied == "yay"
    assert args.source == "yay"
