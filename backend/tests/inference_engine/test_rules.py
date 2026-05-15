import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from inference_engine.schemas import (
    IPFOutcome, AvatarMode, TRAOutcome, LMEOutcome,
)
from inference_engine.metrics.tra import classify_tra, TRAResult
from inference_engine.rules.ipf_rules import evaluate_ipf
from inference_engine.rules.tra_rules import evaluate_tra
from inference_engine.rules.lme_rules import evaluate_lme
from inference_engine.rules.constants import (
    IPF_MASTERY, IPF_BLOCK_STREAK,
    TRA_FLUENCY_MS, TRA_TIMEOUT_MS, TRA_CONSECUTIVE_TIMEOUT,
    LME_TELEGRAPHIC_LOW,
)


# ──────────────────────────────────────────────
# TRA classification
# ──────────────────────────────────────────────

class TestClassifyTRA:
    def test_fluent(self):
        result = classify_tra(3000)
        assert result.is_fluent is True
        assert result.is_timeout is False

    def test_exactly_at_fluency_boundary(self):
        result = classify_tra(TRA_FLUENCY_MS)
        assert result.is_fluent is True

    def test_hint_triggered(self):
        result = classify_tra(6000)
        assert result.is_hint_triggered is True
        assert result.is_fluent is False

    def test_timeout(self):
        result = classify_tra(TRA_TIMEOUT_MS)
        assert result.is_timeout is True

    def test_below_hint(self):
        result = classify_tra(3000)
        assert result.is_hint_triggered is False


# ──────────────────────────────────────────────
# IPF Rules
# ──────────────────────────────────────────────

class TestIPFRules:
    def test_none_ipf_returns_skip(self):
        result = evaluate_ipf(None, False, 0)
        assert result.outcome == IPFOutcome.SKIP

    def test_low_confidence_returns_low_confidence(self):
        result = evaluate_ipf(85.0, True, 0)
        assert result.outcome == IPFOutcome.LOW_CONFIDENCE
        assert result.trigger_override is False

    def test_mastery_threshold(self):
        result = evaluate_ipf(IPF_MASTERY, False, 0)
        assert result.outcome == IPFOutcome.MASTERED
        assert result.avatar_mode == AvatarMode.CHALLENGE

    def test_above_mastery(self):
        result = evaluate_ipf(95.0, False, 0)
        assert result.outcome == IPFOutcome.MASTERED

    def test_practice_range(self):
        result = evaluate_ipf(65.0, False, 0)
        assert result.outcome == IPFOutcome.PRACTICE

    def test_below_block_no_streak(self):
        result = evaluate_ipf(30.0, False, 1)
        assert result.outcome == IPFOutcome.PRACTICE
        assert result.trigger_override is False
        assert result.avatar_mode == AvatarMode.SUPPORT

    def test_below_block_with_streak_triggers_override(self):
        result = evaluate_ipf(30.0, False, IPF_BLOCK_STREAK)
        assert result.outcome == IPFOutcome.HARDWARE_OVERRIDE
        assert result.trigger_override is True
        assert result.avatar_mode == AvatarMode.SUPPORT


# ──────────────────────────────────────────────
# TRA Rules
# ──────────────────────────────────────────────

class TestTRARules:
    def test_fluent_and_correct(self):
        tra = TRAResult(tra_ms=3000, is_timeout=False, is_hint_triggered=False, is_fluent=True)
        result = evaluate_tra(tra, 0, is_correct=True)
        assert result.outcome == TRAOutcome.FLUENT

    def test_delayed_and_correct(self):
        tra = TRAResult(tra_ms=6000, is_timeout=False, is_hint_triggered=True, is_fluent=False)
        result = evaluate_tra(tra, 0, is_correct=True)
        assert result.outcome == TRAOutcome.DELAYED

    def test_timeout(self):
        tra = TRAResult(tra_ms=10000, is_timeout=True, is_hint_triggered=True, is_fluent=False)
        result = evaluate_tra(tra, 0)
        assert result.outcome == TRAOutcome.TIMEOUT

    def test_vm_blocked_after_consecutive_timeouts(self):
        tra = TRAResult(tra_ms=10000, is_timeout=True, is_hint_triggered=True, is_fluent=False)
        result = evaluate_tra(tra, TRA_CONSECUTIVE_TIMEOUT)
        assert result.outcome == TRAOutcome.VM_BLOCKED
        assert result.trigger_vm_block is True

    def test_vm_block_priority_over_timeout(self):
        """VM_BLOCKED should take priority even if this specific response is a timeout."""
        tra = TRAResult(tra_ms=10000, is_timeout=True, is_hint_triggered=True, is_fluent=False)
        result = evaluate_tra(tra, TRA_CONSECUTIVE_TIMEOUT + 1)
        assert result.outcome == TRAOutcome.VM_BLOCKED


# ──────────────────────────────────────────────
# LME Rules
# ──────────────────────────────────────────────

class TestLMERules:
    def test_none_lme_returns_skip(self):
        result = evaluate_lme(None, 1)
        assert result.outcome == LMEOutcome.SKIP

    def test_zero_at_level_1_is_valid(self):
        result = evaluate_lme(0.0, 1)
        assert result.outcome == LMEOutcome.VALID_ZERO
        assert result.suggest_level is None

    def test_zero_at_level_2_is_valid(self):
        result = evaluate_lme(0.0, 2)
        assert result.outcome == LMEOutcome.VALID_ZERO

    def test_telegraphic_range(self):
        result = evaluate_lme(3.0, 2)
        assert result.outcome == LMEOutcome.TELEGRAPHIC
        assert result.suggest_level == 2

    def test_at_telegraphic_boundary_low(self):
        result = evaluate_lme(LME_TELEGRAPHIC_LOW, 2)
        assert result.outcome == LMEOutcome.TELEGRAPHIC

    def test_syntactic_above_threshold(self):
        result = evaluate_lme(5.0, 2)
        assert result.outcome == LMEOutcome.SYNTACTIC
        assert result.suggest_level == 3

    def test_transitional_below_telegraphic(self):
        result = evaluate_lme(1.5, 3)
        assert result.outcome == LMEOutcome.TRANSITIONAL
        assert result.suggest_level is None
