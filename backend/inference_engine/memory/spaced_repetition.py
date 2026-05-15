import time

# Leitner-style intervals (in hours)
REVIEW_INTERVALS = {
    1: 24,
    2: 72,
    3: 168,
    4: 504,
}

MASTERY_THRESHOLD_FOR_QUEUE = 0.85
MAX_REVIEWS_PER_SESSION = 2
REVIEW_FAIL_IPF_THRESHOLD = 60.0
GRADUATION_STAGE = 4

def compute_next_review_timestamp(
    stage: int, now_ts: float | None = None
) -> float:
    if now_ts is None:
        now_ts = time.time()
    hours = REVIEW_INTERVALS.get(stage, REVIEW_INTERVALS[GRADUATION_STAGE])
    return now_ts + (hours * 3600)

def should_enqueue(p_mastery: float) -> bool:
    return p_mastery >= MASTERY_THRESHOLD_FOR_QUEUE

def process_review_result(
    current_stage: int, ipf_score: float
) -> tuple[int, bool]:
    """Returns (new_stage, is_graduated).

    IPF >= 60 → advance stage. If stage was 4 → graduated.
    IPF < 60  → reset to stage 1.
    """
    if ipf_score < REVIEW_FAIL_IPF_THRESHOLD:
        return (1, False)

    if current_stage >= GRADUATION_STAGE:
        return (current_stage, True)

    return (current_stage + 1, False)

def pick_reviews_for_session(
    pending_reviews: list[dict],
    now_ts: float,
    max_count: int = MAX_REVIEWS_PER_SESSION,
) -> list[str]:
    """From pending reviews, returns up to max_count hito IDs
    whose next_review_ts <= now. Sorted by oldest first.
    """
    due = [
        r for r in pending_reviews
        if r["next_review_ts"] <= now_ts
    ]
    due.sort(key=lambda r: r["next_review_ts"])
    return [r["hito_id"] for r in due[:max_count]]
