# -*- coding: utf-8 -*-
"""Command line scripts to launch a `ShengBTECalculation` for testing and demonstration purposes."""
import json
import click
from aiida.cmdline.utils import decorators
from tempfile import NamedTemporaryFile
from ..utils import options
from . import cmd_launch
import logging

logging.basicConfig(level=logging.INFO)


@cmd_launch.command("control")
@click.option(
    "-i",
    "--input",
    required=True,
    help="input file(json or control)",
)
@click.option(
    "-f",
    "--format",
    default="control",
    help="format that the input file should be transformed to.(dict -> control or control -> dict)",
)
@click.option(
    "-o",
    "--output",
    help="output filename.",
)
@options.STRUCTURE()
@decorators.with_dbenv()
def launch_tools(input, format, structure, output):
    """Run a tool to transform control file."""
    from aiida_shengbte.parsers.data_parser.control_parser import ControlParser

    if format == "control":
        with open(input, "r") as f:
            control_dict = json.loads(f)
            parser = ControlParser(control_dict, logging.getLogger())

            if structure is not None:
                parser.generate_from_structure(structure)
            parser.validate_input()
        if output:
            parser.write_control(output)
        else:
            with NamedTemporaryFile(suffix=".CONTROL") as tf:
                parser.write_control(tf.name)
                tf.seek(0)
                stream = tf.read()
                print(stream)
    # TODO: control to dict
    if format == "dict":
        print("Under developing......")


if __name__ == "__main__":
    launch_tools()  # pylint: disable = no-value-for-parameter