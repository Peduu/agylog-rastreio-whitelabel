const modelosAlert = document.getElementById("modelosAlert");
const bipagemAlert = document.getElementById("bipagemAlert");
const bipagemInput = document.getElementById("bipagemInput");
const limparBipagemBtn = document.getElementById("limparBipagemBtn");
const operacaoSummaryCards = document.getElementById("operacaoSummaryCards");
const operacaoTableBody = document.getElementById("operacaoTableBody");
const modelosBuscaInput = document.getElementById("modelosBuscaInput");
const modelosFiltroModelo = document.getElementById("modelosFiltroModelo");
const modelosFiltroUf = document.getElementById("modelosFiltroUf");
const modelosFiltroCidade = document.getElementById("modelosFiltroCidade");
const modelosFiltroArquivo = document.getElementById("modelosFiltroArquivo");
const modelosLimiteSelect = document.getElementById("modelosLimiteSelect");
const consultarModelosBtn = document.getElementById("consultarModelosBtn");
const limparModelosBtn = document.getElementById("limparModelosBtn");
const exportarModelosBtn = document.getElementById("exportarModelosBtn");
const colunasEssenciaisBtn = document.getElementById("colunasEssenciaisBtn");
const colunasTodasBtn = document.getElementById("colunasTodasBtn");
const colunasNenhumaBtn = document.getElementById("colunasNenhumaBtn");
const modelosColumnsContainer = document.getElementById("modelosColumnsContainer");
const modelosTableHeadRow = document.getElementById("modelosTableHeadRow");
const modelosTableBody = document.getElementById("modelosTableBody");
const modelosDetalhesVazio = document.getElementById("modelosDetalhesVazio");
const modelosDetalhesWrap = document.getElementById("modelosDetalhesWrap");
const modelosDetalhesGrid = document.getElementById("modelosDetalhesGrid");
const modelosExtrasTableBody = document.getElementById("modelosExtrasTableBody");
const modelosMenuToggle = document.getElementById("modelosMenuToggle");
const modelosMenuItems = document.getElementById("modelosMenuItems");

const metaTotalRegistros = document.getElementById("metaTotalRegistros");
const metaTotalModelos = document.getElementById("metaTotalModelos");
const metaTotalArquivos = document.getElementById("metaTotalArquivos");
const metaUltimaAtualizacao = document.getElementById("metaUltimaAtualizacao");

const COLUNAS_ESSENCIAIS = [
  "idSolicitacaoInterno",
  "nroPedido",
  "destinatario_nome",
  "destinatario_logradouro",
  "destinatario_numero",
  "destinatario_bairro",
  "destinatario_cep",
  "destinatario_cidade",
  "destinatario_uf",
  "nome_arquivo",
  "modelo_nome",
  "criado_em",
];

let colunasDisponiveis = [];
let ultimaConsulta = null;
let registrosBipados = [];

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function setAlert(message = "", isError = false) {
  if (!modelosAlert) return;
  modelosAlert.textContent = message;
  modelosAlert.classList.toggle("hidden", !message);
  modelosAlert.style.background = isError ? "rgba(255, 107, 107, 0.10)" : "rgba(42, 127, 255, 0.10)";
  modelosAlert.style.border = isError ? "1px solid rgba(255, 107, 107, 0.25)" : "1px solid rgba(66, 199, 255, 0.25)";
  modelosAlert.style.color = isError ? "#ffd4d4" : "#d9f2ff";
}

function setBipagemAlert(message = "", isError = false) {
  if (!bipagemAlert) return;
  bipagemAlert.textContent = message;
  bipagemAlert.classList.toggle("hidden", !message);
  bipagemAlert.style.background = isError ? "rgba(255, 107, 107, 0.10)" : "rgba(42, 127, 255, 0.10)";
  bipagemAlert.style.border = isError ? "1px solid rgba(255, 107, 107, 0.25)" : "1px solid rgba(66, 199, 255, 0.25)";
  bipagemAlert.style.color = isError ? "#ffd4d4" : "#d9f2ff";
}

function toggleMenu(forceOpen = null) {
  if (!modelosMenuItems || !modelosMenuToggle) return;
  const shouldOpen = forceOpen === null ? !modelosMenuItems.classList.contains("show") : forceOpen;
  modelosMenuItems.classList.toggle("show", shouldOpen);
  modelosMenuToggle.setAttribute("aria-expanded", String(shouldOpen));
}

