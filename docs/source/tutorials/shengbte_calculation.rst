.. _shengbte_calculation:

=======================================
Base Shengbte Calculation and WorkChain
=======================================

This page can contain a tutorial for `ShengbteCalculation` and `ShengbteWorkChain`.

ShengbteCalculation
+++++++++++++++++++

If you already have ``CONTROL``, ``FORCE_CONSTANTS_2ND`` and ``FORCE_CONSTANTS_2ND``, just construct a ``control`` in `Dict` type and transfer ``FORCE_CONSTANTS`` files to `SinglefileData` and run ShengbteCalculation. See ``examples/example_base.py`` in repository.

.. aiida-calcjob:: ShengbteCalculation
    :module: aiida_shengbte.calculations.shengbte

ShengbteWorkChain
+++++++++++++++++

By passing StructureData to `ShengbteWorkChain`, you don't need set some parameters in ``control``. The optinal parameters you may set are::

    _CONTROL_OPTIONAL = {
        'allocations': ['ngrid', 'norientations'],
        'crystal': ['orientations', 'masses', 'gfactors', 'scell', 'born', 'epsilon', 'lfactor'],
        'parameters': ['T', 'T_min', 'T_max', 'T_step', 'omega_max', 'scalebroad', 'rmin', 'rmax', 'dr', 'maxiter', 'nticks', 'eps'],
        'flag': ['espresso', 'nonanalytic', 'convergence', 'isotopes', 'autoisotopes', 'nanowires', 'onlyharmonic']
    }

See ``examples/example_shengbte_workflow.py`` in repository.

.. aiida-workchain:: ShengbteWorkChain
    :module: aiida_shengbte.workflows.shengbte
