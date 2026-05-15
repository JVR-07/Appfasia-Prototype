import unicodedata
import py_stringmatching as sm
from inference_engine.rules.constants import STT_CONFIDENCE_MIN

# Initialize Editex evaluator once to reuse across calls
editex_evaluator = sm.Editex()

def normalize_text(text: str) -> str:
    text = text.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')

def compute_ipf(target_word: str, observed_transcript: str) -> float:
    """
    Returns IPF as 0-100 float.
    
    Steps:
    1. Normalize both strings (lowercase, strip accents for comparison)
    2. Compute editex phonetic distance using py_stringmatching
    3. Map distance to correct phoneme ratio
    4. IPF = (correct_phonemes / total_expected_phonemes) * 100
    """
    if not observed_transcript.strip():
        return 0.0
        
    target_norm = normalize_text(target_word)
    obs_norm = normalize_text(observed_transcript)
    
    if target_norm == obs_norm:
        return 100.0
        
    expected_phonemes = len(target_norm)
    if expected_phonemes == 0:
        return 0.0
        
    # py_stringmatching returns the raw editex distance (lower is closer)
    distance = editex_evaluator.get_raw_score(target_norm, obs_norm)
    correct_phonemes = max(0, expected_phonemes - distance)
    
    return (correct_phonemes / expected_phonemes) * 100.0

def is_low_confidence(stt_confidence: float) -> bool:
    return stt_confidence < STT_CONFIDENCE_MIN
