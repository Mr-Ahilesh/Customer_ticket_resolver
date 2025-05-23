# auto_approval.py
import os
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util

HISTORICAL_CSV = r"..\data\historical_tickets.csv"

class AutoApprovalSystem:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.historical_data = []
        self.embeddings = None
        self.approval_metadata = []
        self.category_thresholds = {
            'Technical': 0.85,
            'Billing': 0.78,
            'Account': 0.80,
            'General': 0.75
        }
        self._load_historical_data()

    def _load_historical_data(self):
        
        if os.path.exists(HISTORICAL_CSV):
            df = pd.read_csv(HISTORICAL_CSV)
            
           
            required_columns = [
                'ticket_id', 'customer_id', 'date_created', 'category',
                'resolution', 'issue_description'
            ]
            if not all(col in df.columns for col in required_columns):
                raise ValueError("Historical CSV missing required columns")
            
            df = df.dropna(subset=['category', 'resolution'])
            self.historical_data = df.to_dict('records')
            
            
            resolutions_with_context = [
                f"{row['category']}: {row['resolution']}" 
                for row in self.historical_data
            ]
            self.embeddings = self.model.encode(
                resolutions_with_context, 
                convert_to_tensor=True
            )

    def _get_dynamic_threshold(self, category, data_size):
        
        base_threshold = self.category_thresholds.get(category, 0.75)
        
        
        if data_size < 50:
            return max(base_threshold - 0.15, 0.5)
        elif data_size < 100:
            return max(base_threshold - 0.1, 0.6)
        return base_threshold

    def evaluate_response(self, new_issue, draft_resolution, category):
        """
        Evaluate a resolution draft against historical patterns
        Returns: 
            {
                'auto_approved': bool,
                'confidence': float,
                'threshold': float,
                'similar_ticket': dict | None,
                'category': str
            }
        """
        result_template = {
            'auto_approved': False,
            'confidence': 0.0,
            'threshold': 0.0,
            'similar_ticket': None,
            'category': category
        }

        if not self.historical_data:
            return result_template

        try:
            resolution_with_context = f"{category}: {draft_resolution}"
            draft_embedding = self.model.encode(
                resolution_with_context, 
                convert_to_tensor=True
            )

            similarities = util.cos_sim(draft_embedding, self.embeddings)[0]
            max_sim_idx = torch.argmax(similarities).item()
            max_confidence = similarities[max_sim_idx].item()

            
            data_size = len(self.historical_data)
            threshold = self._get_dynamic_threshold(category, data_size)

            
            self.approval_metadata.append({
                'category': category,
                'auto_approved': max_confidence >= threshold,
                'confidence': max_confidence,
                'threshold': threshold
            })

            return {
                'auto_approved': max_confidence >= threshold,
                'confidence': max_confidence,
                'threshold': threshold,
                'similar_ticket': self.historical_data[max_sim_idx],
                'category': category
            }

        except Exception as e:
            print(f"Approval evaluation failed: {str(e)}")
            return result_template

    def add_resolved_ticket(self, ticket_data):
        """
        Add a resolved ticket to historical data
        Requires full ticket data matching historical CSV schema
        """
        
        required_fields = [
            'ticket_id', 'customer_id', 'date_created', 'category',
            'resolution', 'issue_description'
        ]
        for field in required_fields:
            if field not in ticket_data:
                raise ValueError(f"Missing required field: {field}")

        
        self.historical_data.append(ticket_data)
        
        
        resolution_with_context = f"{ticket_data['category']}: {ticket_data['resolution']}"
        new_embedding = self.model.encode(
            resolution_with_context, 
            convert_to_tensor=True
        )
        
        if self.embeddings is None:
            self.embeddings = new_embedding.unsqueeze(0)
        else:
            self.embeddings = torch.cat([self.embeddings, new_embedding.unsqueeze(0)])

        pd.DataFrame([ticket_data]).to_csv(
            HISTORICAL_CSV, 
            mode='a', 
            header=not os.path.exists(HISTORICAL_CSV),
            index=False
        )

    def get_approval_stats(self):
        """Get performance statistics across categories"""
        if not self.approval_metadata:
            return {}

        df = pd.DataFrame(self.approval_metadata)
        stats = df.groupby('category').agg(
            total_decisions=('category', 'size'),
            approval_rate=('auto_approved', 'mean'),
            avg_confidence=('confidence', 'mean'),
            avg_threshold=('threshold', 'mean')
        ).reset_index()

        return stats.to_dict('records')

    def update_threshold(self, category, new_threshold):
        """Update approval threshold for a specific category"""
        if 0 <= new_threshold <= 1:
            self.category_thresholds[category] = new_threshold
        else:
            raise ValueError("Threshold must be between 0 and 1")


#the below portion is added for testing purposes

if __name__ == "__main__":
    
    approver = AutoApprovalSystem()
    
    test_ticket = {
        'ticket_id': 'TEST_123',
        'customer_id': 'CUST_001',
        'date_created': '2023-08-20 14:30:00',
        'category': 'Technical',
        'subcategory': 'Password',
        'priority': 'High',
        'issue_description': "Can't reset password",
        'resolution': "Use password reset tool at example.com/reset",
        'resolution_time_hours': 0,
        'customer_satisfaction': '',
        'agent_id': 'AUTO'
    }

    evaluation = approver.evaluate_response(
        new_issue=test_ticket['issue_description'],
        draft_resolution=test_ticket['resolution'],
        category=test_ticket['category']
    )

    print(f"Auto-Approved: {evaluation['auto_approved']}")
    print(f"Confidence: {evaluation['confidence']:.2%} (Threshold: {evaluation['threshold']:.2%})")
    
    if evaluation['auto_approved']:
        print("Adding to historical data...")
        approver.add_resolved_ticket(test_ticket)
