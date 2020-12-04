""" Tests for calculations
"""
import logging
from os import path
from aiida import orm


def test_process(shengbte_code):
    """Test running a calculation
    note this does not test that the expected outputs are created of output parsing"""
    from aiida.plugins import DataFactory, CalculationFactory
    from aiida.engine import run

    from aiida_shengbte import helpers
    if not shengbte_code:
        # get code
        computer = helpers.get_computer()
        shengbte_code = helpers.get_code(entry_point='shengbte', computer=computer)
        logging.info(shengbte_code)

    # set up calculation
    inputs = {
        'code': shengbte_code,
        'structure': helpers.get_test_structure(),
        'supercell_matrix': [3, 3, 3],
        # 'clean_workdir': orm.Bool(True),
        'metadata': {
            'description': "Test job submission with the aiida_shengbte plugin",
        },
    }

    result = run(CalculationFactory('shengbte.thirdorder_sow'), **inputs)
    logging.info(result)

    # assert 'bte' in result


if __name__ == "__main__":
    from aiida import load_profile
    load_profile()
    test_process(None)
