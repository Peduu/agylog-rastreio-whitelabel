const buscarCustodiaBtn = document.getElementById("buscarCustodiaBtn");
const codigoCustodia = document.getElementById("custodiaCodigoInput");
const custodiaAlertBox = document.getElementById("custodiaAlert");
const custodiaResultado = document.getElementById("custodiaResultado");

const custodiaCodigo = document.getElementById("custodiaCodigo");
const custodiaDestinatario = document.getElementById("custodiaNome");
const custodiaStatus = document.getElementById("custodiaStatus");
const custodiaUltimoStatus = document.getElementById("custodiaCidade");

const novoEnderecoForm = document.getElementById("novoEnderecoForm");
const enviarSolicitacaoCustodiaBtn = document.getElementById("enviarCustodiaBtn");

const voltarRastreioBtn = document.getElementById("voltarRastreioBtn");
const custodiaMenuToggle = document.getElementById("custodiaMenuToggle");
const custodiaMenuItems = document.getElementById("custodiaMenuItems");

function toggleCustodiaMenu(forceOpen = null) {
  if (!custodiaMenuItems || !custodiaMenuToggle) return;
  const shouldOpen = forceOpen === null ? !custodiaMenuItems.classList.contains("show") : forceOpen;
  custodiaMenuItems.classList.toggle("show", shouldOpen);
  custodiaMenuToggle.setAttribute("aria-expanded", String(shouldOpen));
}

custodiaMenuToggle?.addEventListener("click", () => toggleCustodiaMenu());

document.addEventListener("click", (event) => {
  if (!custodiaMenuItems || !custodiaMenuToggle) return;
  const inside = custodiaMenuItems.contains(event.target) || custodiaMenuToggle.contains(event.target);
  if (!inside) toggleCustodiaMenu(false);
});

voltarRastreioBtn?.addEventListener("click", () => {
  localStorage.setItem("irParaRastreio", "true");
  window.location.href = "/";
});

function showAlert(message) {
  if (!custodiaAlertBox) return;
  custodiaAlertBox.textContent = message;
  custodiaAlertBox.classList.add("show");
}

function hideAlert() {
  if (!custodiaAlertBox) return;
  custodiaAlertBox.textContent = "";
  custodiaAlertBox.classList.remove("show");
}

document.addEventListener("change", function (e) {
  if (e.target.name === "tipoSolicitacao") {
    novoEnderecoForm.classList.toggle("hidden", e.target.value !== "NOVO_ENDERECO");
  }
});

buscarCustodiaBtn?.addEventListener("click", async () => {
  hideAlert();
  custodiaResultado.classList.add("hidden");

  const codigo = codigoCustodia.value.trim();
  if (!codigo) {
    showAlert("Digite uma AR.");
    return;
  }

  try {
    const response = await fetch("/api/custodia/buscar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ codigo })
    });

    const data = await response.json();

    if (!data.success) {
      showAlert(data.message || "Erro ao buscar AR.");
      return;
    }

    custodiaCodigo.textContent = data.ar.codigo || "";
    custodiaDestinatario.textContent = data.ar.destinatario || "";
    custodiaStatus.textContent = data.ar.statusBadge || "";
    custodiaUltimoStatus.textContent = data.ar.ultimoStatus || "";

    custodiaResultado.classList.remove("hidden");
  } catch (error) {
    console.error("Erro ao buscar custódia:", error);
    showAlert("Erro ao conectar com o servidor.");
  }
});

enviarSolicitacaoCustodiaBtn?.addEventListener("click", async () => {
  hideAlert();

  const tipo = document.querySelector('input[name="tipoSolicitacao"]:checked')?.value || "MESMO_ENDERECO";

  const payload = {
    codigo_ar: custodiaCodigo.textContent.trim(),
    tipo_solicitacao: tipo,
    nome: document.getElementById("novoNome").value.trim(),
    endereco: document.getElementById("novoEndereco").value.trim(),
    numero: document.getElementById("novoNumero").value.trim(),
    complemento: document.getElementById("novoComplemento").value.trim(),
    bairro: document.getElementById("novoBairro").value.trim(),
    cidade: document.getElementById("novoCidade").value.trim(),
    cep: document.getElementById("novoCep").value.trim(),
    uf: document.getElementById("novoUf").value.trim(),
    ponto_referencia: document.getElementById("novoReferencia").value.trim()
  };

  try {
    const response = await fetch("/api/custodia/solicitar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!data.success) {
      showAlert(data.message || "Erro ao enviar solicitação.");
      return;
    }

    showAlert(data.message || "Solicitação enviada com sucesso.");

    setTimeout(() => {
      // limpa input principal
      codigoCustodia.value = "";

      // esconde resultado
      custodiaResultado.classList.add("hidden");

      // limpa campos de exibição
      custodiaCodigo.textContent = "";
      custodiaDestinatario.textContent = "";
      custodiaStatus.textContent = "";
      custodiaUltimoStatus.textContent = "";

      // volta opção padrão
      const radioMesmo = document.querySelector('input[name="tipoSolicitacao"][value="MESMO_ENDERECO"]');
      if (radioMesmo) radioMesmo.checked = true;

      // esconde form novo endereço
      novoEnderecoForm.classList.add("hidden");

      // limpa campos
      document.getElementById("novoNome").value = "";
      document.getElementById("novoCep").value = "";
      document.getElementById("novoEndereco").value = "";
      document.getElementById("novoNumero").value = "";
      document.getElementById("novoComplemento").value = "";
      document.getElementById("novoBairro").value = "";
      document.getElementById("novoCidade").value = "";
      document.getElementById("novoUf").value = "";
      document.getElementById("novoReferencia").value = "";

      hideAlert();
    }, 1500);

  } catch (error) {
    console.error("Erro ao enviar solicitação:", error);
    showAlert("Erro ao conectar com o servidor.");
  }
});
