def predict_priority(title, description, category):
    """
    Predict the priority of a civic issue.

    Returns:
        High, Medium, or Low
    """

    title = title.lower().strip()
    description = description.lower().strip()
    category = category.lower().strip()

    text = f"{title} {description} {category}"

    high_keywords = [
        "danger",
        "dangerous",
        "accident",
        "accidents",
        "injury",
        "injuries",
        "blocked",
        "flood",
        "flooding",
        "fire",
        "electric shock",
        "electrical hazard",
        "major pothole",
        "large pothole",
        "severe",
        "emergency",
        "broken bridge",
        "open manhole"
    ]

    medium_keywords = [
        "leak",
        "leakage",
        "garbage",
        "waste",
        "overflow",
        "not working",
        "damaged",
        "damage",
        "crack",
        "water pipe",
        "streetlight"
    ]

    for keyword in high_keywords:

        if keyword in text:
            return "High"

    for keyword in medium_keywords:

        if keyword in text:
            return "Medium"

    if category in [
        "roads",
        "water",
        "streetlights"
    ]:
        return "Medium"

    return "Low"