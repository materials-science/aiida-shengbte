"""
# TODO: To Support Quantum Espresso
"""
from aiida.orm import Dict, StructureData, Bool
from aiida.common import AttributeDict
from aiida.plugins import WorkflowFactory, DataFactory
from aiida.engine import ToContext, if_
from aiida_shengbte.workflows import BaseWorkChain

SinglefileData = DataFactory('singlefile')

PhonopyWorkChain = WorkflowFactory('phonopy.phonopy')
ThirdorderWorkChain = WorkflowFactory('shengbte.thirdorder')
ShengBTEWorkChain = WorkflowFactory('shengbte.shengbte')


def validate_inputs(inputs, ctx=None):  # pylint: disable=unused-argument
    """Validate the inputs of the entire input namespace."""


class ShengBTEQEWorkChain(BaseWorkChain):
    """ShengBTE WorkChain to run ShengBTE Calculation with force constants and other parameters calculating by qe and thirdorder(or phono3py).
    """
    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.expose_inputs(ThirdorderWorkChain, namespace='thirdorder',
                           exclude=('structure', 'vasp_settings', 'clean_workdir', 'dry_run'))
        spec.expose_inputs(ShengBTEWorkChain, namespace='shengbte',
                           exclude=('structure', 'control', 'clean_workdir', 'calculation.FORCE_CONSTANTS_2ND', 'calculation.FORCE_CONSTANTS_3RD'))
        spec.input('structure', valid_type=StructureData)
        spec.input('run_thirdorder', valid_type=Bool, default=lambda: Bool(True),
                   help='Calculating the third order force constants with thirdorder. Set False to call phono3py.')
        spec.input('calculator_settings', valid_type=Dict)
        spec.input('dry_run', valid_type=Bool, default=lambda: Bool(False))

        spec.outline(
            cls.setup,
            cls.get_force_constants_2nd,
            if_(cls.should_run_thirdorder)(
                cls.run_thirdorder,
                cls.inspect_thirdorder
            ).else_(
                cls.run_phono3py,
                cls.inspect_phono3py
            ),
            cls.run_shengbte,
            cls.inspect_shengbte
        )

        spec.expose_outputs(ShengBTEWorkChain, namespace='shengbte')

        spec.exit_code(401, 'ERROR_SUB_PROCESS_FAILED',
                       message='The sub process failed')

    def setup(self):
        """Define the current structure in the context to be the input structure."""
        self.report('initialize')

    def get_force_constants_2nd(self):
        pass

    def should_run_thirdorder(self):
        return self.inputs.run_thirdorder

    def run_phono3py(self):
        pass

    def inspect_phono3py(self):
        pass

    def run_thirdorder(self):
        pass

    def inspect_thirdorder(self):
        pass

    def run_shengbte(self):
        pass

    def inspect_shengbte(self):
        pass
