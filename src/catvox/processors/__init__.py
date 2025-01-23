import abc
import importlib
import inspect
import logging
import pkgutil
from argparse import ArgumentParser

logger = logging.getLogger(__name__)


class Processor(abc.ABC):
    """
    Base class for all audio processors.
    """

    def __init__(self, args):
        self.args = args
        self.disabled = False
        self._is_running = False

    @abc.abstractmethod
    def check(self, args):
        """
        Check if the processor is available with the given arguments.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def add_arguments(cls, parser: ArgumentParser):
        """
        Add arguments to the command line parser.
        """
        pass


def get_processors():
    """
    Return a list of processors
    """
    processors = []

    for module_info in pkgutil.walk_packages(__path__, prefix=__name__ + "."):
        module_name = module_info.name
        try:
            module = importlib.import_module(module_name)

            for obj in vars(module).values():
                is_processor = inspect.isclass(obj) and issubclass(obj, Processor)
                can_create = not inspect.isabstract(obj)

                if is_processor and can_create:
                    processors.append(obj)

        except ImportError as e:
            logger.error(f"Failed to import {module_name}: {e}")
            logger.debug(e, exc_info=True)

    return processors
