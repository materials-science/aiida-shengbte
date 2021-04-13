from aiida.parsers.parser import Parser
from aiida.engine import ExitCode
import os


class ShengBTEParser(Parser):
    """Parser for an `ShengBTECalculation` job."""

    def parse(self, **kwargs):
        """Parse the contents of the output files stored in the `retrieved` output node."""
        from aiida.orm import Str

        # try:
        #     with self.retrieved.open(self.node.get_option('output_filename'), 'r') as handle:
        #         result = handle.read()
        # except OSError:
        #     return self.exit_codes.ERROR_READING_OUTPUT_FILE
        # except ValueError:
        #     return self.exit_codes.ERROR_INVALID_OUTPUT

        uuid = self.retrieved.uuid
        node_dirpath = os.path.join(
            "repository", "node", uuid[:2], uuid[2:4], uuid[4:], "path"
        )
        self.out("outpath", Str(node_dirpath))
        return ExitCode(0)
