from datetime import date
from calendar import month_abbr
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import extract

from extensions import db
from models import Transaction, Goal, Planning

dashboard_bp = Blueprint("dashboard", __name__)


def _meses_anteriores(qtd=6):
    """Retorna lista de tuplas (ano, mes) dos últimos `qtd` meses, incluindo o atual."""
    hoje = date.today()
    meses = []
    ano, mes = hoje.year, hoje.month
    for _ in range(qtd):
        meses.append((ano, mes))
        mes -= 1
        if mes == 0:
            mes = 12
            ano -= 1
    return list(reversed(meses))


@dashboard_bp.route("/dashboard")
@login_required
def index():
    hoje = date.today()
    user_id = current_user.id

    transacoes_mes = Transaction.query.filter(
        Transaction.user_id == user_id,
        extract("year", Transaction.date) == hoje.year,
        extract("month", Transaction.date) == hoje.month,
    ).all()

    receitas_mes = sum(t.amount for t in transacoes_mes if t.type == "receita")
    despesas_mes = sum(t.amount for t in transacoes_mes if t.type == "despesa")
    economia_mes = receitas_mes - despesas_mes

    qtd_receitas = sum(1 for t in transacoes_mes if t.type == "receita")
    qtd_despesas = sum(1 for t in transacoes_mes if t.type == "despesa")

    todas = Transaction.query.filter_by(user_id=user_id).all()
    saldo_atual = sum(t.amount if t.type == "receita" else -t.amount for t in todas)

    meta_atual = (
        Goal.query.filter_by(user_id=user_id)
        .order_by(Goal.id.desc())
        .first()
    )

    planning = Planning.query.filter_by(user_id=user_id).first()

    # Dados para o gráfico de receitas x despesas (últimos 6 meses)
    meses = _meses_anteriores(6)
    labels_meses = [f"{month_abbr[m].capitalize()}/{str(a)[-2:]}" for a, m in meses]
    receitas_por_mes = []
    despesas_por_mes = []
    for ano, mes in meses:
        r = sum(
            t.amount for t in todas
            if t.type == "receita" and t.date.year == ano and t.date.month == mes
        )
        d = sum(
            t.amount for t in todas
            if t.type == "despesa" and t.date.year == ano and t.date.month == mes
        )
        receitas_por_mes.append(round(r, 2))
        despesas_por_mes.append(round(d, 2))

    # Dados para o gráfico de despesas por categoria (mês atual)
    categorias = {}
    for t in transacoes_mes:
        if t.type == "despesa":
            categorias[t.category or "Outros"] = categorias.get(t.category or "Outros", 0) + t.amount

    return render_template(
        "dashboard.html",
        saldo_atual=round(saldo_atual, 2),
        receitas_mes=round(receitas_mes, 2),
        despesas_mes=round(despesas_mes, 2),
        economia_mes=round(economia_mes, 2),
        qtd_receitas=qtd_receitas,
        qtd_despesas=qtd_despesas,
        meta_atual=meta_atual,
        planning=planning,
        labels_meses=labels_meses,
        receitas_por_mes=receitas_por_mes,
        despesas_por_mes=despesas_por_mes,
        categorias_labels=list(categorias.keys()),
        categorias_valores=[round(v, 2) for v in categorias.values()],
    )
