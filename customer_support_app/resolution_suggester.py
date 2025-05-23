from sentence_transformers import SentenceTransformer, util
import pandas as pd
import os

HISTORICAL_CSV = r'C:\Users\hello\OneDrive\Desktop\customer_support_app\data\historical_tickets.csv'
model = SentenceTransformer('all-MiniLM-L6-v2')


historical_issues = []
historical_resolutions = []
embeddings = None

if os.path.exists(HISTORICAL_CSV):
    df = pd.read_csv(HISTORICAL_CSV)
    historical_issues = df['issue_description'].tolist()
    historical_resolutions = df['resolution'].tolist()
    embeddings = model.encode(historical_issues, convert_to_tensor=True)  # SBERT-style tensor encoding

def get_suggested_resolution(new_issue):
    if not historical_issues or embeddings is None:
        return "No historical data available"
    
    new_embedding = model.encode(new_issue, convert_to_tensor=True)
    cos_scores = util.pytorch_cos_sim(new_embedding, embeddings)[0]  # SBERT-style similarity
    best_match_idx = cos_scores.argmax().item()
    return historical_resolutions[best_match_idx]