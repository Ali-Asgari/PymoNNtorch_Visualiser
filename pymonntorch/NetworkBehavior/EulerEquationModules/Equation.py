from pymonntorch.NetworkCore.Behavior import Behavior
from pymonntorch.NetworkBehavior.EulerEquationModules.Helper import (
    eq_split,
    remove_units,
)
from sympy import symbols
import torch


class Equation(Behavior):
    def set_variables(self, neurons):
        super().set_variables(neurons)
        n = neurons
        self.add_tag("EquationModule")
        self.step_size = self.get_init_attr("step_size", "1*ms", neurons)
        eq_parts = eq_split(self.get_init_attr("eq", None))

        if (
            eq_parts[0][0] == "d"
            and eq_parts[1] == "/"
            and eq_parts[2] == "dt"
            and eq_parts[3] == "="
        ):
            self.variable = eq_parts[0][1:]
            symbols("n." + self.variable)
        else:
            print("invalid equation")

        for i in range(4, len(eq_parts)):
            if eq_parts[i] in neurons.__dict__:
                eq_parts[i] = "n." + eq_parts[i]

        eq_parts = remove_units(eq_parts, 4)

        self.evaluation = (
            "n."
            + self.variable
            + "+("
            + "".join(eq_parts[4:])
            + ")*{}".format(neurons.clock_step_size)
        )

        self.compiled_evaluation = compile(self.evaluation, "<string>", "eval")

        print(self.evaluation)

    def new_iteration(self, n):
        new = eval(self.compiled_evaluation)
        setattr(n, self.variable + "_new", torch.tensor(new, device=n.device))
