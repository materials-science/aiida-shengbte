# !/usr/bin/env python
"""Run a test calculation on localhost.

Usage: ./example_01.py
"""
from os import path
from aiida_shengbte import helpers
from aiida import cmdline, engine, orm
from aiida.plugins import DataFactory, CalculationFactory
import click
import logging
logging.basicConfig(level=logging.INFO)

INPUT_DIR = path.join(path.dirname(path.realpath(__file__)), 'input_files')


def test_run(thirdorder_reap_code):
    """Run a calculation on the localhost computer.

    Uses test helpers to create AiiDA Code on the fly.
    """
    if not thirdorder_reap_code:
        # get code
        computer = helpers.get_computer(name='vasp', workdir='/workdir/aiida/')
        thirdorder_reap_code = helpers.get_code(
            entry_point='thirdorder_vasp_reap', computer=computer, prepend_text='find job.* -name vasprun.xml|sort -n|')

    from aiida.orm import load_node
    from aiida.orm.nodes.data.folder import FolderData
    thirdorder_sow = load_node(1999)
    vasp_works = [load_node(i) for i in range(2080, 2760, 10)]

    tempfolder = FolderData()
    try:
        for calc in vasp_works:
            # e.g. "3RD.POSCAR.01"
            num = calc.label.split('.')[-1]
            label = f'vasp_force_calc_{num}'
            with calc.outputs.retrieved.open('vasprun.xml') as handle:
                tempfolder.put_object_from_filelike(handle, f'{num}')
    except OSError:
        return logging.error('ERROR_READING_VASPRUN_XML_FILE')
    except (ValueError, TypeError):
        return logging.error('ERROR_PARSING_VASPRUN_XML_FAILED')

    # set up calculation
    inputs = {
        'code': thirdorder_reap_code,
        'structure': helpers.get_test_structure(),
        'vasp_folder': tempfolder,
        'supercells_folder': thirdorder_sow.outputs.retrieved,
        'parameters': orm.Dict(dict={
            'supercell_matrix': [3, 3, 3],
            'option': 3
        }),
        # 'clean_workdir': orm.Bool(True),
        'metadata': {
            'description': "Test job submission with the aiida_shengbte plugin",
            # 'dry_run': True,
        },
    }
    result = engine.run(CalculationFactory(
        'shengbte.thirdorder_reap'), **inputs)

    logging.info(result)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
def cli(code):
    """Run example.

    Example usage: $ ./example_01.py -- code diff@localhost

    Alternative (creates diff@localhost-test code): $ ./example_01.py

    Help: $ ./example_01.py -- help
    """
    test_run(code)


if __name__ == '__main__':
    cli()  # pylint: disable = no-value-for-parameter
