from aiida.common import datastructures, exceptions
from aiida.plugins import DataFactory
from aiida_shengbte.calculations import BaseCalculation
StructureData = DataFactory('structure')
SinglefileData = DataFactory('singlefile')
Dict = DataFactory('dict')
FolderData = DataFactory('folder')


class BaseThirdorderCalculation(BaseCalculation):
    """
    A basic plugin for calculating force constants using Thirdorder.
    """

    _DEFAULT_INPUT_FILE = 'POSCAR'
    _DEFAULT_PARAMETERS = {
        'supercell_matrix': [3, 3, 3],
        'option': '-3'
    }

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.inputs['metadata']['options']['withmpi'].default = False

        spec.input('parameters', valid_type=Dict,
                   default=lambda: Dict(cls._DEFAULT_PARAMETERS))
        spec.input('structure', valid_type=StructureData)

        spec.output('out_path')

        spec.exit_code(201, 'ERROR_IN_PARSING_DATA',
                       message='Failed to parse structure data to poscar.')
        spec.exit_code(202, 'ERROR_READING_SUPERCELL_FILE',
                       message='Failed to read supercell file from thirdorder_sow outputs.')
        spec.exit_code(203, 'ERROR_PARSING_SUPERCELL_FAILED',
                       message='Failed to parse supercell data from thirdorder_sow outputs.')
        spec.exit_code(204, 'ERROR_READING_VASPRUN_XML_FILE',
                       message='Failed to read vasprun.xml file from vasp outputs.')
        spec.exit_code(205, 'ERROR_PARSING_VASPRUN_XML_FAILED',
                       message='Failed to parse vasprun.xml file from vasp outputs.')
        spec.exit_code(310, 'ERROR_READING_OUTPUT_FILE',
                       message='The output file could not be read.')
        spec.exit_code(320, 'ERROR_NO_OUTPUT',
                       message='No out files produced, e.g. 3RD.POSCAR.*')
        spec.exit_code(321, 'ERROR_INVALID_OUTPUT',
                       message='The output file contains invalid output.')

    def prepare_for_submission(self, folder):
        dst = folder.get_abs_path(self._DEFAULT_INPUT_FILE)
        try:
            self.inputs.structure.get_ase().write(dst, 'vasp')
        except RuntimeError:
            return self.exit_codes.ERROR_IN_PARSING_DATA


class ThirdorderSowCalculation(BaseThirdorderCalculation):
    """Thirdorder Calculation executing command `thirdorder_<vasp/qe/>.py sow`
    """
    _PREFIX = 'aiida'

    @classmethod
    def define(cls, spec):
        """
        docstring
        """
        super().define(spec)

        # set default values for AiiDA options
        spec.inputs['metadata']['options']['parser_name'].default = 'thirdorder_sow'

        # TODO: Whether to output supercells data
        # spec.output('supercells_folder')
        # start exit codes - marker for docs
        # spec.exit_code(201, 'ERROR_IN_PARSING_DATA',
        #                message='Failed to parse structure data to poscar.')

    def prepare_for_submission(self, folder):
        super().prepare_for_submission(folder)

        cmdline_params = ['sow', ]

        codeinfo = datastructures.CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        cmdline_params.extend(
            [str(i) for i in self.inputs.parameters["supercell_matrix"]])
        cmdline_params.extend([f'-{self.inputs.parameters["option"]}'])
        codeinfo.cmdline_params = cmdline_params
        codeinfo.withmpi = False

        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = []
        calcinfo.retrieve_list = [('3RD.POSCAR.*', '.', 1)]

        return calcinfo


class ThirdorderReapCalculation(BaseThirdorderCalculation):
    """Thirdorder Calculation executing command `thirdorder_<vasp/qe/>.py reap`
    """
    _PREFIX = 'aiida'
    _DEFAULT_OUTPUT_FILE = 'FORCE_CONSTANTS_3RD'

    @classmethod
    def define(cls, spec):
        """
        docstring
        """
        super().define(spec)

        # set default values for AiiDA options
        spec.inputs['metadata']['options']['parser_name'].default = 'thirdorder_reap'

        # input parameters for thirdorder reap
        spec.input('vasp_folder', valid_type=FolderData)
        spec.input('supercells_folder', valid_type=FolderData)

        spec.output('FORCE_CONSTANTS_3RD')

    def prepare_for_submission(self, tempfolder):
        super().prepare_for_submission(tempfolder)

        local_copy_list = []
        cmdline_params = ['reap', ]
        cmdline_params.extend(
            [str(i) for i in self.inputs.parameters["supercell_matrix"]])
        cmdline_params.extend([f'-{self.inputs.parameters["option"]}'])

        codeinfo = datastructures.CodeInfo()
        codeinfo.cmdline_params = cmdline_params
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.withmpi = False

        calcinfo = datastructures.CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.codes_info = [codeinfo]

        # TODO: use a more efficient way to handle multiple vasprun.xml and poscar data
        from aiida.orm.nodes.data.singlefile import SinglefileData
        vasp_folder = self.inputs.vasp_folder
        supercells_folder = self.inputs.supercells_folder
        for name in vasp_folder.list_object_names():
            folder = tempfolder.get_subfolder(f'job.{name}', create=True)
            try:
                with supercells_folder.open(f'3RD.POSCAR.{name}') as handle:
                    with open(folder.get_abs_path('POSCAR'), 'w') as poscar:
                        poscar.write(handle.read())
            except OSError:
                raise exceptions.InternalError(
                    self.exit_codes.ERROR_READING_SUPERCELL_FILE)
            except (ValueError, TypeError) as e:
                raise exceptions.ParsingError(
                    (self.exit_codes.ERROR_PARSING_SUPERCELL_FAILED))
            try:
                with vasp_folder.open(name) as handle:
                    with open(folder.get_abs_path('vasprun.xml'), 'w') as vasprun_xml:
                        vasprun_xml.write(handle.read())
            except OSError:
                raise exceptions.InternalError(
                    self.exit_codes.ERROR_READING_VASPRUN_XML_FILE)
            except (ValueError, TypeError):
                raise exceptions.ParsingError(
                    self.exit_codes.ERROR_PARSING_VASPRUN_XML_FAILED)

        calcinfo.local_copy_list = local_copy_list
        calcinfo.retrieve_list = [self._DEFAULT_OUTPUT_FILE]
        return calcinfo
