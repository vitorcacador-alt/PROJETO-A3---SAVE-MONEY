from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import extract

from extensions import db
from models import Planning, Transaction

planning_bp = Blueprint("planning", __name__)


@planning_bp.route("/planejamento", methods=["GET", "POST"])
@login_required
def index():
    plano = Planning.query.filter_by(user_id=current_user.id).first()
    if not plano:
        plano = Planning(user_id=current_user.id, expected_income=0, expected_expense=0, monthly_limit=0)
        db.session.add(plano)
        db.session.commit()

    if request.method == "POST":
        try:
            plano.expected_income = float(request.form.get("expected_income", "0").replace(",", "."))
            plano.expected_expense = float(request.form.get("expected_expense", "0").replace(",", "."))
            plano.monthly_limit = float(request.form.get("monthly_limit", "0").replace(",", "."))
            db.session.commit()
            flash("Planejamento atualizado com sucesso.", "success")
        except ValueError:
            flash("Informe valores numéricos válidos.", "danger")
        return redirect(url_for("planning.index"))

    hoje = date.today()
    gasto_atual = (
        db.session.query(db.func.coalesce(db.func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "despesa",
            extract("year", Transaction.date) == hoje.year,
            extract("month", Transaction.date) == hoje.month,
        )
        .scalar()
    )

    disponivel_previsto = plano.expected_income - plano.expected_expense
    disponivel_limite = plano.monthly_limit - gasto_atual
    ultrapassou = gasto_atual > plano.monthly_limit and plano.monthly_limit > 0

    return render_template(
        "planning.html",
        plano=plano,
        gasto_atual=round(gasto_atual, 2),
        disponivel_previsto=round(disponivel_previsto, 2),
        disponivel_limite=round(disponivel_limite, 2),
        ultrapassou=ultrapassou,
    )
