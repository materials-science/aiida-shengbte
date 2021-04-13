# -*- coding: utf-8 -*-
# pylint: disable=cyclic-import,reimported,unused-import,wrong-import-position
"""Module with CLI commands for the various calculation job implementations."""
from .. import cmd_root


@cmd_root.group("tools")
def cmd_test():
    """Commands to launch and interact with test."""


@cmd_test.group("launch")
def cmd_launch():
    """Launch tools."""


# Import the sub commands to register them with the CLI
from .control import launch_tools