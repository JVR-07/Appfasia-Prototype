from inference_engine.schemas import TRARuleResult, TRAOutcome
from inference_engine.metrics.tra import TRAResult
from inference_engine.rules.constants import TRA_CONSECUTIVE_TIMEOUT


def evaluate_tra(
    tra_result: TRAResult,
    consecutive_timeouts: int,
    is_correct: bool = True
) -> TRARuleResult:
    """
    Evaluates the TRA metric and returns a typed result.

    Decision table (evaluated in priority order):
      - 3+ consecutive timeouts       → VM_BLOCKED (switch to T-A)
      - TRA >= 10s                     → TIMEOUT (null attempt)
      - TRA <= 4s AND correct          → FLUENT
      - TRA > 4s AND correct           → DELAYED (stay at level)
      - else                           → NORMAL
    """
    if consecutive_timeouts >= TRA_CONSECUTIVE_TIMEOUT:
        return TRARuleResult(outcome=TRAOutcome.VM_BLOCKED, trigger_vm_block=True)

    if tra_result.is_timeout:
        return TRARuleResult(outcome=TRAOutcome.TIMEOUT, trigger_vm_block=False)

    if tra_result.is_fluent and is_correct:
        return TRARuleResult(outcome=TRAOutcome.FLUENT, trigger_vm_block=False)

    if not tra_result.is_fluent and is_correct:
        return TRARuleResult(outcome=TRAOutcome.DELAYED, trigger_vm_block=False)

    return TRARuleResult(outcome=TRAOutcome.NORMAL, trigger_vm_block=False)
