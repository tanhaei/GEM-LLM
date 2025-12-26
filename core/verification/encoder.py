class SMTEncoder:
    """
    Transforms Java-IR slices into SMT-LIB constraints.
    Handles SSA versioning and OO features like Inheritance[cite: 179, 189].
    """
    def __init__(self):
        self.var_counters = {}

    def to_ssa(self, variable: str) -> str:
        """Maps program variables to versioned logical constants[cite: 180]."""
        if variable not in self.var_counters:
            self.var_counters[variable] = 0
        else:
            self.var_counters[variable] += 1
        return f"{variable}_{self.var_counters[variable]}"

    def encode_ite(self, condition: str, then_branch: str, else_branch: str) -> str:
        """Encodes conditional logic using the ITE operator[cite: 184, 185]."""
        return f"(ite {condition} {then_branch} {else_branch})"

    def handle_exception(self, path_condition: str) -> str:
        """Models exception paths by pruning execution branches[cite: 195]."""
        return f"(assert (=> exception_thrown (not {path_condition})))"
