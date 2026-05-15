import spacy
import sys

try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    print("Warning: es_core_news_sm not found. Run: python -m spacy download es_core_news_sm", file=sys.stderr)
    nlp = None

def compute_lme(transcript: str, level: int = 1) -> float:
    """
    Returns LME as float (morpheme count per utterance).
    
    Implementation:
    - Load es_core_news_sm
    - Tokenize and count morphological units
    - For Levels 1-2: LME=0 is valid (short/single-word output expected)
    - For empty transcript: return 0.0
    
    Formula: LME = total_morphemes / utterance_count
    Since we evaluate one utterance at a time: LME = morpheme_count
    """
    if not transcript.strip():
        return 0.0
        
    if nlp is None:
        words = [w for w in transcript.strip().split() if any(c.isalnum() for c in w)]
        return float(len(words))
        
    doc = nlp(transcript)
    # Approximation of morphemes by counting valid tokens
    morpheme_count = len([token for token in doc if not token.is_punct and not token.is_space])
    
    return float(morpheme_count)
