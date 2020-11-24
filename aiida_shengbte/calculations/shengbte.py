from aiida.common import AttributeDict
from aiida.engine import CalcJob
from aiida import orm
from aiida.common import datastructures, AIIDA_LOGGER
from aiida_shengbte.parsers.data_parser.control_parser import ControlParser


class ShengbteCalculation(CalcJob):
    """[summary]

    Args:
        CalcJob ([type]): [description]

    Returns:
        [type]: [description]
    """
    """
    # * `mandatory` default false
    """
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
                'mandatory': True
            },
            'types': {
                # <len natoms>
                'mandatory': True
            },
            'elements': {
                # <len nelements>
                'mandatory': True
            },
            'positions': {
                # <3 * natoms>
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
            },
            'born': {
                # <3 * 3 * natoms>
            },
            'scell': {
                # <len 3>
                'mandatory': True
            },
            'orientations': {
                # <3 * norientations> mandatory unless norientations == 0
                'mandatory': True
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

    @classmethod
    def define(cls, spec):
        """
        docstring
        """
        super(ShengbteCalculation, cls).define(spec)
        cls._logger = AIIDA_LOGGER.getChild(cls.__class__.__name__)

        # set default values for AiiDA options
        spec.inputs['metadata']['options']['resources'].default = {
            'num_machines': 1,
            'num_mpiprocs_per_machine': 1,
        }
        spec.inputs['metadata']['options']['parser_name'].default = 'shengbte'
        spec.inputs['metadata']['options'][
            'input_filename'].default = 'aiida.in'
        spec.inputs['metadata']['options'][
            'output_filename'].default = 'aiida.out'

        spec.input('control',
                   valid_type=orm.Dict,
                   help='parameters in CONTROL file of ShengBTE')
        spec.input('FORCE_CONSTANTS_2ND',
                   valid_type=orm.SinglefileData,
                   help='FORCE_CONSTANTS file of Phonopy or espresso.ifc2')
        spec.input('FORCE_CONSTANTS_3ND',
                   valid_type=orm.SinglefileData,
                   help='third-order interatomic force constant matrix')

        spec.input('metadata.dry_run',
                   valid_type=bool,
                   required=False,
                   default=False,
                   non_db=True,
                   help='dry run without submission for test')
        spec.input('metadata.store_provenance',
                   valid_type=bool,
                   required=False,
                   default=True,
                   non_db=True,
                   help='Set False to unable creating nodes')
        spec.input('clean_workdir',
                   valid_type=orm.Bool,
                   required=False,
                   default=orm.Bool(False),
                   help="""
            If True, clean the work dir upon the completion of a successfull calculation.
            """)
        spec.output('result')
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

    def validate_control(self):
        control = AttributeDict(self.inputs.control.get_dict())
        valid_control = {}

        for key, inner in control.items():
            if key not in self._CONTROL:
                self._logger.error(f'key `{key}` is not valid in CONTRL')
                return self.exit_codes.ERROR_KEY_IN_INPUT

            _inner = self._CONTROL[key]
            valid_inner = {}

            for inner_key, attr in inner.items():
                if inner_key not in _inner:
                    self._logger.error(
                        f'key `{inner_key}` is not valid in CONTRL.{key}')
                    return self.exit_codes.ERROR_KEY_IN_INPUT
                _attr = _inner[inner_key]
                if 'type' in _attr and not isinstance(attr, _attr['type']):
                    self._logger.error(
                        f'key `{inner_key}` is not in valid type in CONTRL.{key}'
                    )
                    return self.exit_codes.ERROR_TYPE_IN_INPUT
                valid_inner[inner_key] = attr

            for inner_key in _inner:
                _attr = _inner[inner_key]
                if inner_key not in inner:
                    if 'mandatory' in _attr and _attr['mandatory'] is True:
                        self._logger.error(
                            f'key `{inner_key}` is not in CONTRL.{key}')
                        return self.exit_codes.ERROR_KEY_IN_INPUT
                    if 'default' in _attr:
                        valid_inner[inner_key] = _attr['default']
            valid_control[key] = valid_inner

        # arrange in order
        # ? only available in python version>=3.6
        valid_dict = {}
        for key in self._CONTROL:
            if key not in control:
                self._logger.error(f'key `{key}` is not in CONTRL')
                return self.exit_codes.ERROR_KEY_IN_INPUT
            valid_dict[key] = valid_control[key]

        return valid_dict

    def prepare_for_submission(self, folder):
        self.control_parser = ControlParser(self.inputs.control.get_dict(), self._logger)
        try:
            self.control_parser.validate_input()
        except RuntimeError as err:
            return self.exit_codes[str(err)] if str(err) in self.exit_codes.keys() else self._logger.error(err)

        control_dst = folder.get_abs_path("CONTROL")
        self.report(control_dst)
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
        codeinfo.stdin_name = self.options.input_filename
        codeinfo.stdout_name = self.options.output_filename

        calcinfo = datastructures.CalcInfo()
        calcinfo.codes_info = [codeinfo]
        # todo check compatibility of FORCE_CONSTANTS_2ND and CONTROL
        calcinfo.local_copy_list = [
            (self.inputs.FORCE_CONSTANTS_2ND.uuid,
             self.inputs.FORCE_CONSTANTS_2ND.filename,
             self.inputs.FORCE_CONSTANTS_2ND.filename),
            (self.inputs.FORCE_CONSTANTS_3ND.uuid,
             self.inputs.FORCE_CONSTANTS_3ND.filename,
             self.inputs.FORCE_CONSTANTS_3ND.filename),
        ]
        calcinfo.retrieve_list = [self.options.output_filename]

        return calcinfo

    def on_terminated(self):
        """Clean remote folders of the calculations called in the workchain if the clean_workdir input is True."""

        super(ShengbteCalculation, self).on_terminated()  # pylint: disable=no-member
        # Do not clean if we do not want to or the calculation failed
        if self.node.exit_status or self.inputs.clean_workdir.value is False:
            self.report('not cleaning the remote folders')  # pylint: disable=not-callable
            return

        cleaned_calcs = []
        # try:
        for called_descendant in self.node.called_descendants:
            # self.outputs.remote_folder._clean()
            called_descendant.outputs.remote_folder._clean()
            cleaned_calcs.append(called_descendant.pk)
        # except BaseException:
        #         pass
        if cleaned_calcs:
            self.report('cleaned remote folders of calculations: {}'.format(
                ' '.join(map(str, cleaned_calcs))))  # pylint: disable=not-callable

    def write_control(self, dst, data):
        with open(dst, 'w', encoding='utf8') as handle:
            # impact of order of namelist
            for key in data:
                handle.write(f'${key}\n')
                inner = data[key]
                for inner_key in inner:
                    # todo to write vectors and other types to CONTROL in correct format
                    handle.write(f'\t{inner_key}={inner[inner_key]},\n')
                handle.write('$end\n')
