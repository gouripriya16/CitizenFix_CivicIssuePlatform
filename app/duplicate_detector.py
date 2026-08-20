import re

from difflib import SequenceMatcher


# --------------------------------------------------
# Text cleaning
# --------------------------------------------------

def clean_text(text):

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# --------------------------------------------------
# Text similarity
# --------------------------------------------------

def calculate_text_similarity(
    text1,
    text2
):

    text1 = clean_text(text1)

    text2 = clean_text(text2)

    if not text1 or not text2:
        return 0.0

    return SequenceMatcher(
        None,
        text1,
        text2
    ).ratio()


# --------------------------------------------------
# Location similarity
# --------------------------------------------------

def calculate_location_similarity(
    location1,
    location2
):

    location1 = clean_text(location1)

    location2 = clean_text(location2)

    if not location1 or not location2:
        return 0.0

    return SequenceMatcher(
        None,
        location1,
        location2
    ).ratio()


# --------------------------------------------------
# Duplicate detection
# --------------------------------------------------

def find_possible_duplicate(
    title,
    description,
    category,
    location,
    existing_issues
):

    new_text = (
        title
        + " "
        + description
    )


    best_match = None

    best_score = 0.0


    for issue in existing_issues:

        # Category must match
        if (
            issue.category.lower().strip()
            != category.lower().strip()
        ):
            continue


        # Compare issue text
        text_score = calculate_text_similarity(
            new_text,
            issue.title + " " + issue.description
        )


        # Compare locations
        location_score = calculate_location_similarity(
            location,
            issue.location
        )


        # Combined score
        combined_score = (
            (text_score * 0.7)
            + (location_score * 0.3)
        )


        if combined_score > best_score:

            best_score = combined_score

            best_match = issue


    # ----------------------------------------------
    # Duplicate threshold
    # ----------------------------------------------

    if (
        best_match is not None
        and best_score >= 0.60
    ):

        return {
            "is_duplicate": True,
            "score": best_score,
            "issue": best_match
        }


    return {
        "is_duplicate": False,
        "score": best_score,
        "issue": None
    }