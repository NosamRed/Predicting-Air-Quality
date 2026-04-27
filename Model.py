import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


model = None
data = None
y_test = None
y_pred = None


pm25_breakpoints = [
    {"C_lo": 0.0, "C_hi": 12.0, "I_lo": 0, "I_hi": 50},
    {"C_lo": 12.1, "C_hi": 35.4, "I_lo": 51, "I_hi": 100},
    {"C_lo": 35.5, "C_hi": 55.4, "I_lo": 101, "I_hi": 150},
    {"C_lo": 55.5, "C_hi": 150.4, "I_lo": 151, "I_hi": 200},
    {"C_lo": 150.5, "C_hi": 250.4, "I_lo": 201, "I_hi": 300},
    {"C_lo": 250.5, "C_hi": 350.4, "I_lo": 301, "I_hi": 400},
    {"C_lo": 350.5, "C_hi": 500.4, "I_lo": 401, "I_hi": 500},
]


def calculate_aqi_from_pm25(C):
    for bp in pm25_breakpoints:
        if bp["C_lo"] <= C <= bp["C_hi"]:
            return ((bp["I_hi"] - bp["I_lo"]) /
                    (bp["C_hi"] - bp["C_lo"])) * (C - bp["C_lo"]) + bp["I_lo"]
    return None


def get_aqi_status(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy"
    elif aqi <= 200:
        return "Very Unhealthy"
    else:
        return "Hazardous"


def resource_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)


def read_csv_safely(csv_path):
    try:
        return pd.read_csv(csv_path, encoding="utf-8-sig", on_bad_lines="skip")
    except UnicodeDecodeError:
        return pd.read_csv(csv_path, encoding="cp1252", on_bad_lines="skip")


def load_model_from_csv(csv_path):
    global model, data, y_test, y_pred

    data = read_csv_safely(csv_path)
    data.columns = [col.strip().lower() for col in data.columns]

    input_columns = [
        "co aqi value",
        "ozone aqi value",
        "no2 aqi value",
        "pm2.5 aqi value"
    ]

    for col in input_columns:
        if col not in data.columns:
            raise ValueError(f"Missing required column: {col}")

    for col in input_columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=input_columns)

    # If AQI Value exists, use it. If not, calculate it from PM2.5.
    if "aqi value" in data.columns:
        data["aqi value"] = pd.to_numeric(data["aqi value"], errors="coerce")
    else:
        data["aqi value"] = data["pm2.5 aqi value"].apply(calculate_aqi_from_pm25)

    data = data.dropna(subset=["aqi value"])

    data["aqi value"] = data["aqi value"].round(0).astype(int)
    data["aqi status"] = data["aqi value"].apply(get_aqi_status)

    if len(data) < 5:
        raise ValueError("Not enough valid rows after cleaning the CSV.")

    X = data[input_columns]
    y = data["aqi value"]

    X_train, X_test, y_train, y_test_local = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    y_test = y_test_local
    y_pred = model.predict(X_test)


def load_default_model():
    default_csv = resource_path("Test.csv")
    load_model_from_csv(default_csv)


def plot_actual_vs_predicted():
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.scatter(y_test, y_pred)
    ax.set_xlabel("Actual AQI")
    ax.set_ylabel("Predicted AQI")
    ax.set_title("Actual vs Predicted AQI")
    fig.tight_layout()
    return fig


def plot_feature_importance():
    fig, ax = plt.subplots(figsize=(5, 3))

    importances = model.feature_importances_
    feature_names = [
        "CO",
        "Ozone",
        "NO2",
        "PM2.5"
    ]

    ax.bar(feature_names, importances)
    ax.set_title("Feature Importance")
    ax.set_ylabel("Importance")
    fig.tight_layout()
    return fig


def get_model_metrics():
    return {
        "mae": round(mean_absolute_error(y_test, y_pred), 3),
        "mse": round(mean_squared_error(y_test, y_pred), 3),
        "r2": round(r2_score(y_test, y_pred), 3),
        "model_name": "Random Forest Regressor"
    }


def get_data_preview(rows=5):
    return data.head(rows)


def get_latest_aqi():
    latest = data.tail(1).iloc[0]

    return {
        "aqi": int(latest["aqi value"]),
        "status": latest["aqi status"],
        "co": latest["co aqi value"],
        "ozone": latest["ozone aqi value"],
        "no2": latest["no2 aqi value"],
        "pm25": latest["pm2.5 aqi value"]
    }