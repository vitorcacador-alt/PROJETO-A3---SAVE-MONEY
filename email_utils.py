import smtplib
from email.mime.text import MIMEText

from flask import current_app, url_for
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt=current_app.config["SECURITY_PASSWORD_SALT"],
    )


def gerar_token_redefinicao(user) -> str:
    dados = {"user_id": user.id, "pw_fingerprint": user.password[-16:]}
    return _serializer().dumps(dados)


def verificar_token_redefinicao(token: str):
    """Devolve o usuário se o token for válido, ou None se inválido/expirado."""
    from models import User

    try:
        dados = _serializer().loads(
            token, max_age=current_app.config["RESET_TOKEN_MAX_AGE_SECONDS"]
        )
    except (BadSignature, SignatureExpired):
        return None

    user = User.query.get(dados.get("user_id"))
    if user is None:
        return None
    if user.password[-16:] != dados.get("pw_fingerprint"):
        return None
    return user


def enviar_email_redefinicao(user, token: str) -> None:
    """Envia o e-mail com o link de redefinição.

    Se MAIL_USERNAME não estiver configurado, o e-mail não é enviado de
    verdade: o link só é impresso no console, pra testar sem precisar
    configurar e-mail.
    """
    link = url_for("auth.reset_password", token=token, _external=True)

    corpo = (
        f"Olá, {user.name}!\n\n"
        "Recebemos uma solicitação para redefinir a senha da sua conta "
        "no SaveMoney.\n\n"
        f"Clique no link abaixo para criar uma nova senha "
        f"(válido por 30 minutos):\n{link}\n\n"
        "Se você não solicitou isso, pode ignorar este e-mail — "
        "sua senha atual continua a mesma.\n\n"
        "— Equipe SaveMoney"
    )

    remetente = current_app.config.get("MAIL_USERNAME")
    if not remetente:
        print("=" * 70)
        print(f"[SaveMoney] E-mail SMTP não configurado.")
        print(f"Link de redefinição para {user.email}:")
        print(link)
        print("=" * 70)
        return

    mensagem = MIMEText(corpo, "plain", "utf-8")
    mensagem["Subject"] = "Redefinição de senha — SaveMoney"
    mensagem["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    mensagem["To"] = user.email

    with smtplib.SMTP(
        current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"]
    ) as servidor:
        if current_app.config["MAIL_USE_TLS"]:
            servidor.starttls()
        servidor.login(
            current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"]
        )
        servidor.send_message(mensagem)