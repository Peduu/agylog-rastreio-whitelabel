const importRastreiosForm = document.getElementById("importRastreiosForm");
const arquivoRastreiosInput = document.getElementById("arquivoRastreios");
const importRastreiosAlert = document.getElementById("importRastreiosAlert");

const logAcessosAlert = document.getElementById("logAcessosAlert");
const logAcessosTableBody = document.getElementById("logAcessosTableBody");
const logUpdatesAlert = document.getElementById("logUpdatesAlert");
const logUpdatesTableBody = document.getElementById("logUpdatesTableBody");

const usuariosAlert = document.getElementById("usuariosAlert");
const usuariosTableBody = document.getElementById("usuariosTableBody");
const usuariosBuscaInput = document.getElementById("usuariosBuscaInput");

const carregarCustodiasBtn = document.getElementById("carregarCustodiasBtn");
const exportarCustodiasBtn = document.getElementById("exportarCustodiasBtn");
const filtroStatusCustodia = document.getElementById("filtroStatusCustodia");
const custodiasTableBody = document.getElementById("custodiasTableBody");
const custodiasAdminAlert = document.getElementById("custodiasAdminAlert");

const databaseCnpjFilter = document.getElementById("databaseCnpjFilter");
const databaseStatusFilter = document.getElementById("databaseStatusFilter");
const carregarDatabaseBtn = document.getElementById("carregarDatabaseBtn");
const databaseStatusGrid = document.getElementById("databaseStatusGrid");
const databaseRastreiosTableBody = document.getElementById("databaseRastreiosTableBody");

const regraPrevisaoForm = document.getElementById("regraPrevisaoForm");
const regraTipo = document.getElementById("regraTipo");
const regraIdentificadorSelect = document.getElementById("regraIdentificadorSelect");
const regraIdentificadorManual = document.getElementById("regraIdentificadorManual");
const regraDiasPrevisao = document.getElementById("regraDiasPrevisao");
const regraPrioridade = document.getElementById("regraPrioridade");
const regraDescricao = document.getElementById("regraDescricao");
const regrasPrevisaoAlert = document.getElementById("regrasPrevisaoAlert");
const regrasPrevisaoTableBody = document.getElementById("regrasPrevisaoTableBody");
const importarRegrasCsvForm = document.getElementById("importarRegrasCsvForm");
const arquivoRegrasCsv = document.getElementById("arquivoRegrasCsv");

const adminMenuToggle = document.getElementById("adminMenuToggle");
const adminMenuItems = document.getElementById("adminMenuItems");
const cnpjSugestoes = document.getElementById("cnpjSugestoes");

let cnpjsDisponiveis = [];

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function setAlert(element, message = "", isError = false) {
  if (!element) return;
  element.textContent = message;
  element.classList.toggle("hidden", !message);
  element.style.background = isError ? "rgba(255, 107, 107, 0.10)" : "rgba(42, 127, 255, 0.10)";
  element.style.border = isError ? "1px solid rgba(255, 107, 107, 0.25)" : "1px solid rgba(66, 199, 255, 0.25)";
  element.style.color = isError ? "#ffd4d4" : "#d9f2ff";
}

function toggleAdminMenu(forceOpen = null) {
  if (!adminMenuItems || !adminMenuToggle) return;
  const shouldOpen = forceOpen === null ? !adminMenuItems.classList.contains("show") : forceOpen;
  adminMenuItems.classList.toggle("show", shouldOpen);
  adminMenuToggle.setAttribute("aria-expanded", String(shouldOpen));
}

function preencherSugestoesCnpj() {
  const options = cnpjsDisponiveis.map((item) =>
    `<option value="${escapeHtml(item.valor)}"></option>`
  ).join("");

  if (cnpjSugestoes) {
    cnpjSugestoes.innerHTML = options;
  }
}

async function carregarCnpjsDisponiveis() {
  try {
    const response = await fetch("/api/admin/cnpjs");
    const data = await response.json();
    if (!data.success) return;
    cnpjsDisponiveis = data.cnpjs || [];
    preencherSugestoesCnpj();
  } catch (error) {
    console.error("Erro ao carregar CNPJs:", error);
  }
}

