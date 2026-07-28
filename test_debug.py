import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from imblearn.over_sampling import SMOTE

# Load data
df = pd.read_csv("data/dataset_labeled.csv")
X = df.drop(columns=["Label_ISPA", "Diagnosis"])
y = df["Label_ISPA"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("=== JUMLAH DATA TRAIN SEBELUM SMOTE ===")
print(y_train.value_counts())

# Scaling & SMOTE
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)

smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train_scaled, y_train)

print("\n=== JUMLAH DATA TRAIN SESUDAH SMOTE ===")
# Mengubah kembali ke pandas Series untuk menghitung frekuensinya
print(pd.Series(y_train_bal).value_counts())