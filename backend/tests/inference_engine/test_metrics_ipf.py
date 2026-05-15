import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from inference_engine.metrics.ipf import compute_ipf, is_low_confidence, normalize_text
from inference_engine.rules.constants import STT_CONFIDENCE_MIN


class TestNormalizeText:
    def test_lowercase(self):
        assert normalize_text("PERRO") == "perro"

    def test_strip_accents(self):
        assert normalize_text("rápido") == "rapido"

    def test_strip_whitespace(self):
        assert normalize_text("  gato  ") == "gato"

    def test_combined(self):
        assert normalize_text("  Árbol  ") == "arbol"


class TestComputeIPF:
    def test_exact_match_returns_100(self):
        assert compute_ipf("perro", "perro") == 100.0

    def test_exact_match_case_insensitive(self):
        assert compute_ipf("Perro", "perro") == 100.0

    def test_exact_match_with_accents(self):
        assert compute_ipf("rápido", "rapido") == 100.0

    def test_empty_transcript_returns_zero(self):
        assert compute_ipf("perro", "") == 0.0

    def test_whitespace_transcript_returns_zero(self):
        assert compute_ipf("perro", "   ") == 0.0

    def test_partial_match_returns_between_0_and_100(self):
        ipf = compute_ipf("piedra", "piera")
        assert 0.0 < ipf < 100.0

    def test_completely_different_returns_low(self):
        ipf = compute_ipf("mariposa", "xyz")
        assert ipf < 50.0

    def test_one_phoneme_wrong(self):
        ipf = compute_ipf("gato", "pato")
        assert 0.0 < ipf < 100.0

    def test_empty_target_returns_zero(self):
        assert compute_ipf("", "algo") == 0.0


class TestIsLowConfidence:
    def test_below_threshold(self):
        assert is_low_confidence(0.50) is True

    def test_at_threshold(self):
        assert is_low_confidence(STT_CONFIDENCE_MIN) is False

    def test_above_threshold(self):
        assert is_low_confidence(0.95) is False