function montarInputCnpj(usuarioId, valor = "") {
  return `
    <input
      type="text"
      class="admin-search-input cnpj-aprovacao-input"
      data-id="${usuarioId}"
      list="cnpjSugestoes"
      value="${escapeHtml(valor)}"
      placeholder="Escolha ou digite um CNPJ"
      style="min-width:240px; max-width:280px;"
    />
  `;
}

function renderLogUpdates(logs = []) {
  if (!logUpdatesTableBody) return;
  logUpdatesTableBody.innerHTML = logs.length
    ? logs.map((log) => `
        <tr>
          <td>${escapeHtml(log.data_hora)}</td>
          <td>${escapeHtml(log.nome_usuario)}</td>
          <td>${escapeHtml(log.tipo_importacao)}</td>
          <td>${escapeHtml(log.nome_arquivo)}</td>
          <td>${log.inseridos ?? 0}</td>
          <td>${log.atualizados ?? 0}</td>
          <td>${log.ignorados ?? 0}</td>
        </tr>
      `).join("")
    : `<tr><td colspan="7">Nenhum log encontrado.</td></tr>`;
}

function renderLogAcessos(logs = []) {
  if (!logAcessosTableBody) return;
  logAcessosTableBody.innerHTML = logs.length
    ? logs.map((log) => `
        <tr>
          <td>${escapeHtml(log.data_hora)}</td>
          <td>${escapeHtml(log.email_informado)}</td>
          <td>${Number(log.sucesso) === 1 ? "Sim" : "Nao"}</td>
          <td>${escapeHtml(log.ip)}</td>
        </tr>
      `).join("")
    : `<tr><td colspan="4">Nenhum log encontrado.</td></tr>`;
}

async function carregarLogUpdates() {
  try {
    const response = await fetch("/api/admin/log-updates");
    const data = await response.json();
    if (!data.success) {
      setAlert(logUpdatesAlert, data.message || "Erro ao carregar logs.", true);
      renderLogUpdates();
      return;
    }
    setAlert(logUpdatesAlert);
    renderLogUpdates(data.logs || []);
  } catch (error) {
    console.error(error);
    setAlert(logUpdatesAlert, "Erro ao conectar com o servidor.", true);
    renderLogUpdates();
  }
}

async function carregarLogAcessos() {
  try {
    const response = await fetch("/api/admin/log-acessos");
    const data = await response.json();
    if (!data.success) {
      setAlert(logAcessosAlert, data.message || "Erro ao carregar logs de acesso.", true);
      renderLogAcessos();
      return;
    }
    setAlert(logAcessosAlert);
    renderLogAcessos(data.logs || []);
  } catch (error) {
    console.error(error);
    setAlert(logAcessosAlert, "Erro ao conectar com o servidor.", true);
    renderLogAcessos();
  }
}

async function carregarDashboard() {
  try {
    const response = await fetch("/api/admin/dashboard");
    const data = await response.json();
    if (!data.success) return;

    const dash = data.dashboard || {};
    document.getElementById("dashRastreios").textContent = dash.total_rastreios ?? "-";
    document.getElementById("dashUsuarios").textContent = dash.total_usuarios ?? "-";
    document.getElementById("dashLogins").textContent = dash.logins_hoje ?? "-";
    document.getElementById("dashImportacao").textContent = dash.ultima_importacao || "-";
  } catch (error) {
    console.error(error);
  }
}

