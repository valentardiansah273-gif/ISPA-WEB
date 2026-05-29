import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# =========================
# LOAD DATA
# =========================
df = pd.read_csv('data/dataset_labeled.csv')

print("=== KOLOM DATASET ===")
print(df.columns)

# =========================
# TARGET
# =========================
target = 'Label_ISPA'

print("\nDistribusi target:")
print(df[target].value_counts())

# =========================
# DROP KOLOM STRING
# =========================
X = df.drop(columns=[target, 'Diagnosis'])  # 🔥 FIX ERROR
y = df[target]

# =========================
# 🔥 SIMPAN URUTAN FITUR (TAMBAHAN WAJIB)
# =========================
fitur_urutan = list(X.columns)
joblib.dump(fitur_urutan, 'model_saved/fitur_urutan.pkl')

print("\n=== URUTAN FITUR DISIMPAN ===")
print(fitur_urutan)

# =========================
# SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# =========================
# MODEL + TUNING
# =========================
rf = RandomForestClassifier(
    random_state=42,
    class_weight='balanced'  # 🔥 biar tidak bias
)

param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [5, 10, None],
    'min_samples_split': [2, 5],
}

grid = GridSearchCV(
    rf,
    param_grid,
    cv=5,
    n_jobs=-1,
    verbose=1
)

# =========================
# TRAIN
# =========================
grid.fit(X_train, y_train)

best_model = grid.best_estimator_

# =========================
# EVALUASI
# =========================
y_pred = best_model.predict(X_test)

print("\n=== HASIL ===")
print("Best Params:", grid.best_params_)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# =========================
# SAVE MODEL
# =========================
joblib.dump(best_model, 'model_saved/model_rf.pkl')

print("\nModel berhasil disimpan!")
print("\n=== URUTAN FITUR ===")
print(list(X.columns))