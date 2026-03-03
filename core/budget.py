DEFAULT_PLATFORMS = ["TikTok", "Meta/Instagram", "Snapchat", "Spotify", "Google", "YouTube"]

def normalize_weights(weights: dict) -> dict:
    cleaned = {p: float(weights.get(p, 0.0)) for p in DEFAULT_PLATFORMS}
    total = sum(cleaned.values())
    if total <= 0:
        return {p: 1.0 / len(DEFAULT_PLATFORMS) for p in DEFAULT_PLATFORMS}
    return {p: cleaned[p] / total for p in DEFAULT_PLATFORMS}

def allocate_budget(total: float, weights: dict) -> dict:
    allocations = {p: round(float(total) * float(weights.get(p, 0.0)), 2) for p in DEFAULT_PLATFORMS}
    drift = round(float(total) - sum(allocations.values()), 2)
    if abs(drift) >= 0.01:
        allocations[DEFAULT_PLATFORMS[0]] = round(allocations[DEFAULT_PLATFORMS[0]] + drift, 2)
    return allocations
