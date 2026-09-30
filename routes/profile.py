from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        acao = request.form.get("acao")

        if acao == "dados":
            nome = request.form.get("name", "").strip()
            if not nome:
                flash("Informe um nome válido.", "danger")
            else:
                current_user.name = nome
                db.session.commit()
                flash("Dados atualizados com sucesso.", "success")

        elif acao == "senha":
            atual = request.form.get("current_password", "")
            nova = request.form.get("new_password", "")
            confirmar = request.form.get("confirm_password", "")

            if not check_password_hash(current_user.password, atual):
                flash("Senha atual incorreta.", "danger")
            elif len(nova) < 6:
                flash("A nova senha deve ter pelo menos 6 caracteres.", "danger")
            elif nova != confirmar:
                flash("As senhas não coincidem.", "danger")
            else:
                current_user.password = generate_password_hash(nova)
                db.session.commit()
                flash("Senha alterada com sucesso.", "success")

        return redirect(url_for("profile.index"))

    return render_template("profile.html")
