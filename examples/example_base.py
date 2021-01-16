# !/usr/bin/env python
"""Run a test calculation on localhost.

Usage: ./example_base.py
"""
from os import path
from aiida_shengbte import helpers
from aiida import cmdline, engine, orm
from aiida.plugins import DataFactory, CalculationFactory
import click
import logging
logging.basicConfig(level=logging.INFO)

INPUT_DIR = path.join(path.dirname(path.realpath(__file__)), 'input_files')


def test_run(shengbte_code):
    """Run a calculation on the localhost computer.

    Uses test helpers to create AiiDA Code on the fly.
    """
    if not shengbte_code:
        # get code
        computer = helpers.get_computer()
        shengbte_code = helpers.get_code(entry_point='shengbte',
                                         computer=computer,
                                         prepend_text='find _* |')
    logging.info(shengbte_code)

    SinglefileData = DataFactory('singlefile')
    FORCE_CONSTANTS_2ND = SinglefileData(file=path.join(
        INPUT_DIR, 'FORCE_CONSTANTS_2ND'),
        filename='FORCE_CONSTANTS_2ND')
    FORCE_CONSTANTS_3RD = SinglefileData(file=path.join(
        INPUT_DIR, 'FORCE_CONSTANTS_3RD'),
        filename='FORCE_CONSTANTS_3RD')

    import numpy as np
    inputs = {
        'code': shengbte_code,
        'control': orm.Dict(dict={
            'allocations': {
                'nelements': 2,
                'natoms': 2,
                'ngrid': [3, 3, 3],
                'norientations': 3
            },
            'crystal': {
                'lattvec': [
                    [0, 0.5, 0.5],
                    [0.5, 0, 0.5],
                    [0.5, 0.5, 0]],
                'elements': ['In', 'As'],
                'types': [1, 2],
                'positions': [
                    [0, 0, 0],
                    [0.25, 0.25, 0.25]
                ],
                'scell': [5, 5, 5],
                'born': [
                    [
                        [2.67810, 0, 0],
                        [0, 2.67810, 0],
                        [0, 0, 2.67810]
                    ],
                    [
                        [-2.67810, 0, 0],
                        [0, -2.67810, 0],
                        [0, 0, -2.67810]
                    ]
                ],
                'orientations': [[1, 0, 0], [1, 1, 0], [1, 1, 1]]
            },
            'parameters': {
                'T': 300,
            },
            'flags': {
                'espresso': False,
                'nonanalytic': True,
                'nanowires': True
            }
        }),
        'FORCE_CONSTANTS_2ND': FORCE_CONSTANTS_2ND,
        'FORCE_CONSTANTS_3RD': FORCE_CONSTANTS_3RD,
        # 'clean_workdir': orm.Bool(True),
        'metadata': {
            'description':
            "Test job submission with the aiida_shengbte plugin",
            # 'dry_run': True,
            # 'store_provenance': False,
        },
    }

    # Note: in order to submit your calculation to the aiida daemon, do:
    # from aiida.engine import submit
    # future = submit(CalculationFactory('shengbte'), **inputs)
    result = engine.run(CalculationFactory('shengbte.shengbte'), **inputs)

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
