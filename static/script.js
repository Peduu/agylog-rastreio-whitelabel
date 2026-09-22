/**
 * CorelliLog – Frontend de Autenticação e Rastreio
 */
(function () {
  'use strict';

  const metaCsp = document.createElement('meta');
  metaCsp.httpEquiv = 'Content-Security-Policy';
  metaCsp.content = [
  "default-src 'self'",
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
  "font-src 'self' https://fonts.gstatic.com",
  "img-src 'self' data:",
  "script-src 'self'",
  "connect-src 'self' https://viacep.com.br",
    ].join('; ');
  document.head.prepend(metaCsp);

  const MAX_ATTEMPTS      = 5;
  const LOCK_DURATION_MS  = 5 * 60 * 1000;
  const LS_ATTEMPTS       = 'cl_fail_n';
  const LS_LOCKED_UNTIL   = 'cl_lock_ts';
  const CAPTCHA_MAX_AGE   = 120000;

  let loginCaptchaIssuedAt = 0;
  let lockTimerInterval = null;
  let loggedUser = null;
  let resultadosAtuais = [];

  function getAttempts() { return parseInt(localStorage.getItem(LS_ATTEMPTS) || '0', 10); }
  function getLockedUntil() { return parseInt(localStorage.getItem(LS_LOCKED_UNTIL) || '0', 10); }
  function setAttempts(n) { localStorage.setItem(LS_ATTEMPTS, String(n)); }
  function setLockedUntil(t) { localStorage.setItem(LS_LOCKED_UNTIL, String(t)); }
  function clearLockState() {
    localStorage.removeItem(LS_ATTEMPTS);
    localStorage.removeItem(LS_LOCKED_UNTIL);
  }
  function isLocked() { return Date.now() < getLockedUntil(); }

  function escapeHtml(raw) {
    return String(raw ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/`/g, '&#x60;');
  }

  function isValidEmail(v) {
    if (!v || v.length > 254) return false;
    const parts = v.split('@');
    if (parts.length !== 2) return false;
    const [local, domain] = parts;
    return local.length > 0 && local.length <= 64 && domain.includes('.') && domain.length > 3;
  }

  function getCsrfToken() {
    let t = sessionStorage.getItem('cl_csrf');
    if (!t) {
      const arr = new Uint8Array(24);
      crypto.getRandomValues(arr);
      t = Array.from(arr, b => b.toString(16).padStart(2, '0')).join('');
      sessionStorage.setItem('cl_csrf', t);
    }
    return t;
  }

  function secureHeaders(extra = {}) {
    return {
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCsrfToken(),
      ...extra,
    };
  }

  const authScreen         = document.getElementById('authScreen');
  const trackingScreen     = document.getElementById('trackingScreen');

  const tabLogin           = document.getElementById('tabLogin');
  const tabRegister        = document.getElementById('tabRegister');
  const tabIndicator       = document.getElementById('tabIndicator');
  const panelLogin         = document.getElementById('panelLogin');
  const panelRegister      = document.getElementById('panelRegister');

  const loginForm          = document.getElementById('loginForm');
  const loginEmailEl       = document.getElementById('loginEmail');
  const loginPasswordEl    = document.getElementById('loginPassword');
  const loginCaptchaImg    = document.getElementById('loginCaptchaImg');
  const loginCaptchaAns    = document.getElementById('loginCaptchaAnswer');
  const loginCaptchaSts    = document.getElementById('loginCaptchaStatus');
  const loginRefreshBtn    = document.getElementById('refreshLoginCaptcha');
  const loginSubmitBtn     = document.getElementById('loginSubmitBtn');
  const loginAlertBox      = document.getElementById('loginAlertBox');
  const loginLockOverlay   = document.getElementById('loginLockOverlay');
  const loginLockTimer     = document.getElementById('loginLockTimer');
  const toggleLoginPwd     = document.getElementById('toggleLoginPassword');
  const loginHoneypot      = document.getElementById('loginHoneypot');

  const registerForm       = document.getElementById('registerForm');
  const regFirstNameEl     = document.getElementById('regFirstName');
  const regLastNameEl      = document.getElementById('regLastName');
  const regEmailEl         = document.getElementById('regEmail');
  const regPasswordEl      = document.getElementById('regPassword');
  const regConfirmPwdEl    = document.getElementById('regConfirmPassword');
  const regTermsEl         = document.getElementById('regTerms');
  const registerSubmitBtn  = document.getElementById('registerSubmitBtn');
  const registerAlertBox   = document.getElementById('registerAlertBox');
  const registerSuccessBox = document.getElementById('registerSuccessBox');
  const toggleRegPwd       = document.getElementById('toggleRegPassword');
  const strengthFill       = document.getElementById('strengthFill');
  const strengthLabel      = document.getElementById('strengthLabel');
  const regHoneypot        = document.getElementById('regHoneypot');

  const logoutBtn          = document.getElementById('logoutBtn');
  const backToLoginBtn     = document.getElementById('backToLoginBtn');
  const trackingCodes      = document.getElementById('trackingCodes');
  const searchBtn          = document.getElementById('searchBtn');
  const clearBtn           = document.getElementById('clearBtn');
  const exportBtn          = document.getElementById('exportBtn');
  const resultsContainer   = document.getElementById('resultsContainer');
  const trackingAlertBox   = document.getElementById('trackingAlertBox');
  const userAvatar         = document.getElementById('userAvatar');
  const userName           = document.getElementById('userName');
  const menuAdminBtn       = document.getElementById('menuAdminBtn');
  const dashboardCliente   = document.getElementById('dashboardCliente');
  const clienteConsultasHoje = document.getElementById('clienteConsultasHoje');
  const clienteDocumentosDisponiveis = document.getElementById('clienteDocumentosDisponiveis');
  const clienteCustodiasAbertas = document.getElementById('clienteCustodiasAbertas');
  const clienteUltimoCodigo = document.getElementById('clienteUltimoCodigo');
  const clienteUltimoStatus = document.getElementById('clienteUltimoStatus');

  function showAlert(el, msg, type = 'danger') {
    if (!el) return;
    el.textContent = msg;
    el.className = type === 'warning' ? 'alert-box warning show' : 'alert-box show';
  }

  function hideAlert(el) {
    if (!el) return;
    el.textContent = '';
    el.className = 'alert-box';
  }

  function buildThirdPartyTrackingHtml(tracking) {
    const codigoTerceiro = String(tracking?.codigoTerceiro || '').trim();
    if (!codigoTerceiro) return '';

    return `
      <div class="third-party-block">
        <div class="result-grid third-party-grid">
          <div class="info-item">
            <span class="label">Codigo Terceiro</span>
            <strong>${escapeHtml(codigoTerceiro)}</strong>
          </div>
        </div>
      </div>
    `;
  }

  function setCaptchaStatus(el, msg, variant = 'neutral') {
    if (!el) return;
    el.textContent = msg;
    el.className = `captcha-status ${variant}`;
  }

  async function loadLoginCaptcha() {
    hideAlert(loginAlertBox);
    setCaptchaStatus(loginCaptchaSts, 'Gerando novo desafio…', 'neutral');
    loginCaptchaAns.value = '';
    loginCaptchaAns.className = '';
    loginCaptchaIssuedAt = 0;

    if (loginCaptchaImg) {
      loginCaptchaImg.innerHTML =
        '<div class="captcha-loading"><div class="captcha-spinner"></div><span>Gerando desafio…</span></div>';
    }

    try {
      const res = await fetch('/api/captcha/login', { credentials: 'same-origin' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      if (!data.success || !data.svg) {
        throw new Error('Falha ao gerar captcha.');
      }

      loginCaptchaIssuedAt = Date.now();

      const parser = new DOMParser();
      const doc = parser.parseFromString(data.svg, 'image/svg+xml');

      doc.querySelectorAll('script').forEach(el => el.remove());
      doc.querySelectorAll('*').forEach(el => {
        [...el.attributes].forEach(attr => {
          if (attr.name.toLowerCase().startsWith('on')) {
            el.removeAttribute(attr.name);
          }
        });
      });

      if (loginCaptchaImg) {
        loginCaptchaImg.innerHTML = doc.documentElement.outerHTML;
      }
      setCaptchaStatus(loginCaptchaSts, 'Desafio carregado', 'neutral');
    } catch (_) {
      if (loginCaptchaImg) {
        loginCaptchaImg.innerHTML =
          '<div class="captcha-loading">Erro ao carregar. Clique em Atualizar.</div>';
      }
      setCaptchaStatus(loginCaptchaSts, 'Erro ao carregar', 'danger');
    }
  }

  function activateTab(which) {
    const isLogin = which === 'login';
    tabLogin.classList.toggle('active', isLogin);
    tabRegister.classList.toggle('active', !isLogin);
    tabLogin.setAttribute('aria-selected', String(isLogin));
    tabRegister.setAttribute('aria-selected', String(!isLogin));
    panelLogin.style.display = isLogin ? '' : 'none';
    panelRegister.style.display = !isLogin ? '' : 'none';
    tabIndicator.classList.toggle('right', !isLogin);

    if (isLogin) hideAlert(loginAlertBox);
    else hideAlert(registerAlertBox);
  }

  tabLogin?.addEventListener('click', () => activateTab('login'));
  tabRegister?.addEventListener('click', () => activateTab('register'));

  function atualizarDashboardPrincipalAdmin(dashboard = {}) {
    if (clienteConsultasHoje) clienteConsultasHoje.textContent = String(dashboard.total_entregas || 0);
    if (clienteDocumentosDisponiveis) clienteDocumentosDisponiveis.textContent = String(dashboard.entregas_finalizadas || 0);
    if (clienteCustodiasAbertas) clienteCustodiasAbertas.textContent = String(dashboard.entregas_pendentes || 0);

    const ultimaEntrega = dashboard.ultima_entrega || null;
    if (clienteUltimoCodigo) clienteUltimoCodigo.textContent = ultimaEntrega?.codigo || '-';
    if (clienteUltimoStatus) {
      clienteUltimoStatus.textContent = ultimaEntrega
        ? `${ultimaEntrega.status_badge || 'Sem status'} | Previsao: ${ultimaEntrega.previsao || 'Nao definida'}`
        : 'Nenhuma entrega registrada ainda.';
    }
  }

  async function carregarDashboardPrincipalAdmin() {
    if (!loggedUser?.is_admin || !dashboardCliente) return;

    try {
      const res = await fetch('/api/admin/dashboard', {
        method: 'GET',
        credentials: 'same-origin'
      });

      let data = {};
      try { data = await res.json(); } catch {}

      if (!res.ok || !data.success || !data.dashboard) {
        atualizarDashboardPrincipalAdmin({});
        return;
      }

      atualizarDashboardPrincipalAdmin(data.dashboard);
    } catch (_) {
      atualizarDashboardPrincipalAdmin({});
    }
  }

  function goToTracking(userData) {
    loggedUser = userData || {};
    const displayName = userData?.nome || userData?.email || 'Usuário';
    const initials = (displayName || 'U')[0].toUpperCase();
    if (userAvatar) userAvatar.textContent = initials;
    if (userName) userName.textContent = displayName;
    if (menuAdminBtn) menuAdminBtn.classList.toggle('hidden', !userData?.is_admin);
    if (dashboardCliente) dashboardCliente.classList.toggle('hidden', !userData?.is_admin);
    authScreen?.classList.remove('active');
    trackingScreen?.classList.add('active');
    if (userData?.is_admin) carregarDashboardPrincipalAdmin();
  }

  function goToAuth() {
    trackingScreen?.classList.remove('active');
    authScreen?.classList.add('active');
    activateTab('login');
  }

  function registerFailedAttempt() {
    const n = getAttempts() + 1;
    setAttempts(n);
    if (n >= MAX_ATTEMPTS) {
      setLockedUntil(Date.now() + LOCK_DURATION_MS);
      showLockOverlay();
    }
  }

  function showLockOverlay() {
    clearInterval(lockTimerInterval);
    if (loginSubmitBtn) loginSubmitBtn.disabled = true;
    if (loginLockOverlay) loginLockOverlay.style.display = 'flex';

    function tick() {
      const rem = Math.max(0, getLockedUntil() - Date.now());
      if (rem <= 0) {
        clearInterval(lockTimerInterval);
        if (loginLockOverlay) loginLockOverlay.style.display = 'none';
        if (loginSubmitBtn) loginSubmitBtn.disabled = false;
        clearLockState();
        loadLoginCaptcha();
        return;
      }
      const m = Math.floor(rem / 60000);
      const s = Math.floor((rem % 60000) / 1000);
      if (loginLockTimer) {
        loginLockTimer.textContent = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
      }
    }

    tick();
    lockTimerInterval = setInterval(tick, 1000);
  }

  function checkLockOnLoad() {
    if (isLocked()) showLockOverlay();
  }

  loginRefreshBtn?.addEventListener('click', loadLoginCaptcha);

  loginCaptchaAns?.addEventListener('input', () => {
    loginCaptchaAns.classList.remove('valid', 'invalid');
    const v = loginCaptchaAns.value.trim();
    if (!v) {
      setCaptchaStatus(loginCaptchaSts, 'Aguardando validação', 'neutral');
      return;
    }
    setCaptchaStatus(loginCaptchaSts, v.length >= 5 ? 'Pronto para enviar' : 'Digitando…', 'neutral');
  });

  function togglePasswordVisibility(inputEl, btnEl) {
    const show = inputEl.type === 'password';
    inputEl.type = show ? 'text' : 'password';
    btnEl.setAttribute('aria-label', show ? 'Ocultar senha' : 'Mostrar senha');
  }

  toggleLoginPwd?.addEventListener('click', () => togglePasswordVisibility(loginPasswordEl, toggleLoginPwd));
  toggleRegPwd?.addEventListener('click', () => togglePasswordVisibility(regPasswordEl, toggleRegPwd));

  function evalPasswordStrength(pwd) {
    if (!pwd) return { score: 0, label: '—', cls: '' };
    let score = 0;
    if (pwd.length >= 8) score++;
    if (pwd.length >= 12) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^A-Za-z0-9]/.test(pwd)) score++;

    if (score <= 1) return { score: 20, label: 'Fraca', cls: '' };
    if (score <= 2) return { score: 45, label: 'Razoável', cls: '' };
    if (score <= 3) return { score: 70, label: 'Boa', cls: 'medium' };
    return { score: 100, label: 'Forte', cls: 'strong' };
  }

  regPasswordEl?.addEventListener('input', () => {
    const { score, label, cls } = evalPasswordStrength(regPasswordEl.value);
    if (strengthFill) {
      strengthFill.style.width = `${score}%`;
      strengthFill.className = `strength-fill${cls ? ' ' + cls : ''}`;
    }
    if (strengthLabel) strengthLabel.textContent = label;
  });

  loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert(loginAlertBox);

    if (isLocked()) {
      showLockOverlay();
      return;
    }

    if (loginHoneypot?.value) {
      showAlert(loginAlertBox, 'Validação de segurança falhou. Tente novamente mais tarde.');
      return;
    }

    const email = loginEmailEl.value.trim();
    const password = loginPasswordEl.value;
    const captcha = loginCaptchaAns.value.trim().toUpperCase();

    if (!email) {
      showAlert(loginAlertBox, 'Informe um e-mail ou login válido.');
      loginEmailEl.focus();
      return;
    }

    if (!password || password.length < 4) {
      showAlert(loginAlertBox, 'Informe sua senha para continuar.');
      loginPasswordEl.focus();
      return;
    }

    if (!loginCaptchaIssuedAt) {
      showAlert(loginAlertBox, 'Captcha não carregado. Clique em "Atualizar" e tente de novo.');
      return;
    }

    if (Date.now() - loginCaptchaIssuedAt > CAPTCHA_MAX_AGE) {
      showAlert(loginAlertBox, 'O desafio expirou. Um novo será carregado automaticamente.');
      loadLoginCaptcha();
      return;
    }

    if (!captcha) {
      showAlert(loginAlertBox, 'Digite o código de verificação antes de continuar.');
      setCaptchaStatus(loginCaptchaSts, 'Código obrigatório', 'danger');
      loginCaptchaAns.focus();
      return;
    }

    loginSubmitBtn.disabled = true;
    loginSubmitBtn.textContent = 'Verificando…';

    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        credentials: 'same-origin',
        headers: secureHeaders(),
        body: JSON.stringify({
          email: email,
          senha: password,
          captcha_answer: captcha,
          honeypot: loginHoneypot.value.trim()
        })
      });

      let data = {};
      try { data = await res.json(); } catch {}

      if (data.locked) {
        setLockedUntil(Date.now() + ((data.seconds_remaining || 300) * 1000));
        setAttempts(MAX_ATTEMPTS);
        showLockOverlay();
        return;
      }

      if (!data.success) {
        setCaptchaStatus(loginCaptchaSts, 'Código incorreto', 'danger');
        loginCaptchaAns.classList.add('invalid');
        registerFailedAttempt();
        showAlert(loginAlertBox, data.message || 'Credenciais inválidas. Verifique e tente novamente.');
        loadLoginCaptcha();
        return;
      }

      setCaptchaStatus(loginCaptchaSts, 'Autenticado ✓', 'success');
      loginCaptchaAns.classList.add('valid');
      clearLockState();

      setTimeout(() => {
        loginSubmitBtn.textContent = 'Entrar com segurança';
        goToTracking(data.usuario || { email });
      }, 500);

    } catch (_) {
      showAlert(loginAlertBox, 'Falha de conexão. Verifique sua rede e tente novamente.');
    } finally {
      loginSubmitBtn.disabled = false;
      if (loginSubmitBtn.textContent === 'Verificando…') {
        loginSubmitBtn.textContent = 'Entrar com segurança';
      }
    }
  });

  registerForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert(registerAlertBox);
    if (registerSuccessBox) registerSuccessBox.style.display = 'none';

    if (regHoneypot?.value) {
      showAlert(registerAlertBox, 'Validação de segurança falhou.');
      return;
    }

    const firstName = regFirstNameEl.value.trim();
    const lastName = regLastNameEl.value.trim();
    const email = regEmailEl.value.trim().toLowerCase();
    const password = regPasswordEl.value;
    const confirmPwd = regConfirmPwdEl.value;

    if (!firstName || firstName.length < 2) {
      showAlert(registerAlertBox, 'Informe seu nome (mínimo 2 caracteres).');
      regFirstNameEl.focus();
      return;
    }

    if (!lastName || lastName.length < 2) {
      showAlert(registerAlertBox, 'Informe seu sobrenome (mínimo 2 caracteres).');
      regLastNameEl.focus();
      return;
    }

    if (!isValidEmail(email)) {
      showAlert(registerAlertBox, 'Informe um e-mail corporativo válido.');
      regEmailEl.focus();
      return;
    }

    if (!password || password.length < 8) {
      showAlert(registerAlertBox, 'A senha deve ter pelo menos 8 caracteres.');
      regPasswordEl.focus();
      return;
    }

    if (password !== confirmPwd) {
      showAlert(registerAlertBox, 'As senhas não coincidem. Verifique e tente novamente.');
      regConfirmPwdEl.focus();
      return;
    }

    if (!regTermsEl.checked) {
      showAlert(registerAlertBox, 'Você precisa aceitar os Termos de Uso para continuar.');
      return;
    }

    const { score } = evalPasswordStrength(password);
    if (score < 45) {
      showAlert(registerAlertBox, 'Senha muito fraca. Use letras maiúsculas, números e símbolos.');
      regPasswordEl.focus();
      return;
    }

    registerSubmitBtn.disabled = true;
    registerSubmitBtn.textContent = 'Criando conta…';

    try {
      const res = await fetch('/api/register', {
        method: 'POST',
        credentials: 'same-origin',
        headers: secureHeaders(),
        body: JSON.stringify({
          nome: firstName,
          sobrenome: lastName,
          email: email,
          senha: password,
          confirmar_senha: confirmPwd
        })
      });

      let data = {};
      try { data = await res.json(); } catch {}

      if (!data.success) {
        showAlert(registerAlertBox, data.message || 'Erro ao criar conta. Tente novamente.');
        return;
      }

      registerForm.reset();
      if (strengthFill) strengthFill.style.width = '0%';
      if (strengthLabel) strengthLabel.textContent = '—';
      if (registerSuccessBox) registerSuccessBox.style.display = 'flex';

      setTimeout(() => {
        if (registerSuccessBox) registerSuccessBox.style.display = 'none';
        activateTab('login');
        loginEmailEl.value = email;
        loginPasswordEl.focus();
      }, 2200);

    } catch (_) {
      showAlert(registerAlertBox, 'Falha de conexão. Verifique sua rede e tente novamente.');
    } finally {
      registerSubmitBtn.disabled = false;
      registerSubmitBtn.textContent = 'Criar conta segura';
    }
  });

  function renderResultsFromApi(resultados) {
    resultsContainer.innerHTML = '';
    resultadosAtuais = resultados;

    resultados.forEach((data) => {
      const card = document.createElement('section');
      card.className = 'panel result-card';

      const safe = {
        codigo: escapeHtml(data.codigo),
        codigoReferencia: escapeHtml(data.codigoReferencia || ''),
        destinatario: escapeHtml(data.destinatario),
        previsao: escapeHtml(data.previsao),
        dataBaixa: escapeHtml(data.dataBaixa),
        recebidoPor: escapeHtml(data.recebidoPor),
        ultimoStatus: escapeHtml(data.ultimoStatus),
        statusBadge: escapeHtml(data.statusBadge),
        observacaoVinculo: escapeHtml(data.observacaoVinculo || '')
      };
      const thirdPartyHtml = buildThirdPartyTrackingHtml(data.rastreioTerceiro);

      card.innerHTML = `
        <div class="result-top">
          <div>
            <span class="eyebrow">Resultado da consulta</span>
            <h2>Informações do Documento</h2>
          </div>
          <span class="status-badge">${safe.statusBadge}</span>
        </div>
        <div class="result-grid">
          <div class="info-item"><span class="label">Destinatário</span><strong>${safe.destinatario}</strong></div>
          <div class="info-item"><span class="label">Número de rastreio</span><strong>${safe.codigo}</strong></div>
          ${safe.codigoReferencia ? `<div class="info-item"><span class="label">Rastreado pela AR pai</span><strong>${safe.codigoReferencia}</strong></div>` : ''}
          <div class="info-item"><span class="label">Previsão de entrega</span><strong>${safe.previsao}</strong></div>
          <div class="info-item"><span class="label">Data de baixa</span><strong>${safe.dataBaixa}</strong></div>
          <div class="info-item"><span class="label">Recebido por</span><strong>${safe.recebidoPor}</strong></div>
          <div class="info-item"><span class="label">Último status</span><strong>${safe.ultimoStatus}</strong></div>
          ${safe.observacaoVinculo ? `<div class="info-item"><span class="label">Observação</span><strong>${safe.observacaoVinculo}</strong></div>` : ''}
        </div>
        ${thirdPartyHtml}
      `;

      resultsContainer.appendChild(card);
    });

    resultsContainer.classList.remove('hidden');

    if (exportBtn) {
      exportBtn.classList.toggle('hidden', resultados.length <= 1);
    }
  }

  function escaparCSV(valor) {
    if (valor === null || valor === undefined) return '';
    return `"${String(valor).replace(/"/g, '""')}"`;
  }

  function exportarResultadosCSV() {
    if (!resultadosAtuais || resultadosAtuais.length <= 1) return;

    const cabecalho = [
      'codigo',
      'destinatario',
      'previsao',
      'data_baixa',
      'recebido_por',
      'ultimo_status',
      'status_badge'
    ];

    const linhas = [cabecalho.join(',')];

    resultadosAtuais.forEach((item) => {
      linhas.push([
        escaparCSV(item.codigo),
        escaparCSV(item.destinatario),
        escaparCSV(item.previsao),
        escaparCSV(item.dataBaixa),
        escaparCSV(item.recebidoPor),
        escaparCSV(item.ultimoStatus),
        escaparCSV(item.statusBadge)
      ].join(','));
    });

    const conteudoCSV = '\uFEFF' + linhas.join('\n');
    const blob = new Blob([conteudoCSV], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `rastreios_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  }

  searchBtn?.addEventListener('click', async () => {
    hideAlert(trackingAlertBox);

    const raw = trackingCodes.value.trim();
    if (!raw) {
      showAlert(trackingAlertBox, 'Digite ao menos um código de rastreio para continuar.', 'warning');
      resultsContainer.classList.add('hidden');
      resultsContainer.innerHTML = '';
      resultadosAtuais = [];
      if (exportBtn) exportBtn.classList.add('hidden');
      return;
    }

    const codes = raw
      .split(/[\n,;]/)
      .map(c => c.trim())
      .filter(Boolean)
      .slice(0, 50);

    if (!codes.length) {
      showAlert(trackingAlertBox, 'Nenhum código válido identificado.', 'warning');
      return;
    }

    try {
      const res = await fetch('/api/rastreio', {
        method: 'POST',
        credentials: 'same-origin',
        headers: secureHeaders(),
        body: JSON.stringify({ codigos: codes })
      });

      const data = await res.json();

      if (!data.success) {
        showAlert(trackingAlertBox, data.message || 'Erro ao consultar rastreios.');
        resultadosAtuais = [];
        if (exportBtn) exportBtn.classList.add('hidden');
        return;
      }

      if (!data.resultados || data.resultados.length === 0) {
        showAlert(trackingAlertBox, 'Nenhum rastreio encontrado.', 'warning');
        resultsContainer.innerHTML = '';
        resultsContainer.classList.add('hidden');
        resultadosAtuais = [];
        if (exportBtn) exportBtn.classList.add('hidden');
        return;
      }

      renderResultsFromApi(data.resultados);
      if (loggedUser?.is_admin) {
        carregarDashboardPrincipalAdmin();
      }
    } catch (_) {
      showAlert(trackingAlertBox, 'Falha de conexão. Verifique sua rede e tente novamente.');
    }
  });

  clearBtn?.addEventListener('click', () => {
    trackingCodes.value = '';
    resultsContainer.innerHTML = '';
    resultsContainer.classList.add('hidden');
    resultadosAtuais = [];
    if (exportBtn) exportBtn.classList.add('hidden');
    hideAlert(trackingAlertBox);
  });

  exportBtn?.addEventListener('click', exportarResultadosCSV);

  function resetSession() {
    loginForm?.reset();
    registerForm?.reset();
    if (loginPasswordEl) loginPasswordEl.type = 'password';
    if (regPasswordEl) regPasswordEl.type = 'password';
    if (trackingCodes) trackingCodes.value = '';
    if (resultsContainer) {
      resultsContainer.innerHTML = '';
      resultsContainer.classList.add('hidden');
    }
    resultadosAtuais = [];
    if (exportBtn) exportBtn.classList.add('hidden');

    hideAlert(trackingAlertBox);
    hideAlert(loginAlertBox);
    hideAlert(registerAlertBox);

    if (registerSuccessBox) registerSuccessBox.style.display = 'none';
    if (loginLockOverlay) loginLockOverlay.style.display = 'none';
    clearInterval(lockTimerInterval);

    if (strengthFill) strengthFill.style.width = '0%';
    if (strengthLabel) strengthLabel.textContent = '—';

    loggedUser = null;
    goToAuth();
    loadLoginCaptcha();
  }

  logoutBtn?.addEventListener('click', async () => {
    try {
      await fetch('/api/logout', {
        method: 'POST',
        credentials: 'same-origin'
      });
    } catch (_) {}

    resetSession();
  });

  backToLoginBtn?.addEventListener('click', goToAuth);

  function openModal(id) {
    const m = document.getElementById(id);
    if (m) {
      m.style.display = 'flex';
      document.body.style.overflow = 'hidden';
    }
  }

  function closeModal(id) {
    const m = document.getElementById(id);
    if (m) {
      m.style.display = 'none';
      document.body.style.overflow = '';
    }
  }

  document.getElementById('openTermos')?.addEventListener('click', () => openModal('modalTermos'));
  document.getElementById('openPrivacidade')?.addEventListener('click', () => openModal('modalPrivacidade'));
  document.getElementById('closeTermos')?.addEventListener('click', () => closeModal('modalTermos'));
  document.getElementById('closeTermosBtn')?.addEventListener('click', () => closeModal('modalTermos'));
  document.getElementById('closePrivacidade')?.addEventListener('click', () => closeModal('modalPrivacidade'));
  document.getElementById('closePrivBtn')?.addEventListener('click', () => closeModal('modalPrivacidade'));

  ['modalTermos', 'modalPrivacidade'].forEach(id => {
    document.getElementById(id)?.addEventListener('click', e => {
      if (e.target.id === id) closeModal(id);
    });
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      closeModal('modalTermos');
      closeModal('modalPrivacidade');
    }
  });

  const FORMS_URL = 'https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=eHl3FFmoEkiRa4wUbwLEav2UfWHIGghNqa9JA1GwxlhUQzNZVVZRUE1IQTFRNDk5OFQ0NkpHQlpORC4u';
document.getElementById('solicitacaoBtn')?.addEventListener('click', () => {
  window.open(FORMS_URL, '_blank', 'noopener,noreferrer');
});


function abrirTelaCorretaAoCarregar() {
  const irParaRastreio = localStorage.getItem("irParaRastreio");

  if (irParaRastreio === "true") {
    localStorage.removeItem("irParaRastreio");

    authScreen?.classList.remove('active');
    trackingScreen?.classList.add('active');

    return true;
  }

  return false;
}

async function restaurarSessaoDoServidor() {
  try {
    const res = await fetch('/api/session', {
      method: 'GET',
      credentials: 'same-origin'
    });

    let data = {};
    try { data = await res.json(); } catch {}

    if (!res.ok || !data.authenticated || !data.usuario) {
      return false;
    }

    const email = data.usuario.email || data.usuario.nome || 'Usuário';
    goToTracking(data.usuario);
    return true;

  } catch (_) {
    return false;
  }
}

async function init() {
  const abriuRastreio = abrirTelaCorretaAoCarregar();

  const restaurou = await restaurarSessaoDoServidor();
  if (restaurou) {
    return;
  }

  if (abriuRastreio) {
    goToAuth();
    return;
  }

  activateTab('login');
  loadLoginCaptcha();
  checkLockOnLoad();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
})();
