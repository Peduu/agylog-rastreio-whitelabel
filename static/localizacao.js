/* Cartao "Onde esta seu pedido" (spec e plano de 08/10/2026).
 *
 * - Cena de rota montada com as pecas do gerador das cenas (static/scenes/<cliente>-rota.js) nas posicoes 145/420/692.
 * - Mapinha no canto: contornos oficiais das UFs (IBGE) e pontos na MESMA projecao (Web Mercator), pin onde o pedido
 *   esta e bandeira quadriculada no endereco de entrega. Coordenadas = sede do municipio no IBGE (vem do backend).
 * - Nome de cidade so entra como TEXTO (textContent). O SVG so recebe numeros e as pecas estaticas do gerador.
 */
(function () {
  'use strict';

  const VERSAO = '20261009a';                    // suba quando regenerar pecas ou dados geograficos (cache do navegador)
  const SLOT_X = { 1: 145, 2: 420, 3: 692 };
  const CAMINHAO_X = { estrada12: 282, slot2: 420, estrada23: 566, slot3: 600 };
  const ESTRADA_Y = 264;
  const MAPA = { x: 520, y: 8, w: 268, h: 128 };   // canto do ceu; acima dos telhados (y 142)
  const RAD = Math.PI / 180;
  const cache = { rotas: {}, indice: null, ufs: {} };
  let ultimaChave = '';
  let geracao = 0;

  function carregarScript(src) {
    return new Promise((ok, erro) => {
      const s = document.createElement('script');
      s.src = src;
      s.onload = ok;
      s.onerror = erro;
      document.head.appendChild(s);
    });
  }

  async function pecasDoCliente(cliente) {
    if (!/^[a-z0-9]+$/.test(cliente || '')) return null;
    if (window.AgyRotas && window.AgyRotas[cliente]) return window.AgyRotas[cliente];
    if (!cache.rotas[cliente]) {
      cache.rotas[cliente] = carregarScript(`/static/scenes/${cliente}-rota.js?v=${VERSAO}`).catch(() => null);
    }
    await cache.rotas[cliente];
    return (window.AgyRotas && window.AgyRotas[cliente]) || null;
  }

  async function buscarJson(url) {
    const r = await fetch(url, { credentials: 'same-origin' });
    if (!r.ok) throw new Error(url);
    return r.json();
  }

  // ---- projecao (a MESMA para contornos e pontos) ----------------------------------------------------------------------
  function merc(lon, lat) {
    return [lon * RAD, -Math.log(Math.tan(Math.PI / 4 + (lat * RAD) / 2))];
  }

  function inversa(mx, my) {
    return [mx / RAD, (2 * Math.atan(Math.exp(-my)) - Math.PI / 2) / RAD];
  }

  function enquadrar(pontos) {
    const ms = pontos.map((p) => merc(p.lon, p.lat));
    const xs = ms.map((m) => m[0]);
    const ys = ms.map((m) => m[1]);
    const cx = (Math.min(...xs) + Math.max(...xs)) / 2;
    const cy = (Math.min(...ys) + Math.max(...ys)) / 2;
    let sx = (Math.max(...xs) - Math.min(...xs)) * 1.6 + 0.035;   // margem + vao minimo (~2 graus) para mostrar a regiao
    let sy = (Math.max(...ys) - Math.min(...ys)) * 1.6 + 0.035;
    const aspecto = MAPA.w / MAPA.h;
    if (sx / sy > aspecto) sy = sx / aspecto; else sx = sy * aspecto;
    const esc = MAPA.w / sx;
    const x0 = cx - sx / 2;
    const y0 = cy - sy / 2;
    const proj = (lon, lat) => {
      const m = merc(lon, lat);
      return [MAPA.x + (m[0] - x0) * esc, MAPA.y + (m[1] - y0) * esc];
    };
    const [lonA, latA] = inversa(x0, y0 + sy);
    const [lonB, latB] = inversa(x0 + sx, y0);
    return { proj, caixa: [lonA, latA, lonB, latB] };
  }

  async function contornos(caixa) {
    if (!cache.indice) cache.indice = buscarJson(`/static/data/uf/indice.json?v=${VERSAO}`);
    const indice = await cache.indice;
    const ufs = Object.keys(indice).filter((uf) => {
      const [x0, y0, x1, y1] = indice[uf];
      return !(x1 < caixa[0] || x0 > caixa[2] || y1 < caixa[1] || y0 > caixa[3]);
    });
    const saida = {};
    await Promise.all(ufs.map(async (uf) => {
      if (!/^[A-Z]{2}$/.test(uf)) return;
      if (!cache.ufs[uf]) cache.ufs[uf] = buscarJson(`/static/data/uf/${uf}.json?v=${VERSAO}`);
      saida[uf] = await cache.ufs[uf];
    }));
    return saida;
  }

  const n = (v) => (Math.round(v * 10) / 10).toFixed(1);

  function pin(x, y, cor, fundo) {
    return `<g data-marcador="pin" data-x="${n(x)}" data-y="${n(y)}" transform="translate(${n(x)},${n(y)})">`
      + `<ellipse cx="0" cy="0.6" rx="3.4" ry="1.3" fill="#000" fill-opacity=".25"/>`
      + `<path d="M0,0 C-1.4,-3.6 -6.2,-7.6 -6.2,-12.2 A6.2,6.2 0 1 1 6.2,-12.2 C6.2,-7.6 1.4,-3.6 0,0 Z" fill="${cor}" stroke="${fundo}" stroke-width="1.3"/>`
      + `<circle cx="0" cy="-12.2" r="2.4" fill="${fundo}"/></g>`;
  }

  function bandeiraXadrez(x, y, tinta) {
    let quadros = '';
    for (let l = 0; l < 2; l += 1) {
      for (let c = 0; c < 3; c += 1) {
        quadros += `<rect x="${c * 3.4}" y="${l * 3.4}" width="3.4" height="3.4" fill="${(c + l) % 2 ? '#ffffff' : '#17171c'}"/>`;
      }
    }
    return `<g data-marcador="chegada" data-x="${n(x)}" data-y="${n(y)}" transform="translate(${n(x)},${n(y)})">`
      + `<rect x="-0.7" y="-17" width="1.4" height="17" rx=".7" fill="${tinta}" fill-opacity=".8"/>`
      + `<g transform="translate(0.7,-16.6) skewY(-8)">${quadros}`
      + `<rect width="10.2" height="6.8" fill="none" stroke="${tinta}" stroke-opacity=".45" stroke-width=".6"/></g></g>`;
  }

  async function mapinha(pfx, cor, pontos) {
    const comPin = pontos.filter((p) => p.papel !== 'destino');
    if (!pontos.length) return '';
    const { proj, caixa } = enquadrar(pontos);
    let ufs;
    try {
      ufs = await contornos(caixa);
    } catch (e) {
      return '';
    }
    const atual = pontos.find((p) => p.papel === 'atual') || pontos.find((p) => p.papel === 'destino');
    let estados = '';
    Object.keys(ufs).sort().forEach((uf) => {
      const d = ufs[uf].map((anel) => 'M' + anel.map(([lon, lat]) => proj(lon, lat).map(n).join(',')).join('L') + 'Z').join('');
      const destaque = atual && atual.uf === uf;
      estados += `<path data-uf="${uf}" d="${d}" fill="${destaque ? cor.acento : cor.tinta}" fill-opacity="${destaque ? '.16' : '.07'}"`
        + ` stroke="${cor.tinta}" stroke-opacity=".24" stroke-width=".7" stroke-linejoin="round"/>`;
    });
    const xy = comPin.map((p) => proj(p.lon, p.lat));
    const linha = xy.length > 1
      ? `<path d="M${xy.map((q) => q.map(n).join(',')).join('L')}" fill="none" stroke="${cor.acento}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>`
      : '';
    let marcas = '';
    comPin.forEach((p, i) => {
      const [x, y] = xy[i];
      if (p.papel === 'origem' || p.papel === 'passagem') {
        marcas += `<circle data-marcador="${p.papel}" cx="${n(x)}" cy="${n(y)}" r="${p.papel === 'origem' ? 2.6 : 2}" fill="${cor.tinta}" fill-opacity=".7"/>`;
      }
    });
    const destino = pontos.find((p) => p.papel === 'destino');
    const pinAtual = pontos.find((p) => p.papel === 'atual');
    if (destino) {
      const [x, y] = proj(destino.lon, destino.lat);
      const mesmoLugar = pinAtual && pinAtual.lat === destino.lat && pinAtual.lon === destino.lon;
      marcas += bandeiraXadrez(x + (mesmoLugar ? 6.5 : 0), y, cor.tinta);   // mesma cidade: a bandeira fica ao lado da ponta do pin
    }
    if (pinAtual) {
      const [x, y] = proj(pinAtual.lon, pinAtual.lat);
      marcas += pin(x, y, cor.acento, cor.painel);
    }
    const { x, y, w, h } = MAPA;
    return `<g data-mapinha="1"><clipPath id="${pfx}mm"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10"/></clipPath>`
      + `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="${cor.painel}" fill-opacity=".94" stroke="${cor.tinta}" stroke-opacity=".16"/>`
      + `<g clip-path="url(#${pfx}mm)">${estados}${linha}${marcas}</g>`
      + `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="none" stroke="${cor.tinta}" stroke-opacity=".16"/></g>`;
  }

  function cenaSvg(p, pfx, cena) {
    const g = (x, s) => `<g transform="translate(${x},0)">${s}</g>`;
    let s = p.ceu;
    if (cena.slot1) s += g(SLOT_X[1], p.galpao);
    if (cena.slot3 === 'casa') s += g(SLOT_X[3], p.casa);
    else if (cena.slot3 === 'apagado') s += g(SLOT_X[3], p.galpao_apagado);
    s += g(SLOT_X[2], cena.slot2 === 'apagado' ? p.galpao_apagado : p.galpao);
    s += p.estrada;
    const ini = cena.slot1 ? SLOT_X[1] : SLOT_X[2];
    const xc = CAMINHAO_X[cena.caminhao] || SLOT_X[2];
    const chegou = cena.caminhao === 'slot3';                     // entregue: o trajeto inteiro fica cheio, sem tracejado
    const fim = chegou ? xc : (cena.slot3 ? SLOT_X[3] : SLOT_X[2]);
    const acento = p.cor.acento;
    const xCheio = chegou ? SLOT_X[3] : xc;
    if (xCheio > ini) {
      s += `<line x1="${ini}" x2="${xCheio}" y1="${ESTRADA_Y}" y2="${ESTRADA_Y}" stroke="${acento}" stroke-width="5" stroke-linecap="round"/>`;
    }
    if (fim > xc + 12) {
      s += `<line class="${pfx}dash" x1="${xc}" x2="${fim}" y1="${ESTRADA_Y}" y2="${ESTRADA_Y}" stroke="${acento}" stroke-opacity=".75" stroke-width="5" stroke-linecap="round"/>`;
    }
    const rodando = cena.caminhao === 'estrada12' || cena.caminhao === 'estrada23';
    s += g(xc, rodando ? p.caminhao_rodando : p.caminhao);
    return s;
  }

  function iconeChegada() {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 14 16');
    svg.setAttribute('class', 'loc-icone-chegada');
    svg.setAttribute('aria-hidden', 'true');
    let quadros = '';
    for (let l = 0; l < 2; l += 1) {
      for (let c = 0; c < 3; c += 1) {
        quadros += `<rect x="${2 + c * 3.6}" y="${1.5 + l * 3.6}" width="3.6" height="3.6" fill="${(c + l) % 2 ? '#ffffff' : '#17171c'}"/>`;
      }
    }
    svg.innerHTML = `<rect x="1" y="1" width="1.4" height="14.5" rx=".7" fill="currentColor"/>${quadros}`
      + '<rect x="2" y="1.5" width="10.8" height="7.2" fill="none" stroke="currentColor" stroke-opacity=".5" stroke-width=".6"/>';
    return svg;
  }

  function preencherFrase(destino, frase) {
    destino.textContent = '';
    (frase || []).forEach((s) => {
      if (!s.b) {
        destino.appendChild(document.createTextNode(String(s.t || '')));
        return;
      }
      const b = document.createElement('b');
      if (s.uf && /^[A-Z]{2}$/.test(s.uf)) {
        const img = document.createElement('img');
        img.className = 'loc-flag';
        img.src = `/static/flags/uf/${s.uf}.png?v=${VERSAO}`;
        img.alt = '';
        img.setAttribute('aria-hidden', 'true');
        img.width = 21;
        img.height = 15;
        b.appendChild(img);
      }
      b.appendChild(document.createTextNode(String(s.t || '')));
      destino.appendChild(b);
    });
  }

  function preencherTrilho(destino, trilho) {
    destino.textContent = '';
    (trilho || []).forEach((item) => {
      const x = SLOT_X[item.slot];
      if (!x) return;
      const d = document.createElement('div');
      d.className = 'loc-ponto';
      d.style.left = `${(x / 8).toFixed(2)}%`;
      d.style.setProperty('--slot', String(item.slot));          // no celular o trilho vira 3 colunas (localizacao.css)
      const t = document.createElement('strong');
      if (item.icone === 'chegada') t.appendChild(iconeChegada());
      t.appendChild(document.createTextNode(String(item.titulo || '')));
      const s = document.createElement('span');
      s.textContent = String(item.sub || '');
      d.appendChild(t);
      d.appendChild(s);
      destino.appendChild(d);
    });
  }

  async function render(dados, cliente) {
    const card = document.getElementById('localizacaoCard');
    if (!card) return;
    const loc = dados && dados.localizacao;
    if (!loc || !loc.cena) {
      limpar();
      return;
    }
    const chave = JSON.stringify([cliente, loc]);
    if (chave === ultimaChave && !card.hidden) return;        // atualizacao automatica sem mudanca: nao reinicia a animacao
    ultimaChave = chave;
    const minha = ++geracao;
    preencherFrase(document.getElementById('locFrase'), loc.frase);
    preencherTrilho(document.getElementById('locTrilho'), loc.trilho);
    const nota = document.getElementById('locNota');
    if (nota) nota.textContent = loc.atualizado ? `Posição pela última leitura numa unidade AGYLOG (${loc.atualizado}).` : 'Posição pela última leitura numa unidade AGYLOG.';
    const palco = document.getElementById('locCena');
    card.hidden = false;
    const p = await pecasDoCliente(cliente);
    if (minha !== geracao) return;
    if (!p) {
      palco.hidden = true;                                       // sem pecas: fica so a frase e o trilho
      return;
    }
    const pfx = (p.defs.match(/id="([a-z0-9]+rt_)glow"/) || [])[1] || 'locrt_';
    const mapa = await mapinha(pfx, p.cor, loc.pontos || []);
    if (minha !== geracao) return;
    palco.hidden = false;
    palco.style.background = p.cor.painel;
    // O mapinha e um SVG a parte (mesmas coordenadas da cena): no computador fica no canto do ceu; no celular desce para baixo
    // da cena em tamanho legivel (localizacao.css).
    const { x, y, w, h } = MAPA;
    const mapaSvg = mapa
      ? `<div class="loc-mapa"><svg xmlns="http://www.w3.org/2000/svg" viewBox="${x - 1} ${y - 1} ${w + 2} ${h + 2}" role="img"`
        + ` aria-label="Mapa da região do pedido" class="loc-mapa-svg">${mapa}</svg></div>`
      : '';
    palco.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 290" role="img" aria-label="Trajeto do pedido"`
      + ` class="loc-svg"><style>${p.css}</style><defs>${p.defs}</defs>${cenaSvg(p, pfx, loc.cena)}</svg>${mapaSvg}`;
  }

  function limpar() {
    geracao += 1;
    ultimaChave = '';
    const card = document.getElementById('localizacaoCard');
    if (!card) return;
    card.hidden = true;
    ['locFrase', 'locTrilho', 'locCena'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.textContent = '';
    });
  }

  window.AgyLocalizacao = { render, limpar };
}());
