from aiida import orm
from aiida.orm import Str, Code, Dict, StructureData, Group, Float, Bool, CalcJobNode, WorkChainNode, Int, KpointsData
from aiida.common import AttributeDict
from aiida.plugins import WorkflowFactory, DataFactory
from aiida.engine import WorkChain, ToContext, if_, run_get_node
from aiida.orm.nodes.data.upf import get_pseudos_from_structure
from aiida.orm.utils import load_node
from aiida.plugins.factories import CalculationFactory

PhonopyWorkChain = WorkflowFactory('phonopy.phonopy')
ShengbteCalculation = CalculationFactory('shengbte.shengbte')


def validate_inputs(inputs, ctx=None):  # pylint: disable=unused-argument
    """Validate the inputs of the entire input namespace."""


class ShengbteWorkChain(WorkChain):
    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.expose_inputs(ShengbteCalculation, namespace='base')

    def setup(self):
        """Define the current structure in the context to be the input structure."""

    def on_terminated(self):
        """Clean the working directories of all child calculations if `clean_workdir=True` in the inputs."""
        super().on_terminated()

        if self.inputs.clean_workdir.value is False:
            self.report('remote folders will not be cleaned')
            return

        cleaned_calcs = []

        for called_descendant in self.node.called_descendants:
            if isinstance(called_descendant, CalcJobNode):
                try:
                    called_descendant.outputs.remote_folder._clean()  # pylint: disable=protected-access
                    cleaned_calcs.append(called_descendant.pk)
                except (IOError, OSError, KeyError):
                    pass

        if cleaned_calcs:
            self.report('cleaned remote folders of calculations: {}'.format(
                ' '.join(map(str, cleaned_calcs))))
