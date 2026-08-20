import os

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "priority_training_data_v11.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "priority_model_v11.pkl"
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("Loading Version 11 training data...")

df = pd.read_csv(DATA_FILE)


# --------------------------------------------------
# Validate required columns
# --------------------------------------------------

required_columns = [
    "title",
    "description",
    "category",
    "priority"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns: {missing_columns}"
    )


# --------------------------------------------------
# Clean data
# --------------------------------------------------

for column in required_columns:

    df[column] = (
        df[column]
        .fillna("")
        .astype(str)
        .str.strip()
    )


# --------------------------------------------------
# Combine text features
# --------------------------------------------------

df["text"] = (
    df["title"]
    + " "
    + df["description"]
    + " "
    + df["category"]
)


X = df["text"]

y = df["priority"]


# --------------------------------------------------
# Display dataset information
# --------------------------------------------------

print()
print("Total records:", len(df))

print()
print("Priority distribution:")
print(
    y.value_counts()
)


# --------------------------------------------------
# Split dataset
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print()
print("Training records:", len(X_train))
print("Testing records:", len(X_test))


# --------------------------------------------------
# Create ML pipeline
# --------------------------------------------------

model = Pipeline(
    [
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                max_features=5000
            )
        ),

        (
            "classifier",
            LogisticRegression(
                max_iter=1000
            )
        )
    ]
)


# --------------------------------------------------
# Train model
# --------------------------------------------------

print()
print("Training Version 11 ML model...")

model.fit(
    X_train,
    y_train
)


# --------------------------------------------------
# Evaluate model
# --------------------------------------------------

y_pred = model.predict(
    X_test
)


accuracy = accuracy_score(
    y_test,
    y_pred
)


print()
print(
    f"Version 11 Model Accuracy: {accuracy:.2%}"
)


print()
print("Classification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


# --------------------------------------------------
# Save Version 11 model
# --------------------------------------------------

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


joblib.dump(
    model,
    MODEL_FILE
)


print()
print("Version 11 model saved successfully:")

print(
    MODEL_FILE
)