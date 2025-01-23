from catvox.processors import get_processors


def test_get_processors():
    classes = get_processors()

    assert classes