function humanizarColuna(nome) {
  const mapa = {
    idSolicitacaoInterno: "AR",
    modelo_nome: "Modelo",
    nome_arquivo: "Arquivo",
    criado_em: "Criado em",
    atualizado_em: "Atualizado em",
    destinatario_nome: "Destinatario",
    destinatario_logradouro: "Logradouro",
    destinatario_numero: "Numero",
    destinatario_complemento: "Complemento",
    destinatario_bairro: "Bairro",
    destinatario_cep: "CEP",
    destinatario_cidade: "Cidade",
    destinatario_uf: "UF",
    observacoes: "Observacoes",
    nroPedido: "Pedido",
    qtdeVolumes: "Volumes",
    destinatario_pontoreferencia: "Ponto de referencia",
    destinatario_cpf: "CPF",
    destinatario_telefone: "Telefone",
    destinatario_cnpj: "CNPJ",
    qtdeItens: "Itens",
    OBS1: "OBS1",
    OBS2: "OBS2",
    OBS3: "OBS3",
  };
  return mapa[nome] || nome;
}

function getSelectedColumns() {
  return [...document.querySelectorAll(".modelos-column-checkbox:checked")]
    .map((input) => input.value)
    .filter(Boolean);
}

function marcarColunas(colunas) {
  const wanted = new Set(colunas);
  document.querySelectorAll(".modelos-column-checkbox").forEach((input) => {
    input.checked = wanted.has(input.value);
  });
}

function renderColumnPicker() {
  if (!modelosColumnsContainer) return;
  modelosColumnsContainer.innerHTML = colunasDisponiveis.map((coluna) => `
    <label class="modelos-column-option">
      <input
        type="checkbox"
        class="modelos-column-checkbox"
        value="${escapeHtml(coluna)}"
        ${COLUNAS_ESSENCIAIS.includes(coluna) ? "checked" : ""}
      />
      <span>${escapeHtml(humanizarColuna(coluna))}</span>
    </label>
  `).join("");
}

function preencherSelect(select, values, labelPadrao) {
  if (!select) return;
  const options = [
    `<option value="">${escapeHtml(labelPadrao)}</option>`,
    ...values.map((item) => `<option value="${escapeHtml(item)}">${escapeHtml(item)}</option>`)
  ];
  select.innerHTML = options.join("");
}

function atualizarResumo(meta) {
  const resumo = meta?.resumo || {};
  if (metaTotalRegistros) metaTotalRegistros.textContent = resumo.total_registros ?? "-";
  if (metaTotalModelos) metaTotalModelos.textContent = resumo.total_modelos ?? "-";
  if (metaTotalArquivos) metaTotalArquivos.textContent = resumo.total_arquivos ?? "-";
  if (metaUltimaAtualizacao) metaUltimaAtualizacao.textContent = resumo.ultima_atualizacao || "-";
}

function montarParamsAtual() {
  const params = new URLSearchParams();
  const busca = modelosBuscaInput?.value.trim();
  const modelo = modelosFiltroModelo?.value.trim();
  const uf = modelosFiltroUf?.value.trim();
  const cidade = modelosFiltroCidade?.value.trim();
  const nomeArquivo = modelosFiltroArquivo?.value.trim();
  const limite = modelosLimiteSelect?.value || "100";
  const colunas = getSelectedColumns();

  if (busca) params.set("busca", busca);
  if (modelo) params.set("modelo", modelo);
  if (uf) params.set("uf", uf);
  if (cidade) params.set("cidade", cidade);
  if (nomeArquivo) params.set("nome_arquivo", nomeArquivo);
  if (limite) params.set("limite", limite);
  if (colunas.length) params.set("colunas", colunas.join(","));

  return params;
}

function getBipagemColumns() {
  const selecionadas = getSelectedColumns();
  const base = [
    "id",
    "idSolicitacaoInterno",
    "destinatario_nome",
    "destinatario_cidade",
    "destinatario_uf",
    "nome_arquivo",
    "OBS1",
    "observacoes",
    ...selecionadas,
  ];
  return [...new Set(base)].filter(Boolean);
}

function renderTabela(colunas, registros) {
  if (!modelosTableHeadRow || !modelosTableBody) return;

  const colunasAtivas = colunas.length ? colunas : colunasDisponiveis;
  modelosTableHeadRow.innerHTML = [
    ...colunasAtivas.map((coluna) => `<th>${escapeHtml(humanizarColuna(coluna))}</th>`),
    "<th>Acao</th>"
  ].join("");

  if (!registros.length) {
    modelosTableBody.innerHTML = `<tr><td colspan="${colunasAtivas.length + 1}">Nenhum registro encontrado para os filtros informados.</td></tr>`;
    return;
  }

  modelosTableBody.innerHTML = registros.map((registro) => `
    <tr>
      ${colunasAtivas.map((coluna) => `<td>${escapeHtml(registro[coluna] ?? "")}</td>`).join("")}
      <td><button class="ghost-btn detalhes-modelo-btn" data-id="${registro.id}" type="button">Detalhes</button></td>
    </tr>
  `).join("");
}

