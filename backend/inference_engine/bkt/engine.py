from inference_engine.rules.constants import P_TRANSIT, P_SLIP, P_GUESS

def update(
    p_mastery: float,
    correct: bool,
    p_transit: float = P_TRANSIT,
    p_slip: float = P_SLIP,
    p_guess: float = P_GUESS["T-S_3_options"]
) -> float:
    """
    Returns updated P(mastery) after one observation using the standard BKT formula.
    
    P(L|correct) = [ P(L) * (1 - P(S)) ] / [ P(L)*(1-P(S)) + (1-P(L))*P(G) ]
    P(L|wrong)   = [ P(L) * P(S) ]       / [ P(L)*P(S) + (1-P(L))*(1-P(G)) ]
    P(L_next)    = P(L|obs) + (1 - P(L|obs)) * P(T)
    """
    if correct:
        numerator = p_mastery * (1 - p_slip)
        denominator = numerator + (1 - p_mastery) * p_guess
    else:
        numerator = p_mastery * p_slip
        denominator = numerator + (1 - p_mastery) * (1 - p_guess)
        
    if denominator == 0:
        p_l_obs = p_mastery
    else:
        p_l_obs = numerator / denominator
        
    p_next = p_l_obs + (1 - p_l_obs) * p_transit
    
    # Ensure probabilities are bounded between 0 and 1
    return max(0.0, min(1.0, p_next))
