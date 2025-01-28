import abc
import importlib
import inspect
import logging
import pkgutil

from ..cli.args import ArgumentParser

logger = logging.getLogger(__name__)


class Processor(abc.ABC):
    """
    Base class for all audio processors.
    """

    def __init__(self, args):
        self.args = args
        self.disabled = False
        self._is_running = False

    @classmethod
    @abc.abstractmethod
    def check_args(cls, args):
        """
        Check if the processor is available with the given arguments.
        """
        pass

    @classmethod
    def add_arg_group(cls, parser: ArgumentParser, hidden=True):
        """
        Add a section to the argument parser for this processor.
        """
        name = cls.__name__.lower()
        group = parser.add_argument_group(
            title=name, description=cls.__doc__, hidden=hidden
        )
        group.add_argument(
            f"--{name}",
            action="store_true",
            default=False,
            help=f"Explicitly use {name}",
        )
        group.add_argument(
            f"--no-{name}",
            dest=name,
            action="store_false",
            help=f"Explicitly disable {name}",
        )
        return group

    @classmethod
    def add_args(cls, parser: ArgumentParser):
        """
        Add arguments to the argument parser.
        """
        cls.add_arg_group(parser)

    @classmethod
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

    for module_info in pkgutil.walk_packages(__path__, prefix=__name__ + "."):
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

    return processors