async function carregarUsuariosAdmin() {
  if (!usuariosTableBody) return;

  try {
    const response = await fetch("/api/admin/usuarios");
    const data = await response.json();

    if (!data.success) {
      setAlert(usuariosAlert, data.message || "Erro ao carregar usuarios.", true);
      usuariosTableBody.innerHTML = `<tr><td colspan="7">Erro ao carregar usuarios.</td></tr>`;
      return;
    }

    setAlert(usuariosAlert);
    let usuarios = data.usuarios || [];
    const termo = (usuariosBuscaInput?.value || "").trim().toLowerCase();

    if (termo) {
      usuarios = usuarios.filter((usuario) =>
        (usuario.nome || "").toLowerCase().includes(termo) ||
        (usuario.email || "").toLowerCase().includes(termo)
      );
    }

    if (!usuarios.length) {
      usuariosTableBody.innerHTML = `<tr><td colspan="7">Nenhum usuario encontrado.</td></tr>`;
      return;
    }

    usuariosTableBody.innerHTML = usuarios.map((usuario) => {
      const adminSelect = `
        <select class="admin-select" data-id="${usuario.id}">
          <option value="0" ${Number(usuario.is_admin) === 0 ? "selected" : ""}>Nao</option>
          <option value="1" ${Number(usuario.is_admin) === 1 ? "selected" : ""}>Sim</option>
        </select>
      `;

      let acaoHtml = "-";
      if (Number(usuario.is_admin) !== 1) {
        if (Number(usuario.aprovado) === 1) {
          acaoHtml = `<button class="ghost-btn bloquear-usuario-btn" data-id="${usuario.id}" type="button">Bloquear</button>`;
        } else {
          acaoHtml = `
            <div class="inline-actions">
              ${montarInputCnpj(usuario.id, usuario.cnpj_cliente || "")}
              <button class="primary-btn aprovar-usuario-btn" data-id="${usuario.id}" type="button">Aprovar</button>
            </div>
          `;
        }
      }

      return `
        <tr>
          <td>${usuario.id}</td>
          <td>${escapeHtml(usuario.nome)}</td>
          <td>${escapeHtml(usuario.email)}</td>
          <td>${adminSelect}</td>
          <td>${escapeHtml(usuario.cnpj_cliente || "")}</td>
          <td>${Number(usuario.aprovado) === 1 ? "Sim" : "Nao"}</td>
          <td>${acaoHtml}</td>
        </tr>
      `;
    }).join("");
  } catch (error) {
    console.error(error);
    setAlert(usuariosAlert, "Erro ao conectar com o servidor.", true);
    usuariosTableBody.innerHTML = `<tr><td colspan="7">Erro ao conectar com o servidor.</td></tr>`;
  }
}

function renderDatabaseOverview(overview = {}) {
  if (databaseStatusGrid) {
    const status = overview.status || [];
    databaseStatusGrid.innerHTML = status.map((item) => `
      <div class="database-status-card">
        <strong>${escapeHtml(item.status_badge)}</strong>
        <span>${item.total} registro(s)</span>
      </div>
    `).join("");
  }

  if (databaseRastreiosTableBody) {
    const rastreios = overview.rastreios || [];
    databaseRastreiosTableBody.innerHTML = rastreios.length
      ? rastreios.map((item) => `
          <tr>
            <td>${escapeHtml(item.codigo)}</td>
            <td>${escapeHtml(item.destinatario)}</td>
            <td>${escapeHtml(item.status_badge)}</td>
            <td>${escapeHtml(item.previsao)}</td>
            <td>${escapeHtml(item.cnpj_cliente)}</td>
            <td>${escapeHtml(item.ultima_atualizacao_api || "-")}</td>
          </tr>
        `).join("")
      : `<tr><td colspan="6">Nenhum rastreio encontrado.</td></tr>`;
  }
}

async function carregarDatabaseOverview() {
  if (!databaseRastreiosTableBody) return;

  const params = new URLSearchParams();
  if (databaseCnpjFilter?.value) params.set("cnpj", databaseCnpjFilter.value.trim());
  if (databaseStatusFilter?.value) params.set("status", databaseStatusFilter.value.trim());

  try {
    const response = await fetch(`/api/admin/database-overview?${params.toString()}`);
    const data = await response.json();
    if (!data.success) {
      databaseRastreiosTableBody.innerHTML = `<tr><td colspan="6">Erro ao carregar a base.</td></tr>`;
      return;
    }
    renderDatabaseOverview(data.overview || {});
  } catch (error) {
    console.error(error);
    databaseRastreiosTableBody.innerHTML = `<tr><td colspan="6">Erro ao conectar com o servidor.</td></tr>`;
  }
}

