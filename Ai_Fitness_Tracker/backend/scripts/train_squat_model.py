import pandas as pd
import numpy as np
import pickle
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils.class_weight import compute_class_weight

# ---------------- PATHS ----------------
DATA_PATH = r"C:\Users\admin\Downloads\Ai_Fitness_Tracker\Fit_vision\Ai_Fitness_Tracker\backend\app\core_ai\processing\data\squat_features_augmented.csv"
MODEL_SAVE_PATH = r"C:\Users\admin\Downloads\Ai_Fitness_Tracker\Fit_vision\Ai_Fitness_Tracker\backend\app\core_ai\processing\squat_classifier.pkl"


def add_derived_features(df):
    """🔥 VERY IMPORTANT"""

    df["knee_avg"] = (df["left_knee_angle"] + df["right_knee_angle"]) / 2
    df["hip_avg"] = (df["left_hip_angle"] + df["right_hip_angle"]) / 2
    df["ankle_avg"] = (df["left_ankle_angle"] + df["right_ankle_angle"]) / 2

    df["knee_diff"] = abs(df["left_knee_angle"] - df["right_knee_angle"])
    df["hip_diff"] = abs(df["left_hip_angle"] - df["right_hip_angle"])

    return df


def add_temporal_features(df):
    """🔥 SIMULATED TEMPORAL FEATURES (IMPORTANT)"""

    df = df.sort_values(["video_file", "frame"])

    for col in ["knee_avg", "hip_avg", "spine_angle"]:
        df[f"{col}_vel"] = df.groupby("video_file")[col].diff().fillna(0)
        df[f"{col}_acc"] = df.groupby("video_file")[f"{col}_vel"].diff().fillna(0)

    return df


def train_model():
    if not os.path.exists(DATA_PATH):
        print("Dataset not found!")
        return

    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    # ---------------- FEATURE ENGINEERING ----------------
    df = add_derived_features(df)
    df = add_temporal_features(df)

    # ---------------- FEATURES ----------------
    feature_cols = [
        'left_knee_angle', 'right_knee_angle',
        'left_hip_angle', 'right_hip_angle',
        'left_ankle_angle', 'right_ankle_angle',
        'spine_angle', 'torso_lean',
        'symmetry_score', 'hip_depth',

        # 🔥 NEW FEATURES
        'knee_avg', 'hip_avg', 'ankle_avg',
        'knee_diff', 'hip_diff',

        # 🔥 TEMPORAL
        'knee_avg_vel', 'hip_avg_vel', 'spine_angle_vel',
        'knee_avg_acc', 'hip_avg_acc'
    ]

    X = df[feature_cols].fillna(0)
    y = df["label"]

    # ---------------- HANDLE IMBALANCE ----------------
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(y),
        y=y
    )

    class_weight_dict = dict(zip(np.unique(y), class_weights))

    # ---------------- SPLIT ----------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    # ---------------- MODEL ----------------
    print("Training optimized RandomForest...")

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=3,
        class_weight=class_weight_dict,
        n_jobs=-1,
        random_state=42
    )

    model.fit(X_train, y_train)

    # ---------------- EVALUATION ----------------
    y_pred = model.predict(X_test)

    print("\nAccuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    # ---------------- SAVE ----------------
    print(f"\nSaving model to {MODEL_SAVE_PATH}")

    with open(MODEL_SAVE_PATH, "wb") as f:
        pickle.dump({
            "model": model,
            "features": feature_cols
        }, f)

    print("✅ Training Complete")


if __name__ == "__main__":
    train_model()