from typing import Dict, Iterable, List


class SMTEncoder:
    """
    Transforms a simplified IR into SMT-LIB fragments.
    Provides SSA variable versioning helpers used by the verification phase.
    """

    def __init__(self) -> None:
        self.var_counters: Dict[str, int] = {}

    def current_version(self, variable: str) -> str:
        version = self.var_counters.get(variable, 0)
        return f"{variable}_{version}"

    def to_ssa(self, variable: str) -> str:
        next_version = self.var_counters.get(variable, -1) + 1
        self.var_counters[variable] = next_version
        return f"{variable}_{next_version}"

    def encode_assignment(self, variable: str, expr: str) -> str:
        target = self.to_ssa(variable)
        return f"(assert (= {target} {expr}))"

    def encode_ite(self, condition: str, then_branch: str, else_branch: str) -> str:
        return f"(ite {condition} {then_branch} {else_branch})"

    def encode_phi(self, variable: str, incoming_versions: Iterable[str]) -> str:
        incoming: List[str] = list(incoming_versions)
        if not incoming:
            raise ValueError("Phi node requires at least one incoming version.")
        merged = self.to_ssa(variable)
        if len(incoming) == 1:
            return f"(assert (= {merged} {incoming[0]}))"
        disjuncts = " ".join(f"(= {merged} {v})" for v in incoming)
        return f"(assert (or {disjuncts}))"

    def handle_exception(self, path_condition: str, exception_flag: str = "exception_state") -> str:
        return f"(assert (=> (> {exception_flag} 0) (not {path_condition})))"
