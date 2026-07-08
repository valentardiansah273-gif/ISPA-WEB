import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
import os

# Buat folder jika belum ada
os.makedirs('model_saved', exist_ok=True)

# LOAD DATA
df = pd.read_csv('data/dataset_labeled.csv')
target = 'Label_ISPA'
X = df.drop(columns=[target, 'Diagnosis'])
y = df[target]

# SIMPAN URUTAN FITUR
fitur_urutan = list(X.columns)
joblib.dump(fitur_urutan, 'model_saved/fitur_urutan.pkl')

# NORMALISASI (SCALING)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, 'model_saved/scaler.pkl') # Simpan scaler

# SPLIT DATA
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# MODEL
rf = RandomForestClassifier(random_state=42, class_weight='balanced')
param_grid = {'n_estimators': [100, 200], 'max_depth': [5, 10, None]}
grid = GridSearchCV(rf, param_grid, cv=5, n_jobs=-1)

grid.fit(X_train, y_train)

# SIMPAN MODEL
joblib.dump(grid.best_estimator_, 'model_saved/model_rf.pkl')
print("Training selesai. Scaler dan Model berhasil disimpan.")