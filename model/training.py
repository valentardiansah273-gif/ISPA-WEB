import pandas as pd
import joblib
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.linear_model import LogisticRegression

from imblearn.over_sampling import SMOTE

# ==============================
# LOAD DATA
# ==============================
df = pd.read_csv("data/dataset_labeled.csv")

print("=== DATA AWAL ===")
print(df.head())

# ==============================
# PISAHKAN LABEL
# ==============================
y = df["Label_ISPA"]
X = df.drop(columns=["Label_ISPA"])

# ==============================
# BUANG NON NUMERIK (FIX ERROR)
# ==============================
X = X.select_dtypes(include=['int64', 'float64'])

print("\nKolom fitur:")
print(X.columns)

# ==============================
# DISTRIBUSI DATA
# ==============================
print("\n=== DISTRIBUSI AWAL ===")
print(y.value_counts())

# ==============================
# SPLIT
# ==============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ==============================
# SCALING
# ==============================
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==============================
# SMOTE (BALANCING)
# ==============================
smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train_scaled, y_train)

print("\n=== SETELAH SMOTE ===")
print(pd.Series(y_train_bal).value_counts())

# ==============================
# MODEL
# ==============================
model = LogisticRegression(
    max_iter=1000,
    class_weight='balanced'
)

print("\nTraining model...")
model.fit(X_train_bal, y_train_bal)

# ==============================
# EVALUASI
# ==============================
y_pred = model.predict(X_test_scaled)
y_prob = model.predict_proba(X_test_scaled)

print("\n=== HASIL EVALUASI ===")
print("Accuracy:", accuracy_score(y_test, y_pred))

print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

print("\nClassification Report:\n", classification_report(y_test, y_pred))

# ==============================
# FEATURE IMPORTANCE
# ==============================
print("\n=== FEATURE IMPORTANCE ===")

importance = model.coef_[0]

fitur_importance = pd.DataFrame({
    "Fitur": X.columns,
    "Importance": importance
})

# urutkan dari terbesar
fitur_importance = fitur_importance.sort_values(by="Importance", ascending=False)

print(fitur_importance)

# ==============================
# SIMPAN
# ==============================
joblib.dump(model, "model_saved/model_rf.pkl")
joblib.dump(scaler, "model_saved/scaler.pkl")
joblib.dump(X.columns.tolist(), "model_saved/fitur_urutan.pkl")
joblib.dump(fitur_importance, "model_saved/importance.pkl")

print("\n✅ Semua file berhasil disimpan ke folder model_saved!")