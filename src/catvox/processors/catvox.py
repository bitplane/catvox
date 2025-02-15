from pydantic import Field

from . import Processor


class CatVox(Processor):

    hidden: bool = Field(
        description="Hidden from the help", default=False, exclude=True
    )
    log_level: str = Field(description="Log level", default="WARNING")

    def check(self, args):
        return True
