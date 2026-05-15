from inference_engine.schemas import BKTState

P_L0_BY_LEVEL = {
    1: 0.05,
    2: 0.15,
    3: 0.25,
    4: 0.40,
    5: 0.55,
}

def get_initial_p_l0(detected_level: int) -> float:
    return P_L0_BY_LEVEL.get(detected_level, 0.05)

def calibrate_hito_state(hito_id: str, detected_level: int, hito_level: int) -> BKTState:
    """
    A hito at the same level as detected → full P_L0_BY_LEVEL[level]
    A hito BELOW detected level → assumed mastered (p_mastery = 0.90)
    A hito ABOVE detected level → minimal P(L0) = 0.05
    """
    if hito_level < detected_level:
        p_mastery = 0.90
        is_mastered = True
    elif hito_level == detected_level:
        p_mastery = get_initial_p_l0(detected_level)
        is_mastered = False
    else:
        p_mastery = 0.05
        is_mastered = False
        
    return BKTState(
        hito_id=hito_id,
        p_mastery=p_mastery,
        is_mastered=is_mastered
    )
