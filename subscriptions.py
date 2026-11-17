
from flask import Blueprint, render_template

subscriptions_bp = Blueprint("subscriptions", __name__)


@subscriptions_bp.route("/planos")
def plans():
    planos = [
        {
            "name": "Free",
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
            "price": "R$ 49,90",
            "period": "por mês",
            "description": "Para quem quer ter mais controle e planejamento.",
            "features": [
                "Tudo do plano Free",
                "Relatórios financeiros avançados",
                "Análises detalhadas",
                "Planejamento financeiro avançado",
                "Recursos exclusivos"
            ],
            "highlight": True
        },
        {
            "name": "Business",
            "price": "R$ 89,90",
            "period": "por mês",
            "description": "Para pequenos negócios que querem crescer.",
            "features": [
                "Tudo do plano Pro",
                "Controle financeiro empresarial",
                "Relatórios para negócios",
                "Análise de fluxo de caixa",
                "Recursos para gestão empresarial"
            ],
            "highlight": False
        }
    ]

    return render_template("plans.html", planos=planos)
