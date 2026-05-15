import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from inference_engine.schemas import MinigameType
from inference_engine.rules.dosage_rules import (
    check_session_limit,
    should_trigger_minigame,
    get_session_structure,
)
from inference_engine.rules.constants import (
    SESSION_LIMITS,
    MINIGAME_REWARD_STREAK,
    MINIGAME_RESCUE_STREAK,
)


class TestCheckSessionLimit:
    def test_within_limits(self):
        assert check_session_limit(level=1, elapsed_minutes=5.0, exercises_done=2) is False

    def test_time_exceeded_level_1(self):
        assert check_session_limit(level=1, elapsed_minutes=12.0, exercises_done=1) is True

    def test_time_exceeded_level_3(self):
        assert check_session_limit(level=3, elapsed_minutes=20.0, exercises_done=1) is True

    def test_exercises_exceeded_level_1(self):
        max_ex = SESSION_LIMITS[1]["exercises"][1]
        assert check_session_limit(level=1, elapsed_minutes=1.0, exercises_done=max_ex) is True

    def test_exercises_exceeded_level_5(self):
        max_ex = SESSION_LIMITS[5]["exercises"][1]
        assert check_session_limit(level=5, elapsed_minutes=1.0, exercises_done=max_ex) is True

    def test_just_under_time_limit(self):
        assert check_session_limit(level=3, elapsed_minutes=19.9, exercises_done=1) is False

    def test_invalid_level_defaults_to_1(self):
        result = check_session_limit(level=99, elapsed_minutes=12.0, exercises_done=1)
        assert result is True


class TestShouldTriggerMinigame:
    def test_reward_triggered(self):
        result = should_trigger_minigame(MINIGAME_REWARD_STREAK, 0)
        assert result == MinigameType.REWARD

    def test_rescue_triggered(self):
        result = should_trigger_minigame(0, MINIGAME_RESCUE_STREAK)
        assert result == MinigameType.RESCUE

    def test_no_trigger(self):
        result = should_trigger_minigame(1, 1)
        assert result is None

    def test_reward_takes_priority_over_rescue(self):
        """If both streaks are met, reward wins (it's checked first)."""
        result = should_trigger_minigame(MINIGAME_REWARD_STREAK, MINIGAME_RESCUE_STREAK)
        assert result == MinigameType.REWARD

    def test_below_reward_streak(self):
        result = should_trigger_minigame(MINIGAME_REWARD_STREAK - 1, 0)
        assert result is None


class TestGetSessionStructure:
    def test_all_levels_have_structure(self):
        for level in range(1, 6):
            structure = get_session_structure(level)
            assert "max_minutes" in structure
            assert "exercises" in structure
            assert "minigames" in structure

    def test_level_3_values(self):
        s = get_session_structure(3)
        assert s["max_minutes"] == 20
        assert s["exercises"] == (5, 7)
        assert s["minigames"] == 2
