/* Admin: prazo de entrega por faixa de CEP (prazo_cep.py, 15/10/2026).
 * Tabela oficial de faixas (substitui a anterior a cada importacao), dias corridos/uteis, liga/desliga no rastreio
 * e simulador de um pedido real para conferir com o "Prazo Cliente" do TMS antes de ligar. */
(function () {
  "use strict";

  const estado = document.getElementById("prazoCepEstado");
  const contagem = document.getElementById("prazoCepContagem");
  const ligar = document.getElementById("prazoCepLigar");
  const importarForm = document.getElementById("prazoCepImportarForm");
  const arquivo = document.getElementById("prazoCepArquivo");
  const simularForm = document.getElementById("prazoCepSimularForm");
  const codigo = document.getElementById("prazoCepCodigo");
  const alerta = document.getElementById("prazoCepAlert");
  const resultado = document.getElementById("prazoCepResultado");
  if (!estado) return;

  let ligado = false;

  function aviso(mensagem = "", erro = false) {
    alerta.textContent = mensagem;
    alerta.classList.toggle("hidden", !mensagem);
    alerta.style.background = erro ? "rgba(255, 107, 107, 0.10)" : "rgba(42, 127, 255, 0.10)";
    alerta.style.border = erro ? "1px solid rgba(255, 107, 107, 0.25)" : "1px solid rgba(66, 199, 255, 0.25)";
    alerta.style.color = erro ? "#ffd4d4" : "#d9f2ff";
  }

  async function json(url, opcoes) {
    const resposta = await fetch(url, opcoes);
    const dados = await resposta.json().catch(() => ({}));
    if (!resposta.ok || dados.success === false) throw new Error(dados.message || "Erro ao falar com o servidor.");
    return dados;
  }

  function mostrarEstado(dados) {
    ligado = Boolean(dados.ligado);
    contagem.value = dados.contagem || "corridos";
    const total = Number(dados.total ?? 0);
    estado.textContent = `${total} faixa${total === 1 ? "" : "s"} na tabela · ${Number(dados.registrados_tms ?? 0)} prazos registrados do TMS · `
      + `${Number(dados.observados_cliente ?? 0)} CEPs com prazo próprio do cliente · ${ligado ? "LIGADO no rastreio" : "desligado no rastreio"}`;
    ligar.textContent = ligado ? "Desligar no rastreio" : "Ligar no rastreio";
  }

  async function carregar() {
    try {
      mostrarEstado(await json("/api/admin/prazos-cep"));
    } catch (e) {
      aviso(e.message, true);
    }
  }

  ligar.addEventListener("click", async () => {
    aviso();
    if (!ligado && !window.confirm("Ligar o prazo no rastreio dos clientes? Só ligue depois de conferir alguns pedidos no simulador com o Prazo Cliente do TMS.")) return;
    try {
      const dados = await json("/api/admin/prazos-cep/config", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ligado: !ligado }),
      });
      await carregar();
      aviso(dados.ligado ? "Prazo ligado no rastreio." : "Prazo desligado no rastreio.");
    } catch (e) {
      aviso(e.message, true);
    }
  });

  contagem.addEventListener("change", async () => {
    aviso();
    try {
      await json("/api/admin/prazos-cep/config", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ contagem: contagem.value }),
      });
      aviso(`Contagem salva: dias ${contagem.value === "uteis" ? "úteis" : "corridos"}.`);
    } catch (e) {
      aviso(e.message, true);
      await carregar();
    }
  });

  importarForm.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    aviso();
    const f = arquivo.files && arquivo.files[0];
    if (!f) {
      aviso("Selecione a tabela (CSV ou Excel).", true);
      return;
    }
    const corpo = new FormData();
    corpo.append("arquivo", f);
    try {
      const dados = await json("/api/admin/prazos-cep/importar", { method: "POST", body: corpo });
      importarForm.reset();
      await carregar();
      aviso(dados.message || "Tabela importada.");
    } catch (e) {
      aviso(e.message, true);
    }
  });

  simularForm.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    aviso();
    resultado.textContent = "";
    const valor = codigo.value.trim().toUpperCase();
    if (!valor) return;
    try {
      const d = await json(`/api/admin/prazos-cep/simular?codigo=${encodeURIComponent(valor)}`);
      const linhas = [
        ["Código", d.codigo], ["Pedido no TMS", d.pedido || "-"], ["Status", d.status || "-"], ["CEP do destinatário", d.cep || "-"],
        ["Dias da faixa", d.dias ?? "-"], ["Contagem", d.contagem === "uteis" ? "dias úteis" : "dias corridos"],
        ["Cadastro no TMS", d.cadastro || "-"], ["Prazo", d.prazo || "-"], ["Fonte do prazo", d.fonte || "-"],
        ["O cliente veria", d.cliente_veria || "nada (fora de 'a caminho', vencido ou sem dado)"], ["Motivo", d.motivo || "-"],
      ];
      const tabela = document.createElement("table");
      tabela.className = "admin-table";
      const corpo = document.createElement("tbody");
      linhas.forEach(([rotulo, texto]) => {
        const tr = document.createElement("tr");
        const th = document.createElement("th");
        th.textContent = rotulo;
        const td = document.createElement("td");
        td.textContent = String(texto);
        tr.append(th, td);
        corpo.appendChild(tr);
      });
      tabela.appendChild(corpo);
      resultado.appendChild(tabela);
    } catch (e) {
      aviso(e.message, true);
    }
  });

  carregar();
}());
