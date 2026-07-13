import pandas as pd
import joblib
import numpy as np
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from imblearn.over_sampling import SMOTE

# ==============================
# 1. LOAD DATA
# ==============================
# Pastikan file ada di folder 'data'
df = pd.read_csv("data/dataset_labeled.csv")

print("=== DATA AWAL ===")
print(df.head())

# ==============================
# 2. PREPROCESSING
# ==============================
# Hapus kolom non-numerik agar tidak error saat training
X = df.drop(columns=["Label_ISPA", "Diagnosis"])
y = df["Label_ISPA"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scaling
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Balancing dengan SMOTE
smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train_scaled, y_train)

# ==============================
# 3. HYPERPARAMETER TUNING (Grid Search)
# ==============================
print("\nSedang mencari parameter terbaik (Tuning)...")

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5]
}

rf = RandomForestClassifier(random_state=42, class_weight='balanced')

# Grid Search mencari kombinasi terbaik
grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, n_jobs=-1, scoring='accuracy')
grid_search.fit(X_train_bal, y_train_bal)

# Mengambil model terbaik
model = grid_search.best_estimator_

print(f"\nParameter terbaik ditemukan: {grid_search.best_params_}")

# ==============================
# 4. EVALUASI
# ==============================
y_pred = model.predict(X_test_scaled)

print("\n=== HASIL EVALUASI ===")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# ==============================
# 5. FEATURE IMPORTANCE
# ==============================
print("\n=== FEATURE IMPORTANCE ===")
importances = model.feature_importances_
fitur_importance = pd.DataFrame({
    "Fitur": X.columns,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

print(fitur_importance)

# ==============================
# 6. SIMPAN MODEL & ASSET
# ==============================
os.makedirs("model_saved", exist_ok=True)

joblib.dump(model, "model_saved/model_rf.pkl")
joblib.dump(scaler, "model_saved/scaler.pkl")
joblib.dump(X.columns.tolist(), "model_saved/fitur_urutan.pkl")
joblib.dump(fitur_importance, "model_saved/importance.pkl")

print("\n✅ Model, Scaler, dan Importance berhasil disimpan ke folder 'model_saved/'!")