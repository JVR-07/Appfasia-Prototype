# Constants and Thresholds for Inference Engine

# BKT Parameters
P_TRANSIT = 0.20
P_SLIP = 0.10
P_MASTERY_THRESHOLD = 0.80

P_GUESS = {
    "T-S_2_options": 0.50,
    "T-S_3_options": 0.33,
    "T-S_4_options": 0.25,
    "V-M": 0.00,
    "T-A": 0.05,
}

# Phonological Precision Index (IPF)
IPF_MASTERY = 80.0
IPF_PRACTICE_LOW = 50.0
IPF_BLOCK = 50.0
IPF_BLOCK_STREAK = 3
STT_CONFIDENCE_MIN = 0.70

# Auditory Response Rate (TRA)
TRA_FLUENCY_MS = 4000
TRA_COGNITIVE_DELAY_MS = 5000
TRA_HINT_MS = 5000
TRA_TIMEOUT_MS = 10000
TRA_CONSECUTIVE_TIMEOUT = 3

# Mean Length of Utterance (LME)
LME_TELEGRAPHIC_LOW = 2.0
LME_TELEGRAPHIC_HIGH = 4.0
LME_SYNTACTIC = 4.0
LME_ZERO_VALID = True

# Session duration limits
SESSION_LIMITS = {
    1: {"max_minutes": 12, "exercises": (3, 4), "minigames": 1},
    2: {"max_minutes": 12, "exercises": (3, 4), "minigames": 1},
    3: {"max_minutes": 20, "exercises": (5, 7), "minigames": 2},
    4: {"max_minutes": 30, "exercises": (8, 12), "minigames": 2},
    5: {"max_minutes": 30, "exercises": (8, 12), "minigames": 2},
}

# Minigame triggers
MINIGAME_REWARD_STREAK = 3
MINIGAME_RESCUE_STREAK = 2

# EMA Formula
EMA_WEIGHT_R0 = 0.50
EMA_WEIGHT_R1 = 0.30
EMA_WEIGHT_R2 = 0.20
LEVEL_DOWN_SESSIONS = 3

# Diagnostic Parameters
DIAGNOSTIC_MAX_INTERACTIONS = 15
DIAGNOSTIC_BASAL_STREAK = 3
DIAGNOSTIC_BASAL_TRA_LIMIT_MS = 4000
DIAGNOSTIC_CEILING_STREAK = 3
DIAGNOSTIC_FIRST_TIMEOUT_GRACE = True
