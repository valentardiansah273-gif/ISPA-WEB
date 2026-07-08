import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE

# =========================
# 0. PERSIAPAN FOLDER
# =========================
if not os.path.exists('model_saved'):
    os.makedirs('model_saved')
    print("Folder 'model_saved' berhasil dibuat.")

# =========================
# 1. LOAD DATA
# =========================
df = pd.read_csv('data/dataset_labeled.csv')
target = 'Label_ISPA'
X = df.drop(columns=[target, 'Diagnosis'])
y = df[target]

print("\n=== DISTRIBUSI KELAS (Sebelum SMOTE) ===")
print(y.value_counts())

# =========================
# 2. SIMPAN URUTAN FITUR
# =========================
fitur_urutan = list(X.columns)
joblib.dump(fitur_urutan, 'model_saved/fitur_urutan.pkl')

# =========================
# 3. NORMALISASI & PENYEIMBANGAN (SMOTE)
# =========================
# Scaling dulu baru SMOTE
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, 'model_saved/scaler.pkl')

# SMOTE untuk mengatasi akurasi yang stuck
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_scaled, y)

print("\n=== DISTRIBUSI KELAS (Setelah SMOTE) ===")
print(y_resampled.value_counts())

# =========================
# 4. SPLIT DATA
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.2, random_state=42
)

# =========================
# 5. MODEL + TUNING
# =========================
print("\nMemulai training model...")
rf = RandomForestClassifier(random_state=42)

param_grid = {
    'n_estimators': [200, 500],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5]
}

grid = GridSearchCV(rf, param_grid, cv=5, n_jobs=-1, verbose=1)
grid.fit(X_train, y_train)

best_model = grid.best_estimator_

# =========================
# 6. EVALUASI
# =========================
y_pred = best_model.predict(X_test)
print("\n=== HASIL EVALUASI ===")
print("Best Params:", grid.best_params_)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# =========================
# 7. SAVE MODEL
# =========================
joblib.dump(best_model, 'model_saved/model_rf.pkl')
print("\nProses selesai. Model, Scaler, dan Urutan Fitur tersimpan.")