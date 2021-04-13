# -*- coding: utf-8 -*-
# pylint: disable=cyclic-import,reimported,unused-import,wrong-import-position
"""Module with CLI commands for the various calculation job implementations."""
from .. import cmd_root


@cmd_root.group("test")
def cmd_test():
    """Commands to launch and interact with test."""


@cmd_test.group("launch")
def cmd_launch():
    """Launch test."""


# Import the sub commands to register them with the CLI
from .shengbte import launch_test