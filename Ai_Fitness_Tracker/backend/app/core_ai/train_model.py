import os
import argparse
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from joblib import dump
from .utils import compute_bmi, compute_bmr, intensity_from_experience, random_goal

def load_dataset(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in df.columns]
    for c in cols:
        if df[c].dtype.kind in "biufc":
            df[c] = df[c].fillna(df[c].median())
        else:
            df[c] = df[c].fillna(df[c].mode().iloc[0] if not df[c].mode().empty else "unknown")
    if "Weight" in df.columns and "Height" in df.columns and "BMI" not in df.columns:
        df["BMI"] = df.apply(lambda r: compute_bmi(float(r["Weight"]), float(r["Height"])), axis=1)
    if "Gender" not in df.columns and "gender" in df.columns:
        df["Gender"] = df["gender"]
    if "Workout_Type" not in df.columns and "workout_type" in df.columns:
        df["Workout_Type"] = df["workout_type"]
    if "Experience_Level" not in df.columns and "experience_level" in df.columns:
        df["Experience_Level"] = df["experience_level"]
    if "Age" not in df.columns and "age" in df.columns:
        df["Age"] = df["age"]
    if "weight" in df.columns and "Weight" not in df.columns:
        df["Weight"] = df["weight"]
    if "height_cm" in df.columns and "Height" not in df.columns:
        df["Height"] = df["height_cm"]
    if "workout_frequency" not in df.columns:
        df["workout_frequency"] = 3
    if "session_duration" not in df.columns:
        df["session_duration"] = 30
    if "goal" not in df.columns:
        df["goal"] = [random_goal() for _ in range(len(df))]
    def rec_cal(row):
        bmr = compute_bmr(str(row["Gender"]), float(row["Weight"]), float(row["Height"]), int(row["Age"]))
        return bmr * (1.2 + float(row["workout_frequency"]) * 0.1)
    def rec_water(row):
        return float(row["Weight"]) * 0.035 + float(row["session_duration"]) * 0.5
    def rec_intensity(row):
        return intensity_from_experience(str(row["Experience_Level"]))
    df["recommended_calories"] = df.apply(rec_cal, axis=1)
    df["recommended_water"] = df.apply(rec_water, axis=1)
    df["recommended_intensity"] = df.apply(rec_intensity, axis=1)
    return df

def build_and_train(df: pd.DataFrame, model_out: str):
    features = ["Gender","Workout_Type","Experience_Level","Age","Height","Weight","BMI","workout_frequency","session_duration"]
    X = df[features].copy()
    y = df[["recommended_calories","recommended_water","recommended_intensity"]].copy()
    cat = ["Gender","Workout_Type","Experience_Level"]
    num = [c for c in features if c not in cat]
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
        ("num", "passthrough", num),
    ])
    rf = RandomForestRegressor(n_estimators=200, random_state=42)
    model = Pipeline(steps=[
        ("pre", pre),
        ("rf", MultiOutputRegressor(rf))
    ])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, pred, multioutput="raw_values")
    rmse = np.sqrt(mean_squared_error(y_test, pred, multioutput="raw_values"))
    print("MAE:", mae.tolist())
    print("RMSE:", rmse.tolist())
    dump(model, model_out)
    print("Saved:", model_out)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default=os.getenv("FITNESS_DATA_PATH", "data/fitness.csv"))
    p.add_argument("--out", default=os.getenv("PERSONALIZATION_MODEL_PATH", "backend/app/core_ai/personalization_model.joblib"))
    args = p.parse_args()
    df = load_dataset(args.data)
    df = preprocess(df)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    build_and_train(df, args.out)

if __name__ == "__main__":
    main()
