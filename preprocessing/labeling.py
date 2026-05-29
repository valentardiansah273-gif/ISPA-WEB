import pandas as pd

df = pd.read_csv('data/dataset_ispa.csv')

# Mapping label
ispa = ['Bronkitis', 'Demam Biasa', 'Faringitis', 'Laringitis', 'Pneumonia', 'Sinusitis']
non_ispa = ['Asma', 'Tidak ISPA']

def label_func(x):
    if x in ispa:
        return 1
    else:
        return 0

df['Label_ISPA'] = df['Diagnosis'].apply(label_func)

df.to_csv('data/dataset_labeled.csv', index=False)

print("Labeling selesai!")