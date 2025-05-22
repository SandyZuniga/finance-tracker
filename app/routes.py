from flask import Blueprint, render_template, redirect, url_for, request, flash, Response, send_file
from . import db, login_manager
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Transaction
from .forms import RegisterForm, LoginForm, TransactionForm
from werkzeug.security import generate_password_hash, check_password_hash
import plotly.graph_objs as go
from collections import defaultdict
from datetime import datetime
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def home():
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(email=form.email.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password.')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = TransactionForm()
    if form.validate_on_submit():
        new_tx = Transaction(
            type=form.type.data,
            category=form.category.data,
            amount=form.amount.data,
            user_id=current_user.id
        )
        db.session.add(new_tx)
        db.session.commit()
        return redirect(url_for('main.dashboard'))

    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    income = sum(t.amount for t in transactions if t.type == 'income')
    expense = sum(t.amount for t in transactions if t.type == 'expense')

    # Pie chart for expenses by category
    categories = [t.category for t in transactions if t.type == 'expense']
    values = [t.amount for t in transactions if t.type == 'expense']
    fig = go.Figure([go.Pie(labels=categories, values=values)])
    fig.update_layout(title='Expenses by Category')
    pie_chart = fig.to_html(full_html=False)

    # Monthly summary bar chart
    monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0})
    for t in transactions:
        month = t.date.strftime('%Y-%m')
        monthly_data[month][t.type] += t.amount

    months = sorted(monthly_data.keys())
    income_per_month = [monthly_data[m]['income'] for m in months]
    expense_per_month = [monthly_data[m]['expense'] for m in months]

    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(name='Income', x=months, y=income_per_month, marker_color='green'))
    bar_fig.add_trace(go.Bar(name='Expense', x=months, y=expense_per_month, marker_color='red'))
    bar_fig.update_layout(barmode='group', title='Monthly Income vs Expense')
    monthly_bar_chart = bar_fig.to_html(full_html=False)

    return render_template('dashboard.html', form=form, transactions=transactions,
                           income=income, expense=expense, pie_chart=pie_chart,
                           monthly_bar_chart=monthly_bar_chart)

@main.route('/export_csv')
@login_required
def export_csv():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    def generate():
        yield 'Type,Category,Amount,Date\n'
        for t in transactions:
            yield f"{t.type},{t.category},{t.amount},{t.date.strftime('%Y-%m-%d')}\n"

    return Response(
        generate(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=transactions.csv"}
    )

@main.route('/export_pdf')
@login_required
def export_pdf():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setTitle("Transactions Report")

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Personal Finance Transactions Report")

    pdf.setFont("Helvetica-Bold", 12)
    y = height - 80
    pdf.drawString(50, y, "Type")
    pdf.drawString(120, y, "Category")
    pdf.drawString(250, y, "Amount")
    pdf.drawString(350, y, "Date")

    pdf.setFont("Helvetica", 12)
    y -= 20
    for t in transactions:
        if y < 50:
            pdf.showPage()
            y = height - 50
        pdf.drawString(50, y, t.type.title())
        pdf.drawString(120, y, t.category)
        pdf.drawString(250, y, f"${t.amount:.2f}")
        pdf.drawString(350, y, t.date.strftime('%Y-%m-%d'))
        y -= 20

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='transactions.pdf', mimetype='application/pdf')
