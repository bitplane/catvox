import abc
import importlib
import inspect
import logging
import os
import pkgutil

from pydantic import BaseModel, Field

from ..cli.args import ArgumentParser

logger = logging.getLogger(__name__)


class Processor(BaseModel, abc.ABC):
    """
    Base class for all audio pipeline processors.
    """

    hidden: bool = Field(description="Hidden from the help", default=True, exclude=True)
    disabled: bool = Field(
        description="Explicitly disable this processor", default=False
    )
    required: bool = Field(
        description="Processor was explicitly asked for", default=False
    )
    priotity: int = Field(description="Priority of this processor", default=0)

    def __init__(self, **data):
        super().__init__(**data)
        if self.disabled and self.required:
            raise ValueError(f"{self.name} was requested but is disabled")

    def __lt__(self, other: "Processor"):
        return self.priority < other.priority

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def add_args(self, parser: ArgumentParser):
        """
        Add a section to the argument parser for this processor.
        """
        group = parser.add_argument_group(
            title=self.name, description=self.__doc__, hidden=self.hidden
        )

        for name, field in self.model_fields.items():
            if field.exclude:
                continue
            parser.add_argument(
                f"--{self.name}-{name}",
                type=field.annotation,
                default=field.default,
                help=field.description,
            )
        return group

    @classmethod
    @abc.abstractmethod
    def request(cls, output_format):
        """
        Yields input formats that would allow this processor to
        produce the requested output format.
        """
        pass


def get_processors() -> list[Processor]:
    """
    Return a list of all processors
    """
    processors = []
    path = os.path.dirname(__file__)
    module_name = __name__.rsplit(".", 1)[0]

    for module_info in pkgutil.walk_packages([path], prefix=module_name + "."):
        module_name = module_info.name
        try:
            module = importlib.import_module(module_name)

            for obj in vars(module).values():
                is_processor = inspect.isclass(obj) and issubclass(obj, Processor)
                can_create = not inspect.isabstract(obj)

                if is_processor:
                    if can_create:
                        processors.append(obj)

        except ImportError as e:
            logger.error(f"Failed to import {module_name}: {e}")
            logger.debug(e, exc_info=True)

    processors.sort()
    return processors
