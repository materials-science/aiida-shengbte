""" Tests for calculations

"""
import logging
from os import path
from aiida import orm
INPUT_DIR = path.join(path.dirname(path.realpath(__file__)), 'input_files')


def test_process(shengbte_code):
    """Test running a calculation
    note this does not test that the expected outputs are created of output parsing"""
    from aiida.plugins import DataFactory, CalculationFactory
    from aiida.engine import run

    # Prepare input parameters
    # DiffParameters = DataFactory('shengbte')
    # parameters = DiffParameters({'ignore-case': True})

    SinglefileData = DataFactory('singlefile')
    FORCE_CONSTANTS_2ND = SinglefileData(file=path.join(
        INPUT_DIR, 'file1.txt'),
        filename='FORCE_CONSTANTS_2ND')
    FORCE_CONSTANTS_3ND = SinglefileData(file=path.join(
        INPUT_DIR, 'file2.txt'),
        filename='FORCE_CONSTANTS_3ND')

    from aiida_shengbte import helpers
    if not shengbte_code:
        # get code
        computer = helpers.get_computer()
        shengbte_code = helpers.get_code(entry_point='shengbte',
                                         computer=computer)
        logging.info(shengbte_code)

    # set up calculation
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
        'FORCE_CONSTANTS_3ND': FORCE_CONSTANTS_3ND,
        # 'clean_workdir': orm.Bool(True),
        'metadata': {
            'description':
            "Test job submission with the aiida_shengbte plugin",
            'dry_run': True,
            'store_provenance': False,
        },
    }

    result = run(CalculationFactory('shengbte.shengbte'), **inputs)
    logging.info(result)

    # assert 'bte' in result
