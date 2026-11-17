
from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from datetime import datetime, timedelta

from flask_login import current_user, login_required

from extensions import db
from models import Subscription
from helpers import obter_plano_usuario

subscriptions_bp = Blueprint("subscriptions", __name__)


@subscriptions_bp.route("/planos")
def plans():
    plano_atual = None

    if current_user.is_authenticated:
        plano_atual = obter_plano_usuario(current_user)

    planos = [
        {
            "name": "Free",
            "slug": "free",
            "price": "R$ 0,00",
            "period": "para sempre",
            "description": "Para começar a organizar suas finanças.",
            "features": [
                "Controle de receitas e despesas",
                "Dashboard financeiro",
                "Categorias personalizadas",
                "Histórico de transações",
                "Metas financeiras básicas"
            ],
            "highlight": False
        },
        {
            "name": "Pro",
            "slug": "pro",
            "price": "R$ 49,90",
            "period": "por mês",
            "description": "Para quem quer mais controle e planejamento.",
            "features": [
                "Tudo do plano Free",
                "Relatórios financeiros avançados",
                "Análises detalhadas",
                "Planejamento financeiro avançado",
                "Recursos exclusivos"
            ],
            "highlight": True
        }
    ]

    return render_template(
        "plans.html",
        planos=planos,
        plano_atual=plano_atual
    )


@subscriptions_bp.route("/pagamento/<plano>", methods=["GET", "POST"])
@login_required
def payment_demo(plano):
    planos_pagamento = {
        "pro": {
            "name": "Pro",
            "price": "R$ 49,90",
            "period": "por mês"
        }
    }

    plano_escolhido = planos_pagamento.get(plano)

    if not plano_escolhido:
        abort(404)

    if request.method == "POST":
        agora = datetime.utcnow()

        assinatura = current_user.subscription

        if assinatura is None:
            assinatura = Subscription(user_id=current_user.id)
            db.session.add(assinatura)

        assinatura.plan = plano
        assinatura.status = "active"
        assinatura.payment_method = "demonstrativo"
        assinatura.started_at = agora
        assinatura.expires_at = agora + timedelta(days=30)

        db.session.commit()

        flash(
            f"Plano {plano_escolhido['name']} ativado com sucesso! "
            "Esta foi uma contratação demonstrativa, sem cobrança.",
            "success"
        )

        return redirect(url_for("dashboard.index"))

    return render_template(
        "payment_demo.html",
        plano=plano_escolhido
    )



