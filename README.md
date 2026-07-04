# Smart Ration Distribution Management System

A Flask web application to manage government ration distribution digitally — tracking beneficiaries, stock, distributions, complaints, and audit logs.

## Features

- Role-based login (Admin, Beneficiary, Shopkeeper)
- Beneficiary management (add/edit/delete)
- Stock management (ration items + shop allocation)
- Ration distribution with automatic stock deduction and duplicate prevention
- Audit logging of all key actions
- Reports: monthly distribution, stock status, performance metrics
- Complaint raising and resolution tracking

## Tech Stack

- Python, Flask
- Flask-SQLAlchemy (SQLite database)
- Jinja2 templates (HTML)
- python-dotenv for environment configuration

## Setup

1. Clone the repository

git clone https://github.com/prachipragyan2005/smart-ration-distribution-system.git
cd smart-ration-distribution-system

2. Install dependencies

pip install -r requirements.txt

3. Create a .env file in the root folder with:

SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///ration.db

4. Create the database

python create_db.py

5. Add an admin user

python add_user.py

6. Run the app

python app.py

7. Visit http://127.0.0.1:5000/login

## Default Admin Login

- Username: admin
- Password: 1234

## Project Structure

- app.py — main Flask application and routes
- models.py — database models
- templates/ — HTML templates
- create_db.py — initializes the database
- add_user.py — creates the default admin user