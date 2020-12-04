# !/usr/bin/env python
"""Run a test calculation on localhost.

Usage: ./example_01.py
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
        # logging.info(computer.get_name())
        # shengbte_code = load_code('test@test')
    logging.info(shengbte_code)

    # # Prepare input parameters
    # DiffParameters = DataFactory('shengbte')
    # parameters = DiffParameters({'ignore-case': True})

    SinglefileData = DataFactory('singlefile')
    FORCE_CONSTANTS_2ND = SinglefileData(file=path.join(
        INPUT_DIR, 'file1.txt'),
        filename='FORCE_CONSTANTS_2ND')
    FORCE_CONSTANTS_3RD = SinglefileData(file=path.join(
        INPUT_DIR, 'file2.txt'),
        filename='FORCE_CONSTANTS_3RD')

    inputs = {
        'code': shengbte_code,
        'control': orm.Dict(dict={
            'allocations': {
                'nelements': 3,
                'natoms': 2,
                'ngrid': [3, 3, 3],
                'norientations': 0
            },
            'crystal': {
                'lattvec': [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]],
                'types': [1, 2],
                'elements': ['h', 'i', 'j'],
                'positions': [[1, 2, 3],
                              [4, 5, 6],
                              [7, 8, 9]],
                'scell': [3, 3, 3],
                'born': [
                    [
                        [1, 2, 3],
                        [4, 5, 6],
                        [7, 8, 9]
                    ],
                    [
                        [1, 2, 3],
                        [4, 5, 6],
                        [7, 8, 9]
                    ]
                ]
                # 'orientations': [3, 2, 1]
            },
            'parameters': {
                'T': 5,
            },
            'flags': {
                'espresso': True
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
