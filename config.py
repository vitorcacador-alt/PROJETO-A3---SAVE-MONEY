import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Em produção, defina SECRET_KEY como variável de ambiente.
    SECRET_KEY = os.environ.get("SECRET_KEY", "chave-secreta-dev-savemoney-troque-em-producao")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database", "savemoney.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # --- E-mail (usado em "Esqueci minha senha") ---
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    # --- Token de redefinição de senha ---
    SECURITY_PASSWORD_SALT = os.environ.get(
        "SECURITY_PASSWORD_SALT", "salt-dev-savemoney-troque-em-producao"
    )
    RESET_TOKEN_MAX_AGE_SECONDS = 30 * 60  # 30 minutos