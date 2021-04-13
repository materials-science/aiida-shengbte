""" Helper functions for automatically setting up computer & code.
Helper functions for setting up 

 1. An AiiDA localhost computer
 2. A "diff" code on localhost
 
Note: Point 2 is made possible by the fact that the ``diff`` executable is
available in the PATH on almost any UNIX system.
"""
import tempfile
import shutil

from aiida.plugins.factories import DataFactory

LOCALHOST_NAME = "localhost-test"

executables = {
    "shengbte": "/workdir/shengbte/ShengBTE",
    "thirdorder_vasp_sow": "/workdir/thirdorder/thirdorder_vasp.py",
    "thirdorder_vasp_reap": "/workdir/thirdorder/thirdorder_vasp.py",
}


def get_path_to_executable(executable):
    """Get path to local executable.
    :param executable: Name of executable in the $PATH variable
    :type executable: str
    :return: path to executable
    :rtype: str
    """
    if "".find("/") == -1:
        path = shutil.which(executable)
        if path is None:
            raise ValueError(
                "'{}' executable not found in PATH.".format(executable)
            )
        return path
    else:
        return executable


def get_computer(name=LOCALHOST_NAME, workdir=None):
    """Get AiiDA computer.
    Loads computer 'name' from the database, if exists.
    Sets up local computer 'name', if it isn't found in the DB.

    :param name: Name of computer to load or set up.
    :param workdir: path to work directory
        Used only when creating a new computer.
    :return: The computer node
    :rtype: :py:class:`aiida.orm.Computer`
    """
    from aiida.orm import Computer
    from aiida.common.exceptions import NotExistent

    try:
        computer = Computer.objects.get(name=name)
    except NotExistent:
        if workdir is None:
            workdir = tempfile.mkdtemp()

        computer = Computer(
            name=name,
            description="localhost computer set up by aiida_diff tests",
            hostname=name,
            workdir=workdir,
            transport_type="local",
            scheduler_type="direct",
        )
        computer.store()
        computer.set_minimum_job_poll_interval(0.0)
        computer.configure()

    return computer


def get_code(entry_point, computer, prepend_text=None):
    """Get local code.
    Sets up code for given entry point on given computer.

    :param entry_point: Entry point of calculation plugin
    :param computer: (local) AiiDA computer
    :return: The code node
    :rtype: :py:class:`aiida.orm.Code`
    """
    from aiida.orm import Code

    try:
        executable = executables[entry_point]
    except KeyError:
        raise KeyError(
            "Entry point '{}' not recognized. Allowed values: {}".format(
                entry_point, list(executables.keys())
            )
        )

    codes = Code.objects.find(
        filters={"label": entry_point}
    )  # pylint: disable=no-member
    if codes:
        return codes[0]

    path = get_path_to_executable(executable)
    code = Code(
        input_plugin_name=entry_point,
        remote_computer_exec=[computer, path],
    )
    if prepend_text is not None:
        code.set_prepend_text(prepend_text)
    code.label = executable
    return code.store()


def get_test_structure():
    """
    Set up InAs primitive cell
    """
    import numpy as np

    structure_data = DataFactory("structure")
    alat = 3.9
    lattice = np.array([[0.5, 0.5, 0], [0, 0.5, 0.5], [0.5, 0, 0.5]]) * alat
    structure = structure_data(cell=lattice)
    positions = [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]]

    pos_cartesian = np.dot(positions[0], lattice)
    structure.append_atom(position=pos_cartesian, symbols="In")
    pos_cartesian = np.dot(positions[1], lattice)
    structure.append_atom(position=pos_cartesian, symbols="As")
    return structure


def get_protocol_parameters(name="default", type="default"):
    protocol = {
        "default": {
            "test": {
                # phonopy
                "mesh": 50,
                "symmetry_tolerance": 1e-5,
                "kpoints_density": 0.4,
                # vasp
                "kpoints_distance": 0.4,
                "incar": {
                    "PREC": "Low",
                    "EDIFF": 1e-4,
                    "NELMIN": 5,
                    "NELM": 100,
                    "ENCUT": 240,
                    "IALGO": 38,
                    "ISMEAR": 0,
                    "SIGMA": 0.1,
                    "LREAL": False,
                    "lcharg": False,
                    "lwave": False,
                },
                "parser_settings": {
                    "add_energies": True,
                    "add_forces": True,
                    "add_stress": True,
                },
                "nac_parser_settings": {
                    "add_born_charges": True,
                    "add_dielectrics": True,
                },
                "nac_incar": {"LEPSILON": True, "IBRION": 8},
            },
            "default": {
                # phonopy
                "mesh": 50,
                "symmetry_tolerance": 1e-5,
                "kpoints_density": 0.4,
                # vasp
                "kpoints_distance": 0.01,
                "incar": {
                    "PREC": "Accurate",
                    "EDIFF": 1e-8,
                    "NELMIN": 5,
                    "NELM": 100,
                    "ENCUT": 240,
                    "IALGO": 38,
                    "ISMEAR": 0,
                    "SIGMA": 0.1,
                    "LREAL": False,
                    "lcharg": False,
                    "lwave": False,
                },
                "parser_settings": {
                    "add_energies": True,
                    "add_forces": True,
                    "add_stress": True,
                },
                "nac_parser_settings": {
                    "add_born_charges": True,
                    "add_dielectrics": True,
                },
                "nac_incar": {"LEPSILON": True, "IBRION": 8},
            },
        }
    }
    return protocol[name][type]
