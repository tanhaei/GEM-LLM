import re
from typing import Optional, Tuple

import z3


class ContextualEquivalenceSolver:
    """
    Implements Phase 3: formal verification using Z3.
    Equivalence is confirmed when the conjunction
    invariant AND NOT(original == mutant) is UNSAT.
    """

    def __init__(self, timeout_ms: int = 10000) -> None:
        self.timeout_ms = timeout_ms
        self.solver = z3.Solver()
        self.solver.set("timeout", timeout_ms)

    @staticmethod
    def normalize_smt_script(smt_script: str) -> str:
        if not smt_script or not smt_script.strip():
            raise ValueError("SMT script is empty.")

        normalized = smt_script
        normalized = re.sub(r";.*$", "", normalized, flags=re.MULTILINE)
        normalized = re.sub(r"\(check-sat\)", "", normalized)
        normalized = re.sub(r"\(get-model\)", "", normalized)
        normalized = re.sub(r"\(get-unsat-core\)", "", normalized)
        normalized = re.sub(r"\bif\b", "ite", normalized)
        return normalized.strip()

    def verify(self, smt_script: str) -> Tuple[str, Optional[z3.ModelRef]]:
        try:
            normalized = self.normalize_smt_script(smt_script)
            assertions = z3.parse_smt2_string(normalized)
            self.solver.reset()
            self.solver.set("timeout", self.timeout_ms)
            self.solver.add(assertions)

            result = self.solver.check()
            if result == z3.unsat:
                return "EQUIVALENT", None
            if result == z3.sat:
                return "NON-EQUIVALENT", self.solver.model()
            return "UNKNOWN", None
        except Exception as exc:
            return f"ERROR: {exc}", None


if __name__ == "__main__":
    verifier = ContextualEquivalenceSolver()
    banking_smt = """
    (declare-fun amount () Int)
    (assert (and (> amount 100) (<= amount 5000)))
    (define-fun p ((x Int)) Int (ite (> x 0) 10 0))
    (define-fun m ((x Int)) Int (ite (not (= x 0)) 10 0))
    (assert (not (= (p amount) (m amount))))
    """
    status, model = verifier.verify(banking_smt)
    print(f"Result: {status}")
    if model is not None:
        print(model)
