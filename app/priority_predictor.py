import os
import joblib


# --------------------------------------------------
# Find the project root
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# --------------------------------------------------
# Version 11 ML model
# --------------------------------------------------

MODEL_FILE = os.path.join(
    BASE_DIR,
    "models",
    "priority_model_v11.pkl"
)


# --------------------------------------------------
# Check that model exists
# --------------------------------------------------

if not os.path.exists(MODEL_FILE):
    raise FileNotFoundError(
        f"Priority model not found: {MODEL_FILE}"
    )


# --------------------------------------------------
# Load the trained ML model
# --------------------------------------------------

model = joblib.load(MODEL_FILE)


# --------------------------------------------------
# Predict issue priority
# --------------------------------------------------

def predict_priority(title, description, category):

    title = str(title).strip()
    description = str(description).strip()
    category = str(category).strip()

    # Combine issue information
    issue_text = (
        title
        + " "
        + description
        + " "
        + category
    )

    # Predict using Version 11 ML model
    prediction = model.predict([issue_text])

    return prediction[0]