function renderOperacaoSummary() {
  if (!operacaoSummaryCards) return;

  if (!registrosBipados.length) {
    operacaoSummaryCards.innerHTML = "";
    return;
  }

  const resumo = registrosBipados.reduce((acc, item) => {
    const agencia = String(item.agencia || "Sem agencia").trim() || "Sem agencia";
    acc[agencia] = (acc[agencia] || 0) + 1;
    return acc;
  }, {});

  operacaoSummaryCards.innerHTML = Object.entries(resumo)
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([agencia, total]) => `
      <div class="database-status-card">
        <strong>${escapeHtml(agencia)}</strong>
        <span>${total} envio(s)</span>
      </div>
    `).join("");
}

function renderOperacaoTable() {
  if (!operacaoTableBody) return;

  if (!registrosBipados.length) {
    operacaoTableBody.innerHTML = `<tr><td colspan="6">Nenhum cartao bipado ainda.</td></tr>`;
    renderOperacaoSummary();
    return;
  }

  operacaoTableBody.innerHTML = registrosBipados.map((registro) => `
    <tr>
      <td>${escapeHtml(registro.agencia || "-")}</td>
      <td>${escapeHtml(registro.idSolicitacaoInterno || registro.nroPedido || "-")}</td>
      <td>${escapeHtml(registro.destinatario_nome || "-")}</td>
      <td>${escapeHtml(registro.destinatario_cidade || "-")}</td>
      <td>${escapeHtml(registro.destinatario_uf || "-")}</td>
      <td>${escapeHtml(registro.nome_arquivo || "-")}</td>
    </tr>
  `).join("");

  renderOperacaoSummary();
}

function renderDetalhes(detalhes) {
  if (!modelosDetalhesWrap || !modelosDetalhesGrid || !modelosExtrasTableBody || !modelosDetalhesVazio) return;

  const registro = detalhes?.registro || {};
  const extras = detalhes?.extras || [];

  modelosDetalhesGrid.innerHTML = Object.entries(registro).map(([campo, valor]) => `
    <div class="modelos-detail-item">
      <span>${escapeHtml(humanizarColuna(campo))}</span>
      <strong>${escapeHtml(valor ?? "")}</strong>
    </div>
  `).join("");

  modelosExtrasTableBody.innerHTML = extras.length
    ? extras.map((item) => `
        <tr>
          <td>${escapeHtml(item.campo)}</td>
          <td>${escapeHtml(item.valor ?? "")}</td>
        </tr>
      `).join("")
    : `<tr><td colspan="2">Nenhum campo extra encontrado.</td></tr>`;

  modelosDetalhesVazio.classList.add("hidden");
  modelosDetalhesWrap.classList.remove("hidden");
  document.getElementById("detalhesSection")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function carregarMeta() {
  try {
    const response = await fetch("/api/admin/modelos-db/meta");
    const data = await response.json();
    if (!data.success) {
      setAlert(data.message || "Erro ao carregar configuracao da base.", true);
      return;
    }

    const meta = data.meta || {};
    colunasDisponiveis = meta.colunas || [];
    atualizarResumo(meta);
    preencherSelect(modelosFiltroModelo, meta.modelos || [], "Todos os modelos");
    preencherSelect(modelosFiltroUf, meta.ufs || [], "Todas as UFs");
    renderColumnPicker();
  } catch (error) {
    console.error(error);
    setAlert("Erro ao carregar metadados da base.", true);
  }
}

async function consultarBase() {
  const params = montarParamsAtual();
  const selectedColumns = getSelectedColumns();

  if (!selectedColumns.length) {
    setAlert("Selecione ao menos uma coluna para exibir.", true);
    return;
  }

  try {
    const response = await fetch(`/api/admin/modelos-db?${params.toString()}`);
    const data = await response.json();
    if (!data.success) {
      setAlert(data.message || "Erro ao consultar a base.", true);
      renderTabela(selectedColumns, []);
      return;
    }

    const resultado = data.resultado || {};
    ultimaConsulta = params.toString();
    setAlert(`${resultado.total || 0} registro(s) carregado(s).`);
    renderTabela(resultado.colunas || selectedColumns, resultado.registros || []);
  } catch (error) {
    console.error(error);
    setAlert("Erro ao conectar com o servidor.", true);
    renderTabela(selectedColumns, []);
  }
}

async function carregarDetalhes(registroId) {
  try {
    const response = await fetch(`/api/admin/modelos-db/${registroId}`);
    const data = await response.json();
    if (!data.success) {
      setAlert(data.message || "Erro ao carregar detalhes.", true);
      return;
    }
    renderDetalhes(data.detalhes || {});
  } catch (error) {
    console.error(error);
    setAlert("Erro ao carregar detalhes do registro.", true);
  }
}

function limparFiltros() {
  if (modelosBuscaInput) modelosBuscaInput.value = "";
  if (modelosFiltroModelo) modelosFiltroModelo.value = "";
  if (modelosFiltroUf) modelosFiltroUf.value = "";
  if (modelosFiltroCidade) modelosFiltroCidade.value = "";
  if (modelosFiltroArquivo) modelosFiltroArquivo.value = "";
  if (modelosLimiteSelect) modelosLimiteSelect.value = "100";
  marcarColunas(COLUNAS_ESSENCIAIS.filter((coluna) => colunasDisponiveis.includes(coluna)));
  setAlert();
}

function limparBipagem() {
  registrosBipados = [];
  if (bipagemInput) bipagemInput.value = "";
  setBipagemAlert();
  renderOperacaoTable();
  bipagemInput?.focus();
}

function exportarCsv() {
  const params = montarParamsAtual();
  const selectedColumns = getSelectedColumns();
  if (!selectedColumns.length) {
    setAlert("Selecione ao menos uma coluna para exportar.", true);
    return;
  }
  window.open(`/api/admin/modelos-db/exportar?${params.toString()}`, "_blank");
}

async function processarBipagem() {
  const codigo = bipagemInput?.value.trim();
  if (!codigo) return;

  try {
    const response = await fetch("/api/admin/modelos-db/bipar", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        codigo,
        colunas: getBipagemColumns()
      })
    });

    const data = await response.json();
    if (!data.success) {
      setBipagemAlert(data.message || "Cartao nao encontrado.", true);
      if (bipagemInput) {
        bipagemInput.select();
        bipagemInput.focus();
      }
      return;
    }

    const registro = data.registro || {};
    const chaveUnica = String(registro.id || registro.idSolicitacaoInterno || codigo);
    const existente = registrosBipados.findIndex((item) => String(item.id || item.idSolicitacaoInterno) === chaveUnica);

    if (existente >= 0) {
      registrosBipados.splice(existente, 1);
    }

    registrosBipados.unshift(registro);
    setBipagemAlert(`Cartao ${codigo} adicionado na lista. Agencia: ${registro.agencia || "Sem agencia"}.`);
    renderOperacaoTable();

    if (bipagemInput) {
      bipagemInput.value = "";
      bipagemInput.focus();
    }
  } catch (error) {
    console.error(error);
    setBipagemAlert("Erro ao consultar o cartao bipado.", true);
  }
}

