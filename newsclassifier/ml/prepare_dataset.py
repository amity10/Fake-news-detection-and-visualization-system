# newsclassifier/ml/prepare_dataset.py

import pandas as pd

# Load the raw datasets
df_fake = pd.read_csv('dataset/raw/Fake.csv')
df_true = pd.read_csv('dataset/raw/True.csv')

# Add labels
df_fake['label'] = 0
df_true['label'] = 1

# Combine the datasets
df_combined = pd.concat([df_fake, df_true], ignore_index=True)

# Select necessary columns (assuming 'title' and 'text' exist)
df_combined = df_combined[['title', 'text', 'label']]
df_combined = df_combined.dropna()  # Drop rows with missing values

# Save to cleaned_data.csv
df_combined.to_csv('dataset/cleaned/cleaned_data.csv', index=False)

print("✅ cleaned_data.csv created successfully.")
