# -*- coding: utf-8 -*-
"""Command line scripts to launch a `ShengBTECalculation` for testing and demonstration purposes."""
import click

from aiida.cmdline.params import options as options_core
from aiida.cmdline.params import types
from aiida.cmdline.utils import decorators
from ..utils import launch
from ..utils import options
from . import cmd_launch
import logging

logging.basicConfig(level=logging.INFO)


@cmd_launch.command("shengbte")
@options_core.CODE()
@options.MAX_NUM_MACHINES()
@options.NUM_MPIPROCS_PER_MACHINE()
@options.WITH_MPI()
@options.DAEMON()
@decorators.with_dbenv()
def launch_test(
    code,
    max_num_machines,
    num_mpiprocs_per_machine,
    with_mpi,
    daemon,
):
    """Run a ShengBTE Calculation test calculation."""
    import os
    from aiida_shengbte import helpers
    from aiida import orm
    from aiida.plugins import DataFactory, CalculationFactory

    if not code:
        # get code
        computer = helpers.get_computer()
        code = helpers.get_code(entry_point="shengbte", computer=computer)
    fc_dir = os.path.normcase(
        os.path.join(os.path.abspath(__file__), "../input_files")
    )
    SinglefileData = DataFactory("singlefile")
    FORCE_CONSTANTS_2ND = SinglefileData(
        file=fc_dir + "/FORCE_CONSTANTS_2ND",
        filename="FORCE_CONSTANTS_2ND",
    )
    FORCE_CONSTANTS_3RD = SinglefileData(
        file=fc_dir + "/FORCE_CONSTANTS_3RD",
        filename="FORCE_CONSTANTS_3RD",
    )

    inputs = {
        "code": code,
        "control": orm.Dict(
            dict={
                "allocations": {
                    "nelements": 2,
                    "natoms": 2,
                    "ngrid": [3, 3, 3],
                    "norientations": 3,
                },
                "crystal": {
                    "lattvec": [[0, 0.5, 0.5], [0.5, 0, 0.5], [0.5, 0.5, 0]],
                    "elements": ["In", "As"],
                    "types": [1, 2],
                    "positions": [[0, 0, 0], [0.25, 0.25, 0.25]],
                    "scell": [5, 5, 5],
                    "born": [
                        [[2.67810, 0, 0], [0, 2.67810, 0], [0, 0, 2.67810]],
                        [[-2.67810, 0, 0], [0, -2.67810, 0], [0, 0, -2.67810]],
                    ],
                    "orientations": [[1, 0, 0], [1, 1, 0], [1, 1, 1]],
                },
                "parameters": {
                    "T": 300,
                },
                "flags": {
                    "espresso": False,
                    "nonanalytic": True,
                    "nanowires": True,
                },
            }
        ),
        "FORCE_CONSTANTS_2ND": FORCE_CONSTANTS_2ND,
        "FORCE_CONSTANTS_3RD": FORCE_CONSTANTS_3RD,
        # 'clean_workdir': orm.Bool(True),
        "metadata": {
            "description": "Test job submission with the aiida_shengbte plugin",
            "options": {
                "resources": {
                    "num_machines": int(max_num_machines),
                    "num_mpiprocs_per_machine": int(num_mpiprocs_per_machine),
                },
                "withmpi": with_mpi,
            }
            # 'dry_run': True,
            # 'store_provenance': False,
        },
    }

    launch.launch_process(
        CalculationFactory("shengbte.shengbte"), daemon, **inputs
    )


if __name__ == "__main__":
    launch_test()  # pylint: disable = no-value-for-parameter