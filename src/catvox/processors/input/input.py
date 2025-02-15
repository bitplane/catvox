import sys

from pydantic import Field

from .. import Processor

input_classes = []


class Input(Processor):
    """
    Selects input source(s) to process.

    If no sources are provided then it'll default to stdin if there's input, and fall
    back to the default microphone if not.
    """

    hidden: bool = Field(
        description="Hidden from the help", default=False, exclude=True
    )
    file: list[str] = Field(
        description="Input from a file. Use '-' for stdin", default=[]
    )
    source: list[str] = Field(description="Use specific input sources", default=[])
    as_channels: bool = Field(
        description="Treat each source as a separate channel", default=False
    )
    auto_select: bool = Field(
        description="Automatically select input source", default=True
    )

    def __init__(self, **data):
        super().__init__(**data)

        if self.auto_select and not self.source:
            if not self.file and self.stdin_has_data():
                self.source = ["file"]
                self.file = ["-"]
            else:
                self.source = ["mic"]

    def stdin_has_data(self):
        """
        Check if stdin has data
        """
        try:
            has_data = bool(sys.stdin.buffer.peek(1))
            return has_data
        except (BrokenPipeError, OSError):
            return False


class Output(Processor):
    hidden: bool = Field(
        description="Hidden from the help", default=False, exclude=True
    )
    file: list[str] = Field(
        description="Input from a file. Use '-' for stdout", default=["-"]
    )
    format: str = Field(description="Output format", default="text")
