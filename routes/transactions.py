
from datetime import datetime, date
import calendar

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Transaction, Category, RecurringIncome
from helpers import usuario_tem_recurso

transactions_bp = Blueprint("transactions", __name__)


def _parse_data(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _tem_acesso_recorrencias():
    return usuario_tem_recurso(current_user, "transacoes_recorrentes")


def _bloquear_recorrencias():
    if not _tem_acesso_recorrencias():
        flash(
            "Receitas recorrentes são exclusivas dos planos Pro e Business. "
            "Conheça nossos planos para desbloquear esse recurso.",
            "warning"
        )
        return redirect(url_for("subscriptions.plans"))

    return None


def _gerar_receitas_recorrentes():
    if not _tem_acesso_recorrencias():
        return

    hoje = date.today()

    recorrencias = RecurringIncome.query.filter_by(
        user_id=current_user.id,
        active=True
    ).all()

    alterou = False

    for recorrencia in recorrencias:
        if recorrencia.start_date > hoje:
            continue

        ano = hoje.year
        mes = hoje.month

        if (
            recorrencia.last_generated_year == ano
            and recorrencia.last_generated_month == mes
        ):
            continue

        ultimo_dia = calendar.monthrange(ano, mes)[1]
        dia = min(recorrencia.day_of_month, ultimo_dia)
        data_lancamento = date(ano, mes, dia)

        if data_lancamento < recorrencia.start_date:
            continue

        transacao = Transaction(
            user_id=current_user.id,
            type="receita",
            description=recorrencia.description,
            amount=recorrencia.amount,
            category=recorrencia.category,
            date=data_lancamento,
            payment_method=recorrencia.payment_method,
            observation=recorrencia.observation
        )

        db.session.add(transacao)

        recorrencia.last_generated_year = ano
        recorrencia.last_generated_month = mes
        alterou = True

    if alterou:
        db.session.commit()


def _listar(tipo, template):
    user_id = current_user.id
    busca = request.args.get("busca", "").strip()
    data_inicio = _parse_data(request.args.get("data_inicio"))
    data_fim = _parse_data(request.args.get("data_fim"))
    categoria = request.args.get("categoria", "")

    query = Transaction.query.filter_by(user_id=user_id, type=tipo)

    if busca:
        query = query.filter(Transaction.description.ilike(f"%{busca}%"))
    if data_inicio:
        query = query.filter(Transaction.date >= data_inicio)
    if data_fim:
        query = query.filter(Transaction.date <= data_fim)
    if categoria:
        query = query.filter(Transaction.category == categoria)

    itens = query.order_by(Transaction.date.desc()).all()

    categorias = Category.query.filter_by(
        user_id=user_id, type=tipo
    ).order_by(Category.name).all()

    recorrencias = []

    if tipo == "receita" and _tem_acesso_recorrencias():
        recorrencias = RecurringIncome.query.filter_by(
            user_id=user_id
        ).order_by(RecurringIncome.id.desc()).all()

    return render_template(
        template,
        itens=itens,
        categorias=categorias,
        recorrencias=recorrencias,
        filtros={
            "busca": busca,
            "data_inicio": request.args.get("data_inicio", ""),
            "data_fim": request.args.get("data_fim", ""),
            "categoria": categoria,
        },
        tem_acesso_recorrencias=_tem_acesso_recorrencias(),
    )


def _criar_ou_editar(tipo, redirect_endpoint, transacao=None):
    descricao = request.form.get("description", "").strip()
    valor = request.form.get("amount", "").replace(",", ".")
    categoria = request.form.get("category", "")
    data = _parse_data(request.form.get("date"))
    forma = request.form.get("payment_method", "")
    observacao = request.form.get("observation", "")

    erros = []

    if not descricao:
        erros.append("Informe uma descrição.")

    try:
        valor_float = float(valor)
        if valor_float <= 0:
            erros.append("O valor deve ser maior que zero.")
    except (ValueError, TypeError):
        erros.append("Informe um valor numérico válido.")
        valor_float = 0

    if not data:
        erros.append("Informe uma data válida.")

    if erros:
        for erro in erros:
            flash(erro, "danger")
        return False

    if transacao is None:
        transacao = Transaction(user_id=current_user.id, type=tipo)
        db.session.add(transacao)

    transacao.description = descricao
    transacao.amount = valor_float
    transacao.category = categoria
    transacao.date = data
    transacao.payment_method = forma
    transacao.observation = observacao

    db.session.commit()
    return True


# ---------- RECEITAS ----------

@transactions_bp.route("/receitas")
@login_required
def receitas():
    _gerar_receitas_recorrentes()
    return _listar("receita", "income.html")


@transactions_bp.route("/receitas/nova", methods=["POST"])
@login_required
def nova_receita():
    if _criar_ou_editar("receita", "transactions.receitas"):
        flash("Receita adicionada com sucesso.", "success")

    return redirect(url_for("transactions.receitas"))


@transactions_bp.route("/receitas/editar/<int:id>", methods=["POST"])
@login_required
def editar_receita(id):
    t = Transaction.query.filter_by(
        id=id, user_id=current_user.id, type="receita"
    ).first_or_404()

    if _criar_ou_editar("receita", "transactions.receitas", transacao=t):
        flash("Receita atualizada com sucesso.", "success")

    return redirect(url_for("transactions.receitas"))


@transactions_bp.route("/receitas/excluir/<int:id>", methods=["POST"])
@login_required
def excluir_receita(id):
    t = Transaction.query.filter_by(
        id=id, user_id=current_user.id, type="receita"
    ).first_or_404()

    db.session.delete(t)
    db.session.commit()

    flash("Receita excluída com sucesso.", "success")
    return redirect(url_for("transactions.receitas"))


# ---------- RECEITAS RECORRENTES ----------

@transactions_bp.route("/receitas/recorrente/nova", methods=["POST"])
@login_required
def nova_receita_recorrente():
    bloqueio = _bloquear_recorrencias()
    if bloqueio:
        return bloqueio

    descricao = request.form.get("description", "").strip()
    valor = request.form.get("amount", "").replace(",", ".")
    categoria = request.form.get("category", "")
    forma = request.form.get("payment_method", "")
    observacao = request.form.get("observation", "")
    data_inicio = _parse_data(request.form.get("start_date"))

    try:
        valor_float = float(valor)
    except (ValueError, TypeError):
        valor_float = 0

    try:
        dia = int(request.form.get("day_of_month", "0"))
    except (ValueError, TypeError):
        dia = 0

    if not descricao or valor_float <= 0 or not data_inicio or not 1 <= dia <= 31:
        flash("Confira os dados da receita recorrente.", "danger")
        return redirect(url_for("transactions.receitas"))

    recorrencia = RecurringIncome(
        user_id=current_user.id,
        description=descricao,
        amount=valor_float,
        category=categoria,
        payment_method=forma,
        observation=observacao,
        day_of_month=dia,
        start_date=data_inicio
    )

    db.session.add(recorrencia)
    db.session.commit()

    _gerar_receitas_recorrentes()

    flash("Receita recorrente cadastrada com sucesso.", "success")
    return redirect(url_for("transactions.receitas"))


@transactions_bp.route("/receitas/recorrente/editar/<int:id>", methods=["POST"])
@login_required
def editar_receita_recorrente(id):
    bloqueio = _bloquear_recorrencias()
    if bloqueio:
        return bloqueio

    recorrencia = RecurringIncome.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    descricao = request.form.get("description", "").strip()
    valor = request.form.get("amount", "").replace(",", ".")
    categoria = request.form.get("category", "")
    forma = request.form.get("payment_method", "")
    observacao = request.form.get("observation", "")

    try:
        valor_float = float(valor)
    except (ValueError, TypeError):
        valor_float = 0

    try:
        dia = int(request.form.get("day_of_month", "0"))
    except (ValueError, TypeError):
        dia = 0

    if not descricao or valor_float <= 0 or not 1 <= dia <= 31:
        flash("Confira os dados da receita recorrente.", "danger")
        return redirect(url_for("transactions.receitas"))

    recorrencia.description = descricao
    recorrencia.amount = valor_float
    recorrencia.category = categoria
    recorrencia.payment_method = forma
    recorrencia.observation = observacao
    recorrencia.day_of_month = dia

    db.session.commit()

    flash("Receita recorrente atualizada com sucesso.", "success")
    return redirect(url_for("transactions.receitas"))


@transactions_bp.route("/receitas/recorrente/alternar/<int:id>", methods=["POST"])
@login_required
def alternar_receita_recorrente(id):
    bloqueio = _bloquear_recorrencias()
    if bloqueio:
        return bloqueio

    recorrencia = RecurringIncome.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    recorrencia.active = not recorrencia.active
    db.session.commit()

    flash(
        "Receita recorrente reativada." if recorrencia.active
        else "Receita recorrente pausada.",
        "success"
    )

    return redirect(url_for("transactions.receitas"))


@transactions_bp.route("/receitas/recorrente/excluir/<int:id>", methods=["POST"])
@login_required
def excluir_receita_recorrente(id):
    bloqueio = _bloquear_recorrencias()
    if bloqueio:
        return bloqueio

    recorrencia = RecurringIncome.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    db.session.delete(recorrencia)
    db.session.commit()

    flash(
        "Recorrência excluída. Os lançamentos anteriores foram preservados.",
        "success"
    )

    return redirect(url_for("transactions.receitas"))


# ---------- DESPESAS ----------

@transactions_bp.route("/despesas")
@login_required
def despesas():
    return _listar("despesa", "expenses.html")


@transactions_bp.route("/despesas/nova", methods=["POST"])
@login_required
def nova_despesa():
    if _criar_ou_editar("despesa", "transactions.despesas"):
        flash("Despesa adicionada com sucesso.", "success")

    return redirect(url_for("transactions.despesas"))


@transactions_bp.route("/despesas/editar/<int:id>", methods=["POST"])
@login_required
def editar_despesa(id):
    t = Transaction.query.filter_by(
        id=id, user_id=current_user.id, type="despesa"
    ).first_or_404()

    if _criar_ou_editar("despesa", "transactions.despesas", transacao=t):
        flash("Despesa atualizada com sucesso.", "success")

    return redirect(url_for("transactions.despesas"))


@transactions_bp.route("/despesas/excluir/<int:id>", methods=["POST"])
@login_required
def excluir_despesa(id):
    t = Transaction.query.filter_by(
        id=id, user_id=current_user.id, type="despesa"
    ).first_or_404()

    db.session.delete(t)
    db.session.commit()

    flash("Despesa excluída com sucesso.", "success")
    return redirect(url_for("transactions.despesas"))


# ---------- HISTÓRICO / TRANSAÇÕES ----------

@transactions_bp.route("/transacoes")
@login_required
def historico():
    user_id = current_user.id
    tipo = request.args.get("tipo", "todas")
    busca = request.args.get("busca", "").strip()
    data_inicio = _parse_data(request.args.get("data_inicio"))
    data_fim = _parse_data(request.args.get("data_fim"))
    categoria = request.args.get("categoria", "")

    query = Transaction.query.filter_by(user_id=user_id)

    if tipo in ("receita", "despesa"):
        query = query.filter_by(type=tipo)
    if busca:
        query = query.filter(Transaction.description.ilike(f"%{busca}%"))
    if data_inicio:
        query = query.filter(Transaction.date >= data_inicio)
    if data_fim:
        query = query.filter(Transaction.date <= data_fim)
    if categoria:
        query = query.filter(Transaction.category == categoria)

    itens = query.order_by(Transaction.date.desc()).all()

    todas_categorias = Category.query.filter_by(
        user_id=user_id
    ).order_by(Category.name).all()

    return render_template(
        "transactions.html",
        itens=itens,
        categorias=todas_categorias,
        filtros={
            "tipo": tipo,
            "busca": busca,
            "data_inicio": request.args.get("data_inicio", ""),
            "data_fim": request.args.get("data_fim", ""),
            "categoria": categoria,
        },
    )


@transactions_bp.route("/transacoes/excluir/<int:id>", methods=["POST"])
@login_required
def excluir_transacao(id):
    t = Transaction.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()

    db.session.delete(t)
    db.session.commit()

    flash("Movimentação excluída com sucesso.", "success")
    return redirect(url_for("transactions.historico"))

