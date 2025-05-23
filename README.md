# 🛠️ Customer Ticket Resolver Agent

A Flask-based customer support ticketing system enhanced with machine learning to automate ticket classification, resolution suggestion, and intelligent approval workflows.

---

## 🚀 Overview

This system processes and resolves customer support tickets using ML models. It uses two primary datasets:

- `historical_tickets.csv`: Contains past tickets and their corresponding resolutions.
- `new_tickets.csv`: Contains incoming tickets needing classification and resolution.

---

## 🔧 Features

- 🧾 Maintains a dataset of historical support tickets.
- 📨 Processes new incoming tickets from a CSV file.
- 📂 Categorizes tickets using TF-IDF and Naive Bayes.
- 🤖 Retrieves semantically similar past tickets using SBERT.
- ✍️ Generates draft resolutions based on historical data.
- ✅ Auto-approves resolutions if confidence is high enough.
- ⏱️ Tracks resolution time for each ticket.

---

## 🧠 Machine Learning Components

### 1. Category Predictor (`category_predictor.py`)
- **Purpose:** Predicts the category and subcategory of a new ticket.
- **Tech:** TF-IDF + Multinomial Naive Bayes (One-vs-Rest).
- **Training Data:** `historical_tickets.csv`.

### 2. Resolution Suggester (`resolution_suggester.py`)
- **Purpose:** Finds the most semantically similar historical issue.
- **Tech:** Sentence-BERT (`all-MiniLM-L6-v2`) + Cosine Similarity.

### 3. Auto-Approval System (`auto_approval.py`)
- **Purpose:** Auto-approves suggestions based on similarity scores.
- **Logic:** Compares cosine similarity against category-specific thresholds.

---

## 🌐 Application Routes

| Route | Description |
|-------|-------------|
| `/` | Home page |
| `/submit_ticket` | Form to submit new tickets |
| `/customer/dashboard` | Customer's ticket dashboard |
| `/admin/login` | Admin login page |
| `/admin/dashboard` | Admin dashboard for reviewing tickets |
| `/resolve/<ticket_id>` | Admin resolution endpoint |
| `/admin/thresholds` | Adjust auto-approval thresholds |

---

## 📁 Data Files

- `data/historical_tickets.csv`: Past tickets and resolutions
- `data/tickets.csv`: Current submitted tickets

**Historical fields include:**  
`ticket_id`, `customer_id`, `date_created`, `category`, `subcategory`, `priority`, `issue_description`, `resolution`, `resolution_time_hours`, `customer_satisfaction`, `agent_id`

---

## 🔐 Admin Credentials

- **Username:** `admin`
- **Password:** `admin123`

---

## ⚙️ Adjusting Auto-Approval Thresholds

Admins can fine-tune auto-approval thresholds for each category via `/admin/thresholds`. This allows control over the confidence required to auto-approve a resolution.

---

## 📌 Requirements

- Python 3.7+
- Flask
- scikit-learn
- pandas
- sentence-transformers

Install dependencies:

```bash
pip install -r requirements.txt
