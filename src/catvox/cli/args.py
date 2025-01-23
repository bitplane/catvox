import argparse


class other:
    """
    Placeholder type for arguments that should copy their default
    value from another argument.
    """

    def __init__(self, source):
        self.source = source

    def resolve(self, args, dest):
        value = getattr(args, self.source)
        is_a_copy = isinstance(value, other)

        if is_a_copy:
            value = value.resolve(args, dest)

        setattr(args, dest, value)

        return value


class ArgumentParser(argparse.ArgumentParser):
    """
    ArgumentParser subclass that allows arguments to copy some other value
    """

    def parse_args(self, *args, **kwargs):
        # Parse the arguments as usual
        args = super().parse_args(*args, **kwargs)

        # copy the default values from other arguments
        for action in self._actions:
            defaults_to_another_arg = isinstance(action.default, other)
            dest_value = getattr(args, action.dest, None)
            has_a_value = dest_value not in (None, action.default)
            if defaults_to_another_arg and not has_a_value:
                action.default.resolve(args, action.dest)

        return args
