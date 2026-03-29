import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

data = pd.read_csv('Test.csv')
print(data.head())

# Handle missing values, rename columns, and check data types
data = data.dropna()
data.columns = [col.strip().lower() for col in data.columns]

# Exploratory Data Analysis
sns.pairplot(data)
corr = data.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')

# Feature Selection
X = data[['co aqi value', 'ozone aqi value', 'no2 aqi value', 'pm2.5 aqi value']]
y = data['aqi value']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict and evaluate the model
y_pred = model.predict(X_test)

print("Mean Absolute Error:", mean_absolute_error(y_test, y_pred))
print("Mean Squared Error:", mean_squared_error(y_test, y_pred))
print("R2 Score:", r2_score(y_test, y_pred))

# ----------------------------
# Function to return Actual vs Predicted AQI figure
# ----------------------------
def plot_actual_vs_predicted():
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.scatter(y_test, y_pred)
    ax.set_xlabel("Actual AQI")
    ax.set_ylabel("Predicted AQI")
    ax.set_title("Actual vs Predicted AQI")
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

def plot_feature_importance():
    fig, ax = plt.subplots(figsize=(5, 3))

    importances = model.feature_importances_
    feature_names = ['co aqi value', 'ozone aqi value', 'no2 aqi value', 'pm2.5 aqi value']

    ax.bar(feature_names, importances)
    ax.set_title("Feature Importance")
    ax.set_ylabel("Importance")
    ax.tick_params(axis="x", rotation=20)

    fig.tight_layout()
    return fig