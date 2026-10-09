/* Cartao "Onde esta seu pedido" (spec e plano de 08/10/2026; mapa no lugar da cena em 09/10/2026).
 *
 * - Linha simples da rota com seta e bandeira da UF ("Sao Paulo/SP -> Curitiba/PR").
 * - Mapa grande: contornos oficiais das UFs (IBGE) e pontos na MESMA projecao (Web Mercator), pin onde o pedido
 *   esta e bandeira quadriculada no endereco de entrega. Coordenadas = sede do municipio no IBGE (vem do backend).
 * - Trilho em 3 passos embaixo do mapa (origem, onde esta, destino) com as datas.
 * - Nome de cidade so entra como TEXTO (textContent). O SVG so recebe numeros e cores fixas desta tabela.
 */
(function () {
  'use strict';

  const VERSAO = '20261009a';                    // suba quando mudar os dados geograficos ou as bandeiras (cache do navegador)
  // Cores do mapa por cliente: as mesmas das cenas (KITS em tools/scenes/scenes.py; tests/test_localizacao_front.py confere).
  const CORES = {
    panini: { acento: '#CC0000', tinta: '#FFE9A8', painel: '#110500' },
    brb: { acento: '#4d9fff', tinta: '#BBD4FF', painel: '#0d111a' },
    inter: { acento: '#FF7A00', tinta: '#FFD9B8', painel: '#110500' },
    brbdux: { acento: '#E8E8EE', tinta: '#FFFFFF', painel: '#000000' },
    tricard: { acento: '#00B8A0', tinta: '#B7E9E1', painel: '#0d111a' },
    pinbank: { acento: '#F5A623', tinta: '#FFE2B0', painel: '#0d111a' },
    ip2w: { acento: '#3ECFC0', tinta: '#BFF3EC', painel: '#0d111a' },
    caoa: { acento: '#5dba8d', tinta: '#100c5a', painel: '#eef0f6' },
    ccxp: { acento: '#E33781', tinta: '#FFFFFF', painel: '#000000' },
    paranabanco: { acento: '#3366FF', tinta: '#0B1B3F', painel: '#eef2ff' },
    agy: { acento: '#3B82F6', tinta: '#CFE0FF', painel: '#0b111d' },   // pagina padrao (sem cliente)
  };
  // Area do mapa (unidades do SVG): larga no computador, mais alta no celular para continuar legivel.
  const QUADRO = { largo: { w: 800, h: 330 }, celular: { w: 400, h: 300 } };
  const ESC = 1.8;                                // tamanho de pin, bandeira e traco em relacao ao mapinha antigo
  const CELULAR = window.matchMedia ? window.matchMedia('(max-width: 560px)') : null;
  const RAD = Math.PI / 180;
  const cache = { indice: null, ufs: {} };
  let ultimaChave = '';
  let ultimoPedido = null;
  let geracao = 0;

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

  function enquadrar(pontos, quadro) {
    const ms = pontos.map((p) => merc(p.lon, p.lat));
    const xs = ms.map((m) => m[0]);
    const ys = ms.map((m) => m[1]);
    const cx = (Math.min(...xs) + Math.max(...xs)) / 2;
    const cy = (Math.min(...ys) + Math.max(...ys)) / 2;
    let sx = (Math.max(...xs) - Math.min(...xs)) * 1.6 + 0.045;   // margem + vao minimo (~2,5 graus) para mostrar a regiao
    let sy = (Math.max(...ys) - Math.min(...ys)) * 1.6 + 0.045;
    const aspecto = quadro.w / quadro.h;
    if (sx / sy > aspecto) sy = sx / aspecto; else sx = sy * aspecto;
    const esc = quadro.w / sx;
    const x0 = cx - sx / 2;
    const y0 = cy - sy / 2;
    const proj = (lon, lat) => {
      const m = merc(lon, lat);
      return [(m[0] - x0) * esc, (m[1] - y0) * esc];
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

  // Animacao do mapa (Pedro, 09/10: "estava suave"): a rota se desenha, o pin cai na cidade com um quique e fica
  // balancando de leve, a bandeira quadriculada tremula. Ciclo de 5 s; sem piscar.
  function cssMapa(pfx) {
    const p = `${pfx}mm`;
    return `<style>`
      + `.${p}rota{stroke-dasharray:100;animation:${p}desenha 5s ease-in-out infinite}`
      + `@keyframes ${p}desenha{0%{stroke-dashoffset:100;opacity:1}28%{stroke-dashoffset:0}90%{stroke-dashoffset:0;opacity:1}100%{stroke-dashoffset:0;opacity:0}}`
      + `.${p}cai{animation:${p}cai 5s ease-in-out infinite}`
      + `@keyframes ${p}cai{0%,22%{transform:translateY(-16px);opacity:0}30%{transform:translateY(0);opacity:1}34%{transform:translateY(-4px)}`
      + `38%{transform:translateY(0)}52%{transform:translateY(-2px)}66%{transform:translateY(0)}80%{transform:translateY(-2px)}94%,100%{transform:translateY(0);opacity:1}}`
      + `.${p}sombra{transform-box:fill-box;transform-origin:center;animation:${p}sombra 5s ease-in-out infinite}`
      + `@keyframes ${p}sombra{0%,22%{opacity:0;transform:scale(.4)}30%,100%{opacity:1;transform:scale(1)}}`
      + `.${p}onda{transform-box:fill-box;transform-origin:0 50%;animation:${p}onda 1.4s ease-in-out infinite}`
      + `@keyframes ${p}onda{0%,100%{transform:skewY(-10deg)}50%{transform:skewY(-3deg) scaleX(.92)}}`
      + `@media (prefers-reduced-motion:reduce){.${p}rota,.${p}cai,.${p}sombra,.${p}onda{animation:none!important}}`
      + `</style>`;
  }

  function pin(x, y, cor, fundo, pfx) {
    return `<g data-marcador="pin" data-x="${n(x)}" data-y="${n(y)}" transform="translate(${n(x)},${n(y)}) scale(${ESC})">`
      + `<ellipse class="${pfx}mmsombra" cx="0" cy="0.6" rx="3.4" ry="1.3" fill="#000" fill-opacity=".25"/>`
      + `<g class="${pfx}mmcai"><path d="M0,0 C-1.4,-3.6 -6.2,-7.6 -6.2,-12.2 A6.2,6.2 0 1 1 6.2,-12.2 C6.2,-7.6 1.4,-3.6 0,0 Z" fill="${cor}" stroke="${fundo}" stroke-width="1.3"/>`
      + `<circle cx="0" cy="-12.2" r="2.4" fill="${fundo}"/></g></g>`;
  }

  function bandeiraXadrez(x, y, tinta, pfx) {
    let quadros = '';
    for (let l = 0; l < 2; l += 1) {
      for (let c = 0; c < 3; c += 1) {
        quadros += `<rect x="${c * 3.4}" y="${l * 3.4}" width="3.4" height="3.4" fill="${(c + l) % 2 ? '#ffffff' : '#17171c'}"/>`;
      }
    }
    return `<g data-marcador="chegada" data-x="${n(x)}" data-y="${n(y)}" transform="translate(${n(x)},${n(y)}) scale(${ESC})"><g class="${pfx}mmcai">`
      + `<rect x="-0.7" y="-17" width="1.4" height="17" rx=".7" fill="${tinta}" fill-opacity=".8"/>`
      + `<g transform="translate(0.7,-16.6)"><g class="${pfx}mmonda">${quadros}`
      + `<rect width="10.2" height="6.8" fill="none" stroke="${tinta}" stroke-opacity=".45" stroke-width=".6"/></g></g></g></g>`;
  }

  // Rotulos das cidades (origem e onde esta / entrega): so posicao aqui; o NOME entra depois por textContent.
  function posicoesDosRotulos(marcas, quadro) {
    const rotulos = marcas.map(({ x, y, nome, folga }) => {
      const direita = x < quadro.w * 0.72;
      return { x: direita ? x + folga : x - folga, y: y + 5, ancora: direita ? 'start' : 'end', nome };
    });
    if (rotulos.length === 2) {                                   // cidades proximas: um rotulo para cada lado
      const [a, b] = rotulos;
      if (Math.abs(a.y - b.y) < 22 && Math.abs(a.x - b.x) < 170 && a.ancora === b.ancora) {
        const ma = marcas[0];
        a.ancora = a.ancora === 'start' ? 'end' : 'start';
        a.x = a.ancora === 'start' ? ma.x + ma.folga : ma.x - ma.folga;
      }
    }
    return rotulos;
  }

  async function montarMapa(pfx, cor, pontos, quadro) {
    if (!pontos.length) return null;
    const comPin = pontos.filter((p) => p.papel !== 'destino');
    const ultimo = pontos.find((p) => p.papel === 'destino');
    if (ultimo && !pontos.some((p) => p.papel === 'atual')) comPin.push(ultimo);   // entregue: a linha vai ate a bandeira
    const { proj, caixa } = enquadrar(pontos, quadro);
    let ufs;
    try {
      ufs = await contornos(caixa);
    } catch (e) {
      return null;
    }
    const atual = pontos.find((p) => p.papel === 'atual') || pontos.find((p) => p.papel === 'destino');
    let estados = '';
    Object.keys(ufs).sort().forEach((uf) => {
      const d = ufs[uf].map((anel) => 'M' + anel.map(([lon, lat]) => proj(lon, lat).map(n).join(',')).join('L') + 'Z').join('');
      const destaque = atual && atual.uf === uf;
      estados += `<path data-uf="${uf}" d="${d}" fill="${destaque ? cor.acento : cor.tinta}" fill-opacity="${destaque ? '.16' : '.07'}"`
        + ` stroke="${cor.tinta}" stroke-opacity=".26" stroke-width="1" stroke-linejoin="round"/>`;
    });
    const xy = comPin.map((p) => proj(p.lon, p.lat));
    const linha = xy.length > 1
      ? `<path class="${pfx}mmrota" pathLength="100" d="M${xy.map((q) => q.map(n).join(',')).join('L')}" fill="none" stroke="${cor.acento}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>`
      : '';
    let marcas = '';
    const nomes = [];
    comPin.forEach((p, i) => {
      const [x, y] = xy[i];
      if (p.papel === 'origem' || p.papel === 'passagem') {
        marcas += `<circle data-marcador="${p.papel}" cx="${n(x)}" cy="${n(y)}" r="${p.papel === 'origem' ? 4.6 : 3.4}" fill="${cor.tinta}" fill-opacity=".75"/>`;
      }
      if (p.papel === 'origem') nomes.push({ x, y, nome: p.nome, folga: 10 });
    });
    const destino = pontos.find((p) => p.papel === 'destino');
    const pinAtual = pontos.find((p) => p.papel === 'atual');
    if (destino) {
      const [x, y] = proj(destino.lon, destino.lat);
      const mesmoLugar = pinAtual && pinAtual.lat === destino.lat && pinAtual.lon === destino.lon;
      const dx = mesmoLugar ? 6.5 * ESC : 0;                     // mesma cidade: a bandeira fica ao lado da ponta do pin
      marcas += bandeiraXadrez(x + dx, y, cor.tinta, pfx);
      if (!pinAtual) nomes.push({ x, y, nome: destino.nome, folga: 24 });
    }
    if (pinAtual) {
      const [x, y] = proj(pinAtual.lon, pinAtual.lat);
      marcas += pin(x, y, cor.acento, cor.painel, pfx);
      nomes.push({ x, y, nome: pinAtual.nome, folga: destino ? 34 : 15 });
    }
    const { w, h } = quadro;
    const svg = `<g data-mapinha="1">${cssMapa(pfx)}<clipPath id="${pfx}mm"><rect width="${w}" height="${h}" rx="14"/></clipPath>`
      + `<rect width="${w}" height="${h}" rx="14" fill="${cor.painel}"/>`
      + `<g clip-path="url(#${pfx}mm)">${estados}${linha}${marcas}<g data-rotulos="1"></g></g>`
      + `<rect x=".5" y=".5" width="${w - 1}" height="${h - 1}" rx="14" fill="none" stroke="${cor.tinta}" stroke-opacity=".16"/></g>`;
    return { svg, rotulos: posicoesDosRotulos(nomes, quadro) };
  }

  function escreverRotulos(svg, rotulos, cor) {
    const alvo = svg.querySelector('[data-rotulos]');
    if (!alvo) return;
    rotulos.forEach((r) => {
      const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      t.setAttribute('x', n(r.x));
      t.setAttribute('y', n(r.y));
      t.setAttribute('text-anchor', r.ancora);
      t.setAttribute('class', 'loc-rotulo');
      t.setAttribute('fill', cor.tinta);
      t.setAttribute('stroke', cor.painel);
      t.textContent = String(r.nome || '').replace(/\/[A-Z]{2}$/, '');   // "Curitiba/PR" -> "Curitiba" (a UF ja esta no mapa)
      alvo.appendChild(t);
    });
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

  function seta() {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 24 12');
    svg.setAttribute('class', 'loc-seta');
    svg.setAttribute('aria-hidden', 'true');
    svg.innerHTML = '<path d="M1 6h19M15 1.5 20.5 6 15 10.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>';
    return svg;
  }

  // Linha simples da rota (Pedro, 09/10): "Sao Paulo/SP -> [bandeira] Curitiba/PR"; a cidade onde o pedido esta em
  // destaque e com a bandeira da UF; "em transito" depois da seta quando ainda nao chegou em outra unidade.
  function preencherLinha(destino, loc) {
    destino.textContent = '';
    const partes = (loc.linha || []).map((c) => {
      const el = document.createElement(c.atual ? 'b' : 'span');
      el.className = c.atual ? 'loc-cidade loc-atual' : 'loc-cidade';
      if (/^[A-Z]{2}$/.test(c.uf || '')) {                       // bandeira da UF em todas as cidades da linha (09/10)
        const img = document.createElement('img');
        img.className = 'loc-flag';
        img.src = `/static/flags/uf/${c.uf}.png?v=${VERSAO}`;
        img.alt = '';
        img.setAttribute('aria-hidden', 'true');
        img.width = 21;
        img.height = 15;
        el.appendChild(img);
      }
      const nome = document.createElement('span');
      nome.className = 'loc-nome';
      nome.textContent = String(c.t || '');
      el.appendChild(nome);
      return el;
    });
    if (loc.transito) {
      const t = document.createElement('span');
      t.className = 'loc-transito';
      t.textContent = 'em trânsito';
      partes.push(t);
    }
    partes.forEach((el, i) => {
      if (i > 0) destino.appendChild(seta());
      destino.appendChild(el);
    });
  }

  // Trilho em 3 passos (origem / onde esta / destino) embaixo do mapa; a coluna vem do slot do backend.
  function preencherTrilho(destino, trilho) {
    destino.textContent = '';
    (trilho || []).forEach((item) => {
      if (![1, 2, 3].includes(item.slot)) return;
      const d = document.createElement('div');
      d.className = 'loc-ponto';
      d.style.setProperty('--slot', String(item.slot));
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

  async function desenharMapa(palco, cliente, loc, minha) {
    const cor = CORES[cliente] || CORES.agy;
    const quadro = CELULAR && CELULAR.matches ? QUADRO.celular : QUADRO.largo;
    const pfx = 'loc_';
    const mapa = await montarMapa(pfx, cor, loc.pontos || [], quadro);
    if (minha !== geracao) return;
    if (!mapa) {
      palco.hidden = true;                                       // sem cidade no IBGE: fica so a linha e o trilho
      palco.textContent = '';
      return;
    }
    palco.hidden = false;
    palco.style.background = cor.painel;
    palco.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${quadro.w} ${quadro.h}" role="img"`
      + ` aria-label="Mapa da região do pedido" class="loc-mapa-svg">${mapa.svg}</svg>`;
    escreverRotulos(palco.querySelector('svg'), mapa.rotulos, cor);
  }

  async function render(dados, cliente) {
    const card = document.getElementById('localizacaoCard');
    if (!card) return;
    const loc = dados && dados.localizacao;
    if (!loc || !(loc.linha || []).length) {
      limpar();
      return;
    }
    const chave = JSON.stringify([cliente, loc]);
    if (chave === ultimaChave && !card.hidden) return;        // atualizacao automatica sem mudanca: nao reinicia a animacao
    ultimaChave = chave;
    ultimoPedido = { cliente, loc };
    const minha = ++geracao;
    preencherLinha(document.getElementById('locFrase'), loc);
    preencherTrilho(document.getElementById('locTrilho'), loc.trilho);
    const nota = document.getElementById('locNota');
    if (nota) nota.textContent = loc.atualizado ? `Posição pela última leitura numa unidade AGYLOG (${loc.atualizado}).` : 'Posição pela última leitura numa unidade AGYLOG.';
    card.hidden = false;
    await desenharMapa(document.getElementById('locCena'), cliente, loc, minha);
  }

  function limpar() {
    geracao += 1;
    ultimaChave = '';
    ultimoPedido = null;
    const card = document.getElementById('localizacaoCard');
    if (!card) return;
    card.hidden = true;
    ['locFrase', 'locTrilho', 'locCena'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.textContent = '';
    });
  }

  // Girou o celular / mudou a largura: redesenha so o mapa no formato certo (largo x celular).
  if (CELULAR) {
    const trocar = () => {
      if (!ultimoPedido) return;
      const card = document.getElementById('localizacaoCard');
      if (!card || card.hidden) return;
      desenharMapa(document.getElementById('locCena'), ultimoPedido.cliente, ultimoPedido.loc, ++geracao);
    };
    if (CELULAR.addEventListener) CELULAR.addEventListener('change', trocar);
    else if (CELULAR.addListener) CELULAR.addListener(trocar);
  }

  window.AgyLocalizacao = { render, limpar };
}());
