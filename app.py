from flask import Flask, redirect, render_template, request, url_for, flash, jsonify
from models import db, User, Expense
from os import path
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from datetime import datetime, timedelta
import json


DB_NAME = 'models.db'


def calculate_expense_stats(expenses):

    total_spent = sum(expense.amount for expense in expenses)
    today = datetime.now().date()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())

    monthly_spent = sum(
        expense.amount
        for expense in expenses
        if expense.date.date() >= month_start
    )

    weekly_spent = sum(
        expense.amount
        for expense in expenses
        if expense.date.date() >= week_start
    )

    if expenses:

        dates = {
            expense.date.date()
            for expense in expenses
        }

        average_daily = total_spent / len(dates)

    else:
        average_daily = 0


    expense_count = len(expenses)


    # Category totals

    category_totals = {
        "Food": 0,
        "Transport": 0,
        "Subscription": 0,
        "Shopping": 0,
        "Entertainment": 0,
        "Bills": 0,
        "Other": 0
    }

    for expense in expenses:

        if expense.category in category_totals:
            category_totals[expense.category] += expense.amount

    if category_totals:

        top_category = max(
            category_totals,
            key=category_totals.get
        )

        top_category_amount = category_totals[
            top_category
        ]

    else:

        top_category = "None"
        top_category_amount = 0


    return {
        "total_spent": total_spent,
        "monthly_spent": monthly_spent,
        "weekly_spent": weekly_spent,
        "average_daily": average_daily,
        "expense_count": expense_count,
        "top_category": top_category,
        "top_category_amount": top_category_amount,
        "category_totals": category_totals
    }


def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = "flebelyvqlyuerglwiuyv ujewycelyfb"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    @app.route("/")
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        return render_template("home.html")


    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            user = User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    flash("Logged in successfully!", category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('dashboard'))
                else:
                    flash("Incorrect password", category='error')
            else:
                flash('Email does not exist', category='error')

        return render_template("login.html", user=current_user)


    @app.route("/register", methods=["POST", "GET"])
    def signup():

        if request.method == "POST":
            first_name = request.form.get("fname")
            last_name = request.form.get("lname")
            email = request.form.get("email")
            password = request.form.get("password")

            if User.query.filter_by(email=email).first():
                flash('User already exists with that email', category="error")
                return render_template("signup.html")

            new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('dashboard'))

        return render_template("signup.html", user=current_user)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
        stats = calculate_expense_stats(expenses)

        return render_template("dashboard.html", expenses=expenses, **stats) 


    @app.route("/expenses")
    @login_required
    def expenses():
        expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
        stats = calculate_expense_stats(expenses)

        return render_template("expenses.html", expenses=expenses, **stats)


    @app.route("/expenses/add", methods=["POST", "GET"])
    def add_expense():
        if request.method == "POST":
            title = request.form.get("title")
            category = request.form.get("category")
            amount = float(request.form.get("amount"))
            date = datetime.strptime(request.form.get("date"), "%Y-%m-%d")
            notes = request.form.get("notes")

            new_expense = Expense(title=title, 
                                  category=category, 
                                  amount=amount, 
                                  date=date, 
                                  notes=notes, 
                                  user_id=current_user.id)
            
            db.session.add(new_expense)
            db.session.commit()
            flash('Expense added!', category='success')
            return redirect(url_for("expenses"))
        
        return render_template("add_expense.html", user=current_user)
            
    @app.route('/delete-expense', methods=['POST'])
    def delete_expense():
        expense = json.loads(request.data)
        expenseId = expense['expenseId']
        expense = Expense.query.get(expenseId)
        if expense:
            if expense.user_id == current_user.id:
                db.session.delete(expense)
                db.session.commit()

        return jsonify({})
    
    
    @app.route("/edit-expense/<int:expense_id>", methods=["GET", "POST"])
    def edit_expense(expense_id):
        expense = Expense.query.get_or_404(expense_id)
        if request.method == "POST":
            expense.title = request.form["title"]
            expense.amount = float(request.form["amount"])
            expense.category = request.form["category"]
            expense.date = datetime.strptime(request.form["date"],"%Y-%m-%d").date()
            expense.notes = request.form.get("notes", "")
            db.session.commit()
            return redirect(url_for("expenses"))
        
        return render_template("edit_expense.html", expense=expense)

    @app.route("/analytics")
    @login_required
    def analytics():

        expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
        stats = calculate_expense_stats(expenses)
        today = datetime.now().date()
        days_in_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        daily_spending = [0.0] * days_in_month.day

        for expense in expenses:
            expense_date = expense.date.date() if isinstance(expense.date, datetime) else expense.date
            if expense_date.year == today.year and expense_date.month == today.month:
                daily_spending[expense_date.day - 1] += float(expense.amount)

        return render_template(
            "analytics.html",
            expenses=expenses,
            daily_spending=daily_spending,
            chart_month=today.strftime("%B %Y"),
            **stats,
        )

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
 