function alternarTipoRegra() {
  const usaUf = regraTipo?.value === "UF";
  regraIdentificadorSelect?.classList.toggle("hidden", usaUf);
  regraIdentificadorManual?.classList.toggle("hidden", !usaUf);
}

function renderRegrasPrevisao(regras = []) {
  if (!regrasPrevisaoTableBody) return;
  regrasPrevisaoTableBody.innerHTML = regras.length
    ? regras.map((regra) => `
        <tr>
          <td>${escapeHtml(regra.tipo_regra)}</td>
          <td>${escapeHtml(regra.identificador)}</td>
          <td>${regra.dias_previsao}</td>
          <td>${regra.prioridade}</td>
          <td>${escapeHtml(regra.descricao || "")}</td>
          <td><button class="ghost-btn excluir-regra-btn" data-id="${regra.id}" type="button">Excluir</button></td>
        </tr>
      `).join("")
    : `<tr><td colspan="6">Nenhuma regra cadastrada.</td></tr>`;
}

async function carregarRegrasPrevisao() {
  try {
    const response = await fetch("/api/admin/regras-previsao");
    const data = await response.json();
    if (!data.success) {
      setAlert(regrasPrevisaoAlert, data.message || "Erro ao carregar regras.", true);
      renderRegrasPrevisao();
      return;
    }
    setAlert(regrasPrevisaoAlert);
    renderRegrasPrevisao(data.regras || []);
  } catch (error) {
    console.error(error);
    setAlert(regrasPrevisaoAlert, "Erro ao conectar com o servidor.", true);
    renderRegrasPrevisao();
  }
}

async function carregarCustodiasAdmin() {
  const status = filtroStatusCustodia?.value || "";
  const url = status ? `/api/admin/custodias?status=${encodeURIComponent(status)}` : "/api/admin/custodias";

  try {
    const response = await fetch(url);
    const data = await response.json();
    if (!data.success) {
      setAlert(custodiasAdminAlert, data.message || "Erro ao carregar custodias.", true);
      custodiasTableBody.innerHTML = `<tr><td colspan="9">Erro ao carregar custodias.</td></tr>`;
      return;
    }

    setAlert(custodiasAdminAlert);
    const custodias = data.custodias || [];
    custodiasTableBody.innerHTML = custodias.length
      ? custodias.map((item) => `
          <tr>
            <td>${item.id}</td>
            <td>${escapeHtml(item.codigo_ar)}</td>
            <td>${escapeHtml(item.tipo_solicitacao)}</td>
            <td>${escapeHtml(item.nome || "-")}</td>
            <td>${escapeHtml(item.cidade || "-")}/${escapeHtml(item.uf || "-")}</td>
            <td>${escapeHtml(item.status)}</td>
            <td>${escapeHtml(item.nome_usuario || item.email_usuario || "-")}</td>
            <td>${escapeHtml(item.data_criacao)}</td>
            <td>${item.status === "ABERTO" ? `<button class="primary-btn concluir-custodia-btn" data-id="${item.id}" type="button">Concluir</button>` : "-"}</td>
          </tr>
        `).join("")
      : `<tr><td colspan="9">Nenhuma solicitacao encontrada.</td></tr>`;
  } catch (error) {
    console.error(error);
    setAlert(custodiasAdminAlert, "Erro ao conectar com o servidor.", true);
    custodiasTableBody.innerHTML = `<tr><td colspan="9">Erro ao conectar com o servidor.</td></tr>`;
  }
}

importRastreiosForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  setAlert(importRastreiosAlert);

  const arquivo = arquivoRastreiosInput?.files?.[0];
  if (!arquivo) {
    setAlert(importRastreiosAlert, "Selecione um arquivo para importar.", true);
    return;
  }

  const formData = new FormData();
  formData.append("arquivo", arquivo);

  try {
    const response = await fetch("/api/admin/importar-rastreios", {
      method: "POST",
      body: formData
    });
    const data = await response.json();
    if (!data.success) {
      setAlert(importRastreiosAlert, data.message || "Erro ao importar rastreios.", true);
      return;
    }

    setAlert(importRastreiosAlert, `Importacao concluida. Inseridos: ${data.inseridos} | Atualizados: ${data.atualizados} | Ignorados: ${data.ignorados}`);
    importRastreiosForm.reset();
    await carregarDashboard();
    await carregarLogUpdates();
    await carregarDatabaseOverview();
    await carregarCnpjsDisponiveis();
    await carregarUsuariosAdmin();
  } catch (error) {
    console.error(error);
    setAlert(importRastreiosAlert, "Erro ao conectar com o servidor.", true);
  }
});

importarRegrasCsvForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  setAlert(regrasPrevisaoAlert);

  const arquivo = arquivoRegrasCsv?.files?.[0];
  if (!arquivo) {
    setAlert(regrasPrevisaoAlert, "Selecione um CSV de regras.", true);
    return;
  }

  const formData = new FormData();
  formData.append("arquivo", arquivo);

  try {
    const response = await fetch("/api/admin/regras-previsao/importar-csv", {
      method: "POST",
      body: formData
    });
    const data = await response.json();
    if (!data.success) {
      setAlert(regrasPrevisaoAlert, data.message || "Erro ao importar regras.", true);
      return;
    }
    setAlert(regrasPrevisaoAlert, data.message || "Importacao concluida.");
    importarRegrasCsvForm.reset();
    await carregarRegrasPrevisao();
  } catch (error) {
    console.error(error);
    setAlert(regrasPrevisaoAlert, "Erro ao conectar com o servidor.", true);
  }
});

regraPrevisaoForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const identificador = regraTipo.value === "UF"
    ? regraIdentificadorManual.value.trim().toUpperCase()
    : regraIdentificadorSelect.value.trim();

  try {
    const response = await fetch("/api/admin/regras-previsao", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        tipo_regra: regraTipo.value,
        identificador,
        dias_previsao: regraDiasPrevisao.value,
        prioridade: regraPrioridade.value,
        descricao: regraDescricao.value.trim(),
        codigo_ocorrencia: "GERAL"
      })
    });
    const data = await response.json();
    if (!data.success) {
      setAlert(regrasPrevisaoAlert, data.message || "Erro ao salvar regra.", true);
      return;
    }
    setAlert(regrasPrevisaoAlert, data.message || "Regra salva com sucesso.");
    regraPrevisaoForm.reset();
    alternarTipoRegra();
    await carregarRegrasPrevisao();
  } catch (error) {
    console.error(error);
    setAlert(regrasPrevisaoAlert, "Erro ao conectar com o servidor.", true);
  }
});

usuariosBuscaInput?.addEventListener("input", carregarUsuariosAdmin);
carregarCustodiasBtn?.addEventListener("click", carregarCustodiasAdmin);
filtroStatusCustodia?.addEventListener("change", carregarCustodiasAdmin);
carregarDatabaseBtn?.addEventListener("click", carregarDatabaseOverview);
databaseCnpjFilter?.addEventListener("change", carregarDatabaseOverview);
databaseStatusFilter?.addEventListener("keydown", (event) => {
  if (event.key === "Enter") carregarDatabaseOverview();
});
regraTipo?.addEventListener("change", alternarTipoRegra);
adminMenuToggle?.addEventListener("click", () => toggleAdminMenu());
exportarCustodiasBtn?.addEventListener("click", () => {
  const status = filtroStatusCustodia?.value || "";
  const url = status ? `/api/admin/custodias/exportar?status=${encodeURIComponent(status)}` : "/api/admin/custodias/exportar";
  window.open(url, "_blank");
});

