from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Category, Transaction

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/categorias")
@login_required
def index():
    receitas = Category.query.filter_by(user_id=current_user.id, type="receita").order_by(Category.name).all()
    despesas = Category.query.filter_by(user_id=current_user.id, type="despesa").order_by(Category.name).all()
    return render_template("categories.html", receitas=receitas, despesas=despesas)


@categories_bp.route("/categorias/nova", methods=["POST"])
@login_required
def nova():
    nome = request.form.get("name", "").strip()
    tipo = request.form.get("type")

    if not nome or tipo not in ("receita", "despesa"):
        flash("Informe um nome e tipo de categoria válidos.", "danger")
        return redirect(url_for("categories.index"))

    existente = Category.query.filter_by(user_id=current_user.id, name=nome, type=tipo).first()
    if existente:
        flash("Essa categoria já existe.", "warning")
        return redirect(url_for("categories.index"))

    db.session.add(Category(user_id=current_user.id, name=nome, type=tipo))
    db.session.commit()
    flash("Categoria criada com sucesso.", "success")
    return redirect(url_for("categories.index"))


@categories_bp.route("/categorias/editar/<int:id>", methods=["POST"])
@login_required
def editar(id):
    categoria = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    nome_antigo = categoria.name
    novo_nome = request.form.get("name", "").strip()

    if not novo_nome:
        flash("Informe um nome válido.", "danger")
        return redirect(url_for("categories.index"))

    categoria.name = novo_nome
    # Atualiza transações que usavam o nome antigo da categoria
    Transaction.query.filter_by(user_id=current_user.id, category=nome_antigo).update(
        {"category": novo_nome}
    )
    db.session.commit()
    flash("Categoria atualizada com sucesso.", "success")
    return redirect(url_for("categories.index"))


@categories_bp.route("/categorias/excluir/<int:id>", methods=["POST"])
@login_required
def excluir(id):
    categoria = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(categoria)
    db.session.commit()
    flash("Categoria excluída com sucesso.", "success")
    return redirect(url_for("categories.index"))
