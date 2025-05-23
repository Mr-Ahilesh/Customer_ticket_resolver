from flask import Flask, render_template, request, redirect, url_for, session
import csv
import uuid
from datetime import datetime
from category_predictor import category_predictor
from resolution_suggester import get_suggested_resolution
from auto_approval import AutoApprovalSystem
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

auto_approver = AutoApprovalSystem()
predictor = category_predictor()
predictor.train()

TICKETS_CSV = r"..data\tickets.csv"
HISTORICAL_CSV = r'..\data\historical_tickets.csv'

CSV_HEADERS = [
    'ticket_id', 'customer_id', 'date_created', 'category', 
    'subcategory', 'priority', 'issue_description', 'resolution', 
    'resolution_time_hours', 'customer_satisfaction', 'agent_id'
]

def init_csv():
    if not os.path.exists(TICKETS_CSV):
        with open(TICKETS_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

init_csv()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_ticket', methods=['GET', 'POST'])
def submit_ticket():
    if request.method == 'POST':
        ticket_data = {
            'ticket_id': str(uuid.uuid4()),
            'customer_id': request.form['customer_id'],
            'date_created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'priority': request.form['priority'],
            'issue_description': request.form['issue_description'],
            'resolution': '',
            'resolution_time_hours': '',
            'customer_satisfaction': '',
            'agent_id': ''
        }
        
        category, subcategory = predictor.predict_category(ticket_data['issue_description'])
        suggested_resolution = get_suggested_resolution(ticket_data['issue_description'])
        
        approval_result = auto_approver.evaluate_response(
            new_issue=ticket_data['issue_description'],
            draft_resolution=suggested_resolution,
            category=category
        )
        
        if approval_result['auto_approved']:
            ticket_data.update({
                'resolution': suggested_resolution,
                'resolution_time_hours': 0,
                'agent_id': 'AUTO'
            })
        

        with open(TICKETS_CSV, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                ticket_data['ticket_id'],
                ticket_data['customer_id'],
                ticket_data['date_created'],
                category,
                subcategory,
                ticket_data['priority'],
                ticket_data['issue_description'],
                ticket_data['resolution'],
                ticket_data['resolution_time_hours'],
                ticket_data['customer_satisfaction'],
                ticket_data['agent_id']
            ])
            
        return redirect(url_for('index'))
    
    return render_template('submit_ticket.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    tickets = []
    with open(TICKETS_CSV, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        tickets = [row for row in reader if not row['resolution']]
    
   
    for ticket in tickets:
        
        ticket = dict(ticket)
        ticket['suggested_resolution'] = get_suggested_resolution(ticket['issue_description'])
        approval_result = auto_approver.evaluate_response(
            ticket['issue_description'],
            ticket['suggested_resolution'],
            ticket['category']
        )
        ticket['auto_approve_status'] = approval_result
    
    stats = auto_approver.get_approval_stats()
    
    return render_template('admin_dashboard.html', 
                        tickets=tickets,
                        approval_stats=stats)

@app.route('/resolve/<ticket_id>', methods=['POST'])
def resolve_ticket(ticket_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    
    updated = False
    rows = []
    with open(TICKETS_CSV, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ticket_id'] == ticket_id:
                row.update({
                    'resolution': request.form['resolution'],
                    'resolution_time_hours': request.form['resolution_time'],
                    'agent_id': 'ADMIN_'+session.get('admin_id', '001')
                })
                updated = True
            rows.append(row)
    
    
    if updated:
        with open(TICKETS_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    
    return redirect(url_for('admin_dashboard'))

@app.route('/customer/dashboard', methods=['GET', 'POST'])
def customer_dashboard():
    tickets = []
    customer_id = None
    
    if request.method == 'POST':
        if 'customer_id' in request.form:
            customer_id = request.form['customer_id']
            session['customer_id'] = customer_id
        elif 'ticket_id' in request.form and 'satisfaction' in request.form:
            # Update satisfaction
            ticket_id = request.form['ticket_id']
            satisfaction = request.form['satisfaction']
            
            # Update in tickets.csv
            rows = []
            with open(TICKETS_CSV, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                for row in rows:
                    if row['ticket_id'] == ticket_id:
                        row['customer_satisfaction'] = satisfaction
            
            with open(TICKETS_CSV, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
    
    if customer_id := session.get('customer_id'):
        with open(TICKETS_CSV, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            tickets = [row for row in reader if row['customer_id'] == customer_id]
            
            # Add suggested resolutions (NEW CODE TO ADD)
            for ticket in tickets:
                if not ticket['resolution']:
                    ticket['suggested_resolution'] = get_suggested_resolution(ticket['issue_description'])
                else:
                    ticket['suggested_resolution'] = ticket['resolution']
    
    return render_template('customer_dashboard.html', tickets=tickets)

@app.route('/admin/thresholds', methods=['GET', 'POST'])
def manage_thresholds():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        for category in auto_approver.category_thresholds:
            new_threshold = request.form.get(f'threshold_{category}')
            if new_threshold:
                try:
                    auto_approver.update_threshold(category, float(new_threshold))
                except ValueError:
                    pass
    
    stats = auto_approver.get_approval_stats()
    return render_template('admin_thresholds.html',
                         thresholds=auto_approver.category_thresholds,
                         stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