document.addEventListener("click", (event) => {
  if (!adminMenuItems || !adminMenuToggle) return;
  const inside = adminMenuItems.contains(event.target) || adminMenuToggle.contains(event.target);
  if (!inside) toggleAdminMenu(false);
});

document.querySelectorAll("[data-nav-target]").forEach((button) => {
  button.addEventListener("click", () => {
    const targetId = button.getAttribute("data-nav-target");
    const target = targetId ? document.getElementById(targetId) : null;
    if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
    toggleAdminMenu(false);
  });
});

document.addEventListener("change", async (event) => {
  const target = event.target;
  if (!target.classList.contains("admin-select")) return;

  try {
    const response = await fetch(`/api/admin/usuarios/${target.dataset.id}/definir-admin`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ is_admin: target.value })
    });
    const data = await response.json();
    if (!data.success) {
      alert(data.message || "Erro ao atualizar perfil.");
      await carregarUsuariosAdmin();
      return;
    }
    await carregarUsuariosAdmin();
  } catch (error) {
    console.error(error);
    alert("Erro ao conectar com o servidor.");
  }
});

document.addEventListener("click", async (event) => {
  const target = event.target;

  if (target.classList.contains("aprovar-usuario-btn")) {
    const usuarioId = target.dataset.id;
    const input = document.querySelector(`.cnpj-aprovacao-input[data-id="${usuarioId}"]`);
    const cnpj = input?.value?.trim() || "";

    if (!cnpj) {
      alert("Escolha ou digite um CNPJ antes de aprovar.");
      return;
    }

    try {
      const response = await fetch(`/api/admin/usuarios/${usuarioId}/aprovar`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ cnpj_cliente: cnpj })
      });
      const data = await response.json();
      if (!data.success) {
        alert(data.message || "Erro ao aprovar usuario.");
        return;
      }
      await carregarUsuariosAdmin();
      await carregarDashboard();
      await carregarCnpjsDisponiveis();
    } catch (error) {
      console.error(error);
      alert("Erro ao conectar com o servidor.");
    }
  }

  if (target.classList.contains("bloquear-usuario-btn")) {
    try {
      const response = await fetch(`/api/admin/usuarios/${target.dataset.id}/bloquear`, {
        method: "POST"
      });
      const data = await response.json();
      if (!data.success) {
        alert(data.message || "Erro ao bloquear usuario.");
        return;
      }
      await carregarUsuariosAdmin();
      await carregarDashboard();
    } catch (error) {
      console.error(error);
      alert("Erro ao conectar com o servidor.");
    }
  }

  if (target.classList.contains("concluir-custodia-btn")) {
    try {
      const response = await fetch(`/api/admin/custodias/${target.dataset.id}/concluir`, {
        method: "POST"
      });
      const data = await response.json();
      if (!data.success) {
        setAlert(custodiasAdminAlert, data.message || "Erro ao concluir solicitacao.", true);
        return;
      }
      await carregarCustodiasAdmin();
    } catch (error) {
      console.error(error);
      setAlert(custodiasAdminAlert, "Erro ao conectar com o servidor.", true);
    }
  }

  if (target.classList.contains("excluir-regra-btn")) {
    try {
      const response = await fetch(`/api/admin/regras-previsao/${target.dataset.id}`, {
        method: "DELETE"
      });
      const data = await response.json();
      if (!data.success) {
        setAlert(regrasPrevisaoAlert, data.message || "Erro ao excluir regra.", true);
        return;
      }
      await carregarRegrasPrevisao();
    } catch (error) {
      console.error(error);
      setAlert(regrasPrevisaoAlert, "Erro ao conectar com o servidor.", true);
    }
  }
});

async function init() {
  alternarTipoRegra();
  await carregarCnpjsDisponiveis();
  await Promise.all([
    carregarDashboard(),
    carregarUsuariosAdmin(),
    carregarLogAcessos(),
    carregarLogUpdates(),
    carregarDatabaseOverview(),
    carregarRegrasPrevisao()
  ]);
}

init();
