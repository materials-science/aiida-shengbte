from aiida.parsers.parser import Parser


class ShengbteParser(Parser):
    """Parser for an `ShengbteCalculation` job."""
    def parse(self, **kwargs):
        """Parse the contents of the output files stored in the `retrieved` output node."""
        from aiida.orm import Str

        try:
            with self.retrieved.open(self.node.get_option('output_filename'),
                                     'r') as handle:
                result = handle.read()
        except OSError:
            return self.exit_codes.ERROR_READING_OUTPUT_FILE
        except ValueError:
            return self.exit_codes.ERROR_INVALID_OUTPUT

        self.out('result', Str(result))
