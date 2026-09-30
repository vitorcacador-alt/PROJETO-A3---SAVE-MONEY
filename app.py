import os
from flask import Flask
from flask_login import login_required

from config import Config
from extensions import db, login_manager
from models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Garante que a pasta do banco de dados exista
    os.makedirs(os.path.join(os.path.dirname(__file__), "database"), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registro dos blueprints (rotas)
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.transactions import transactions_bp
    from routes.categories import categories_bp
    from routes.goals import goals_bp
    from routes.planning import planning_bp
    from routes.profile import profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(planning_bp)
    app.register_blueprint(profile_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    # debug=True apenas para desenvolvimento local
    app.run(debug=True, host="127.0.0.1", port=5000)
