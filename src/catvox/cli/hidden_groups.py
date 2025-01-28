import argparse
import sys
from unittest.mock import patch


def create_help_action(parser):
    class _HelpAction(argparse.Action):

        def __init__(
            self,
            option_strings=["-h", "--help"],
            dest=argparse.SUPPRESS,
            default=argparse.SUPPRESS,
            help=None,
            nargs=0,
            const=None,
        ):
            super(_HelpAction, self).__init__(
                option_strings=option_strings,
                dest="help",
                default=None,
                nargs=nargs,
                choices=parser.hidden_group_names,
                help=help,
            )

        def __call__(self, parser, namespace, values, option_string=None):
            parser.print_help(groups=values)
            parser.exit()

    return _HelpAction


class HiddenGroups:
    """
    A mixin to support hidden argument groups in ArgumentParser.
    Groups can be marked as hidden, and their visibility can be toggled.
    """

    def __init__(self, *args, **kwargs):
        """
        Override __init__ to add a custom `--help` argument.
        """
        add_help = kwargs.get("add_help", True)
        kwargs["add_help"] = False
        super().__init__(*args, **kwargs)

        self.hidden_group_names = []

        if add_help:
            action = create_help_action(self)

            prefix = "-" if "-" in self.prefix_chars else self.prefix_chars[0]
            self.add_argument(
                f"{prefix}h",
                f"{prefix*2}help",
                action=action,
                nargs="?",
                const=None,
                default=argparse.SUPPRESS,
                help="Show help message or group-specific help. Use '--help <group>' for details.",
            )

    def add_argument_group(self, *args, hidden=False, **kwargs):
        """
        Override add_argument_group to allow tagging groups as hidden.
        """
        group = super().add_argument_group(*args, **kwargs)
        group.hidden = hidden  # Add a hidden attribute to the group
        if group.hidden:
            self.hidden_group_names.append(group.title)
        return group

    def print_help(self, file=None, groups=None):
        if file is None:
            file = sys.stdout
        self._print_message(self.format_help(groups), file)

    def format_help(self, groups=None):
        """
        Override format_help to selectively display argument groups.

        Args:
            groups (list[str] or None): A list of group names to display.
                - If None, display all non-hidden groups.
                - If a list of group names is provided, display only the specified groups.
        """
        if groups is None:
            groups = [
                group
                for group in self._action_groups
                if not getattr(group, "hidden", False)
            ]
        else:
            # Filter groups by name
            groups = [group for group in self._action_groups if group.title in groups]

        # Temporarily replace _action_groups with the selected groups
        with patch.object(self, "_action_groups", groups):
            help_text = super().format_help()

        return help_text
