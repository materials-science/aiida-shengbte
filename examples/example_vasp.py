# !/usr/bin/env python
"""Run a test calculation on localhost.

Usage: ./example_vasp.py
"""
from os import path
from aiida_shengbte import helpers
from aiida import cmdline, engine
from aiida.orm import Str, Bool, Float
from aiida.plugins import DataFactory, WorkflowFactory
import click
import logging
logging.basicConfig(level=logging.INFO)

INPUT_DIR = path.join(path.dirname(path.realpath(__file__)), 'input_files')
Dict = DataFactory('dict')


def test_run(thirdorder_sow_code=None, thirdorder_reap_code=None, shengbte_code=None):
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
    if not shengbte_code:
        shengbte_code = helpers.get_code(entry_point='shengbte', computer=computer)
    # set up calculation

    base_incar_dict = {
        'PREC': 'Accurate',
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

    base_config = {
        'code_string': 'vasp@vasp',
        'kpoints_density': 0.5,  # k-point density,
        'potential_family': 'pbe',
        'potential_mapping': {'Si': 'Si'},
        'options': {
            'resources': {'num_machines': 1, 'tot_num_mpiprocs': 4},
            'max_wallclock_seconds': 3600 * 10
        },
    }
    base_parser_settings = {'add_energies': True,
                            'add_forces': True,
                            'add_stress': True}
    forces_config = base_config.copy()
    forces_config.update({
        'parser_settings': base_parser_settings,
        'parameters': base_incar_dict
    })
    nac_config = base_config.copy()
    nac_parser_settings = {'add_born_charges': True, 'add_dielectrics': True}
    nac_parser_settings.update(base_parser_settings)
    nac_incar_dict = {'LEPSILON': True, 'IBRION': 8}
    nac_incar_dict.update(base_incar_dict)
    nac_config.update({'parser_settings': nac_parser_settings, 'parameters': nac_incar_dict})

    inputs = {
        'structure': helpers.get_test_structure(),
        'phonopy': {
            'run_phonopy': Bool(True),
            'remote_phonopy': Bool(True),
            'code_string': Str('phonopy@vasp'),
            'phonon_settings': Dict(dict={
                'mesh': 50.0,
                'supercell_matrix': [3, 3, 3],
                'distance': 0.01,
                'is_nac': True
            }),
            'symmetry_tolerance': Float(1e-5),
            'options': Dict(dict=base_config['options']),
            'metadata': {
                'label': "Si 3x3x3 phonon example",
                'description': "Test job submission with the phonopy",
            },
        },
        'thirdorder': {
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
        },
        'shengbte': {
            'control': Dict(dict={
                'allocations': {
                    'ngrid': [3, 3, 3],
                    'norientations': 0
                },
                'crystal': {
                    'orientations': [3, 2, 1],
                    # 'masses': [],
                    # 'gfactors': []
                },
                'parameters': {
                    'T': 5,
                    # 'T_min': 0,
                    # 'T_max': 0,
                    # 'T_step': 0,
                    # 'omega_max': 0,
                    # 'scalebroad': 0,
                    # 'rmin': 0,
                    # 'rmax': 0,
                    # 'dr': 0,
                    # 'maxiter': 0,
                    # 'nticks': 0,
                    # 'eps': 0
                },
            }),
            'calculation': {
                'code': shengbte_code,
            },
        },
        'vasp_settings': Dict(dict={'forces': forces_config, 'nac': nac_config}),
        # 'clean_workdir': orm.Bool(True),
        'metadata': {
            'description': "Test job submission with the aiida_shengbte thirdorder plugin",
        },
    }
    result = engine.run(WorkflowFactory('shengbte.vasp'), **inputs)

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
