from aiida.engine import CalcJob
from aiida import orm
from aiida.common import datastructures
from aiida_shengbte.parsers.data_parser.control_parser import ControlParser
import os


class ShengbteCalculation(CalcJob):
    """[summary]

    Args:
        CalcJob ([type]): [description]

    Returns:
        [type]: [description]
    """
    _OUTPUT_SUBFOLDER = './shengbte/'
    _PREFIX = 'aiida'
    _DEFAULT_INPUT_FILE = 'aiida.in'
    _DEFAULT_OUTPUT_FILE = 'aiida.out'
    _DEFAULT_METADATA_RESOURCES = {
        'num_machines': 1,
        'num_mpiprocs_per_machine': 1,
    }

    @classmethod
    def define(cls, spec):
        """
        docstring
        """
        super(ShengbteCalculation, cls).define(spec)

        # set default values for AiiDA options
        spec.inputs['metadata']['options']['parser_name'].default = 'shengbte'

        # input parameters for shengbte
        spec.input('control',
                   valid_type=orm.Dict,
                   help='Parameters in CONTROL file of ShengBTE')
        spec.input('FORCE_CONSTANTS_2ND',
                   valid_type=orm.SinglefileData,
                   help='FORCE_CONSTANTS file of Phonopy or espresso.ifc2')
        spec.input('FORCE_CONSTANTS_3ND',
                   valid_type=orm.SinglefileData,
                   help='third-order interatomic force constant matrix')

        # optinal parameters for calculation
        spec.input('metadata.options.input_filename',
                   valid_type=str, default=cls._DEFAULT_INPUT_FILE)
        spec.input('metadata.options.output_filename',
                   valid_type=str, default=cls._DEFAULT_OUTPUT_FILE)
        spec.input('metadata.options.withmpi',
                   valid_type=bool,
                   default=False,
                   help='Run with mpi.')
        spec.input('metadata.options.resources',
                   valid_type=dict,
                   default=cls._DEFAULT_METADATA_RESOURCES,
                   help='resources designated for calculation.')
        spec.input('metadata.dry_run',
                   valid_type=bool,
                   required=False,
                   default=False,
                   non_db=True,
                   help='Dry run without submission for test')
        spec.input('metadata.store_provenance',
                   valid_type=bool,
                   required=False,
                   default=True,
                   non_db=True,
                   help='Set False to unable creating nodes')
        spec.input('clean_workdir',
                   valid_type=orm.Bool,
                   required=False,
                   default=lambda: orm.Bool(False),
                   help="""
            If True, clean the work dir upon the completion of a successfull calculation.
            """)

        # TODO(poryoung): to develop a interface for handle outputs of vasp or qe or just restart from itself
        spec.input('parent_folder',
                   valid_type=orm.RemoteData,
                   required=False,
                   help='An optional working directory of a previously completed calculation.')

        # TODO(poryoung): set to not mandatory out port
        spec.output('out_path')
        # start exit codes - marker for docs
        spec.exit_code(201,
                       'ERROR_KEY_IN_INPUT',
                       message='The key inputed is invalid.')
        spec.exit_code(202,
                       'ERROR_TYPE_IN_INPUT',
                       message='The type of value inputed is invalid.')
        spec.exit_code(310,
                       'ERROR_READING_OUTPUT_FILE',
                       message='The output file could not be read.')
        spec.exit_code(320,
                       'ERROR_INVALID_OUTPUT',
                       message='The output file contains invalid output.')

    def prepare_for_submission(self, tempfolder):
        self.control_parser = ControlParser(self.inputs.control.get_dict(), self.logger)
        try:
            self.control_parser.validate_input()
        except RuntimeError as err:
            return self.exit_codes[str(err)] if str(err) in self.exit_codes.keys() else self.logger.error(err)

        folder = tempfolder.get_subfolder(self._OUTPUT_SUBFOLDER, create=True)

        control_dst = folder.get_abs_path("CONTROL")
        try:
            self.control_parser.write_control(control_dst)
        except RuntimeError:
            return self.exit_codes.ERROR_KEY_IN_INPUT

        codeinfo = datastructures.CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.cmdline_params = [
            '-c',
            "/home/por/miniconda3/envs/aiida_shengbte/bin/python /home/por/aiida/aiida-shengbte/examples/test_code.py"
        ]
        # codeinfo.stdin_name = self.options.input_filename
        codeinfo.stdout_name = self.options.output_filename
        codeinfo.withmpi = self.inputs.metadata.options.withmpi

        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        # TODO check compatibility of FORCE_CONSTANTS_2ND and CONTROL
        calcinfo.local_copy_list = [
            (self.inputs.FORCE_CONSTANTS_2ND.uuid,
             self.inputs.FORCE_CONSTANTS_2ND.filename,
             self.get_remote_relative_path(self.inputs.FORCE_CONSTANTS_2ND.filename)),
            (self.inputs.FORCE_CONSTANTS_3ND.uuid,
             self.inputs.FORCE_CONSTANTS_3ND.filename,
             self.get_remote_relative_path(self.inputs.FORCE_CONSTANTS_3ND.filename)),
        ]
        # calcinfo.retrieve_list = [self.options.output_filename]
        calcinfo.retrieve_list = [self.options.output_filename, ('shengbte/BTE.*', '.', 2), ('shengbte/T*K', '.', 2)]

        return calcinfo

    def on_terminated(self):
        """Clean remote folders of the calculations called in the workchain if the clean_workdir input is True."""

        super(ShengbteCalculation, self).on_terminated()  # pylint: disable=no-member
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

    def get_remote_relative_path(self, path):
        return os.path.join(self._OUTPUT_SUBFOLDER, path)
