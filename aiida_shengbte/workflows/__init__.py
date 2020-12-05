from aiida import orm
from aiida.orm import CalcJobNode
from aiida.engine import WorkChain


class BaseWorkChain(WorkChain):
    _DEFAULT_METADATA_RESOURCES = {
        'num_machines': 1,
        'num_mpiprocs_per_machine': 1,
    }

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input('clean_workdir',
                   valid_type=orm.Bool,
                   required=False,
                   default=lambda: orm.Bool(False),
                   help="""
            If True, clean the work dir upon the completion of a successfull calculation.
            """)

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
