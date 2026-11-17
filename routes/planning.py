
from datetime import date
import calendar

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import extract

from extensions import db
from models import Planning, Transaction
from helpers import usuario_tem_recurso

planning_bp = Blueprint("planning", __name__)


@planning_bp.route("/planejamento", methods=["GET", "POST"])
@login_required
def index():
    plano = Planning.query.filter_by(user_id=current_user.id).first()

    if not plano:
        plano = Planning(
            user_id=current_user.id,
            expected_income=0,
            expected_expense=0,
            monthly_limit=0
        )
        db.session.add(plano)
        db.session.commit()

    if request.method == "POST":
        try:
            plano.expected_income = float(
                request.form.get("expected_income", "0").replace(",", ".")
            )
            plano.expected_expense = float(
                request.form.get("expected_expense", "0").replace(",", ".")
            )
            plano.monthly_limit = float(
                request.form.get("monthly_limit", "0").replace(",", ".")
            )

            db.session.commit()
            flash("Planejamento atualizado com sucesso.", "success")

        except ValueError:
            flash("Informe valores numéricos válidos.", "danger")

        return redirect(url_for("planning.index"))

    hoje = date.today()
    dias_no_mes = calendar.monthrange(hoje.year, hoje.month)[1]

    gasto_atual = (
        db.session.query(
            db.func.coalesce(db.func.sum(Transaction.amount), 0)
        )
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

    # Verifica se o usuário tem acesso ao planejamento avançado
    tem_planejamento_avancado = usuario_tem_recurso(
        current_user,
        "planejamento_avancado"
    )

    # Indicadores avançados
    media_diaria = gasto_atual / hoje.day if hoje.day > 0 else 0

    projecao_mensal = media_diaria * dias_no_mes

    percentual_limite = (
        (gasto_atual / plano.monthly_limit) * 100
        if plano.monthly_limit > 0
        else 0
    )

    return render_template(
        "planning.html",
        plano=plano,
        gasto_atual=round(gasto_atual, 2),
        disponivel_previsto=round(disponivel_previsto, 2),
        disponivel_limite=round(disponivel_limite, 2),
        ultrapassou=ultrapassou,
        tem_planejamento_avancado=tem_planejamento_avancado,
        media_diaria=round(media_diaria, 2),
        projecao_mensal=round(projecao_mensal, 2),
        percentual_limite=round(percentual_limite, 2)
    )

