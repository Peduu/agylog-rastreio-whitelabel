// Cartão de rastreio dos Correios, usado pelo portal dos clientes e pela Simple Company.
(function () {
  'use strict';

  const SRO = /^([A-Z]{2})(\d{3})(\d{3})(\d{3})([A-Z]{2})$/;
  const CORREIOS_URL = 'https://rastreamento.correios.com.br/app/index.php?objetos=';

  function fillCode(el, code) {
    el.replaceChildren();
    const match = SRO.exec(code);
    (match ? match.slice(1) : [code]).forEach((part) => {
      const span = document.createElement('span');
      span.textContent = part;
      el.appendChild(span);
    });
  }

  function copyWithFallback(text) {
    const area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    let ok = false;
    try { ok = document.execCommand('copy'); } catch (_) { ok = false; }
    area.remove();
    return ok;
  }

  async function copyCode(card, button) {
    const code = card.dataset.code;
    if (!code) return;
    let ok = false;
    try {
      await navigator.clipboard.writeText(code);
      ok = true;
    } catch (_) {
      ok = copyWithFallback(code);
    }
    if (!ok) return;
    const status = card.querySelector('[data-postal-status]');
    button.classList.add('is-copied');
    button.setAttribute('aria-label', 'Código copiado');
    if (status) status.textContent = 'Código copiado';
    clearTimeout(button.postalTimer);
    button.postalTimer = setTimeout(() => {
      button.classList.remove('is-copied');
      button.setAttribute('aria-label', 'Copiar código de rastreio');
      if (status) status.textContent = '';
    }, 1800);
  }

  function render(card, tracking) {
    if (!card) return;
    const codeEl = card.querySelector('[data-postal-code]');
    const link = card.querySelector('[data-postal-link]');
    const copy = card.querySelector('[data-postal-copy]');
    const code = String(tracking?.codigoTerceiro || '').trim().toUpperCase();

    if (!code) {
      delete card.dataset.code;
      if (codeEl) codeEl.textContent = '—';
      if (link) link.removeAttribute('href');
      card.classList.add('hidden');
      return;
    }

    card.dataset.code = code;
    if (codeEl) fillCode(codeEl, code);
    if (link) link.href = CORREIOS_URL + encodeURIComponent(code);
    if (copy && !copy.dataset.bound) {
      copy.dataset.bound = '1';
      copy.addEventListener('click', () => copyCode(card, copy));
    }
    card.classList.remove('hidden');
  }

  window.AgyCorreios = { render };
})();
