# 🛠️ Customer Ticket Resolver Agent

A **Flask-based customer support ticketing system** that leverages machine learning to automatically classify, retrieve, and draft responses for incoming support tickets. Designed to reduce response time and increase efficiency in help desk operations.

---

## 📌 Features

- Maintains and uses historical support tickets for model training and resolution suggestions.
- Automatically classifies new tickets into predefined categories using **TF-IDF + Naive Bayes**.
- Retrieves semantically similar past tickets using **Sentence-BERT (SBERT)**.
- Suggests resolutions based on past data and computes auto-approval eligibility.
- Simulates a manual approval/edit workflow before finalizing responses.
- Logs resolution time and generates output reports.

---

## 🧠 Machine Learning Components

### 1. `category_predictor.py` – Category Predictor
- **Goal**: Predicts category and subcategory from issue description.
- **Tech**: `TF-IDF` vectorization + `Multinomial Naive Bayes` (One-vs-Rest strategy).
- **Training Data**: `historical_tickets.csv`.

### 2. `resolution_suggester.py` – Resolution Suggester
- **Goal**: Recommends solutions by finding similar historical tickets.
- **Tech**: `Sentence-BERT` (`all-MiniLM-L6-v2`) for embeddings + `cosine similarity`.

### 3. `auto_approval.py` – Auto-Approval System
- **Goal**: Approves resolution drafts automatically if they meet similarity thresholds.
- **Tech**: Cosine similarity comparisons with category-specific thresholds.

---

## 🚀 Application Routes

| Route | Description |
|-------|-------------|
| `/` | Home page |
| `/submit_ticket` | Form to submit new tickets |
| `/customer/dashboard` | Displays tickets and statuses for customers |
| `/admin/login` | Admin login portal |
| `/admin/dashboard` | Displays unresolved tickets with ML suggestions |
| `/resolve/<ticket_id>` | Admin endpoint to resolve tickets manually |
| `/admin/thresholds` | View & modify auto-approval thresholds by category |

---

## 🗂️ Data Files

- `data/historical_tickets.csv`: Historical records with fields like `ticket_id`, `customer_id`, `category`, `issue_description`, `resolution`, etc.
- `data/tickets.csv`: New tickets submitted through the app.

---

## 🔐 Admin Credentials

- **Username**: `admin`  
- **Password**: `admin123`

---

## ⚙️ Adjusting Auto-Approval Thresholds

To fine-tune auto-approval sensitivity per category:
- Visit `/admin/thresholds`
- Update the category-specific cosine similarity thresholds as needed

---


