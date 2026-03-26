"""
KNN-based fitness recommender built from the gym recommendation dataset.
Train once at boot, pickle for reuse. Handles missing user profile values
by imputing from training-set medians/modes.
"""
import pickle
import os
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "gym recommendation.xlsx")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fitness_model.pkl")

NUMERIC_FEATURES = ["Age", "Height", "Weight", "BMI"]
BINARY_FEATURES  = ["Sex", "Hypertension", "Diabetes"]
GOAL_FEATURE     = "Fitness Goal"                      

LEVEL_ALIASES = {"Obuse": "Obese"}


class FitnessRecommender:
    """Nearest-neighbour workout recommender over the gym recommendation dataset."""

    _instance = None  # in-process singleton — loaded once, reused everywhere

    def __init__(self, knn, scaler, df, feature_cols, impute_values):
        self._knn = knn
        self._scaler = scaler
        self._df = df
        self._feature_cols = feature_cols
        self._impute_values = impute_values

    @classmethod
    def get(cls) -> "FitnessRecommender":
        """Return the singleton, loading from disk if not yet in memory."""
        if cls._instance is None:
            cls._instance = cls.load_or_train()
        return cls._instance

    @classmethod
    def load_or_train(cls, data_path=DATA_PATH, model_path=MODEL_PATH):
        """Load cached model from disk if available, otherwise train and save.
        Called at boot by the orchestrator to ensure the model exists on disk."""
        if os.path.exists(model_path):
            try:
                print("  [Fitness model] Loading cached model…", flush=True)
                with open(model_path, "rb") as f:
                    instance = pickle.load(f)
                cls._instance = instance
                return instance
            except Exception as e:
                print(f"  [Fitness model] Cache load failed ({e}), retraining…", flush=True)
                os.remove(model_path)

        print("  [Fitness model] Training KNN on gym dataset…", flush=True)
        instance = cls._train(data_path)
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        with open(model_path, "wb") as f:
            pickle.dump(instance, f)
        print("  [Fitness model] Model saved.", flush=True)
        cls._instance = instance
        return instance

    @classmethod
    def _train(cls, data_path):
        df = pd.read_excel(data_path)

        df["Level"] = df["Level"].replace(LEVEL_ALIASES)

        df["Sex_enc"]          = (df["Sex"]          == "Male").astype(int)
        df["Hypertension_enc"] = (df["Hypertension"] == "Yes").astype(int)
        df["Diabetes_enc"]     = (df["Diabetes"]     == "Yes").astype(int)

        goal_dummies = pd.get_dummies(df[GOAL_FEATURE], prefix="Goal").astype(int)
        df = pd.concat([df, goal_dummies], axis=1)
        goal_cols = goal_dummies.columns.tolist()

        feature_cols = NUMERIC_FEATURES + ["Sex_enc", "Hypertension_enc", "Diabetes_enc"] + goal_cols

        X = df[feature_cols].values

        impute_values = {}
        for i, col in enumerate(feature_cols):
            vals = X[:, i]
            impute_values[col] = float(np.median(vals[~np.isnan(vals)]))

        for i, col in enumerate(feature_cols):
            mask = np.isnan(X[:, i])
            X[mask, i] = impute_values[col]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        knn = NearestNeighbors(n_neighbors=5, metric="euclidean")
        knn.fit(X_scaled)

        return cls(knn, scaler, df, feature_cols, impute_values)


    def recommend(self, user_profile: dict) -> list[dict]:
        """
        Find the 5 nearest neighbours for a user profile dict.

        user_profile keys (all optional — missing values are imputed):
            age, height, weight, bmi, sex, hypertension, diabetes, fitness_goal
        """
        row = self._build_feature_row(user_profile)
        row_scaled = self._scaler.transform([row])
        _, indices = self._knn.kneighbors(row_scaled)

        results = []
        for idx in indices[0]:
            rec = self._df.iloc[idx]
            results.append({
                "fitness_goal":   rec.get("Fitness Goal", ""),
                "fitness_type":   rec.get("Fitness Type", ""),
                "level":          rec.get("Level", ""),
                "exercises":      rec.get("Exercises", ""),
                "equipment":      rec.get("Equipment", ""),
                "diet":           rec.get("Diet", ""),
                "recommendation": rec.get("Recommendation", ""),
            })
        return results

    def _build_feature_row(self, user_profile: dict) -> list[float]:
        """Convert a user profile dict to a feature vector, imputing missing values."""
        bmi = user_profile.get("bmi")
        if bmi is None:
            h = user_profile.get("height")
            w = user_profile.get("weight")
            if h and w and float(h) > 0:
                bmi = float(w) / (float(h) ** 2)

        raw = {
            "Age":              user_profile.get("age"),
            "Height":           user_profile.get("height"),
            "Weight":           user_profile.get("weight"),
            "BMI":              bmi,
            "Sex_enc":          _encode_binary(user_profile.get("sex"), positive="male"),
            "Hypertension_enc": _encode_binary(user_profile.get("hypertension"), positive="yes"),
            "Diabetes_enc":     _encode_binary(user_profile.get("diabetes"), positive="yes"),
        }

        goal = (user_profile.get("fitness_goal") or "").lower()
        for col in self._feature_cols:
            if col.startswith("Goal_"):
                label = col[len("Goal_"):].lower()
                raw[col] = 1 if goal and label in goal else 0

        row = []
        for col in self._feature_cols:
            val = raw.get(col)
            if val is None or (isinstance(val, float) and np.isnan(val)):
                val = self._impute_values[col]
            row.append(float(val))
        return row


def _encode_binary(value, positive: str) -> float | None:
    if value is None:
        return None
    return 1.0 if str(value).lower().strip() == positive else 0.0
