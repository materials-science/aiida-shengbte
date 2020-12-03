from aiida.orm import Bool
from aiida.common import datastructures
from aiida.plugins import DataFactory
from aiida_shengbte.calculations import BaseCalculation
StructureData = DataFactory('structure')
Dict = DataFactory('dict')
FolderData = DataFactory('folder')


class ThirdorderSowCalculation(BaseCalculation):
    """[summary]

    Args:
        CalcJob ([type]): [description]

    Returns:
        [type]: [description]
    """
    _PREFIX = 'aiida'
    _DEFAULT_INPUT_FILE = 'POSCAR'
    _DEFAULT_PARAMETERS = {
        'supercell_matrix': [3, 3, 3],
        'option': '-3'
    }

    @classmethod
    def define(cls, spec):
        """
        docstring
        """
        super().define(spec)

        # set default values for AiiDA options
        spec.inputs['metadata']['options']['parser_name'].default = 'thirdorder_supercell'
        spec.inputs['metadata']['options']['withmpi'].default = False

        # input parameters for shengbte
        spec.input('structure', valid_type=StructureData)
        spec.input('parameters', valid_type=Dict, default=lambda: Dict(cls._DEFAULT_PARAMETERS))

        spec.output('out_path')
        # TODO: Whether to output supercells data
        # spec.output('supercells_folder')
        # start exit codes - marker for docs
        spec.exit_code(201,
                       'ERROR_IN_PARSING_DATA',
                       message='Failed to parse structure data to poscar.')
        spec.exit_code(310,
                       'ERROR_READING_OUTPUT_FILE',
                       message='The output file could not be read.')
        spec.exit_code(320,
                       'ERROR_NO_OUTPUT',
                       message='No 3RD.POSCAR.* files produced.')
        spec.exit_code(321,
                       'ERROR_INVALID_OUTPUT',
                       message='The output file contains invalid output.')

    def prepare_for_submission(self, folder):
        dst = folder.get_abs_path(self._DEFAULT_INPUT_FILE)
        try:
            self.inputs.structure.get_ase().write(dst, 'vasp')
        except RuntimeError:
            return self.exit_codes.ERROR_IN_PARSING_DATA

        cmdline_params = ['sow', ]

        codeinfo = datastructures.CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        cmdline_params.extend([str(i) for i in self.inputs.parameters["supercell_matrix"]])
        cmdline_params.extend([f'{self.inputs.parameters["option"]}'])
        codeinfo.cmdline_params = cmdline_params
        codeinfo.withmpi = False

        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = []
        calcinfo.retrieve_list = [('3RD.POSCAR.*', '.', 1)]

        return calcinfo

    def on_terminated(self):
        """Clean remote folders of the calculations called in the workchain if the clean_workdir input is True."""

        super(ThirdorderSowCalculation, self).on_terminated()  # pylint: disable=no-member
        # Do not clean if we do not want to or the calculation failed
        if self.node.exit_status or self.inputs.clean_workdir.value is False:
            self.report('not cleaning the remote folders')  # pylint: disable=not-callable
            return

        cleaned_calcs = []
        try:
            self.outputs['remote_folder']._clean()
            cleaned_calcs.append(self.node.pk)
        except BaseException:
            pass
        if cleaned_calcs:
            self.report('cleaned remote folders of calculations: {}'.format(
                ' '.join(map(str, cleaned_calcs))))  # pylint: disable=not-callable
