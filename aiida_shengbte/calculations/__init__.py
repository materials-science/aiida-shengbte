"""
aiida_shengbte

aiida plugin for ShengBTE
"""

__version__ = "0.1.0a0"

from aiida.engine import CalcJob
from aiida.orm import Bool


class BaseCalculation(CalcJob):
    """
    A basic plugin.
    """

    _DEFAULT_METADATA_RESOURCES = {
        'num_machines': 1,
        'num_mpiprocs_per_machine': 1,
    }

    @classmethod
    def define(cls, spec):
        super().define(spec)
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
        spec.input('clean_workdir',
                   valid_type=Bool,
                   required=False,
                   default=lambda: Bool(False),
                   help="""If True, clean the work dir upon the completion of a successfull calculation.""")
