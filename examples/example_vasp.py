# !/usr/bin/env python
"""Run a ShengBTE Vasp example.
"""
from os import path
from aiida_shengbte import helpers
from aiida import cmdline, engine
from aiida_shengbte.cli.utils import options
from aiida.orm import Str, Bool, Float
from aiida.plugins import DataFactory, WorkflowFactory
import click
import logging

logging.basicConfig(level=logging.INFO)

INPUT_DIR = path.join(path.dirname(path.realpath(__file__)), "input_files")
Dict = DataFactory("dict")


def get_code_string(code):
    return "{}@{}".format(code.label, code.computer.label)


@click.command()
@cmdline.params.options.CODES(
    required=True,
    help="vasp_code, phonopy_code, thirdorder_reap_code, thirdorder_sow_code, shengbte_code",
)
# @cmdline.params.options.CODE(required=True, help="phonopy_code")
# @cmdline.params.options.CODE(required=True, help="thirdorder_sow_code")
# @cmdline.params.options.CODE(required=True, help="thirdorder_reap_code")
# @cmdline.params.options.CODE(required=True, help="shengbte_code")
@options.STRUCTURE()
@click.option(
    "--protocol",
    default="default",
    show_default=True,
    help="Availables are: default.",
)
@click.option(
    "--parameters",
    default="test",
    show_default=True,
    help="Availables are: test, . Default is test.",
)
@options.SUPERCELL_MATRIX()
@click.option(
    "--neighbor", type=click.INT, default=3, show_default=True, help="neighbor"
)
@click.option(
    "--pseudo-family", default="pbe", show_default=True, help="pseudo family"
)
@options.MAX_NUM_MACHINES()
@options.NUM_MPIPROCS_PER_MACHINE()
@options.WITH_MPI()
@options.MAX_WALLCLOCK_SECONDS()
@options.DAEMON()
@cmdline.utils.decorators.with_dbenv()
def cli(
    codes,
    # vasp_code,
    # phonopy_code,
    # thirdorder_sow_code,
    # thirdorder_reap_code,
    # shengbte_code,
    structure,
    protocol,
    parameters,
    supercell_matrix,
    neighbor,
    pseudo_family,
    max_num_machines,
    num_mpiprocs_per_machine,
    with_mpi,
    max_wallclock_seconds,
    daemon,
):
    """Run a calculation on the localhost computer.

    Uses test helpers to create AiiDA Code on the fly.
    """
    # set up calculation

    if not structure:
        structure = helpers.get_test_structure()

    (
        vasp_code,
        phonopy_code,
        thirdorder_reap_code,
        thirdorder_sow_code,
        shengbte_code,
    ) = codes
    protocol = helpers.get_protocol_parameters(name=protocol, type=parameters)
    potential_mapping = {}
    for kind in structure.get_kind_names():
        potential_mapping[kind] = kind

    base_incar_dict = protocol["incar"]

    base_config = {
        "code_string": get_code_string(vasp_code),
        "kpoints_density": protocol["kpoints_density"],  # k-point density,
        "potential_family": pseudo_family,
        "potential_mapping": potential_mapping,
        "options": {
            "resources": {
                "num_machines": max_num_machines,
                "num_mpiprocs_per_machine": num_mpiprocs_per_machine,
            },
            "max_wallclock_seconds": max_wallclock_seconds,
        },
    }
    base_parser_settings = protocol["parser_settings"]
    forces_config = base_config.copy()
    forces_config.update(
        {
            "parser_settings": base_parser_settings,
            "parameters": {"incar": base_incar_dict},
        }
    )
    nac_config = base_config.copy()
    nac_parser_settings = protocol["nac_parser_settings"]
    nac_parser_settings.update(base_parser_settings)
    nac_incar_dict = protocol["nac_incar"]
    nac_incar_dict.update(base_incar_dict)
    nac_config.update(
        {
            "parser_settings": nac_parser_settings,
            "parameters": {"incar": nac_incar_dict},
        }
    )

    inputs = {
        "structure": structure,
        "phonopy": {
            "run_phonopy": Bool(True),
            "remote_phonopy": Bool(True),
            "code_string": Str(get_code_string(phonopy_code)),
            "phonon_settings": Dict(
                dict={
                    "mesh": protocol["mesh"],
                    "supercell_matrix": supercell_matrix,
                    "distance": protocol["kpoints_distance"],
                    "is_nac": True,
                }
            ),
            "symmetry_tolerance": Float(protocol["symmetry_tolerance"]),
            "options": Dict(dict=base_config["options"]),
            "metadata": {
                "label": "example",
                "description": "Test job submission with the phonopy",
            },
        },
        "thirdorder": {
            "thirdorder_sow": {
                "code": thirdorder_sow_code,
                "parameters": Dict(
                    dict={
                        "supercell_matrix": supercell_matrix,
                        "option": neighbor,
                    }
                ),
            },
            "thirdorder_reap": {
                "code": thirdorder_reap_code,
                "parameters": Dict(
                    dict={
                        "supercell_matrix": supercell_matrix,
                        "option": neighbor,
                    }
                ),
            },
        },
        "shengbte": {
            "control": Dict(
                dict={
                    "allocations": {"ngrid": [3, 3, 3], "norientations": 3},
                    "crystal": {
                        "orientations": [[1, 0, 0], [1, 1, 0], [1, 1, 1]]
                        # 'masses': [],
                        # 'gfactors': []
                    },
                    "parameters": {
                        "T": 300,
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
                    "flags": {
                        # "espresso": False,
                        "nonanalytic": True,
                        "nanowires": True,
                    },
                }
            ),
            "calculation": {
                "code": shengbte_code,
                "metadata": {
                    "options": {
                        "resources": {
                            "num_machines": int(max_num_machines),
                            "num_mpiprocs_per_machine": int(
                                num_mpiprocs_per_machine
                            ),
                        },
                        "withmpi": with_mpi,
                    },
                },
            },
        },
        "vasp_settings": Dict(
            dict={"forces": forces_config, "nac": nac_config}
        ),
        # 'clean_workdir': Bool(True),
        # 'dry_run': Bool(True),
        "metadata": {
            "description": "Test job submission with the aiida_shengbte thirdorder plugin",
        },
    }
    from aiida_shengbte.cli.utils import launch

    launch.launch_process(WorkflowFactory("shengbte.vasp"), daemon, **inputs)


if __name__ == "__main__":
    cli()  # pylint: disable = no-value-for-parameter
