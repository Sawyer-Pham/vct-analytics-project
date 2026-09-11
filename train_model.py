import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# =========================
# LOAD DATA
# =========================

df = pd.read_csv("features.csv")


# =========================
# CHOOSE FEATURES
# =========================

feature_columns = [
    "team_a_win_rate",
    "team_b_win_rate",
    "team_a_recent_win_rate",
    "team_b_recent_win_rate",
    "team_a_matches_played",
    "team_b_matches_played",
    "h2h_a_win_rate",
    "win_rate_diff",
    "recent_win_rate_diff"
]

X = df[feature_columns]

# Target: 1 = Team A wins, 0 = Team B wins
y = df["team_a_won"]


# =========================
# TRAIN / TEST SPLIT
# =========================

# First 80% of matches = training
# Last 20% of matches = testing

split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]


# =========================
# CREATE MODEL
# =========================

model = LogisticRegression(max_iter=1000)


# =========================
# TRAIN MODEL
# =========================

model.fit(X_train, y_train)


# =========================
# MAKE PREDICTIONS
# =========================

predictions = model.predict(X_test)


# =========================
# EVALUATE MODEL
# =========================

accuracy = accuracy_score(y_test, predictions)

print("Training matches:", len(X_train))
print("Testing matches:", len(X_test))
print("Accuracy:", accuracy)

print("\nClassification Report:")
print(classification_report(y_test, predictions))


# =========================
# FEATURE IMPORTANCE
# =========================

print("\nModel Coefficients:")

for feature, coefficient in zip(feature_columns, model.coef_[0]):
    print(f"{feature}: {coefficient:.4f}")