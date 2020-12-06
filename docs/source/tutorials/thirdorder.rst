.. _thirdorder:

====================================
Thirdorder Calculation and WorkChain
====================================

This page can contain a tutorial for `ThirdorderSowCalculation`, `ThirdorderReapCalculation` and `ThirdorderWorkChain`. You usually run `ThirdorderWorkChain`_ to calculate force_constants_3rd, instead of running 
respectively.

ThirdorderSowCalculation
++++++++++++++++++++++++

.. aiida-calcjob:: ThirdorderSowCalculation
    :module: aiida_shengbte.calculations.thirdorder

ThirdorderReapCalculation
+++++++++++++++++++++++++

.. aiida-calcjob:: ThirdorderReapCalculation
    :module: aiida_shengbte.calculations.thirdorder

.. _ThirdorderWorkChain:

ThirdorderWorkChain
+++++++++++++++++++

See ``examples/example_thirdorder.py`` in repository.

.. aiida-workchain:: ThirdorderWorkChain
    :module: aiida_shengbte.workflows.thirdorder
