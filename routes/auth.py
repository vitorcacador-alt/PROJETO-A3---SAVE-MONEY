from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User
from helpers import criar_categorias_padrao, criar_dados_demo
from email_utils import (
    enviar_email_redefinicao,
    gerar_token_redefinicao,
    verificar_token_redefinicao,
)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        erros = []
        if not name or len(name) < 2:
            erros.append("Informe um nome válido.")
        if not email or "@" not in email:
            erros.append("Informe um e-mail válido.")
        if len(password) < 6:
            erros.append("A senha deve ter pelo menos 6 caracteres.")
        if password != confirm:
            erros.append("As senhas não coincidem.")
        if email and User.query.filter_by(email=email).first():
            erros.append("Este e-mail já está cadastrado.")

        if erros:
            for e in erros:
                flash(e, "danger")
            return render_template("register.html", name=name, email=email)

        user = User(name=name, email=email, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

        criar_categorias_padrao(user.id)

        flash("Conta criada com sucesso! Faça login para continuar.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f"Bem-vindo(a), {user.name}!", "success")
            return redirect(url_for("dashboard.index"))

        flash("E-mail ou senha inválidos.", "danger")
        return render_template("login.html", email=email)

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("main.landing"))


@auth_bp.route("/demo-login")
def demo_login():
    """Cria (se necessário) e loga com uma conta de demonstração para facilitar a apresentação."""
    email = "joao@teste.com"
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name="João Silva", email=email, password=generate_password_hash("123456"))
        db.session.add(user)
        db.session.commit()
        criar_categorias_padrao(user.id)
        criar_dados_demo(user.id)

    login_user(user)
    flash("Login de demonstração realizado (usuário: joao@teste.com / senha: 123456).", "info")
    return redirect(url_for("dashboard.index"))

@auth_bp.route("/esqueci-senha", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            token = gerar_token_redefinicao(user)
            enviar_email_redefinicao(user, token)

        flash(
            "Se esse e-mail estiver cadastrado, enviamos um link para "
            "redefinir sua senha. Verifique também a caixa de spam.",
            "info",
        )
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


@auth_bp.route("/redefinir-senha/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    user = verificar_token_redefinicao(token)
    if user is None:
        flash(
            "Este link de redefinição é inválido ou expirou. Solicite um novo.",
            "danger",
        )
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        erros = []
        if len(password) < 6:
            erros.append("A senha deve ter pelo menos 6 caracteres.")
        if password != confirm:
            erros.append("As senhas não coincidem.")

        if erros:
            for e in erros:
                flash(e, "danger")
            return render_template("reset_password.html", token=token)

        user.password = generate_password_hash(password)
        db.session.commit()

        flash("Senha redefinida com sucesso! Faça login com a nova senha.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)
