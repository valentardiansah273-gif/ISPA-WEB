import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, classification_report

# Pastikan folder model_saved ada
if not os.path.exists('model_saved'):
    os.makedirs('model_saved')

# =========================
# 1. LOAD DATA
# =========================
df = pd.read_csv('data/dataset_labeled.csv')

target = 'Label_ISPA'
X = df.drop(columns=[target, 'Diagnosis'])
y = df[target]

# =========================
# 2. SIMPAN URUTAN FITUR
# =========================
fitur_urutan = list(X.columns)
joblib.dump(fitur_urutan, 'model_saved/fitur_urutan.pkl')

# =========================
# 3. 🔥 NORMALISASI (SCALING)
# =========================
# Kita gunakan MinMaxScaler untuk mengubah semua angka ke rentang 0-1
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, 'model_saved/scaler.pkl') # Wajib disimpan untuk app.py

# =========================
# 4. SPLIT
# =========================
# Kita gunakan X_scaled untuk training
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# =========================
# 5. MODEL + TUNING
# =========================
rf = RandomForestClassifier(
    random_state=42,
    class_weight='balanced'
)

param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [5, 10, None],
    'min_samples_split': [2, 5],
}

grid = GridSearchCV(rf, param_grid, cv=5, n_jobs=-1, verbose=1)

# Training dengan data yang sudah di-scale
grid.fit(X_train, y_train)

best_model = grid.best_estimator_

# =========================
# 6. EVALUASI
# =========================
y_pred = best_model.predict(X_test)
print("\n=== HASIL EVALUASI ===")
print("Best Params:", grid.best_params_)
print("Accuracy:", accuracy_score(y_test, y_pred))

# =========================
# 7. SAVE MODEL
# =========================
joblib.dump(best_model, 'model_saved/model_rf.pkl')

print("\nSukses! 'model_rf.pkl', 'scaler.pkl', dan 'fitur_urutan.pkl' sudah diperbarui.")