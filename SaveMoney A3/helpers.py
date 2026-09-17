from datetime import date, timedelta
from extensions import db
from models import Category, Transaction, Goal, Planning

CATEGORIAS_RECEITA = ["Salário", "Freelance", "Investimentos", "Presente", "Venda", "Outros"]
CATEGORIAS_DESPESA = [
    "Alimentação", "Transporte", "Moradia", "Lazer", "Saúde",
    "Educação", "Compras", "Assinaturas", "Contas", "Outros",
]


def criar_categorias_padrao(user_id):
    """Cria as categorias padrão para um novo usuário."""
    categorias = []
    for nome in CATEGORIAS_RECEITA:
        categorias.append(Category(user_id=user_id, name=nome, type="receita"))
    for nome in CATEGORIAS_DESPESA:
        categorias.append(Category(user_id=user_id, name=nome, type="despesa"))
    db.session.bulk_save_objects(categorias)
    db.session.commit()


def criar_dados_demo(user_id):
    """Cria transações, meta e planejamento fictícios para demonstração."""
    hoje = date.today()

    receitas_demo = [
        ("Salário", "Salário mensal", 3000, hoje.replace(day=5) if hoje.day >= 5 else hoje),
        ("Freelance", "Projeto freelance", 450, hoje - timedelta(days=10)),
    ]
    despesas_demo = [
        ("Moradia", "Aluguel", 1200, hoje.replace(day=3) if hoje.day >= 3 else hoje),
        ("Alimentação", "Supermercado", 380, hoje - timedelta(days=4)),
        ("Transporte", "Combustível", 220, hoje - timedelta(days=6)),
        ("Lazer", "Cinema", 60, hoje - timedelta(days=8)),
        ("Contas", "Internet", 100, hoje - timedelta(days=12)),
    ]

    for cat, desc, valor, dt in receitas_demo:
        db.session.add(Transaction(
            user_id=user_id, type="receita", description=desc, amount=valor,
            category=cat, date=dt, payment_method="Transferência",
            observation="Dado de demonstração", is_demo=True,
        ))

    for cat, desc, valor, dt in despesas_demo:
        db.session.add(Transaction(
            user_id=user_id, type="despesa", description=desc, amount=valor,
            category=cat, date=dt, payment_method="Cartão",
            observation="Dado de demonstração", is_demo=True,
        ))

    db.session.add(Goal(
        user_id=user_id, name="Comprar um computador (demonstração)",
        target_amount=5000, current_amount=2000,
        deadline=hoje + timedelta(days=180),
    ))

    db.session.add(Planning(
        user_id=user_id, expected_income=3000, expected_expense=2000, monthly_limit=2500,
    ))

    db.session.commit()
