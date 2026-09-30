from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Goal

goals_bp = Blueprint("goals", __name__)


def _parse_data(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


@goals_bp.route("/metas")
@login_required
def index():
    metas = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.deadline).all()
    return render_template("goals.html", metas=metas)


@goals_bp.route("/metas/nova", methods=["POST"])
@login_required
def nova():
    nome = request.form.get("name", "").strip()
    valor_desejado = request.form.get("target_amount", "").replace(",", ".")
    valor_atual = request.form.get("current_amount", "0").replace(",", ".")
    prazo = _parse_data(request.form.get("deadline"))

    erros = []
    if not nome:
        erros.append("Informe um nome para a meta.")
    try:
        valor_desejado_f = float(valor_desejado)
        if valor_desejado_f <= 0:
            erros.append("O valor da meta deve ser maior que zero.")
    except ValueError:
        erros.append("Informe um valor de meta válido.")
        valor_desejado_f = 0
    try:
        valor_atual_f = float(valor_atual) if valor_atual else 0
    except ValueError:
        valor_atual_f = 0

    if erros:
        for e in erros:
            flash(e, "danger")
        return redirect(url_for("goals.index"))

    db.session.add(Goal(
        user_id=current_user.id, name=nome, target_amount=valor_desejado_f,
        current_amount=valor_atual_f, deadline=prazo,
    ))
    db.session.commit()
    flash("Meta criada com sucesso.", "success")
    return redirect(url_for("goals.index"))


@goals_bp.route("/metas/editar/<int:id>", methods=["POST"])
@login_required
def editar(id):
    meta = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    meta.name = request.form.get("name", meta.name).strip()
    try:
        meta.target_amount = float(request.form.get("target_amount", "").replace(",", "."))
    except ValueError:
        pass
    try:
        meta.current_amount = float(request.form.get("current_amount", "").replace(",", "."))
    except ValueError:
        pass
    prazo = _parse_data(request.form.get("deadline"))
    if prazo:
        meta.deadline = prazo

    db.session.commit()
    flash("Meta atualizada com sucesso.", "success")
    return redirect(url_for("goals.index"))


@goals_bp.route("/metas/excluir/<int:id>", methods=["POST"])
@login_required
def excluir(id):
    meta = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(meta)
    db.session.commit()
    flash("Meta excluída com sucesso.", "success")
    return redirect(url_for("goals.index"))
