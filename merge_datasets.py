# merge_datasets.py
import pandas as pd
import os
from sklearn.utils import shuffle

# ----------------------
# Paths
# ----------------------
DATA_DIR = r"C:\Users\AMIT YADAV\OneDrive\Desktop\fake news detection and visualization project\NEWS TRAINING"

kaggle_path = os.path.join(DATA_DIR, "news.csv")
guardian_path = os.path.join(DATA_DIR, "guardian_articles_labeled.csv")
hindi_path = os.path.join(DATA_DIR, "hindi_dataset.csv")
marathi_path = os.path.join(DATA_DIR, "marathi_dataset.csv")

merged_output_path = os.path.join(DATA_DIR, "merged_training_dataset.csv")

# ----------------------
# Load datasets
# ----------------------
kaggle = pd.read_csv(kaggle_path)
guardian = pd.read_csv(guardian_path)
hindi = pd.read_csv(hindi_path)
marathi = pd.read_csv(marathi_path)

# ----------------------
# Sample Kaggle: 5000 REAL + 5000 FAKE
# ----------------------
kaggle_real = kaggle[kaggle['label']==1].sample(n=5000, random_state=42)
kaggle_fake = kaggle[kaggle['label']==0].sample(n=5000, random_state=42)
kaggle_sample = pd.concat([kaggle_real, kaggle_fake])
kaggle_sample['webUrl'] = ""  # Kaggle has no URLs
kaggle_sample = kaggle_sample[['text', 'label', 'webUrl']]

# ----------------------
# Sample Hindi: 5000 REAL + 5000 FAKE
# ----------------------
hindi_real = hindi[hindi['label']==1].sample(n=5000, random_state=42)
hindi_fake = hindi[hindi['label']==0].sample(n=5000, random_state=42)
hindi_sample = pd.concat([hindi_real, hindi_fake])
hindi_sample['webUrl'] = ""
hindi_sample = hindi_sample[['text', 'label', 'webUrl']]

# ----------------------
# Sample Marathi: 5000 REAL + 5000 FAKE
# ----------------------
marathi_real = marathi[marathi['label']==1].sample(n=5000, random_state=42)
marathi_fake = marathi[marathi['label']==0].sample(n=5000, random_state=42)
marathi_sample = pd.concat([marathi_real, marathi_fake])
marathi_sample['webUrl'] = ""
marathi_sample = marathi_sample[['text', 'label', 'webUrl']]

# ----------------------
# Guardian: Keep all (with URLs)
# ----------------------
guardian_sample = guardian[['bodyContent', 'label', 'webUrl']].copy()
guardian_sample.rename(columns={'bodyContent':'text'}, inplace=True)

# ----------------------
# Merge all
# ----------------------
merged_df = pd.concat([kaggle_sample, hindi_sample, marathi_sample, guardian_sample], ignore_index=True)
merged_df = shuffle(merged_df, random_state=42)

# ----------------------
# Save
# ----------------------
merged_df.to_csv(merged_output_path, index=False)
print(f"✅ Merged dataset saved at {merged_output_path}")
print(f"Total samples: {len(merged_df)}")
