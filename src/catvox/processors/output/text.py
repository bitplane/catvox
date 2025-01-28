from . import Output


class TextOutput(Output):
    """
    Plain text output.
    """

    @classmethod
    def check_args(cls, args):
        return True

    @classmethod
    def add_args(cls, parser):
        pass

    @classmethod
    def request(cls, format):
        if "text" in format["type"]:
            return {
                "type": "text",
                "format": format,
            }
