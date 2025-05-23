import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.multiclass import OneVsRestClassifier
import joblib
import os

class category_predictor:
    def __init__(self):
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_df=0.8, min_df=2)),
            ('clf', OneVsRestClassifier(MultinomialNB(alpha=0.1)))
        ])
        self.categories = []
        self.is_trained = False
        
    def train(self, historical_csv='data/historical_tickets.csv'):
        if os.path.exists(historical_csv):
            df = pd.read_csv(historical_csv)
            if len(df) > 10: 
                X = df['issue_description'].fillna('')
                y = df.apply(lambda x: f"{x['category']}|{x['subcategory']}", axis=1)
                self.model.fit(X, y)
                self.categories = y.unique().tolist()
                self.is_trained = True
                joblib.dump(self.model, 'category_model.pkl')
                
    def predict_category(self, text):
        if not self.is_trained:
            return 'General', 'Uncategorized'
            
        prediction = self.model.predict([text])[0]
        return prediction.split('|')
        

#predictor = CategoryPredictor()
#predictor.train()