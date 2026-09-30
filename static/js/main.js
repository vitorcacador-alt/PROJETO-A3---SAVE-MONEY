// ===== TEMA CLARO/ESCURO =====
function aplicarTemaSalvo() {
    const tema = localStorage.getItem("savemoney_theme") || "light";
    document.documentElement.setAttribute("data-theme", tema);
    atualizarBotaoTema(tema);
}

function alternarTema() {
    const atual = document.documentElement.getAttribute("data-theme") || "light";
    const novo = atual === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", novo);
    localStorage.setItem("savemoney_theme", novo);
    atualizarBotaoTema(novo);
}

function atualizarBotaoTema(tema) {
    const btn = document.getElementById("themeToggleBtn");
    if (btn) {
        btn.textContent = tema === "light" ? "🌙 Escuro" : "☀️ Claro";
    }
}

// ===== MENU MOBILE =====
function alternarMenu() {
    const sidebar = document.getElementById("sidebar");
    if (sidebar) sidebar.classList.toggle("open");
}

// ===== MODAL DE CONFIRMAÇÃO DE EXCLUSÃO =====
let formParaExcluir = null;

function confirmarExclusao(form, mensagem) {
    formParaExcluir = form;
    const modal = document.getElementById("confirmModal");
    const texto = document.getElementById("confirmModalText");
    if (texto) texto.textContent = mensagem || "Tem certeza que deseja excluir este item?";
    if (modal) modal.classList.add("active");
    return false; // impede o submit imediato do form
}

function fecharModalConfirmacao() {
    const modal = document.getElementById("confirmModal");
    if (modal) modal.classList.remove("active");
    formParaExcluir = null;
}

function confirmarExclusaoFinal() {
    if (formParaExcluir) {
        formParaExcluir.submit();
    }
    fecharModalConfirmacao();
}

// ===== FECHAR FLASH MESSAGES AUTOMATICAMENTE =====
document.addEventListener("DOMContentLoaded", function () {
    aplicarTemaSalvo();

    const flashes = document.querySelectorAll(".flash");
    flashes.forEach(function (el) {
        setTimeout(function () {
            el.style.transition = "opacity 0.4s ease";
            el.style.opacity = "0";
            setTimeout(function () { el.remove(); }, 400);
        }, 4500);
    });
});
