
from datetime import date
from calendar import month_abbr

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Transaction, Goal, Planning
from helpers import usuario_tem_recurso


dashboard_bp = Blueprint("dashboard", __name__)


def _meses_anteriores(qtd=6):
    """Retorna os últimos meses, incluindo o atual."""
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


def _calcular_variacao(atual, anterior):
    """Calcula a variação percentual entre dois valores."""
    if anterior == 0:
        return 0 if atual == 0 else None

    return round(((atual - anterior) / abs(anterior)) * 100, 2)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    hoje = date.today()
    user_id = current_user.id

    transacoes_mes = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.date >= hoje.replace(day=1),
        Transaction.date <= hoje,
    ).all()

    receitas_mes = sum(t.amount for t in transacoes_mes if t.type == "receita")
    despesas_mes = sum(t.amount for t in transacoes_mes if t.type == "despesa")
    economia_mes = receitas_mes - despesas_mes

    qtd_receitas = sum(1 for t in transacoes_mes if t.type == "receita")
    qtd_despesas = sum(1 for t in transacoes_mes if t.type == "despesa")

    todas = Transaction.query.filter_by(user_id=user_id).all()

    saldo_atual = sum(
        t.amount if t.type == "receita" else -t.amount
        for t in todas
    )

    meta_atual = (
        Goal.query.filter_by(user_id=user_id)
        .order_by(Goal.id.desc())
        .first()
    )

    planning = Planning.query.filter_by(user_id=user_id).first()

    # Gráfico de receitas x despesas dos últimos 6 meses
    meses = _meses_anteriores(6)

    labels_meses = [
        f"{month_abbr[m].capitalize()}/{str(a)[-2:]}"
        for a, m in meses
    ]

    receitas_por_mes = []
    despesas_por_mes = []

    for ano, mes in meses:
        r = sum(
            t.amount for t in todas
            if t.type == "receita"
            and t.date.year == ano
            and t.date.month == mes
        )

        d = sum(
            t.amount for t in todas
            if t.type == "despesa"
            and t.date.year == ano
            and t.date.month == mes
        )

        receitas_por_mes.append(round(r, 2))
        despesas_por_mes.append(round(d, 2))

    # Gráfico de despesas por categoria
    categorias = {}

    for t in transacoes_mes:
        if t.type == "despesa":
            categoria = t.category or "Outros"
            categorias[categoria] = categorias.get(categoria, 0) + t.amount

    # Verificação dos recursos do plano
    tem_comparacao_mensal = usuario_tem_recurso(
        current_user,
        "comparacao_mensal"
    )

    tem_exportacao_relatorios = usuario_tem_recurso(
        current_user,
        "exportacao_relatorios"
    )

    tem_alertas_gastos = usuario_tem_recurso(
        current_user,
        "alertas_gastos"
    )

    # Sistema de alertas de gastos
    alerta_gastos = None
    percentual_limite = 0
    valor_limite = 0
    valor_excedido = 0

    if tem_alertas_gastos and planning:
        valor_limite = float(planning.monthly_limit or 0)

        if valor_limite > 0:
            percentual_limite = round(
                (despesas_mes / valor_limite) * 100,
                1
            )

            if percentual_limite >= 80:
                if despesas_mes > valor_limite:
                    alerta_gastos = "ultrapassado"
                    valor_excedido = round(
                        despesas_mes - valor_limite,
                        2
                    )
                else:
                    alerta_gastos = "atencao"

    receitas_mes_anterior = 0
    despesas_mes_anterior = 0
    economia_mes_anterior = 0

    variacao_receitas = 0
    variacao_despesas = 0
    variacao_economia = 0

    if tem_comparacao_mensal:
        if hoje.month == 1:
            ano_anterior = hoje.year - 1
            mes_anterior = 12
        else:
            ano_anterior = hoje.year
            mes_anterior = hoje.month - 1

        transacoes_mes_anterior = [
            t for t in todas
            if t.date.year == ano_anterior
            and t.date.month == mes_anterior
        ]

        receitas_mes_anterior = sum(
            t.amount for t in transacoes_mes_anterior
            if t.type == "receita"
        )

        despesas_mes_anterior = sum(
            t.amount for t in transacoes_mes_anterior
            if t.type == "despesa"
        )

        economia_mes_anterior = (
            receitas_mes_anterior - despesas_mes_anterior
        )

        variacao_receitas = _calcular_variacao(
            receitas_mes,
            receitas_mes_anterior
        )

        variacao_despesas = _calcular_variacao(
            despesas_mes,
            despesas_mes_anterior
        )

        variacao_economia = _calcular_variacao(
            economia_mes,
            economia_mes_anterior
        )

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
        categorias_valores=[
            round(v, 2) for v in categorias.values()
        ],
        tem_comparacao_mensal=tem_comparacao_mensal,
        tem_exportacao_relatorios=tem_exportacao_relatorios,
        tem_alertas_gastos=tem_alertas_gastos,
        alerta_gastos=alerta_gastos,
        percentual_limite=percentual_limite,
        valor_limite=round(valor_limite, 2),
        valor_excedido=valor_excedido,
        receitas_mes_anterior=round(receitas_mes_anterior, 2),
        despesas_mes_anterior=round(despesas_mes_anterior, 2),
        economia_mes_anterior=round(economia_mes_anterior, 2),
        variacao_receitas=variacao_receitas,
        variacao_despesas=variacao_despesas,
        variacao_economia=variacao_economia,
    )



