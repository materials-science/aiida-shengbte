from aiida.orm import Dict, StructureData
from aiida.common import AttributeDict
from aiida.engine import ToContext
from aiida.plugins.factories import CalculationFactory
from aiida_shengbte.workflows import BaseWorkChain

ShengBTECalculation = CalculationFactory('shengbte.shengbte')


def validate_inputs(inputs, ctx=None):  # pylint: disable=unused-argument
    """Validate the inputs of the entire input namespace."""


class ShengBTEWorkChain(BaseWorkChain):
    """Class decorator for creating a WorkChain class with StructureData passed.
    """
    _CONTROL_OPTIONAL = {
        'allocations': ['ngrid', 'norientations'],
        'crystal': ['orientations', 'masses', 'gfactors', 'scell', 'born', 'epsilon', 'lfactor'],
        'parameters': ['T', 'T_min', 'T_max', 'T_step', 'omega_max', 'scalebroad', 'rmin', 'rmax', 'dr', 'maxiter', 'nticks', 'eps'],
        'flag': ['espresso', 'nonanalytic', 'convergence', 'isotopes', 'autoisotopes', 'nanowires', 'onlyharmonic']
    }

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.expose_inputs(ShengBTECalculation, namespace='calculation',
                           exclude=('control', 'metadata.dry_run', 'clean_workdir'))
        spec.input('structure', valid_type=StructureData)
        spec.input('control', valid_type=Dict)

        spec.outline(
            cls.setup,
            cls.run_shengbte,
            cls.inspect_shengbte
        )

        spec.expose_outputs(ShengBTECalculation)

        spec.exit_code(201, 'ERROR_KEY_IN_INPUT',
                       message='The key in `control` is invalid.')
        spec.exit_code(401, 'ERROR_SUB_PROCESS_FAILED_SHENGBTE_CALCULATION',
                       message='The ShengBTE Calculation sub process failed.')

    def setup(self):
        """Define the current structure in the context to be the input structure."""
        control = {}
        structure = self.inputs.structure

        allocations = {}
        crystal = {}
        flags = {}
        parameters = {}

        kinds = structure.kinds
        allocations['nelements'] = len(kinds)
        allocations['natoms'] = len(structure.get_site_kindnames())

        crystal['elements'] = structure.get_kind_names()
        sites = structure.sites
        current_element = sites[0].kind_name
        current_index = 1
        positions = []
        types = []
        for site in sites:
            kind = site.kind_name
            if kind != current_element:
                current_index += 1
                current_element = kind
            types.append(current_index)
            positions.append(list(site.position))

        crystal['types'] = types
        crystal['positions'] = positions
        crystal['lattvec'] = self.inputs.structure.cell
        crystal['lfactor'] = 0.1

        control.update({
            'allocations': allocations,
            'crystal': crystal,
            'parameters': parameters,
            'flags': flags
        })

        _control = self.inputs.control.get_dict()
        for name in _control:
            for key in _control[name]:
                if key not in self._CONTROL_OPTIONAL[name]:
                    self.logger.error(f'`{key}` is invalid or not need to specify in `control.{name}`')
                    return self.exit_codes.ERROR_KEY_IN_INPUT
                control[name].update({key: _control[name][key]})

        self.ctx.control = Dict(dict=control)

    def run_shengbte(self):
        """Run shengbte calculation"""
        inputs = AttributeDict(self.exposed_inputs(ShengBTECalculation, namespace='calculation'))
        inputs.metadata.call_link_label = 'shengbte_calculation'
        inputs.control = self.ctx.control

        running = self.submit(ShengBTECalculation, **inputs)

        self.report('launching shengbte Calculation<{}>'.format(running.pk))

        return ToContext(calculation_shengbte=running)

    def inspect_shengbte(self):
        if self.ctx.calculation_shengbte.is_finished_ok:
            self.report('ShengBTE calculation succesfully completed.')
            self.report(self.ctx.calculation_shengbte.outputs.out_path)
            self.out_many(
                self.exposed_outputs(self.ctx.calculation_shengbte, ShengBTECalculation)
            )
        else:
            return self.exit_codes.ERROR_SUB_PROCESS_FAILED_SHENGBTE_CALCULATION
