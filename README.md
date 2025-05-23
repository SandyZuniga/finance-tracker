# Finance Tracker

This is a personal finance tracker app built with Flask.

## Features

- User registration and login  
- Add income and expense transactions  
- Dashboard with summary and charts (Plotly)  
- Export transactions as CSV and PDF  

## Setup Instructions

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

2. Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
                                                                              
3. Set up the database migrations (if using Flask-Migrate):

bash
Copy
# Finance Tracker

This is a personal finance tracker app built with Flask.

## Features

- User registration and login
- Add income and expense transactions
- Dashboard with summary and charts (Plotly)
- Export transactions as CSV and PDF

## Setup Instructions

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask run
Open your browser and go to http://localhost:5000 to use the app.              
Usage
Register a new account or log in

Add income and expense transactions

View your dashboard with charts and summaries

Export your transactions as CSV or PDF files

License
This project is licensed under the MIT License.                                
---

Just open your terminal in your project folder and run:

```bash
nano README.md

