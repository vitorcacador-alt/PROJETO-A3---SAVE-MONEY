import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Em produção, defina SECRET_KEY como variável de ambiente.
    SECRET_KEY = os.environ.get("SECRET_KEY", "chave-secreta-dev-savemoney-troque-em-producao")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database", "savemoney.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
