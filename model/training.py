import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE

# =========================

# 0. FOLDER

# =========================

if not os.path.exists('model_saved'):
       os.makedirs('model_saved')

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

# 3. SPLIT DULU (PENTING!)

# =========================

X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.2, random_state=42, stratify=y
)

# =========================

# 4. SMOTE (HANYA DI TRAIN)

# =========================

smote = SMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

print("\n=== DISTRIBUSI SETELAH SMOTE ===")
print(pd.Series(y_train_res).value_counts())

# =========================

# 5. SCALER (FIT DI TRAIN SAJA)

# =========================

scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train_res)
X_test_scaled = scaler.transform(X_test)

joblib.dump(scaler, 'model_saved/scaler.pkl')

# =========================

# 6. MODEL + TUNING

# =========================

print("\nTraining model...")
rf = RandomForestClassifier(random_state=42)

param_grid = {
'n_estimators': [200, 500],
'max_depth': [10, 20, None],
'min_samples_split': [2, 5]
}

grid = GridSearchCV(rf, param_grid, cv=5, n_jobs=-1, verbose=1)
grid.fit(X_train_scaled, y_train_res)

best_model = grid.best_estimator_

# =========================

# 7. EVALUASI

# =========================

y_pred = best_model.predict(X_test_scaled)

print("\n=== HASIL EVALUASI ===")
print("Best Params:", grid.best_params_)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# =========================

# 8. SAVE MODEL

# =========================

joblib.dump(best_model, 'model_saved/model_rf.pkl')

print("\nModel, scaler, dan fitur berhasil disimpan.")

# =========================

# 9. FEATURE IMPORTANCE

# =========================

importances = best_model.feature_importances_
feature_imp = pd.Series(importances, index=fitur_urutan).sort_values(ascending=False)

print("\n=== FITUR PALING BERPENGARUH ===")
print(feature_imp)
