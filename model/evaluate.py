import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 1. Load data
X_test = pd.read_csv('data/X_test.csv')
y_test = pd.read_csv('data/y_test.csv').values.ravel()

# 2. Load model
model = joblib.load('model_saved/model_rf.pkl')

# 3. Prediksi (dilakukan sekali saja)
y_pred = model.predict(X_test)

# 4. Tampilkan hasil di terminal
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# 5. Visualisasi Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Non-ISPA', 'ISPA'], 
            yticklabels=['Non-ISPA', 'ISPA'])

plt.title('Confusion Matrix - Model Random Forest')
plt.xlabel('Prediksi Model')
plt.ylabel('Kondisi Aktual')

# 6. Simpan gambar
plt.savefig('confusion_matrix.png', dpi=300)
print("\nGambar 'confusion_matrix.png' berhasil dibuat!")
plt.show()