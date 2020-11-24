#!/usr/bin/env python
"""Run a test calculation on localhost.

Usage: ./example_01.py
"""
import logging
from os import path
from aiida_shengbte import helpers
from aiida import cmdline, engine
from aiida.plugins import DataFactory, CalculationFactory
import click

INPUT_DIR = path.join(path.dirname(path.realpath(__file__)), 'input_files')


def test_run(shengbte_code):
    """Run a calculation on the localhost computer.

    Uses test helpers to create AiiDA Code on the fly.
    """
    if not shengbte_code:
        # get code
        computer = helpers.get_computer()
        shengbte_code = helpers.get_code(entry_point='shengbte',
                                         computer=computer)
        logging.info(computer.get_name())
        logging.info(shengbte_code)

    # Prepare input parameters
    DiffParameters = DataFactory('shengbte')
    parameters = DiffParameters({'ignore-case': True})

    SinglefileData = DataFactory('singlefile')
    file1 = SinglefileData(file=path.join(INPUT_DIR, 'file1.txt'))
    file2 = SinglefileData(file=path.join(INPUT_DIR, 'file2.txt'))

    # set up calculation
    inputs = {
        'code': shengbte_code,
        'parameters': parameters,
        'file1': file1,
        'file2': file2,
        'metadata': {
            'description':
            "Test job submission with the aiida_shengbte plugin",
        },
    }
    # inputs = {
    #     parameters: inputs
    # }

    # Note: in order to submit your calculation to the aiida daemon, do:
    # from aiida.engine import submit
    # future = submit(CalculationFactory('shengbte'), **inputs)
    result = engine.run(CalculationFactory('shengbte'), **inputs)

    # print(result)
    logging.info(result)
    computed_diff = result['shengbte'].get_content()
    print("Computed diff between files: \n{}".format(computed_diff))


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
def cli(code):
    """Run example.

    Example usage: $ ./example_01.py --code diff@localhost

    Alternative (creates diff@localhost-test code): $ ./example_01.py

    Help: $ ./example_01.py --help
    """
    test_run(code)


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
