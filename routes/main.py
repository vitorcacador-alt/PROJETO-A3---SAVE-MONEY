from flask import Blueprint, render_template
from flask_login import current_user
from flask import redirect, url_for

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return render_template("landing.html")
