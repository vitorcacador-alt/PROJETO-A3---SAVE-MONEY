
from io import BytesIO
from datetime import datetime

from flask import Blueprint, make_response, redirect, url_for, flash
from flask_login import login_required, current_user

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

from models import Transaction
from helpers import usuario_tem_recurso


reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/relatorios/exportar")
@login_required
def exportar():

    if not usuario_tem_recurso(current_user, "exportacao_relatorios"):
        flash(
            "A exportação de relatórios é exclusiva dos planos Pro e Business.",
            "warning"
        )
        return redirect(url_for("subscriptions.plans"))

    transacoes = (
        Transaction.query
        .filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc())
        .all()
    )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Relatório Financeiro"

    # Título
    sheet.merge_cells("A1:G1")
    sheet["A1"] = "RELATÓRIO FINANCEIRO - SAVEMONEY"
    sheet["A1"].font = Font(
        name="Arial",
        size=16,
        bold=True,
        color="FFFFFF"
    )
    sheet["A1"].fill = PatternFill(
        "solid",
        fgColor="172554"
    )
    sheet["A1"].alignment = Alignment(
        horizontal="center",
        vertical="center"
    )
    sheet.row_dimensions[1].height = 35

    # Informações do relatório
    sheet.merge_cells("A2:G2")
    sheet["A2"] = (
        f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
    )
    sheet["A2"].font = Font(
        name="Arial",
        size=10,
        italic=True,
        color="64748B"
    )

    # Cabeçalho
    cabecalhos = [
        "Data",
        "Tipo",
        "Descrição",
        "Categoria",
        "Forma de pagamento",
        "Valor (R$)",
        "Observação"
    ]

    linha_cabecalho = 4

    for coluna, titulo in enumerate(cabecalhos, start=1):
        celula = sheet.cell(
            row=linha_cabecalho,
            column=coluna,
            value=titulo
        )

        celula.font = Font(
            bold=True,
            color="FFFFFF",
            name="Arial"
        )
        celula.fill = PatternFill(
            "solid",
            fgColor="2563EB"
        )
        celula.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    sheet.row_dimensions[linha_cabecalho].height = 25

    # Dados das transações
    for linha, transacao in enumerate(transacoes, start=5):

        valores = [
            transacao.date.strftime("%d/%m/%Y"),
            transacao.type,
            transacao.description,
            transacao.category or "",
            transacao.payment_method or "",
            float(transacao.amount),
            transacao.observation or ""
        ]

        for coluna, valor in enumerate(valores, start=1):
            celula = sheet.cell(
                row=linha,
                column=coluna,
                value=valor
            )

            celula.font = Font(
                name="Arial",
                size=10,
                color="334155"
            )

            celula.alignment = Alignment(
                vertical="center"
            )

            if linha % 2 == 0:
                celula.fill = PatternFill(
                    "solid",
                    fgColor="EFF6FF"
                )

            if coluna == 6:
                celula.number_format = 'R$ #,##0.00'
                celula.alignment = Alignment(
                    horizontal="right",
                    vertical="center"
                )

        sheet.row_dimensions[linha].height = 22

    # Ajuste automático da largura das colunas
    larguras = {
        "A": 15,
        "B": 16,
        "C": 30,
        "D": 22,
        "E": 25,
        "F": 18,
        "G": 35
    }

    for coluna, largura in larguras.items():
        sheet.column_dimensions[coluna].width = largura

    # Bordas discretas
    borda = Border(
        bottom=Side(
            style="thin",
            color="E2E8F0"
        )
    )

    for linha in sheet.iter_rows(
        min_row=4,
        max_row=max(4, sheet.max_row),
        min_col=1,
        max_col=7
    ):
        for celula in linha:
            celula.border = borda

    # Filtros e tabela
    if transacoes:
        tabela = Table(
            displayName="TabelaTransacoes",
            ref=f"A4:G{sheet.max_row}"
        )

        estilo = TableStyleInfo(
            name="TableStyleMedium2",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False
        )

        tabela.tableStyleInfo = estilo
        sheet.add_table(tabela)
    else:
        sheet.auto_filter.ref = "A4:G4"

    # Congela o cabeçalho
    sheet.freeze_panes = "A5"

    # Configuração de impressão
    sheet.sheet_view.showGridLines = False
    sheet.page_setup.orientation = "landscape"
    sheet.page_setup.fitToWidth = 1
    sheet.sheet_properties.pageSetUpPr.fitToPage = True

    # Gera o arquivo Excel
    arquivo = BytesIO()
    workbook.save(arquivo)
    arquivo.seek(0)

    resposta = make_response(arquivo.getvalue())

    resposta.headers["Content-Type"] = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    resposta.headers["Content-Disposition"] = (
        "attachment; filename=relatorio_savemoney.xlsx"
    )

    return resposta

