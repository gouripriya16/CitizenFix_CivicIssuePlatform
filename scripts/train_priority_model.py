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
    "priority_training_data.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "priority_model.pkl"
)


# --------------------------------------------------
# Load training data
# --------------------------------------------------

print("Loading training data...")

df = pd.read_csv(DATA_FILE)


# --------------------------------------------------
# Clean data
# --------------------------------------------------

df["title"] = (
    df["title"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["description"] = (
    df["description"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["category"] = (
    df["category"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["priority"] = (
    df["priority"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# --------------------------------------------------
# Combine input features
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
# Split training and testing data
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
                max_features=3000
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
print("Training priority prediction model...")

model.fit(
    X_train,
    y_train
)


# --------------------------------------------------
# Test model
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
    f"Model accuracy: {accuracy:.2%}"
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
# Save model
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
print(
    "Model saved successfully:"
)

print(
    MODEL_FILE
)