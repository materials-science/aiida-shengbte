# !/usr/bin/env python
"""Run a test calculation on localhost.

Usage: ./example_01.py
"""
from os import path
from aiida_shengbte import helpers
from aiida import cmdline, engine
from aiida.orm import Str, Bool, Float
from aiida.plugins import DataFactory, CalculationFactory, WorkflowFactory
import click
import logging
logging.basicConfig(level=logging.INFO)

INPUT_DIR = path.join(path.dirname(path.realpath(__file__)), 'input_files')
Dict = DataFactory('dict')


def test_run(shengbte_code=None):
    """Run a calculation on the localhost computer.

    Uses test helpers to create AiiDA Code on the fly.
    """
    computer = helpers.get_computer()
    if not shengbte_code:
        shengbte_code = helpers.get_code(entry_point='shengbte', computer=computer)
    # set up calculation
    SinglefileData = DataFactory('singlefile')
    FORCE_CONSTANTS_2ND = SinglefileData(file=path.join(
        INPUT_DIR, 'file1.txt'),
        filename='FORCE_CONSTANTS_2ND')
    FORCE_CONSTANTS_3RD = SinglefileData(file=path.join(
        INPUT_DIR, 'file2.txt'),
        filename='FORCE_CONSTANTS_3RD')
    inputs = {
        'structure': helpers.get_test_structure(),
        'control': Dict(dict={
            'allocations': {
                'ngrid': [3, 3, 3],
                'norientations': 0
            },
            'crystal': {
                'orientations': [3, 2, 1],
                'scell': [3, 3, 3]
            },
            'parameters': {
                'T_min': 0,
                'T_max': 0,
                'T_step': 0,
            },
        }),
        'calculation': {
            'code': shengbte_code,
            'FORCE_CONSTANTS_2ND': FORCE_CONSTANTS_2ND,
            'FORCE_CONSTANTS_3RD': FORCE_CONSTANTS_3RD,
        },
        # 'clean_workdir': orm.Bool(True),
        'metadata': {
            'description': "Test job submission with the aiida_shengbte thirdorder plugin",
        },
    }
    logging.error(inputs)
    result = engine.run(WorkflowFactory('shengbte.shengbte'), **inputs)

    logging.info(result)


@ click.command()
@ cmdline.utils.decorators.with_dbenv()
@ cmdline.params.options.CODE()
def cli(code):
    """Run example.

    Example usage: $ ./example_01.py -- code diff@localhost

    Alternative (creates diff@localhost-test code): $ ./example_01.py

    Help: $ ./example_01.py -- help
    """
    test_run(code)


if __name__ == '__main__':
    cli()  # pylint: disable = no-value-for-parameter
