[![Build Status](https://github.com/PorYoung/aiida-shengbte/workflows/ci/badge.svg?branch=master)](https://github.com/PorYoung/aiida-shengbte/actions)
[![Coverage Status](https://coveralls.io/repos/github/PorYoung/aiida-shengbte/badge.svg?branch=master)](https://coveralls.io/github/PorYoung/aiida-shengbte?branch=master)
[![Docs status](https://readthedocs.org/projects/aiida-shengbte/badge)](http://aiida-shengbte.readthedocs.io/)
[![PyPI version](https://badge.fury.io/py/aiida-shengbte.svg)](https://badge.fury.io/py/aiida-shengbte)

# aiida-shengbte

aiida plugin for ShengBTE

This plugin is the default output of the
[AiiDA plugin cutter](https://github.com/aiidateam/aiida-plugin-cutter),
intended to help developers get started with their AiiDA plugins.

## Repository contents

-   [`.github/`](.github/): [Github Actions](https://github.com/features/actions) configuration
    -   [`ci.yml`](.github/workflows/ci.yml): runs tests, checks test coverage and builds documentation at every new commit
    -   [`publish-on-pypi.yml`](.github/workflows/publish-on-pypi.yml): automatically deploy git tags to PyPI - just generate a [PyPI API token](https://pypi.org/help/#apitoken) for your PyPI account and add it to the `pypi_token` secret of your github repository
-   [`aiida_shengbte/`](aiida_shengbte/): The main source code of the plugin package
    -   [`data/`](aiida_shengbte/data/): A new `DiffParameters` data class, used as input to the `DiffCalculation` `CalcJob` class
    -   [`calculations.py`](aiida_shengbte/calculations.py): A new `DiffCalculation` `CalcJob` class
    -   [`cli.py`](aiida_shengbte/cli.py): Extensions of the `verdi data` command line interface for the `DiffParameters` class
    -   [`helpers.py`](aiida_shengbte/helpers.py): Helpers for setting up an AiiDA code for `diff` automatically
    -   [`parsers.py`](aiida_shengbte/parsers.py): A new `Parser` for the `DiffCalculation`
-   [`docs/`](docs/): A documentation template ready for publication on [Read the Docs](http://aiida-diff.readthedocs.io/en/latest/)
-   [`examples/`](examples/): An example of how to submit a calculation using this plugin
-   [`tests/`](tests/): Basic regression tests using the [pytest](https://docs.pytest.org/en/latest/) framework (submitting a calculation, ...). Install `pip install -e .[testing]` and run `pytest`.
-   [`.coveragerc`](.coveragerc): Configuration of [coverage.py](https://coverage.readthedocs.io/en/latest) tool reporting which lines of your plugin are covered by tests
-   [`.gitignore`](.gitignore): Telling git which files to ignore
-   [`.pre-commit-config.yaml`](.pre-commit-config.yaml): Configuration of [pre-commit hooks](https://pre-commit.com/) that sanitize coding style and check for syntax errors. Enable via `pip install -e .[pre-commit] && pre-commit install`
-   [`.readthedocs.yml`](.readthedocs.yml): Configuration of documentation build for [Read the Docs](https://readthedocs.org/)
-   [`LICENSE`](LICENSE): License for your plugin
-   [`MANIFEST.in`](MANIFEST.in): Configure non-Python files to be included for publication on [PyPI](https://pypi.org/)
-   [`README.md`](README.md): This file
-   [`conftest.py`](conftest.py): Configuration of fixtures for [pytest](https://docs.pytest.org/en/latest/)
-   [`pytest.ini`](pytest.ini): Configuration of [pytest](https://docs.pytest.org/en/latest/) test discovery
-   [`setup.json`](setup.json): Plugin metadata for registration on [PyPI](https://pypi.org/) and the [AiiDA plugin registry](https://aiidateam.github.io/aiida-registry/) (including entry points)
-   [`setup.py`](setup.py): Installation script for pip / [PyPI](https://pypi.org/)

See also the following video sequences from the 2019-05 AiiDA tutorial:

-   [aiida-diff setup.json](https://www.youtube.com/watch?v=2CxiuiA1uVs&t=240s)
-   [run aiida-diff example calculation](https://www.youtube.com/watch?v=2CxiuiA1uVs&t=403s)
-   [aiida-diff CalcJob plugin](https://www.youtube.com/watch?v=2CxiuiA1uVs&t=685s)
-   [aiida-diff Parser plugin](https://www.youtube.com/watch?v=2CxiuiA1uVs&t=936s)
-   [aiida-diff computer/code helpers](https://www.youtube.com/watch?v=2CxiuiA1uVs&t=1238s)
-   [aiida-diff input data (with validation)](https://www.youtube.com/watch?v=2CxiuiA1uVs&t=1353s)
-   [aiida-diff cli](https://www.youtube.com/watch?v=2CxiuiA1uVs&t=1621s)
-   [aiida-diff tests](https://www.youtube.com/watch?v=2CxiuiA1uVs&t=1931s)
-   [Adding your plugin to the registry](https://www.youtube.com/watch?v=760O2lDB-TM&t=112s)
-   [pre-commit hooks](https://www.youtube.com/watch?v=760O2lDB-TM&t=333s)

For more information, see the [developer guide](https://aiida-diff.readthedocs.io/en/latest/developer_guide) of your plugin.

## Features

-   Add input files using `SinglefileData`:

    ```python
    SinglefileData = DataFactory('singlefile')
    inputs['file1'] = SinglefileData(file='/path/to/file1')
    inputs['file2'] = SinglefileData(file='/path/to/file2')
    ```

-   Specify command line options via a python dictionary and `DiffParameters`:

    ```python
    d = { 'ignore-case': True }
    DiffParameters = DataFactory('shengbte')
    inputs['parameters'] = DiffParameters(dict=d)
    ```

-   `DiffParameters` dictionaries are validated using [voluptuous](https://github.com/alecthomas/voluptuous).
    Find out about supported options:

    ```python
    DiffParameters = DataFactory('shengbte')
    print(DiffParameters.schema.schema)
    ```

-   [ ] ShengBTE Vasp WorkChain
    -   [ ] Covergence criterion
    -   [ ] set potential_mapping for vasp automatically
    -   [ ] set proper parameters of phonopy and vasp
-   [ ] ShengBTE QE WorkChain
-   [ ] tools
    -   [ ] transform `control dict` file to ShengBTE `CONTROL` file or reversely

## Installation

```shell
pip install aiida-shengbte
verdi quicksetup  # better to set up a new profile
verdi plugin list aiida.calculations  # should now show your calclulation plugins
```

### ShengBTE

[ShengBTE 软件编译方法](https://yh-phys.github.io/2020/09/04/ShengBTE-install/)

## Usage

Here goes a complete example of how to submit a test calculation using this plugin.

A quick demo of how to submit a calculation:

```shell
verdi daemon start     # make sure the daemon is running
cd examples
./example_01.py        # run test calculation
verdi process list -a  # check record of the calculation
```

The plugin also includes verdi commands to inspect its data types:

```shell
verdi data shengbte list
verdi data shengbte export <PK>
```

## Notes

```shell
git clone https://github.com/PorYoung/aiida-shengbte .
cd aiida-shengbte
pip install -e .[pre-commit,testing]  # install extra dependencies
pre-commit install  # install pre-commit hooks
pytest -v  # discover and run all tests
```

### input

dict validator

```py
_CONTROL = {
    'allocations': {
        'nelements': {
            'type': int,
            'mandatory': True
        },
        'natoms': {
            'type': int,
            'mandatory': True
        },
        'ngrid': {
            # <len 3>
            'type': list,
            'mandatory': True
        },
        'norientations': {
            'type': int,
            'default': 0
        }
    },
    'crystal': {
        'lfactor': {
            'type': float,
            'default': 1.0
        },
        'lattvec': {
            # <3*3>
            'type': list,
            'mandatory': True
        },
        'types': {
            # <len natoms>
            'type': list,
            'mandatory': True
        },
        'elements': {
            # <len nelements>
            'type': list,
            'mandatory': True
        },
        'positions': {
            # <3 * natoms>
            'type': list,
            'mandatory': True
        },
        'masses': {
            'type': float
        },
        'gfactors': {
            'type': float
        },
        'epsilon': {
            # <3 * 3>
            'type': list,
        },
        'born': {
            # <3 * 3 * natoms>
            'type': list,
        },
        'scell': {
            # <len 3>
            'type': list,
            'mandatory': True
        },
        'orientations': {
            # <3 * norientations> mandatory unless norientations == 0
            'type': list,
            # 'mandatory': True
        }
    },
    'parameters': {
        'T': {},
        'T_min': {},
        'T_max': {},
        'T_step': {},
        'omega_max': {
            'default': 1.e100
        },
        'scalebroad': {
            'default': 1.0
        },
        'rmin': {
            'default': 5.0
        },
        'rmax': {
            'default': 505.0
        },
        'dr': {
            'default': 100.0
        },
        'maxiter': {
            'default': 1000
        },
        'nticks': {
            'default': 100
        },
        'eps': {
            'default': 1.e-5
        },
    },
    'flags': {
        'nonanalytic': {
            'default': True
        },
        'convergence': {
            'default': True
        },
        'isotopes': {
            'default': True
        },
        'autoisotopes': {
            'default': True
        },
        'nanowires': {
            'default': False
        },
        'onlyharmonic': {
            'default': False
        },
        'espresso': {
            'default': False
        }
    }
}
```

#### Retrieve List

[About Retrieve List of CalcJob](https://aiida.readthedocs.io/projects/aiida-core/en/latest/_modules/aiida/common/datastructures.html?highlight=retrieve_list#)

##### Exit code conventions

-   0 - 99: Reserved for internal use by aiida-core

-   100 - 199: Reserved for errors parsed from scheduler output of calculation jobs (note: this is not yet implemented)

-   200 - 299: Suggested to be used for process input validation errors

-   300 - 399: Suggested for critical process errors

-   For any other exit codes, one can use the integers from 400 and up.

See the [developer guide](http://aiida-shengbte.readthedocs.io/en/latest/developer_guide/index.html) for more information.

#### Phonopy Workflow

##### Installation

1. aiida container

    ```py

    ```

2. vasp container(or other remote container)
    1. clone phono3py repository
    1. create `setup_mkl.py` file in phono3py repository
    1. `pip install -e .`

##### Inputs

##### Outputs

1. force_constants

    - type: `ArrayData`
    - `get_array('force_constants')` return force constants array
    - `get_array(p2s_map)`
    - `phonopy.fileIO.write_FORCE_CONSTANTS( force_constants, filename='FORCE_CONSTANTS', p2s_map=None,)`

2. nac_params
    - type: `ArrayData`
    - `get_array('epsilon')`
    - `get_array('born_charges')`

#### ThirdOrder

##### Inputs

-   VASP
    1. require `POSCAR`
    2. `PhonopyWorkChainNode.outputs.primitive.get_ase()` return ase Atom Object
    3. `ase.write('POSCAR','vasp')`

##### Outputs

## Issues

1. ShengBTE 真实环境计算流程（如改变温度）
2. 计算结果的存储

    - 分别就地存储
    - [x] retrieve all results by aiida

3. Get the real path of nodes in aiida

[ref](https://aiida.readthedocs.io/projects/aiida-core/en/latest/_modules/aiida/backends/general/migrations/utils.html?highlight=repository#)

```py
def get_node_repository_sub_folder(uuid):
    """Return the absolute path to the sub folder `path` within the repository of the node with the given UUID.

    :param uuid: UUID of the node
    :return: absolute path to node repository folder, i.e `/some/path/repository/node/12/ab/c123134-a123/path`
    """
    from aiida.manage.configuration import get_profile

    uuid = str(uuid)

    repo_dirpath = os.path.join(get_profile().repository_path, 'repository')
    node_dirpath = os.path.join(repo_dirpath, 'node', uuid[:2], uuid[2:4], uuid[4:], 'path')

    return node_dirpath
```

### ShengBTE Vasp WorkChain

#### Bugs

1. Vasp failed with code 7 when 'tot_num_mpiprocs' set to 30
2. ShengBTEVaspWorkflow cannot run correctly while using `submit` rather than `run`. (some Vasp calculations failed and exited)

    After submitting the workflow, all the calculations will start at the same time using the number of processes defined, so some will crash. So if the hpc has a job management system such as Torque or has sufficient processes, it would be ok.

### ThirdOrder Reap Calculation

#### Error handle

1. Warning: supercell too small to find n-th neighbors

## Schedules

### Test

-   [ ] Test current Calculations

    -   [ ] Thirdorder Sow
    -   [ ] Thirdorder Reap
    -   [ ] ShengBTE Calculation

-   [ ] Test current Workflows
    -   [ ] Thirdorder WorkChain
    -   [ ] ShengBTE WorkChain
    -   [ ] ShengBTE Vasp WorkChain

## License

MIT

## Contact

poryoung@outlook.com
