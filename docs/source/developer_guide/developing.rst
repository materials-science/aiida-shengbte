================
Under developing
================

Schedules
+++++++++

Test
----

- [ ] Test current Calculations
    - [ ] Thirdorder Sow
    - [ ] Thirdorder Reap
    - [ ] ShengBTE Calculation

- [ ] Test current Workflows
    - [ ] Thirdorder WorkChain
    - [ ] ShengBTE WorkChain
    - [ ] ShengBTE Vasp WorkChain

Features
--------

- [ ] ShengBTE Vasp WorkChain
    - [ ] Covergence criterion
    - [ ] set potential_mapping for vasp automatically
    - [ ] set proper parameters of phonopy and vasp
- [ ] ShengBTE QE WorkChain
- [ ] tools
    - [ ] transform `control dict` file to ShengBTE `CONTROL` file or reversely

Issues
++++++

ShengBTE Vasp WorkChain
-----------------------

Bugs
~~~~

1. Vasp failed with code 7 when 'tot_num_mpiprocs' set to 30
2. ShengBTEVaspWorkflow cannot run correctly while using `submit` rather than `run`. (some Vasp calcs failed and exited)


ThirdOrder Reap Calculation
---------------------------

Error handle
~~~~~~~~~~~~

1. Warning: supercell too small to find n-th neighbours