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

## Installation

```shell
pip install aiida-shengbte
verdi quicksetup  # better to set up a new profile
verdi plugin list aiida.calculations  # should now show your calclulation plugins
```

## Usage

Here goes a complete example of how to submit a test calculation using this plugin.

A quick demo of how to submit a calculation:

```shell
verdi daemon start     # make sure the daemon is running
cd examples
./example_01.py        # run test calculation
verdi process list -a  # check record of calculation
```

The plugin also includes verdi commands to inspect its data types:

```shell
verdi data shengbte list
verdi data shengbte export <PK>
```

## Development

```shell
git clone https://github.com/PorYoung/aiida-shengbte .
cd aiida-shengbte
pip install -e .[pre-commit,testing]  # install extra dependencies
pre-commit install  # install pre-commit hooks
pytest -v  # discover and run all tests
```

### input

```py
{
    "allocations": {
        "nelements": (integer, mandatory),
        "natoms": (integer, mandatory),
        "ngrid": (integer, 3, mandatory),
        "norientations": (integer, default=0)
    },
    "crystal":{
        "lfactor": (real, nm, default=1.0),
        "lattvec": (real, 3 x 3, mandatory),
        "types": (integer, natoms, mandatory),
        "elements": (string, nelements, mandatory),
        "positions": (real, 3 x natoms, mandatory),
        "masses": (real, nelements, g/mol, default=automatic),
        "gfactors": (real, nelements, default=automatic),
        "epsilon": (real, 3 x 3, &Epsilon;<sub>0</sub>, default=1),
        "born": (real, 3 x 3 x natoms, e, default=0),
        "scell": (integer, 3, mandatory),
        "orientations": (integer, 3 x norientations, mandatory unless norientations==0)
    },
    "parameters":{
        "T": (real, K),
        # T_min,T_max,T_step (real, K)
        "omega_max": (real, rad/ps, default=1.e100),
        "scalebroad": (real, default=1.0),
        "rmin": (real, nm, default=5.0),
        "rmax": (real, nm, default=505.0),
        "dr": (real, nm, default=100.0),
        "maxiter": (integer, default=1000),
        "nticks": (integer, default=100),
        "eps": (real, default=10<sup>-5</sup>)
    },
    "flags": {
        "nonanalytic": (logical, default=.true.),
        "convergence": (logical, default=.true.),
        "isotopes": (logical, default=.true.),
        "autoisotopes": (logical, default=.true.),
        "nanowires": (logical, default=.false.),
        "onlyharmonic": (logical, default=.false.),
        "espresso": (logical, default=.false.)
    }
}
```

### dev docs

#### Exit code conventions

-   0 - 99: Reserved for internal use by aiida-core

-   100 - 199: Reserved for errors parsed from scheduler output of calculation jobs (note: this is not yet implemented)

-   200 - 299: Suggested to be used for process input validation errors

-   300 - 399: Suggested for critical process errors

-   For any other exit codes, one can use the integers from 400 and up.

See the [developer guide](http://aiida-shengbte.readthedocs.io/en/latest/developer_guide/index.html) for more information.

## License

MIT

## Contact

poryoung@outlook.com
