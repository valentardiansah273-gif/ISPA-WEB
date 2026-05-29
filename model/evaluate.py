import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

X_test = pd.read_csv('data/X_test.csv')
y_test = pd.read_csv('data/y_test.csv').values.ravel()

model = joblib.load('model_saved/model_rf.pkl')

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))