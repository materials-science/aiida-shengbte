import os
from aiida.parsers.parser import Parser
from aiida.engine import ExitCode
from aiida.orm import Str
from aiida.plugins import DataFactory


class ThirdorderSowParser(Parser):
    """Parser for an `ThirdorderSowCalculation` job."""

    def parse(self, **kwargs):
        """Parse the contents of the output files stored in the `retrieved` output node."""
        try:
            with self.retrieved.open('_scheduler-stderr.txt', 'r') as handle:
                result = handle.read()
                self.logger.warning(result)
        except OSError:
            return self.exit_codes.ERROR_READING_OUTPUT_FILE
        names = self.retrieved.list_object_names()
        try:
            number = len(names) - 2
            if number <= 0:
                raise ValueError
        except ValueError:
            return self.exit_codes.ERROR_NO_OUTPUT

        uuid = self.retrieved.uuid
        node_dirpath = os.path.join('repository', 'node', uuid[:2], uuid[2:4], uuid[4:], 'path')
        self.out('out_path', Str(node_dirpath))
        return ExitCode(0)


class ThirdorderReapParser(Parser):
    """Parser for an `ThirdorderSowCalculation` job."""

    def parse(self, **kwargs):
        """Parse the contents of the output files stored in the `retrieved` output node."""
        try:
            with self.retrieved.open('_scheduler-stderr.txt', 'r') as handle:
                result = handle.read()
                self.logger.warning(result)
        except OSError:
            return self.exit_codes.ERROR_READING_OUTPUT_FILE

        try:
            with self.retrieved.open('FORCE_CONSTANTS_3RD', 'r') as handle:
                pass
        except OSError:
            return self.exit_codes.ERROR_READING_OUTPUT_FILE

        uuid = self.retrieved.uuid
        node_dirpath = os.path.join('repository', 'node', uuid[:2], uuid[2:4], uuid[4:], 'path')
        self.out('out_path', Str(node_dirpath))
        return ExitCode(0)
