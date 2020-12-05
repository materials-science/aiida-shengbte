# !/usr/bin/env python
"""Run a test calculation on localhost.

Usage: ./example_01.py
"""
from os import path
from aiida_shengbte import helpers
from aiida import cmdline, engine, orm
from aiida.plugins import DataFactory, CalculationFactory, WorkflowFactory
import click
import logging
logging.basicConfig(level=logging.INFO)

INPUT_DIR = path.join(path.dirname(path.realpath(__file__)), 'input_files')
Dict = DataFactory('dict')


def test_run(thirdorder_sow_code=None, thirdorder_reap_code=None):
    """Run a calculation on the localhost computer.

    Uses test helpers to create AiiDA Code on the fly.
    """
    computer = helpers.get_computer()
    if not thirdorder_sow_code:
        # get code
        thirdorder_sow_code = helpers.get_code(entry_point='thirdorder_vasp_sow', computer=computer)
    if not thirdorder_reap_code:
        thirdorder_reap_code = helpers.get_code(entry_point='thirdorder_vasp_reap',
                                                computer=computer, prepend_text='find job.* -name vasprun.xml|sort -n|')
    # set up calculation
    base_incar_dict = {
        'PREC': 'Accurate',
        'IBRION': 8,
        'EDIFF': 1e-8,
        'NELMIN': 5,
        'NELM': 100,
        'ENCUT': 240,
        'IALGO': 38,
        'ISMEAR': 0,
        'SIGMA': 0.1,
        'LREAL': False,
        'lcharg': False,
        'lwave': False,
    }
    forces_config = {
        'code_string': 'vasp@vasp',
        'kpoints_density': 0.5,  # k-point density,
        'potential_family': 'pbe',
        'potential_mapping': {'Si': 'Si'},
        'options': {
            'resources': {'num_machines': 1, 'tot_num_mpiprocs': 4},
            'max_wallclock_seconds': 3600 * 10
        },
        'parser_settings': {
            'add_energies': True,
            'add_forces': True,
            'add_stress': True
        },
        'parameters': base_incar_dict
    }

    inputs = {
        'structure': helpers.get_test_structure(),
        'thirdorder_sow': {
            'code': thirdorder_sow_code,
            'parameters': Dict(dict={
                'supercell_matrix': [3, 3, 3],
                'option': '-3'
            })
        },
        'thirdorder_reap': {
            'code': thirdorder_reap_code,
            'parameters': Dict(dict={
                'supercell_matrix': [3, 3, 3],
                'option': '-3'
            })
        },
        'vasp_settings': Dict(dict={'forces': forces_config}),
        # 'clean_workdir': orm.Bool(True),
        'metadata': {
            'description': "Test job submission with the aiida_shengbte thirdorder plugin",
        },
    }
    logging.error(inputs)
    result = engine.run(WorkflowFactory('shengbte.thirdorder'), **inputs)

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
