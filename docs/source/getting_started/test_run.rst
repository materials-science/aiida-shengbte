.. _test_run:

======================================
4. Test a simple ShengBTE calculations
======================================

In this part we will simply launch a `ShengBTE`_ calculation using the ``StructData``, ``FORCE_CONSTANTS_2ND`` and ``FORCE_CONSTANTS_3RD`` files, which are under `./input_files` directory, provied by ShengBTE official `Test-VASP` example. Here we use ``ase.io.vasp.read_vasp`` to read a ``POSCAR`` to ``StructData`` that `AiiDA`_ supports. Any other formats such as ``CIF``, ``XYZ`` also work importing by relative importors.

|   You'd better import StructData firstly, then you can use ``load_node`` to load your StructData easily.

Make sure your `AiiDA`_ virtual environment is activated, and computer(here is ``cluster``) and code(here is ``shengbte``) have installed correctly.

1. example code::

    """Run a test calculation."""
    from os import path
    from aiida import engine
    from aiida.plugins import DataFactory, WorkflowFactory
    from aiida.orm import Code, Dict, StructData
    from ase.io.vasp import read_vasp
    import logging
    logging.basicConfig(level=logging.INFO)

    INPUT_DIR = path.join(path.dirname(path.realpath(__file__)), 'input_files')

    shengbte_code = Code.get_from_string('shengbte@mycluster')
    # set up calculation
    SinglefileData = DataFactory('singlefile')
    FORCE_CONSTANTS_2ND = SinglefileData(file=path.join(
        INPUT_DIR, 'FORCE_CONSTANTS_2ND'),
        filename='FORCE_CONSTANTS_2ND')
    FORCE_CONSTANTS_3RD = SinglefileData(file=path.join(
        INPUT_DIR, 'FORCE_CONSTANTS_2ND'),
        filename='FORCE_CONSTANTS_3RD')
    inputs = {
        'structure': StructData().set_ase(read_vasp(path.join(INPUT_DIR, 'POSCAR'))),
        'control': Dict(dict={
            'allocations': {
                'ngrid': [12, 12, 12],
                'norientations': 3
            },
            'crystal': {
                'lfactor': 0.6059141,
                'epsilon': [
                    [19.643, 0, 0],
                    [0, 19.643, 0],
                    [0, 0, 19.643]
                ],
                'born': [
                    [
                        [2.67810, 0, 0],
                        [0, 2.67810, 0],
                        [0, 0, 2.67810]
                    ],
                    [
                        [-2.67558, 0, 0],
                        [0, -2.67558, 0],
                        [0, 0, -2.67558]
                    ]
                ]
                'orientations': [
                    [1, 1, 1],
                    [0, 1, 1],
                    [0, 0, 1]
                ],
                'scell': [5, 5, 5]
            },
            'parameters': {
                'T': 300,
                'scalebroad': 1.0
            },
            'flags': {
                'nonanalytic': True,
                'nanowires': True
            }
        }),
        'calculation': {
            'code': shengbte_code,
            'FORCE_CONSTANTS_2ND': FORCE_CONSTANTS_2ND,
            'FORCE_CONSTANTS_3RD': FORCE_CONSTANTS_3RD,
        },
        'clean_workdir': orm.Bool(False),
        'metadata': {
            'description': "Test job submission with the aiida_shengbte thirdorder plugin",
            'resources' : {'num_machines': 1, 'num_mpiprocs_per_machine': 16}
        },
    }
    logging.error(inputs)
    result = engine.run(WorkflowFactory('shengbte.shengbte'), **inputs)
    logging.info(result)

2. check that the daemon is running::

    $ verdi daemon status

3. Have a look at the ``run_test.py`` file and see if you can intuitively understand what it does. Most likely, you need to modify the following entries::

    shengbte_code = Code.get_from_string('shengbte@mycluster')
    resources = {'num_machines': 1, 'num_mpiprocs_per_machine': 16}
    # modify StructData if need

4. Submit the `ShengBTE`_ calculation by executing::

    verdi run_test.py
    # or
    # python run_test.py

.. _AiiDA: https://www.aiida.net
.. _ShengBTE: http://www.shengbte.org/
.. _Thirdorder: https://bitbucket.org/sousaw/thirdorder/
.. _Spglib: https://spglib.github.io/spglib/