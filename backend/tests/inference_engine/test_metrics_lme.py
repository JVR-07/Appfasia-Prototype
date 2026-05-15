import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from inference_engine.metrics.lme import compute_lme


class TestComputeLME:
    def test_empty_string_returns_zero(self):
        assert compute_lme("") == 0.0

    def test_whitespace_returns_zero(self):
        assert compute_lme("   ") == 0.0

    def test_single_word(self):
        lme = compute_lme("gato")
        assert lme >= 1.0

    def test_multi_word_sentence(self):
        lme = compute_lme("El perro corre muy rápido")
        assert lme >= 4.0

    def test_level_1_zero_is_valid(self):
        lme = compute_lme("", level=1)
        assert lme == 0.0

    def test_level_2_zero_is_valid(self):
        lme = compute_lme("", level=2)
        assert lme == 0.0

    def test_returns_float(self):
        result = compute_lme("hola mundo")
        assert isinstance(result, float)

    def test_punctuation_excluded(self):
        lme_with_punct = compute_lme("Hola, mundo!")
        lme_without_punct = compute_lme("Hola mundo")
        # Punctuation should not count as morphemes
        assert lme_with_punct == lme_without_punct
