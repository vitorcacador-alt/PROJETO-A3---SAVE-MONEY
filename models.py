
from datetime import datetime
from flask_login import UserMixin
from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship(
        "Transaction", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    recurring_incomes = db.relationship(
        "RecurringIncome", backref="user", lazy=True,
        cascade="all, delete-orphan"
    )
    goals = db.relationship(
        "Goal", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    categories = db.relationship(
        "Category", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    planning = db.relationship(
        "Planning", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    subscription = db.relationship(
        "Subscription",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(20), nullable=False)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80))
    date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(80))
    observation = db.Column(db.Text)
    is_demo = db.Column(db.Boolean, default=False)


class RecurringIncome(db.Model):
    __tablename__ = "recurring_incomes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80))
    payment_method = db.Column(db.String(80))
    observation = db.Column(db.Text)

    day_of_month = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)

    active = db.Column(db.Boolean, default=True, nullable=False)

    last_generated_year = db.Column(db.Integer)
    last_generated_month = db.Column(db.Integer)


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)
    deadline = db.Column(db.Date)

    @property
    def progress(self):
        if not self.target_amount:
            return 0
        pct = (self.current_amount / self.target_amount) * 100
        return max(0, min(100, round(pct, 1)))


class Planning(db.Model):
    __tablename__ = "planning"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    expected_income = db.Column(db.Float, default=0)
    expected_expense = db.Column(db.Float, default=0)
    monthly_limit = db.Column(db.Float, default=0)


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )
    plan = db.Column(db.String(20), default="free", nullable=False)
    status = db.Column(db.String(20), default="active", nullable=False)
    payment_method = db.Column(db.String(30))
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
