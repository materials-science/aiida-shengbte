.. _vasp_shengbte:

========================================
ShengBTE Calculation with VASP Interface
========================================

This page can contain a tutorial for `ShengBTEVaspWorkChain`. It will use `VASP`_ to calculate ``FORCE CONSTANTS`` and other parameters `ShengBTE`_ requires.

Example
+++++++

1. required code setup

2. upload vasp potential

3. run example code in ``examples/example_vasp.py``

ShengBTEVaspWorkChain
+++++++++++++++++++

See ``examples/example_vasp.py`` in repository.

.. aiida-workchain:: ShengBTEVaspWorkChain
    :module: aiida_shengbte.workflows.vasp

.. _AiiDA: https://www.aiida.net
.. _ShengBTE: http://www.shengbte.org/
.. _ShengBTE wiki: http://www.shengbte.org/documentation
.. _VASP: https://www.vasp.at