consultarModelosBtn?.addEventListener("click", consultarBase);
limparModelosBtn?.addEventListener("click", async () => {
  limparFiltros();
  await consultarBase();
});
exportarModelosBtn?.addEventListener("click", exportarCsv);
colunasEssenciaisBtn?.addEventListener("click", () => marcarColunas(COLUNAS_ESSENCIAIS.filter((coluna) => colunasDisponiveis.includes(coluna))));
colunasTodasBtn?.addEventListener("click", () => marcarColunas(colunasDisponiveis));
colunasNenhumaBtn?.addEventListener("click", () => marcarColunas([]));
modelosMenuToggle?.addEventListener("click", () => toggleMenu());
limparBipagemBtn?.addEventListener("click", limparBipagem);

document.addEventListener("click", (event) => {
  const target = event.target;

  if (target.classList.contains("detalhes-modelo-btn")) {
    carregarDetalhes(target.dataset.id);
    return;
  }

  if (!modelosMenuItems || !modelosMenuToggle) return;
  const inside = modelosMenuItems.contains(target) || modelosMenuToggle.contains(target);
  if (!inside) toggleMenu(false);
});

document.querySelectorAll("[data-nav-target]").forEach((button) => {
  button.addEventListener("click", () => {
    const targetId = button.getAttribute("data-nav-target");
    const target = targetId ? document.getElementById(targetId) : null;
    if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
    toggleMenu(false);
  });
});

[modelosBuscaInput, modelosFiltroCidade, modelosFiltroArquivo].forEach((input) => {
  input?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") consultarBase();
  });
});

bipagemInput?.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    processarBipagem();
  }
});

[modelosFiltroModelo, modelosFiltroUf, modelosLimiteSelect].forEach((input) => {
  input?.addEventListener("change", consultarBase);
});

async function init() {
  await carregarMeta();
  await consultarBase();
  renderOperacaoTable();
  bipagemInput?.focus();
}

init();
