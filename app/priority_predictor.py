import os

import joblib


# --------------------------------------------------
# Find the trained ML model
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_FILE = os.path.join(
    BASE_DIR,
    "models",
    "priority_model.pkl"
)


# --------------------------------------------------
# Load the model once when Flask starts
# --------------------------------------------------

if not os.path.exists(MODEL_FILE):

    raise FileNotFoundError(
        f"Priority model not found: {MODEL_FILE}"
    )


model = joblib.load(
    MODEL_FILE
)


# --------------------------------------------------
# Predict issue priority
# --------------------------------------------------

def predict_priority(
    title,
    description,
    category
):

    title = str(title).strip()

    description = str(description).strip()

    category = str(category).strip()


    # Combine all issue information
    issue_text = (
        title
        + " "
        + description
        + " "
        + category
    )


    # Ask the trained ML model
    prediction = model.predict(
        [issue_text]
    )


    return prediction[0]