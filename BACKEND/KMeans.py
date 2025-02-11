import pandas as pd
from transformers import BertTokenizer, BertModel
import torch
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
import numpy as np
import joblib

# Check if GPU is available and move model to GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the dataset
df = pd.read_csv('/content/supreme_court_cases4.csv')  # Ensure 'Caseid' and 'content' are in the CSV file

# Load LegalBERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('nlpaueb/legal-bert-base-uncased')
model = BertModel.from_pretrained('nlpaueb/legal-bert-base-uncased').to(device)

# Function to extract embeddings using LegalBERT
def extract_features(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}  # Move to GPU
    with torch.no_grad():
        outputs = model(**inputs)
        cls_embedding = outputs.last_hidden_state[:, 0, :].cpu().squeeze().numpy()  # [CLS] token
    return cls_embedding

# Extract features and normalize them
df['features'] = df['content'].apply(extract_features)
features_list = df['features'].tolist()
X_normalized = normalize(features_list)

# Save the normalized features to an .npz file
np.savez_compressed('normalized_features.npz', X_normalized)

# Train KMeans on the normalized features
best_num_clusters = 5  # Adjust based on your previous analysis
kmeans = KMeans(n_clusters=best_num_clusters, n_init=10, random_state=42)
df['cluster'] = kmeans.fit_predict(X_normalized)

# Save KMeans model
joblib.dump(kmeans, 'kmeans_model.pkl')

# Save the updated DataFrame (without normalized features) to CSV
df.drop(columns=['features'], inplace=True)  # Drop features column, as it's stored separately
df.to_csv('court_cases_with_clusters.csv', index=False)

print("KMeans model and CSV saved successfully!")
