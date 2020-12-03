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
        shengbte_code = helpers.get_code(entry_point='thirdorder_vasp', computer=computer)
        logging.info(shengbte_code)

    # set up calculation
    inputs = {
        'code': shengbte_code,
        'structure': helpers.get_test_structure(),
        'parameters': orm.Dict(dict={
            'supercell_matrix': [3, 3, 3],
            'option': '-3'
        }),
        # 'clean_workdir': orm.Bool(True),
        'metadata': {
            'description': "Test job submission with the aiida_shengbte plugin",
            # 'dry_run': True,
        },
    }
    logging.error(inputs)
    result = engine.run(CalculationFactory('shengbte.thirdorder_sow'), **inputs)

    logging.info(result)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
def cli(code):
    """Run example.

    Example usage: $ ./example_01.py -- code diff@localhost

    Alternative (creates diff@localhost-test code): $ ./example_01.py

    Help: $ ./example_01.py -- help
    """
    test_run(code)


if __name__ == '__main__':
    cli()  # pylint: disable = no-value-for-parameter
