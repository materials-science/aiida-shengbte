import json
from aiida.orm import Dict, StructureData, Bool, CalcJobNode
from aiida.common import AttributeDict
from aiida.plugins import WorkflowFactory, DataFactory
from aiida.engine import ToContext, if_
from aiida_shengbte.workflows import BaseWorkChain

SinglefileData = DataFactory("singlefile")

PhonopyWorkChain = WorkflowFactory("phonopy.phonopy")
ThirdorderWorkChain = WorkflowFactory("shengbte.thirdorder")
ShengBTEWorkChain = WorkflowFactory("shengbte.shengbte")


def validate_inputs(inputs, ctx=None):  # pylint: disable=unused-argument
    """Validate the inputs of the entire input namespace."""


class ShengBTEVaspWorkChain(BaseWorkChain):
    """ShengBTE WorkChain to run ShengBTE Calculation with force constants and other parameters calculating by vasp, phonopy and thirdorder."""

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.expose_inputs(
            PhonopyWorkChain,
            namespace="phonopy",
            exclude=(
                "structure",
                "calculator_settings",
                "calculation_nodes",
                "dry_run",
            ),
        )
        spec.expose_inputs(
            ThirdorderWorkChain,
            namespace="thirdorder",
            exclude=("structure", "vasp_settings", "clean_workdir", "dry_run"),
        )
        spec.expose_inputs(
            ShengBTEWorkChain,
            namespace="shengbte",
            exclude=(
                "structure",
                "clean_workdir",
                "calculation.FORCE_CONSTANTS_2ND",
                "calculation.FORCE_CONSTANTS_3RD",
            ),
        )
        spec.input("structure", valid_type=StructureData)
        spec.input(
            "run_thirdorder",
            valid_type=Bool,
            default=lambda: Bool(True),
            help="Calculating the third order force constants with thirdorder. Set False to call phono3py.",
        )
        spec.input("vasp_settings", valid_type=Dict)
        spec.input("dry_run", valid_type=Bool, default=lambda: Bool(False))

        spec.outline(
            cls.setup,
            cls.run_phonopy,
            cls.inspect_phonopy,
            if_(cls.should_run_thirdorder)(
                cls.run_thirdorder, cls.inspect_thirdorder
            ).else_(cls.run_phono3py, cls.inspect_phono3py),
            cls.run_shengbte,
            cls.inspect_shengbte,
        )

        spec.expose_outputs(ShengBTEWorkChain, namespace="shengbte")
        spec.output("control", valid_type=Dict, required=False)
        spec.output("phonopy_out", valid_type=Dict)
        spec.output("FORCE_CONSTANTS_2ND", valid_type=SinglefileData)
        spec.output("FORCE_CONSTANTS_3RD", valid_type=SinglefileData)

        spec.exit_code(
            401, "ERROR_SUB_PROCESS_FAILED", message="The sub process failed"
        )

    def setup(self):
        """Define the current structure in the context to be the input structure."""
        self.report("initialize")
        base_config = self.inputs.vasp_settings.get_dict().copy()
        self.ctx.current_structure = self.inputs.structure
        self.ctx.forces_settings = base_config["forces"]
        self.ctx.dry_run = self.inputs.dry_run.value
        self.ctx.lost_parameters = {}

    def run_phonopy(self):
        inputs = AttributeDict(
            self.exposed_inputs(PhonopyWorkChain, namespace="phonopy")
        )
        inputs.metadata.call_link_label = "phonopy"
        inputs.structure = self.ctx.current_structure
        inputs.calculator_settings = self.inputs.vasp_settings

        running = self.submit(PhonopyWorkChain, **inputs)

        self.ctx.phonopy_supercell_matrix = inputs.phonon_settings[
            "supercell_matrix"
        ]

        self.report("launching Phonopy WorkChain<{}>".format(running.pk))

        return ToContext(workchain_phonopy=running)

    def inspect_phonopy(self):
        if not self.ctx.workchain_phonopy.is_finished_ok:
            self.report(
                "Phonopy WorkChain failed with exit status {}".format(
                    self.ctx.workchain_phonopy.exit_status
                )
            )
            return self.exit_codes.ERROR_SUB_PROCESS_FAILED

        self.report("collecting phonopy workchain outputs")

        ph_out = self.ctx.workchain_phonopy.outputs
        force_constants = ph_out.force_constants
        from phonopy import file_IO
        from io import BytesIO

        try:
            lines = file_IO.get_FORCE_CONSTANTS_lines(
                force_constants.get_array("force_constants"),
                force_constants.get_array("p2s_map"),
            )
        except KeyError as err:
            self.report(err)
            lines = file_IO.get_FORCE_CONSTANTS_lines(
                force_constants.get_array("force_constants")
            )
        FORCE_CONSTANTS_2ND = SinglefileData(
            BytesIO(bytes("\n".join(lines), encoding="utf8")),
            "FORCE_CONSTANTS_2ND",
        )
        self.ctx.epsilon = ph_out.nac_params.get_array("epsilon")
        self.ctx.born_charges = ph_out.nac_params.get_array("born_charges")
        self.ctx.FORCE_CONSTANTS_2ND = FORCE_CONSTANTS_2ND

        self.report("collected FORCE_CONSTANTS_2ND, epsilon, born_charges")
        self.report(
            "[data] The id of FORCE_CONSTANTS_2ND(SinglefileData) is {}".format(
                self.ctx.FORCE_CONSTANTS_2ND.id
            )
        )
        phonopy_out = Dict(dict={})
        phonopy_out["epsilon"] = self.ctx.epsilon
        phonopy_out["born_charges"] = self.ctx.born_charges
        phonopy_out.store()
        self.out("FORCE_CONSTANTS_2ND", self.ctx.FORCE_CONSTANTS_2ND)
        self.out("phonopy_out", phonopy_out)

    def should_run_thirdorder(self):
        return self.inputs.run_thirdorder

    def run_phono3py(self):
        # TODO(aiida-phonopy): phono3py workflow in aiida-phonopy is under developing
        self.report("start run phono3py.")

    def inspect_phono3py(self):
        self.report("collecting output data from phono3py.")

    def run_thirdorder(self):
        """Run thirdorder workchain"""
        inputs = AttributeDict(
            self.exposed_inputs(ThirdorderWorkChain, namespace="thirdorder")
        )
        inputs.metadata.call_link_label = "thirdorder"
        inputs.structure = self.ctx.current_structure
        inputs.vasp_settings = Dict(dict={"forces": self.ctx.forces_settings})

        running = self.submit(ThirdorderWorkChain, **inputs)

        self.report("launching Thirdorder WorkChain<{}>".format(running.pk))

        return ToContext(workchain_thirdorder=running)

    def inspect_thirdorder(self):
        if not self.ctx.workchain_thirdorder.is_finished_ok:
            self.report(
                "Thirdorder WorkChain failed with exit status {}".format(
                    self.ctx.workchain_thirdorder.exit_status
                )
            )
            return self.exit_codes.ERROR_SUB_PROCESS_FAILED

        self.ctx.FORCE_CONSTANTS_3RD = (
            self.ctx.workchain_thirdorder.outputs.FORCE_CONSTANTS_3RD
        )
        self.report("collected FORCE_CONSTANTS_3RD")
        self.report(
            "[data] The id of FORCE_CONSTANTS_2ND(SinglefileData) is {}".format(
                self.ctx.FORCE_CONSTANTS_3RD.id
            )
        )
        self.out("FORCE_CONSTANTS_3RD", self.ctx.FORCE_CONSTANTS_3RD)

    def run_shengbte(self):
        """Run shengbte calculation"""
        inputs = AttributeDict(
            self.exposed_inputs(ShengBTEWorkChain, namespace="shengbte")
        )
        inputs.metadata.call_link_label = "shengbte"
        inputs.structure = self.ctx.current_structure
        inputs.calculation.FORCE_CONSTANTS_3RD = self.ctx.FORCE_CONSTANTS_3RD
        inputs.calculation.FORCE_CONSTANTS_2ND = self.ctx.FORCE_CONSTANTS_2ND
        control = inputs.control.get_dict()
        try:
            control["flags"]
        except KeyError:
            control["flags"] = {}
        control["flags"]["espresso"] = False

        try:
            control["crystal"]
        except KeyError:
            control["crystal"] = {}
        control["crystal"]["born"] = self.ctx.born_charges
        control["crystal"]["epsilon"] = self.ctx.epsilon
        control["crystal"]["scell"] = self.ctx.phonopy_supercell_matrix
        inputs.control = Dict(dict=control)

        running = self.submit(ShengBTEWorkChain, **inputs)

        self.report("launching ShengBTE WorkChain<{}>".format(running.pk))

        return ToContext(workchain_shengbte=running)

    def inspect_shengbte(self):
        if not self.ctx.workchain_shengbte.is_finished_ok:
            if "control" in self.ctx.workchain_shengbte.outputs:
                self.ctx.control = self.ctx.workchain_shengbte.outputs.control
            self.report(
                "ShengBTE WorkChain failed with exit status {}".format(
                    self.ctx.workchain_shengbte.exit_status
                )
            )
            self.report(
                "[data] The generated control dict is :\n {}".format(
                    json.dumps(self.ctx.control.get_dict())
                )
            )
            self.out("control", self.ctx.control)
            return self.exit_codes.ERROR_SUB_PROCESS_FAILED

        self.report("ShengBTE WorkChain succesfully completed.")
        self.out_many(
            self.exposed_outputs(
                self.ctx.workchain_shengbte,
                ShengBTEWorkChain,
                namespace="shengbte",
            )
        )

    def on_terminated(self):
        """Clean the working directories of all child calculations if `clean_workdir=True` in the inputs. Save part of produced results if the task failed."""
        super().on_terminated()

        if self.inputs.clean_workdir.value is False:
            self.report("remote folders will not be cleaned")
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
            self.report(
                f"cleaned remote folders of calculations: {' '.join(map(str, cleaned_calcs))}"
            )
