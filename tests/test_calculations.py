""" Tests for calculations

"""
import logging
import os
from typing import Dict
from . import TEST_DIR


def test_process(shengbte_code):
    """Test running a calculation
    note this does not test that the expected outputs are created of output parsing"""
    from aiida.plugins import DataFactory, CalculationFactory
    from aiida.engine import run

    # Prepare input parameters
    DiffParameters = DataFactory('shengbte')
    parameters = DiffParameters({'ignore-case': True})

    from aiida.orm import SinglefileData
    file1 = SinglefileData(
        file=os.path.join(TEST_DIR, "input_files", 'file1.txt'))
    file2 = SinglefileData(
        file=os.path.join(TEST_DIR, "input_files", 'file2.txt'))

    # set up calculation
    inputs = {
        'code': shengbte_code,
        'parameters': parameters,
        'file1': file1,
        'file2': file2,
        'metadata': {
            'options': {
                'max_wallclock_seconds': 30
            },
        },
    }
    from aiida_shengbte import helpers
    if not shengbte_code:
        # get code
        computer = helpers.get_computer()
        shengbte_code = helpers.get_code(entry_point='shengbte',
                                         computer=computer)
        logging.info(computer.get_name())
        logging.info(shengbte_code)

    # inputs = {
    #     'code': shengbte_code,
    #     'test': Dict({
    #         'name': 'por'
    #     })
    # }

    result = run(CalculationFactory('shengbte'), **inputs)
    # logging.info(result)
    computed_diff = result['shengbte'].get_content()
    logging.info(computed_diff)

    assert 'content1' in computed_diff
    assert 'content2' in computed_diff
