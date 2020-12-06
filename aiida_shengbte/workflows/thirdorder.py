from aiida.orm import Dict, StructureData
from aiida.common import AttributeDict
from aiida.engine import ToContext
from aiida.plugins.factories import CalculationFactory
from aiida_shengbte.workflows import BaseWorkChain
ThirdorderSowCalculation = CalculationFactory('shengbte.thirdorder_sow')
ThirdorderReapCalculation = CalculationFactory('shengbte.thirdorder_reap')


def validate_inputs(inputs, ctx=None):  # pylint: disable=unused-argument
    """Validate the inputs of the entire input namespace."""


class ThirdorderWorkChain(BaseWorkChain):
    """Thirdorder WorkChain to run both ThirdorderSow Calculation and ThirdorderReap Calculation.
    """
    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.expose_inputs(ThirdorderSowCalculation, namespace='thirdorder_sow', exclude=('structure',))
        spec.expose_inputs(ThirdorderReapCalculation, namespace='thirdorder_reap',
                           exclude=('vasp_folder', 'supercells_folder',))
        spec.input('structure', valid_type=StructureData)
        # TODO: add quantumrespresso support
        spec.input('vasp_settings', valid_type=Dict)

        spec.outline(
            cls.setup,
            cls.run_thirdorder_sow,
            cls.inspect_thirdorder_sow,
            cls.run_vasp,
            cls.run_thirdorder_reap
        )
        spec.output('FORCE_CONSTANTS_3RD')
        spec.exit_code(201, 'ERROR_READING_SUPERCELL_FILE',
                       message='Failed to read supercell file from thirdorder_sow outputs.')
        spec.exit_code(202, 'ERROR_PARSING_SUPERCELL_FAILED',
                       message='Failed to parse supercell data from thirdorder_sow outputs.')
        spec.exit_code(203, 'ERROR_READING_VASPRUN_XML_FILE',
                       message='Failed to read vasprun.xml file from vasp outputs.')
        spec.exit_code(203, 'ERROR_PARSING_VASPRUN_XML_FAILED',
                       message='Failed to parse vasprun.xml file from vasp outputs.')
        spec.exit_code(401, 'ERROR_SUB_PROCESS_FAILED_THIRDORDER_SOW',
                       message='The thirdorder sow Calculation sub process failed')

    def setup(self):
        """Define the current structure in the context to be the input structure."""
        self.ctx.current_structure = self.inputs.structure

    def run_thirdorder_sow(self):
        inputs = AttributeDict(self.exposed_inputs(
            ThirdorderSowCalculation, namespace='thirdorder_sow'))
        inputs.metadata.call_link_label = 'thirdorder_sow'
        inputs.structure = self.ctx.current_structure

        running = self.submit(ThirdorderSowCalculation, **inputs)

        self.report('launching Thirdorder Sow Calculation<{}>'.format(running.pk))

        return ToContext(calculation_thirdorder_sow=running)

    def inspect_thirdorder_sow(self):
        calculation = self.ctx.calculation_thirdorder_sow

        if not calculation.is_finished_ok:
            self.report('Thirdorder sow failed with exit status {}'.format(calculation.exit_status))
            return self.exit_codes.ERROR_SUB_PROCESS_FAILED_THIRDORDER_SOW

        self.ctx.supercells_folder = calculation.outputs.retrieved
        from ase.io.vasp import read_vasp

        self.ctx.supercells = {}
        try:
            for supercell_name in self.ctx.supercells_folder.list_object_names():
                if supercell_name.find('3RD.POSCAR') == -1:
                    continue
                supercell = StructureData()
                with self.ctx.supercells_folder.open(supercell_name) as handle:
                    supercell.set_ase(read_vasp(handle))
                self.ctx.supercells[supercell_name] = supercell
        except OSError:
            return self.exit_codes.ERROR_READING_SUPERCELL_FILE
        except (ValueError, TypeError):
            return self.exit_codes.ERROR_PARSING_SUPERCELL_FAILED

    def run_vasp(self):
        from aiida_phonopy.common.builders import get_calcjob_builder
        for key in self.ctx.supercells:
            builder = get_calcjob_builder(self.ctx.supercells[key],
                                          self.inputs.vasp_settings,
                                          calc_type='forces',
                                          label=key)
            future = self.submit(builder)
            label = f'vasp_force_calc_{key.split(".")[-1]}'
            self.report('{} pk = {}'.format(label, future.pk))
            self.to_context(**{label: future})

    def inspect_vasp(self):
        self.report('collecting vasprun.xml files.')
        from aiida.orm.nodes.data.folder import FolderData
        # TODO: use a more efficient way to handle multiple vasprun.xml data
        tempfolder = FolderData()
        try:
            for key in self.ctx.supercells:
                # e.g. "3RD.POSCAR.01"
                num = key.split('.')[-1]
                label = f'vasp_force_calc_{num}'
                calc = self.ctx[label]
                with calc.outputs.retrieved.open('vasprun.xml') as handle:
                    tempfolder.put_object_from_filelike(handle, f'{num}')
        except OSError:
            return self.exit_codes.ERROR_READING_VASPRUN_XML_FILE
        except (ValueError, TypeError):
            return self.exit_codes.ERROR_PARSING_VASPRUN_XML_FAILED
        self.ctx.vasprun_xml_folder = tempfolder

    def run_thirdorder_reap(self):
        inputs = AttributeDict(self.exposed_inputs(
            ThirdorderReapCalculation, namespace='thirdorder_reap'))
        inputs.metadata.call_link_label = 'thirdorder_reap'
        inputs.vasp_folder = self.ctx.vasprun_xml_folder
        inputs.supercells_folder = self.ctx.supercells_folder

        running = self.submit(ThirdorderReapCalculation, **inputs)

        self.report('launching  Thirdorder Reap Calculation<{}>'.format(running.pk))

        return ToContext(calculation_thirdorder_reap=running)

    def inspect_thirdorder_reap(self):
        self.report('output FORCE_CONSTANTS_3RD.')
        self.out('FORCE_CONSTANTS_3RD', self.ctx.calculation_thirdorder_reap.outputs.FORCE_CONSTANTS_3RD)
