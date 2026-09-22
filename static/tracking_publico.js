// ── CLIENT THEMES ────────────────────────────────────────────────────────
  const CCXP_LOGO_DATA_URI = 'data:image/png;base64,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';
  const CLIENT_THEMES = {
    panini: {
      name: 'Panini',
      slug: 'panini',
      headerBg: '#FFD600',
      headerText: '#CC0000',
      accent: '#CC0000',
      accentHover: '#a80000',
      footerBg: '#1a1200',
      footerText: '#FFD600',
      pillBg: 'rgba(204,0,0,0.18)',
      pillColor: '#ff4444',
      logoSvg: `<img src="/static/logos/logo-panini.png?v=2" style="height:48px;width:auto;display:block;">`,
      partnerLine: 'Entrega realizada por <strong>AGYLOG</strong> em parceria com Panini'
    },
    brb: {
      name: 'Banco BRB',
      slug: 'brb',
      headerBg: '#002f7a',
      headerText: '#ffffff',
      accent: '#4d9fff',
      accentHover: '#1a7de0',
      footerBg: '#001a4d',
      footerText: '#a8c8ff',
      pillBg: 'rgba(77,159,255,0.15)',
      pillColor: '#4d9fff',
      logoSvg: `<img src="/static/logos/logo-brb.png?v=2" style="height:56px;width:auto;display:block;mix-blend-mode:screen;">`,
      partnerLine: 'Entrega realizada por <strong>AGYLOG</strong> em parceria com Banco BRB'
    },
    inter: {
      name: 'Banco Inter',
      slug: 'inter',
      headerBg: '#FF7A00',
      headerText: '#ffffff',
      accent: '#FF7A00',
      accentHover: '#e06a00',
      footerBg: '#7a3a00',
      footerText: '#ffe0c0',
      pillBg: 'rgba(255,122,0,0.18)',
      pillColor: '#ff9933',
      logoSvg: `<img src="/static/logos/logo-inter.png?v=2" style="height:56px;width:auto;display:block;">`,
      partnerLine: 'Entrega realizada por <strong>AGYLOG</strong> em parceria com Banco Inter'
    },
  brbdux:{name:"BRB DUX",slug:"brbdux",headerBg:"#000",headerText:"#fff",accent:"#fff",accentHover:"#ccc",footerBg:"#111",footerText:"#888",pillBg:"rgba(255,255,255,0.15)",pillColor:"#fff",logoSvg:"<img src='/static/logos/logo-brbdux.png' style='height:52px;width:auto;display:block;'>",partnerLine:"Entrega realizada por <strong>AGYLOG</strong> em parceria com BRB DUX"},
  tricard:{name:"Tricard",slug:"tricard",headerBg:"#1B3F7A",headerText:"#fff",accent:"#00B8A0",accentHover:"#009D8A",footerBg:"#132E5C",footerText:"#88BBD6",pillBg:"rgba(0,184,160,0.18)",pillColor:"#00D4B8",logoSvg:"<img src='/static/logos/logo-tricard.png' style='height:48px;width:auto;display:block;'>",partnerLine:"Entrega realizada por <strong>AGYLOG</strong> em parceria com Tricard"},
  pinbank:{name:"PinBank",slug:"pinbank",headerBg:"#111827",headerText:"#fff",accent:"#F5A623",accentHover:"#E09015",footerBg:"#0A0A14",footerText:"#F5A623",pillBg:"rgba(0,229,255,0.12)",pillColor:"#00E5FF",logoSvg:"<img src='/static/logos/logo-pinbank.png' style='height:48px;width:auto;display:block;'>",partnerLine:"Entrega realizada por <strong>AGYLOG</strong> em parceria com PinBank"},
  ip2w:{name:"IP2W",slug:"ip2w",headerBg:"#0d1b2a",headerText:"#ffffff",accent:"#3ECFC0",accentHover:"#2bb8a8",footerBg:"#0a1520",footerText:"#7be3d6",pillBg:"rgba(62,207,192,0.18)",pillColor:"#3ECFC0",logoSvg:"<img src='/static/logos/logo-ip2w.png?v=1' style='height:52px;width:auto;display:block;'>",partnerLine:"Entrega realizada por <strong>IP2W</strong>"},
  caoa:{name:"CAOA",slug:"caoa",headerBg:"#ffffff",headerText:"#100c5a",accent:"#5dba8d",accentHover:"#3da870",footerBg:"#f6f7fb",footerText:"#100c5a",pillBg:"rgba(93,186,141,0.15)",pillColor:"#3da870",logoSvg:"<img src='/static/logos/logo-caoa.png?v=1' style='height:44px;width:auto;display:block;'>",partnerLine:"Entrega realizada por <strong>CAOA</strong>"},
  ccxp:{name:"CCXP 26",slug:"ccxp",headerBg:"#000000",headerText:"#ffffff",accent:"#E33781",accentHover:"#C42D6E",footerBg:"#000000",footerText:"rgba(255,255,255,0.68)",pillBg:"rgba(227,55,129,0.16)",pillColor:"#E33781",logoSvg:`<img src="${CCXP_LOGO_DATA_URI}" alt="CCXP 26" style="height:64px;width:auto;display:block;mix-blend-mode:screen;">`,partnerLine:"Entrega realizada por <strong>AGYLOG</strong> na CCXP 26"},
  };

  function detectClient() {
    // 1) Query param: /tracking/CODE?cliente=panini
    const qp = new URLSearchParams(window.location.search).get('cliente');
    if (qp && CLIENT_THEMES[qp.toLowerCase()]) return qp.toLowerCase();
    // 2) Path slug: /tracking/panini or /tracking/panini/CODE
    const parts = window.location.pathname.split('/').filter(Boolean);
    if (parts.length >= 2 && parts[0] === 'tracking') {
      const slug = parts[1].toLowerCase();
      if (CLIENT_THEMES[slug]) return slug;
    }
    return null;
  }

  function getTrackingCodeFromURL() {
    const parts = window.location.pathname.split('/').filter(Boolean);
    if (parts.length >= 2 && parts[0] === 'tracking') {
      const slug = parts[1].toLowerCase();
      if (CLIENT_THEMES[slug]) {
        return parts.length >= 3 ? parts[2].toUpperCase() : '';
      }
      return parts[1].toUpperCase();
    }
    return '';
  }

  function applyClientTheme(slug) {
    if (!slug) return;
    const t = CLIENT_THEMES[slug];
    if (!t) return;

    // CSS custom properties
    const root = document.documentElement;
    root.style.setProperty('--brand-accent',       t.accent);
    root.style.setProperty('--brand-accent-hover',  t.accentHover);
    root.style.setProperty('--brand-header-bg',     t.headerBg);
    root.style.setProperty('--brand-header-text',   t.headerText);
    root.style.setProperty('--brand-footer-bg',     t.footerBg);
    root.style.setProperty('--brand-footer-text',   t.footerText);
    root.style.setProperty('--brand-pill-bg',       t.pillBg);
    root.style.setProperty('--brand-pill-color',    t.pillColor);
    document.body.setAttribute('data-client', slug);

    // Inject full page theme
    let _ts = document.getElementById('client-theme-style');
    if (_ts) _ts.remove();
    _ts = document.createElement('style');
    _ts.id = 'client-theme-style';
const _pageThemes = {
        panini: `
          *{font-weight:700!important;}
          body,[data-client=panini]{background:linear-gradient(145deg,#1a0f00,#0d0800)!important;}
          .page-wrap,.app-root{background:linear-gradient(145deg,#1a0f00,#0d0800)!important;}
          .bg-glow{background:radial-gradient(circle,rgba(255,214,0,.18) 0%,transparent 70%)!important;filter:none!important;}
          h1,h2,.hero-title,.page-title,.dest-header-main h1{background:linear-gradient(90deg,#FFD600,#CC0000)!important;-webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important;background-clip:text!important;}
          p,.subtitle,.page-subtitle,.journey-message,.section-title{color:rgba(255,220,120,.6)!important;}
          .timeline-stage h4,.timeline-stage time,.timeline-stage p{color:rgba(255,220,120,.7)!important;}
          .card,.result-card,.search-card,.history-card,.timeline-container{background:rgba(255,214,0,.04)!important;border-color:rgba(255,214,0,.12)!important;}
          input,.search-input{border-color:rgba(255,214,0,.25)!important;background:rgba(26,15,0,.8)!important;color:#fff!important;}
          input:focus,.search-input:focus{border-color:rgba(255,214,0,.6)!important;box-shadow:0 0 0 3px rgba(255,214,0,.12)!important;}
          .nova-busca-btn,.demo-btn{border-color:rgba(204,0,0,.3)!important;color:rgba(255,214,0,.8)!important;}
          .nova-busca-btn:hover,.demo-btn:hover{border-color:rgba(204,0,0,.6)!important;color:#FFD600!important;background:rgba(204,0,0,.1)!important;}
          .progress-line-fill{background:linear-gradient(90deg,#7a3500 0%,#CC0000 72%,#FFD600 100%)!important;}
          .timeline-stage.active .timeline-node{border-color:rgba(204,0,0,.6)!important;box-shadow:0 0 24px rgba(204,0,0,.3)!important;}
          .timeline-stage.done .timeline-node{border-color:rgba(255,214,0,.5)!important;background:rgba(255,214,0,.15)!important;}
          .timeline-node-check{color:#FFD600!important;}
          .timeline-stage.attention .timeline-node{border-color:rgba(204,0,0,.7)!important;box-shadow:0 0 20px rgba(204,0,0,.4)!important;}
          .timeline-stage.final .timeline-node{border-color:rgba(255,214,0,.8)!important;box-shadow:0 0 32px rgba(255,214,0,.4)!important;}
          .status-visual-scene,.status-visual-copy{background:linear-gradient(145deg,#1a0f00,#0d0800)!important;}
          .history-list{border-color:rgba(255,214,0,.1)!important;}
          .history-item{border-color:rgba(255,214,0,.08)!important;}
          .history-dot{background:#CC0000!important;box-shadow:0 0 8px rgba(204,0,0,.5)!important;}
          .history-item.success .history-dot{background:#FFD600!important;box-shadow:0 0 8px rgba(255,214,0,.5)!important;}
          .history-item.warning .history-dot{background:#e87020!important;}
          .history-item.danger .history-dot{background:#CC0000!important;}
          .history-body strong{color:rgba(255,214,0,.9)!important;}
          .history-body p{color:rgba(255,200,100,.6)!important;}
          .status-pill,.brand-pill{background:rgba(204,0,0,.2)!important;border-color:rgba(204,0,0,.4)!important;color:#FFD600!important;}
          .client-logo-wrap img{height:52px!important;width:auto!important;max-width:240px!important;display:block!important;}
        `,
        brb: `
          *{font-weight:700!important;}
          body,[data-client=brb]{background:linear-gradient(145deg,#000e2a,#000818)!important;}
          .page-wrap,.app-root{background:linear-gradient(145deg,#000e2a,#000818)!important;}
          .bg-glow{background:radial-gradient(circle,rgba(0,80,200,.25) 0%,transparent 70%)!important;filter:none!important;}
          h1,h2,.hero-title,.page-title,.dest-header-main h1{background:linear-gradient(90deg,#7aaaff,#a8d4ff)!important;-webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important;background-clip:text!important;}
          p,.subtitle,.page-subtitle,.journey-message,.section-title{color:rgba(168,200,255,.55)!important;}
          .timeline-stage h4,.timeline-stage time,.timeline-stage p{color:rgba(168,200,255,.75)!important;}
          .card,.result-card,.search-card,.history-card,.timeline-container{background:rgba(77,159,255,.04)!important;border-color:rgba(77,159,255,.12)!important;}
          input,.search-input{border-color:rgba(77,159,255,.25)!important;background:rgba(0,14,42,.8)!important;color:#fff!important;}
          input:focus,.search-input:focus{border-color:rgba(77,159,255,.6)!important;box-shadow:0 0 0 3px rgba(77,159,255,.12)!important;}
          .nova-busca-btn,.demo-btn{border-color:rgba(77,159,255,.3)!important;color:rgba(168,200,255,.8)!important;}
          .nova-busca-btn:hover,.demo-btn:hover{border-color:rgba(77,159,255,.6)!important;color:#a8d4ff!important;background:rgba(77,159,255,.1)!important;}
          .progress-line-fill{background:linear-gradient(90deg,#1a3a6a 0%,#4d9fff 72%,#a8d4ff 100%)!important;}
          .timeline-stage.active .timeline-node{border-color:rgba(77,159,255,.6)!important;box-shadow:0 0 24px rgba(77,159,255,.3)!important;}
          .timeline-stage.done .timeline-node{border-color:rgba(77,159,255,.5)!important;background:rgba(77,159,255,.15)!important;}
          .timeline-node-check{color:#4d9fff!important;}
          .timeline-stage.attention .timeline-node{border-color:rgba(255,180,0,.7)!important;box-shadow:0 0 20px rgba(255,180,0,.3)!important;}
          .timeline-stage.final .timeline-node{border-color:rgba(77,159,255,.9)!important;box-shadow:0 0 32px rgba(77,159,255,.45)!important;}
          .status-visual-scene,.status-visual-copy{background:linear-gradient(145deg,#000e2a,#000818)!important;}
          .history-list{border-color:rgba(77,159,255,.1)!important;}
          .history-item{border-color:rgba(77,159,255,.08)!important;}
          .history-dot{background:#4d9fff!important;box-shadow:0 0 8px rgba(77,159,255,.5)!important;}
          .history-item.success .history-dot{background:#4d9fff!important;box-shadow:0 0 8px rgba(77,159,255,.5)!important;}
          .history-item.warning .history-dot{background:#f59e0b!important;}
          .history-item.danger .history-dot{background:#ef4444!important;}
          .history-body strong{color:rgba(168,200,255,.9)!important;}
          .history-body p{color:rgba(168,200,255,.6)!important;}
          .status-pill,.brand-pill{background:rgba(77,159,255,.15)!important;border-color:rgba(77,159,255,.4)!important;color:#a8d4ff!important;}
          .client-logo-wrap img{height:52px!important;width:auto!important;max-width:240px!important;display:block!important;}
        `,
        inter: `
          *{font-weight:700!important;}
          body,[data-client=inter]{background:linear-gradient(145deg,#1a0800,#0f0500)!important;}
          .page-wrap,.app-root{background:linear-gradient(145deg,#1a0800,#0f0500)!important;}
          .bg-glow{background:radial-gradient(circle,rgba(255,122,0,.2) 0%,transparent 70%)!important;filter:none!important;}
          h1,h2,.hero-title,.page-title,.dest-header-main h1{background:linear-gradient(90deg,#FF7A00,#FFB347)!important;-webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important;background-clip:text!important;}
          p,.subtitle,.page-subtitle,.journey-message,.section-title{color:rgba(255,180,100,.6)!important;}
          .timeline-stage h4,.timeline-stage time,.timeline-stage p{color:rgba(255,180,100,.75)!important;}
          .card,.result-card,.search-card,.history-card,.timeline-container{background:rgba(255,122,0,.04)!important;border-color:rgba(255,122,0,.12)!important;}
          input,.search-input{border-color:rgba(255,122,0,.25)!important;background:rgba(26,8,0,.8)!important;color:#fff!important;}
          input:focus,.search-input:focus{border-color:rgba(255,122,0,.6)!important;box-shadow:0 0 0 3px rgba(255,122,0,.12)!important;}
          .nova-busca-btn,.demo-btn{border-color:rgba(255,122,0,.3)!important;color:rgba(255,179,71,.8)!important;}
          .nova-busca-btn:hover,.demo-btn:hover{border-color:rgba(255,122,0,.65)!important;color:#FFB347!important;background:rgba(255,122,0,.1)!important;}
          .progress-line-fill{background:linear-gradient(90deg,#7f4500 0%,#FF7A00 72%,#FFB347 100%)!important;}
          .timeline-stage.active .timeline-node{border-color:rgba(255,122,0,.6)!important;box-shadow:0 0 24px rgba(255,122,0,.3)!important;}
          .timeline-stage.done .timeline-node{border-color:rgba(255,122,0,.5)!important;background:rgba(255,122,0,.15)!important;}
          .timeline-node-check{color:#FF7A00!important;}
          .timeline-stage.attention .timeline-node{border-color:rgba(255,80,0,.7)!important;box-shadow:0 0 20px rgba(255,80,0,.4)!important;}
          .timeline-stage.final .timeline-node{border-color:rgba(255,122,0,.9)!important;box-shadow:0 0 32px rgba(255,122,0,.5)!important;}
          .status-visual-scene,.status-visual-copy{background:linear-gradient(145deg,#1a0800,#0f0500)!important;}
          .history-list{border-color:rgba(255,122,0,.1)!important;}
          .history-item{border-color:rgba(255,122,0,.08)!important;}
          .history-dot{background:#FF7A00!important;box-shadow:0 0 8px rgba(255,122,0,.5)!important;}
          .history-item.success .history-dot{background:#FF7A00!important;box-shadow:0 0 8px rgba(255,122,0,.55)!important;}
          .history-item.warning .history-dot{background:#f59e0b!important;}
          .history-item.danger .history-dot{background:#ef4444!important;}
          .history-body strong{color:rgba(255,180,100,.9)!important;}
          .history-body p{color:rgba(255,170,80,.6)!important;}
          .status-pill,.brand-pill{background:rgba(255,122,0,.15)!important;border-color:rgba(255,122,0,.4)!important;color:#FFB347!important;}
          .client-logo-wrap img{height:52px!important;width:auto!important;max-width:240px!important;display:block!important;}
        `
      ,
    pinbank: `
    *{font-weight:700!important;}
    body,[data-client=pinbank]{background:linear-gradient(145deg,#0A0A14,#111827)!important;}
    .page-wrap,.app-root{background:linear-gradient(145deg,#0A0A14,#111827)!important;}
    .bg-glow{background:radial-gradient(circle,rgba(245,166,35,.18) 0%,transparent 70%)!important;filter:none!important;}
    [data-client=pinbank] .hero-title,[data-client=pinbank] .page-title,[data-client=pinbank] .brand-title{color:#F5A623!important;}
    [data-client=pinbank] .rastrear-btn{background:linear-gradient(135deg,#F5A623 0%,#E09015 100%)!important;color:#111!important;}
    [data-client=pinbank] .rastrear-btn:hover{box-shadow:0 12px 34px rgba(245,166,35,.38)!important;}
    [data-client=pinbank] .progress-line-fill{background:linear-gradient(90deg,#F5A623 0%,#00E5FF 100%)!important;}
    [data-client=pinbank] .timeline-stage.active .timeline-node{border-color:#F5A623!important;box-shadow:0 0 18px rgba(245,166,35,.45)!important;}
  `,
  brbdux: `
  [data-client=brbdux] *{font-weight:700 !important;}
  body,[data-client=brbdux]{background:radial-gradient(circle at 50% 18%,rgba(255,255,255,.085) 0%,rgba(255,255,255,.025) 31%,transparent 62%),linear-gradient(145deg,#090909 0%,#020202 48%,#000 100%) !important;}
  .page-wrap,.app-root,.root-wrap{background:transparent !important;}
  [data-client=brbdux] .dest-header,[data-client=brbdux] .site-header,[data-client=brbdux] header{background:#000 !important;min-height:92px !important;height:92px !important;border-bottom:1px solid rgba(255,255,255,.24) !important;box-shadow:0 1px 0 rgba(255,255,255,.06),0 14px 42px rgba(0,0,0,.45) !important;overflow:visible !important;}
  [data-client=brbdux] .dest-header-inner,[data-client=brbdux] .client-header-inner{gap:28px !important;align-items:center !important;}
  [data-client=brbdux] .client-logo-wrap{background:transparent !important;border:0 !important;border-radius:0 !important;padding:0 !important;width:150px !important;height:76px !important;max-width:none !important;overflow:visible !important;display:flex !important;align-items:center !important;justify-content:center !important;box-shadow:none !important;flex:0 0 150px !important;}
  [data-client=brbdux] .client-logo-wrap img{content:url('/static/logos/logo-brbdux-trim.png?v=9') !important;display:block !important;height:76px !important;width:auto !important;max-width:none !important;filter:drop-shadow(0 0 14px rgba(255,255,255,.16)) !important;object-fit:contain !important;flex:0 0 auto !important;}
  [data-client=brbdux] .bg-glow{background:radial-gradient(circle,rgba(255,255,255,.24) 0%,rgba(255,255,255,.075) 34%,transparent 72%) !important;filter:none !important;opacity:.92 !important;}
  [data-client=brbdux] .tracking-hero-title,[data-client=brbdux] h1,[data-client=brbdux] h2,[data-client=brbdux] .hero-title,[data-client=brbdux] .page-title,[data-client=brbdux] .brand-title{background:linear-gradient(90deg,#fff 0%,#f0f0f0 38%,#bdbdbd 100%) !important;-webkit-background-clip:text !important;-webkit-text-fill-color:transparent !important;background-clip:text !important;text-shadow:0 18px 48px rgba(255,255,255,.08) !important;}
  [data-client=brbdux] p,[data-client=brbdux] .subtitle,[data-client=brbdux] .page-subtitle,[data-client=brbdux] .journey-message,[data-client=brbdux] .section-title,[data-client=brbdux] .hero-sub,[data-client=brbdux] .tracking-label,[data-client=brbdux] .info-label{color:rgba(255,255,255,.64) !important;}
  [data-client=brbdux] .card,[data-client=brbdux] .result-card,[data-client=brbdux] .search-card,[data-client=brbdux] .tracking-card,[data-client=brbdux] .info-card,[data-client=brbdux] .status-visual-card,[data-client=brbdux] .third-party-card,[data-client=brbdux] .history-card,[data-client=brbdux] .timeline-container{background:linear-gradient(180deg,rgba(255,255,255,.075),rgba(255,255,255,.032)) !important;border:1px solid rgba(255,255,255,.18) !important;box-shadow:0 26px 85px rgba(0,0,0,.62),inset 0 1px 0 rgba(255,255,255,.08) !important;backdrop-filter:blur(18px) !important;}
  [data-client=brbdux] .tracking-input,[data-client=brbdux] input,[data-client=brbdux] .search-input{background:rgba(0,0,0,.78) !important;border:1px solid rgba(255,255,255,.22) !important;color:#fff !important;box-shadow:inset 0 1px 0 rgba(255,255,255,.06) !important;}
  [data-client=brbdux] .tracking-input:focus,[data-client=brbdux] input:focus,[data-client=brbdux] .search-input:focus{border-color:rgba(255,255,255,.62) !important;box-shadow:0 0 0 3px rgba(255,255,255,.12),0 0 28px rgba(255,255,255,.12) !important;}
  [data-client=brbdux] .paste-btn,[data-client=brbdux] .nova-busca-btn,[data-client=brbdux] .demo-btn{background:rgba(255,255,255,.07) !important;color:rgba(255,255,255,.82) !important;border:1px solid rgba(255,255,255,.22) !important;}
  [data-client=brbdux] .paste-btn:hover,[data-client=brbdux] .nova-busca-btn:hover,[data-client=brbdux] .demo-btn:hover{background:rgba(255,255,255,.12) !important;border-color:rgba(255,255,255,.5) !important;color:#fff !important;}
  [data-client=brbdux] .rastrear-btn{background:linear-gradient(135deg,#fff 0%,#f1f1f1 48%,#d6d6d6 100%) !important;color:#030303 !important;box-shadow:0 12px 34px rgba(255,255,255,.20),0 2px 0 rgba(255,255,255,.42) inset !important;}
  [data-client=brbdux] .rastrear-btn:hover{box-shadow:0 16px 46px rgba(255,255,255,.34),0 2px 0 rgba(255,255,255,.55) inset !important;transform:translateY(-1px) !important;}
  [data-client=brbdux] .progress-line-fill{background:linear-gradient(90deg,#4a4a4a 0%,#fff 72%,#dcdcdc 100%) !important;box-shadow:0 0 24px rgba(255,255,255,.22) !important;}
  [data-client=brbdux] .timeline-stage h4,[data-client=brbdux] .timeline-stage time,[data-client=brbdux] .timeline-stage p{color:rgba(255,255,255,.76) !important;}
  [data-client=brbdux] .timeline-stage.active .timeline-node{border-color:rgba(255,255,255,.72) !important;box-shadow:0 0 28px rgba(255,255,255,.28) !important;}
  [data-client=brbdux] .timeline-stage.done .timeline-node{border-color:rgba(255,255,255,.55) !important;background:rgba(255,255,255,.14) !important;}
  [data-client=brbdux] .timeline-node-check{color:#fff !important;background:#3a3a3a !important;}
  [data-client=brbdux] .timeline-stage.active .timeline-node-check,[data-client=brbdux] .timeline-stage.done .timeline-node-check,[data-client=brbdux] .timeline-stage.final .timeline-node-check,[data-client=brbdux] .timeline-stage.final .timeline-node{background:#fff !important;border-color:#fff !important;color:#050505 !important;box-shadow:0 0 30px rgba(255,255,255,.42) !important;}
  [data-client=brbdux] .timeline-kicker,[data-client=brbdux] .timeline-stage.active .timeline-kicker{color:#fff !important;}
  [data-client=brbdux] .status-visual-scene,[data-client=brbdux] .status-visual-copy{background:linear-gradient(145deg,rgba(255,255,255,.07),rgba(255,255,255,.018)) !important;border:1px solid rgba(255,255,255,.11) !important;}
  [data-client=brbdux] .history-list{border-color:rgba(255,255,255,.12) !important;}
  [data-client=brbdux] .history-item{border-color:rgba(255,255,255,.08) !important;}
  [data-client=brbdux] .history-item.success .history-dot,[data-client=brbdux] .history-dot{background:#fff !important;box-shadow:0 0 12px rgba(255,255,255,.48) !important;}
  [data-client=brbdux] .history-body strong,[data-client=brbdux] .history-body,[data-client=brbdux] .history-desc{color:rgba(255,255,255,.9) !important;}
  [data-client=brbdux] .history-body p,[data-client=brbdux] .history-date,[data-client=brbdux] .history-time{color:rgba(255,255,255,.56) !important;}
  [data-client=brbdux] .status-pill,[data-client=brbdux] .brand-pill{background:rgba(255,255,255,.12) !important;border:1px solid rgba(255,255,255,.36) !important;color:#fff !important;}
  [data-client=brbdux] .site-footer,[data-client=brbdux] footer{background:#050505 !important;border-top:1px solid rgba(255,255,255,.14) !important;color:#999 !important;}
  [data-client=brbdux] .partner-line,[data-client=brbdux] .footer-partner,[data-client=brbdux] .client-partner-line{color:#cfcfcf !important;}
  @media (max-width:640px){[data-client=brbdux] .dest-header,[data-client=brbdux] header{height:86px !important;min-height:86px !important;}[data-client=brbdux] .client-logo-wrap{height:66px !important;width:132px !important;flex-basis:132px !important;}[data-client=brbdux] .client-logo-wrap img{height:66px !important;}}
  /* CODEX MOBILE HEADER FIT */
  @media (max-width:640px){
    [data-client=brbdux] .dest-header-inner,[data-client=brbdux] .client-header-inner,[data-client=tricard] .dest-header-inner,[data-client=tricard] .client-header-inner{gap:14px !important;padding-left:16px !important;padding-right:16px !important;box-sizing:border-box !important;min-width:0 !important;}
    [data-client=brbdux] .dest-header-main,[data-client=brbdux] .client-header-copy,[data-client=tricard] .dest-header-main,[data-client=tricard] .client-header-copy{min-width:0 !important;flex:1 1 auto !important;}
    [data-client=brbdux] .dest-header-main h1,[data-client=brbdux] .client-header-copy h1,[data-client=tricard] .dest-header-main h1,[data-client=tricard] .client-header-copy h1{font-size:15px !important;line-height:1.15 !important;white-space:normal !important;overflow:visible !important;text-overflow:clip !important;max-width:none !important;}
    [data-client=brbdux] .dest-header .client-logo-wrap,[data-client=brbdux] header .client-logo-wrap{height:58px !important;width:118px !important;flex:0 0 118px !important;}
    [data-client=brbdux] .dest-header .client-logo-wrap img,[data-client=brbdux] header .client-logo-wrap img{height:58px !important;}
    [data-client=tricard] .dest-header .client-logo-wrap,[data-client=tricard] header .client-logo-wrap{height:44px !important;width:126px !important;flex:0 0 126px !important;}
    [data-client=tricard] .dest-header .client-logo-wrap img,[data-client=tricard] header .client-logo-wrap img{height:44px !important;}
  }
  /* CODEX MOBILE TAGLINE FIT */
  @media (max-width:640px){
    [data-client=brbdux] .dest-header-inner,[data-client=brbdux] .client-header-inner,[data-client=tricard] .dest-header-inner,[data-client=tricard] .client-header-inner{width:100% !important;max-width:none !important;margin:0 !important;justify-content:flex-start !important;}
    [data-client=brbdux] .client-header-tagline,[data-client=tricard] .client-header-tagline{font-size:14px !important;line-height:1.12 !important;white-space:normal !important;overflow:visible !important;text-overflow:clip !important;max-width:176px !important;display:block !important;}
  }
  /* CODEX SOBER BACKGROUND */
  body[data-client=brbdux],[data-client=brbdux]{background:linear-gradient(180deg,#070707 0%,#040404 44%,#000 100%) !important;}
  [data-client=brbdux] .page-wrap,[data-client=brbdux] .app-root,[data-client=brbdux] .root-wrap{background:transparent !important;}
  [data-client=brbdux] .bg-glow{display:none !important;opacity:0 !important;background:none !important;filter:none !important;}
  [data-client=brbdux] .timeline-stage .timeline-node-check{background:#111 !important;color:#fff !important;}
  [data-client=brbdux] .timeline-stage.done .timeline-node-check,[data-client=brbdux] .timeline-stage.final .timeline-node-check{background:#1a1a1a !important;color:#fff !important;}
  [data-client=brbdux] .timeline-stage.active .timeline-node-check{background:#1e1e1e !important;color:#fff !important;}
  [data-client=brbdux] .timeline-stage.attention .timeline-node-check{background:#1a1509 !important;color:#ffd166 !important;}  [data-client=brbdux] .timeline-node{filter:none !important;}
  [data-client=brbdux] .timeline-stage .timeline-node-check{box-shadow:none !important;}
  [data-client=brbdux] .timeline-stage.done .timeline-node-check{box-shadow:0 0 12px rgba(255,255,255,.2) !important;}
  [data-client=brbdux] .timeline-stage.active .timeline-node-check{box-shadow:0 0 16px rgba(255,255,255,.35) !important;}
  [data-client=brbdux] .timeline-stage.final .timeline-node-check{box-shadow:0 0 20px rgba(255,255,255,.45) !important;}
  [data-client=brbdux] .timeline-stage.attention .timeline-node-check{box-shadow:0 0 14px rgba(255,180,0,.35) !important;}
`,
    ccxp: `
  body[data-client=ccxp],[data-client=ccxp]{background:#000 !important;color:#fff !important;}
  [data-client=ccxp] .app-root,[data-client=ccxp] .root-wrap,[data-client=ccxp] .page-wrap{background:radial-gradient(circle at 78% 6%,rgba(227,55,129,.26) 0%,rgba(227,55,129,.09) 28%,transparent 54%),linear-gradient(180deg,#050505 0%,#000 48%,#040104 100%) !important;color:#fff !important;}
  [data-client=ccxp] .bg-glow{background:radial-gradient(circle,rgba(227,55,129,.34) 0%,rgba(227,55,129,.12) 34%,transparent 72%) !important;filter:none !important;opacity:.88 !important;}
  [data-client=ccxp] header,[data-client=ccxp] .site-header,[data-client=ccxp] .dest-header{background:#000 !important;min-height:96px !important;height:96px !important;border-bottom:1px solid rgba(227,55,129,.44) !important;box-shadow:0 18px 54px rgba(0,0,0,.68),0 1px 0 rgba(255,255,255,.08) inset !important;overflow:visible !important;}
  [data-client=ccxp] .dest-header-inner,[data-client=ccxp] .client-header-inner{display:flex !important;align-items:center !important;gap:26px !important;min-width:0 !important;}
  [data-client=ccxp] .dest-header-main,[data-client=ccxp] .client-header-copy{min-width:0 !important;color:#fff !important;}
  [data-client=ccxp] .dest-header-main h1,[data-client=ccxp] .client-header-copy h1{color:#fff !important;}
  [data-client=ccxp] .client-logo-wrap,[data-client=ccxp] .dest-header .client-logo-wrap,[data-client=ccxp] header .client-logo-wrap{background:transparent !important;border:0 !important;border-radius:0 !important;box-shadow:none !important;display:flex !important;align-items:center !important;justify-content:center !important;overflow:visible !important;padding:0 !important;width:248px !important;height:68px !important;max-width:none !important;flex:0 0 248px !important;}
  [data-client=ccxp] .client-logo-wrap img,[data-client=ccxp] .dest-header .client-logo-wrap img,[data-client=ccxp] header .client-logo-wrap img{display:block !important;width:auto !important;height:64px !important;max-width:none !important;object-fit:contain !important;filter:drop-shadow(0 0 16px rgba(227,55,129,.34)) !important;mix-blend-mode:screen !important;}
  [data-client=ccxp] .client-header-tagline{color:rgba(255,255,255,.82) !important;font-size:14px !important;font-weight:800 !important;text-transform:uppercase !important;letter-spacing:.08em !important;white-space:normal !important;text-shadow:0 0 18px rgba(227,55,129,.38) !important;}
  [data-client=ccxp] .brand-pill,[data-client=ccxp] .status-pill{background:rgba(227,55,129,.16) !important;border:1px solid rgba(227,55,129,.46) !important;color:#E33781 !important;box-shadow:0 0 18px rgba(227,55,129,.16) !important;}
  [data-client=ccxp] .brand-title,[data-client=ccxp] .partner-line,[data-client=ccxp] .client-partner-line{color:#fff !important;}
  [data-client=ccxp] .tracking-hero-title,[data-client=ccxp] h1,[data-client=ccxp] h2,[data-client=ccxp] .page-title,[data-client=ccxp] .hero-title,[data-client=ccxp] .section-title,[data-client=ccxp] .tracking-card h1,[data-client=ccxp] .tracking-card h2{background:linear-gradient(90deg,#E33781,#F091BA) !important;-webkit-background-clip:text !important;-webkit-text-fill-color:transparent !important;background-clip:text !important;}
  [data-client=ccxp] *{font-weight:700 !important;}
  [data-client=ccxp] .rastrear-btn{box-shadow:0 4px 22px rgba(227,55,129,.35) !important;}
  [data-client=ccxp] .rastrear-btn:hover{box-shadow:0 6px 28px rgba(227,55,129,.5) !important;}
  [data-client=ccxp] p,[data-client=ccxp] .page-subtitle,[data-client=ccxp] .subtitle,[data-client=ccxp] .hero-sub,[data-client=ccxp] .tracking-label,[data-client=ccxp] .info-label,[data-client=ccxp] .journey-message{color:rgba(255,255,255,.70) !important;}
  [data-client=ccxp] .search-card,[data-client=ccxp] .card,[data-client=ccxp] .info-card,[data-client=ccxp] .result-card,[data-client=ccxp] .tracking-card,[data-client=ccxp] .third-party-card,[data-client=ccxp] .status-visual-card,[data-client=ccxp] .timeline-container,[data-client=ccxp] .history-card{background:linear-gradient(180deg,rgba(227,55,129,.11),rgba(255,255,255,.035)) !important;border:1px solid rgba(227,55,129,.28) !important;box-shadow:0 28px 90px rgba(0,0,0,.72),0 0 46px rgba(227,55,129,.08),inset 0 1px 0 rgba(255,255,255,.07) !important;backdrop-filter:blur(18px) !important;color:#fff !important;}
  [data-client=ccxp] .search-input,[data-client=ccxp] .tracking-input,[data-client=ccxp] input{background:rgba(0,0,0,.82) !important;border:1px solid rgba(227,55,129,.42) !important;color:#fff !important;box-shadow:inset 0 1px 0 rgba(255,255,255,.05) !important;}
  [data-client=ccxp] .search-input:focus,[data-client=ccxp] .tracking-input:focus,[data-client=ccxp] input:focus{border-color:#E33781 !important;box-shadow:0 0 0 3px rgba(227,55,129,.20),0 0 32px rgba(227,55,129,.24) !important;outline:none !important;}
  [data-client=ccxp] input::placeholder{color:rgba(255,255,255,.36) !important;}
  [data-client=ccxp] .nova-busca-btn,[data-client=ccxp] .paste-btn,[data-client=ccxp] .demo-btn{background:rgba(227,55,129,.10) !important;color:#fff !important;border:1px solid rgba(227,55,129,.36) !important;}
  [data-client=ccxp] .nova-busca-btn:hover,[data-client=ccxp] .paste-btn:hover,[data-client=ccxp] .demo-btn:hover{background:rgba(227,55,129,.20) !important;border-color:#E33781 !important;color:#fff !important;box-shadow:0 0 24px rgba(227,55,129,.20) !important;}
  [data-client=ccxp] .timeline-container{border-color:rgba(227,55,129,.30) !important;}
  [data-client=ccxp] .timeline-kicker,[data-client=ccxp] .timeline-stage.active .timeline-kicker,[data-client=ccxp] .visual-kicker{color:#E33781 !important;}
  [data-client=ccxp] .timeline-stage h4,[data-client=ccxp] .timeline-stage p,[data-client=ccxp] .timeline-stage time{color:rgba(255,255,255,.78) !important;}
  [data-client=ccxp] .timeline-node{background:#080308 !important;border-color:rgba(227,55,129,.32) !important;filter:none !important;}
  [data-client=ccxp] .timeline-node-check{background:#140711 !important;color:#E33781 !important;box-shadow:none !important;}
  [data-client=ccxp] .timeline-stage.active .timeline-node{border-color:#E33781 !important;box-shadow:0 0 28px rgba(227,55,129,.36) !important;}
  [data-client=ccxp] .timeline-stage{justify-content:flex-start !important;align-self:start !important;}
  [data-client=ccxp] .timeline-stage.ccxp-treatment .timeline-node{border-color:#E33781 !important;color:#fff !important;box-shadow:0 0 28px rgba(227,55,129,.36) !important;}
  [data-client=ccxp] .timeline-stage.ccxp-treatment .timeline-node-emoji{width:30px !important;height:30px !important;border-radius:50% !important;background:#E33781 !important;color:#fff !important;display:flex !important;align-items:center !important;justify-content:center !important;}
  [data-client=ccxp] .timeline-stage.done .timeline-node{border-color:rgba(227,55,129,.58) !important;background:rgba(227,55,129,.12) !important;}
  [data-client=ccxp] .timeline-stage.active .timeline-node-check,[data-client=ccxp] .timeline-stage.done .timeline-node-check,[data-client=ccxp] .timeline-stage.final .timeline-node-check{background:#E33781 !important;border-color:#E33781 !important;color:#fff !important;box-shadow:0 0 24px rgba(227,55,129,.50) !important;}
  [data-client=ccxp] .timeline-stage.final .timeline-node{border-color:#E33781 !important;box-shadow:0 0 28px rgba(227,55,129,.42) !important;}
  [data-client=ccxp] .timeline-stage.final.done .timeline-node{background:#E33781 !important;}
  [data-client=ccxp] .timeline-stage.attention .timeline-node-check{background:#241304 !important;color:#ffd166 !important;box-shadow:0 0 14px rgba(255,180,0,.34) !important;}
  [data-client=ccxp] .progress-line-fill{background:linear-gradient(90deg,#581333 0%,#E33781 72%,#fff 115%) !important;box-shadow:0 0 28px rgba(227,55,129,.36) !important;}
  [data-client=ccxp] .status-visual-card,[data-client=ccxp] .status-visual-copy,[data-client=ccxp] .status-visual-scene{background:#000 !important;background-image:none !important;border:1px solid rgba(227,55,129,.22) !important;color:#fff !important;box-shadow:0 24px 70px rgba(0,0,0,.76),0 0 38px rgba(227,55,129,.10) !important;}
  [data-client=ccxp] .status-visual-media{background:#000 !important;background-image:none !important;border:1px solid rgba(227,55,129,.20) !important;box-shadow:none !important;}
  [data-client=ccxp] .status-visual-media::before,[data-client=ccxp] .status-visual-media::after{background:radial-gradient(circle,rgba(227,55,129,.20) 0%,transparent 64%) !important;opacity:.70 !important;}
  [data-client=ccxp] .status-visual-media > *,[data-client=ccxp] .status-visual-scene,[data-client=ccxp] .default-wrap,[data-client=ccxp] .delivered-wrap,[data-client=ccxp] .returned-wrap,[data-client=ccxp] .route-wrap{background:#000 !important;background-image:none !important;color:#fff !important;}
  [data-client=ccxp] .status-visual-media img,[data-client=ccxp] .status-visual-media svg,[data-client=ccxp] .status-visual-media canvas{filter:none !important;mix-blend-mode:normal !important;}
  [data-client=ccxp] .history-list{border-color:rgba(227,55,129,.15) !important;}
  [data-client=ccxp] .history-item{border-color:rgba(227,55,129,.11) !important;}
  [data-client=ccxp] .history-dot,[data-client=ccxp] .history-item.success .history-dot{background:#E33781 !important;box-shadow:0 0 14px rgba(227,55,129,.58) !important;}
  [data-client=ccxp] .history-body,[data-client=ccxp] .history-body strong,[data-client=ccxp] .history-desc{color:rgba(255,255,255,.92) !important;}
  [data-client=ccxp] .history-body p,[data-client=ccxp] .history-date,[data-client=ccxp] .history-time{color:rgba(255,255,255,.58) !important;}
  [data-client=ccxp] footer,[data-client=ccxp] .site-footer{background:#000 !important;border-top:1px solid rgba(227,55,129,.30) !important;color:rgba(255,255,255,.68) !important;box-shadow:0 -18px 52px rgba(0,0,0,.72) !important;}
  [data-client=ccxp] .footer-partner,[data-client=ccxp] .client-footer-copy{color:rgba(255,255,255,.62) !important;}
  [data-client=ccxp] .footer-partner strong,[data-client=ccxp] .client-partner-line strong{color:#fff !important;}
  @media (max-width:640px){[data-client=ccxp] header,[data-client=ccxp] .dest-header{height:88px !important;min-height:88px !important;}[data-client=ccxp] .dest-header-inner,[data-client=ccxp] .client-header-inner{gap:14px !important;padding-left:16px !important;padding-right:16px !important;width:100% !important;box-sizing:border-box !important;}[data-client=ccxp] .client-logo-wrap,[data-client=ccxp] .dest-header .client-logo-wrap{width:152px !important;height:48px !important;flex:0 0 152px !important;}[data-client=ccxp] .client-logo-wrap img{height:44px !important;}[data-client=ccxp] .client-header-tagline{font-size:11px !important;line-height:1.15 !important;max-width:132px !important;}[data-client=ccxp] .dest-header-inner::after,[data-client=ccxp] .client-header-inner::after{display:none !important;}}
`,
    tricard: `
  [data-client=tricard] *{font-weight:700 !important;}
  body,[data-client=tricard]{background:radial-gradient(circle at 50% 18%,rgba(0,184,160,.16) 0%,rgba(0,184,160,.045) 33%,transparent 64%),linear-gradient(145deg,#071a31 0%,#04111f 52%,#020910 100%) !important;}
  .page-wrap,.app-root,.root-wrap{background:transparent !important;}
  [data-client=tricard] .dest-header,[data-client=tricard] .site-header,[data-client=tricard] header{background:linear-gradient(90deg,#1B3F7A 0%,#17376f 58%,#102b58 100%) !important;min-height:92px !important;height:92px !important;border-bottom:1px solid rgba(0,184,160,.30) !important;box-shadow:0 14px 42px rgba(0,0,0,.32) !important;overflow:visible !important;}
  [data-client=tricard] .dest-header-inner,[data-client=tricard] .client-header-inner{gap:28px !important;align-items:center !important;}
  [data-client=tricard] .client-logo-wrap{background:transparent !important;border:0 !important;border-radius:0 !important;padding:0 !important;width:174px !important;height:58px !important;max-width:none !important;overflow:visible !important;display:flex !important;align-items:center !important;justify-content:center !important;box-shadow:none !important;flex:0 0 174px !important;}
  [data-client=tricard] .client-logo-wrap img{content:url('/static/logos/logo-tricard-trim.png?v=9') !important;display:block !important;height:58px !important;width:auto !important;max-width:none !important;filter:none !important;object-fit:contain !important;flex:0 0 auto !important;}
  [data-client=tricard] .bg-glow{background:radial-gradient(circle,rgba(0,184,160,.36) 0%,rgba(0,184,160,.11) 35%,transparent 72%) !important;filter:none !important;opacity:.95 !important;}
  [data-client=tricard] .tracking-hero-title,[data-client=tricard] h1,[data-client=tricard] h2,[data-client=tricard] .hero-title,[data-client=tricard] .page-title,[data-client=tricard] .brand-title{background:linear-gradient(90deg,#00E8D4 0%,#35f7df 46%,#79d8ff 100%) !important;-webkit-background-clip:text !important;-webkit-text-fill-color:transparent !important;background-clip:text !important;text-shadow:0 18px 48px rgba(0,184,160,.14) !important;}
  [data-client=tricard] p,[data-client=tricard] .subtitle,[data-client=tricard] .page-subtitle,[data-client=tricard] .journey-message,[data-client=tricard] .section-title,[data-client=tricard] .hero-sub,[data-client=tricard] .tracking-label,[data-client=tricard] .info-label{color:rgba(129,238,225,.76) !important;}
  [data-client=tricard] .card,[data-client=tricard] .result-card,[data-client=tricard] .search-card,[data-client=tricard] .tracking-card,[data-client=tricard] .info-card,[data-client=tricard] .status-visual-card,[data-client=tricard] .third-party-card,[data-client=tricard] .history-card,[data-client=tricard] .timeline-container{background:linear-gradient(180deg,rgba(0,184,160,.115),rgba(8,28,47,.78)) !important;border:1px solid rgba(0,184,160,.30) !important;box-shadow:0 26px 85px rgba(0,0,0,.50),0 0 44px rgba(0,184,160,.09),inset 0 1px 0 rgba(255,255,255,.05) !important;backdrop-filter:blur(18px) !important;}
  [data-client=tricard] .tracking-input,[data-client=tricard] input,[data-client=tricard] .search-input{background:rgba(3,12,24,.78) !important;border:1px solid rgba(0,184,160,.34) !important;color:#e8fffb !important;box-shadow:inset 0 1px 0 rgba(255,255,255,.05) !important;}
  [data-client=tricard] .tracking-input:focus,[data-client=tricard] input:focus,[data-client=tricard] .search-input:focus{border-color:rgba(0,232,212,.72) !important;box-shadow:0 0 0 3px rgba(0,184,160,.16),0 0 30px rgba(0,184,160,.18) !important;}
  [data-client=tricard] .paste-btn,[data-client=tricard] .nova-busca-btn,[data-client=tricard] .demo-btn{background:rgba(0,184,160,.09) !important;color:#72fff0 !important;border:1px solid rgba(0,184,160,.32) !important;}
  [data-client=tricard] .paste-btn:hover,[data-client=tricard] .nova-busca-btn:hover,[data-client=tricard] .demo-btn:hover{background:rgba(0,184,160,.16) !important;border-color:rgba(0,232,212,.58) !important;color:#bffcf5 !important;}
  [data-client=tricard] .rastrear-btn{background:linear-gradient(135deg,#00B8A0 0%,#00D7C1 52%,#49f2df 100%) !important;color:#fff !important;box-shadow:0 14px 38px rgba(0,184,160,.40),0 2px 0 rgba(255,255,255,.20) inset !important;}
  [data-client=tricard] .rastrear-btn:hover{box-shadow:0 18px 52px rgba(0,184,160,.56),0 2px 0 rgba(255,255,255,.30) inset !important;transform:translateY(-1px) !important;}
  [data-client=tricard] .progress-line-fill{background:linear-gradient(90deg,#005c52 0%,#00B8A0 68%,#58f4e4 100%) !important;box-shadow:0 0 24px rgba(0,184,160,.28) !important;}
  [data-client=tricard] .timeline-stage h4,[data-client=tricard] .timeline-stage time,[data-client=tricard] .timeline-stage p{color:rgba(129,238,225,.78) !important;}
  [data-client=tricard] .timeline-stage.active .timeline-node{border-color:rgba(0,232,212,.78) !important;box-shadow:0 0 30px rgba(0,184,160,.35) !important;}
  [data-client=tricard] .timeline-stage.done .timeline-node{border-color:rgba(0,184,160,.58) !important;background:rgba(0,184,160,.16) !important;}
  [data-client=tricard] .timeline-node-check{color:#dffffb !important;background:#007c70 !important;}
  [data-client=tricard] .timeline-stage.active .timeline-node-check,[data-client=tricard] .timeline-stage.done .timeline-node-check,[data-client=tricard] .timeline-stage.final .timeline-node-check,[data-client=tricard] .timeline-stage.final .timeline-node{background:#00D7C1 !important;border-color:#00D7C1 !important;color:#001c19 !important;box-shadow:0 0 32px rgba(0,184,160,.55) !important;}
  [data-client=tricard] .timeline-kicker,[data-client=tricard] .timeline-stage.active .timeline-kicker{color:#79fff1 !important;}
  [data-client=tricard] .status-visual-scene,[data-client=tricard] .status-visual-copy{background:linear-gradient(145deg,rgba(0,184,160,.11),rgba(5,20,35,.72)) !important;border:1px solid rgba(0,184,160,.18) !important;}
  [data-client=tricard] .history-list{border-color:rgba(0,184,160,.17) !important;}
  [data-client=tricard] .history-item{border-color:rgba(0,184,160,.12) !important;}
  [data-client=tricard] .history-item.success .history-dot,[data-client=tricard] .history-dot{background:#00D7C1 !important;box-shadow:0 0 12px rgba(0,184,160,.58) !important;}
  [data-client=tricard] .history-body strong,[data-client=tricard] .history-body,[data-client=tricard] .history-desc{color:rgba(225,255,251,.92) !important;}
  [data-client=tricard] .history-body p,[data-client=tricard] .history-date,[data-client=tricard] .history-time{color:rgba(129,238,225,.64) !important;}
  [data-client=tricard] .status-pill,[data-client=tricard] .brand-pill{background:rgba(0,184,160,.16) !important;border:1px solid rgba(0,184,160,.40) !important;color:#9cfff5 !important;}
  [data-client=tricard] .site-footer,[data-client=tricard] footer{background:rgba(2,9,16,.96) !important;border-top:1px solid rgba(0,184,160,.24) !important;color:#8ec8dc !important;}
  [data-client=tricard] .partner-line,[data-client=tricard] .footer-partner,[data-client=tricard] .client-partner-line{color:#43e5d3 !important;}
  @media (max-width:640px){[data-client=tricard] .client-logo-wrap{height:50px !important;width:150px !important;flex-basis:150px !important;}[data-client=tricard] .client-logo-wrap img{height:50px !important;}}
  /* CODEX MOBILE HEADER FIT */
  @media (max-width:640px){
    [data-client=brbdux] .dest-header-inner,[data-client=brbdux] .client-header-inner,[data-client=tricard] .dest-header-inner,[data-client=tricard] .client-header-inner{gap:14px !important;padding-left:16px !important;padding-right:16px !important;box-sizing:border-box !important;min-width:0 !important;}
    [data-client=brbdux] .dest-header-main,[data-client=brbdux] .client-header-copy,[data-client=tricard] .dest-header-main,[data-client=tricard] .client-header-copy{min-width:0 !important;flex:1 1 auto !important;}
    [data-client=brbdux] .dest-header-main h1,[data-client=brbdux] .client-header-copy h1,[data-client=tricard] .dest-header-main h1,[data-client=tricard] .client-header-copy h1{font-size:15px !important;line-height:1.15 !important;white-space:normal !important;overflow:visible !important;text-overflow:clip !important;max-width:none !important;}
    [data-client=brbdux] .dest-header .client-logo-wrap,[data-client=brbdux] header .client-logo-wrap{height:58px !important;width:118px !important;flex:0 0 118px !important;}
    [data-client=brbdux] .dest-header .client-logo-wrap img,[data-client=brbdux] header .client-logo-wrap img{height:58px !important;}
    [data-client=tricard] .dest-header .client-logo-wrap,[data-client=tricard] header .client-logo-wrap{height:44px !important;width:126px !important;flex:0 0 126px !important;}
    [data-client=tricard] .dest-header .client-logo-wrap img,[data-client=tricard] header .client-logo-wrap img{height:44px !important;}
  }
  /* CODEX MOBILE TAGLINE FIT */
  @media (max-width:640px){
    [data-client=brbdux] .dest-header-inner,[data-client=brbdux] .client-header-inner,[data-client=tricard] .dest-header-inner,[data-client=tricard] .client-header-inner{width:100% !important;max-width:none !important;margin:0 !important;justify-content:flex-start !important;}
    [data-client=brbdux] .client-header-tagline,[data-client=tricard] .client-header-tagline{font-size:14px !important;line-height:1.12 !important;white-space:normal !important;overflow:visible !important;text-overflow:clip !important;max-width:176px !important;display:block !important;}
  }
  /* CODEX SOBER BACKGROUND */
  body[data-client=tricard],[data-client=tricard]{background:linear-gradient(180deg,#07182e 0%,#061321 46%,#020910 100%) !important;}
  [data-client=tricard] .page-wrap,[data-client=tricard] .app-root,[data-client=tricard] .root-wrap{background:transparent !important;}
  [data-client=tricard] .bg-glow{display:none !important;opacity:0 !important;background:none !important;filter:none !important;}
  [data-client=tricard] .timeline-stage .timeline-node-check{background:#030d18 !important;color:#eaffff !important;}
  [data-client=tricard] .timeline-stage.done .timeline-node-check,[data-client=tricard] .timeline-stage.final .timeline-node-check{background:#071520 !important;color:#eaffff !important;}
  [data-client=tricard] .timeline-stage.active .timeline-node-check{background:#0a1e2c !important;color:#eaffff !important;}
  [data-client=tricard] .timeline-stage.attention .timeline-node-check{background:#0f1a0a !important;color:#ffd166 !important;}  [data-client=tricard] .timeline-node{filter:none !important;}
  [data-client=tricard] .timeline-stage .timeline-node-check{box-shadow:none !important;}
  [data-client=tricard] .timeline-stage.done .timeline-node-check{box-shadow:0 0 12px rgba(0,184,160,.4) !important;}
  [data-client=tricard] .timeline-stage.active .timeline-node-check{box-shadow:0 0 16px rgba(0,184,160,.55) !important;}
  [data-client=tricard] .timeline-stage.final .timeline-node-check{box-shadow:0 0 20px rgba(0,184,160,.65) !important;}
  [data-client=tricard] .timeline-stage.attention .timeline-node-check{box-shadow:0 0 14px rgba(255,180,0,.35) !important;}
`,
        ip2w: `
          [data-client=ip2w] *{font-weight:700!important;}
          [data-client=ip2w] .rastrear-btn{box-shadow:0 4px 22px rgba(62,207,192,.35)!important;}
          [data-client=ip2w] .rastrear-btn:hover{box-shadow:0 6px 28px rgba(62,207,192,.5)!important;}
          /* ip2w-checks-white-v1 */
          [data-client=ip2w] .timeline-node-check{color:#0d1b2a!important;background:#ffffff!important;box-shadow:0 0 8px rgba(255,255,255,.5)!important;}
          [data-client=ip2w] .timeline-stage.done .timeline-node-check,[data-client=ip2w] .timeline-stage.active .timeline-node-check,[data-client=ip2w] .timeline-stage.final .timeline-node-check{background:#ffffff!important;color:#0d1b2a!important;}
          [data-client=ip2w] .timeline-stage.done .timeline-node-check,[data-client=ip2w] .timeline-stage.final .timeline-node-check{box-shadow:0 0 12px rgba(255,255,255,.55)!important;}
          [data-client=ip2w] .timeline-stage.active .timeline-node-check{box-shadow:0 0 16px rgba(255,255,255,.55)!important;}
          [data-client=ip2w] .timeline-stage.attention .timeline-node-check{background:#ffd166!important;color:#0d1b2a!important;box-shadow:0 0 14px rgba(255,209,102,.5)!important;}
          /* hide-agy-header */
          [data-client=ip2w] .client-header-inner::before,[data-client=ip2w] .client-header-inner::after,[data-client=ip2w] .dest-header-inner::before,[data-client=ip2w] .dest-header-inner::after{display:none!important;content:none!important;background:none!important;border:none!important;width:0!important;height:0!important;margin:0!important;padding:0!important;}
          body,[data-client=ip2w]{background:linear-gradient(145deg,#0d1b2a,#06101a)!important;}
          .page-wrap,.app-root{background:linear-gradient(145deg,#0d1b2a,#06101a)!important;}
          .bg-glow{background:radial-gradient(circle,rgba(62,207,192,.22) 0%,transparent 70%)!important;filter:none!important;}
          h1,h2,.hero-title,.page-title,.dest-header-main h1{background:linear-gradient(90deg,#3ECFC0,#7be3d6)!important;-webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important;background-clip:text!important;}
          p,.subtitle,.page-subtitle,.journey-message,.section-title{color:rgba(180,230,225,.6)!important;}
          .timeline-stage h4,.timeline-stage time,.timeline-stage p{color:rgba(180,230,225,.75)!important;}
          .card,.result-card,.search-card,.history-card,.timeline-container{background:rgba(62,207,192,.04)!important;border-color:rgba(62,207,192,.12)!important;}
          input,.search-input{border-color:rgba(62,207,192,.25)!important;background:rgba(13,27,42,.8)!important;color:#fff!important;}
          input:focus,.search-input:focus{border-color:rgba(62,207,192,.6)!important;box-shadow:0 0 0 3px rgba(62,207,192,.12)!important;}
          .nova-busca-btn,.demo-btn{border-color:rgba(62,207,192,.3)!important;color:rgba(180,230,225,.8)!important;}
          .nova-busca-btn:hover,.demo-btn:hover{border-color:rgba(62,207,192,.65)!important;color:#7be3d6!important;background:rgba(62,207,192,.1)!important;}
          .progress-line-fill{background:linear-gradient(90deg,#1a4a44 0%,#3ECFC0 72%,#7be3d6 100%)!important;}
          .timeline-stage.active .timeline-node{border-color:rgba(62,207,192,.6)!important;box-shadow:0 0 24px rgba(62,207,192,.3)!important;}
          .timeline-stage.done .timeline-node{border-color:rgba(62,207,192,.5)!important;background:rgba(62,207,192,.15)!important;}
          .timeline-node-check{color:#3ECFC0!important;}
          .timeline-stage.attention .timeline-node{border-color:rgba(255,180,0,.7)!important;box-shadow:0 0 20px rgba(255,180,0,.3)!important;}
          .timeline-stage.final .timeline-node{border-color:rgba(62,207,192,.9)!important;box-shadow:0 0 32px rgba(62,207,192,.45)!important;}
          .status-visual-scene,.status-visual-copy{background:linear-gradient(145deg,#0d1b2a,#06101a)!important;}
          .history-list{border-color:rgba(62,207,192,.1)!important;}
          .history-item{border-color:rgba(62,207,192,.08)!important;}
          .history-dot{background:#3ECFC0!important;box-shadow:0 0 8px rgba(62,207,192,.5)!important;}
          .history-item.success .history-dot{background:#3ECFC0!important;box-shadow:0 0 8px rgba(62,207,192,.5)!important;}
          .history-item.warning .history-dot{background:#f59e0b!important;}
          .history-item.danger .history-dot{background:#ef4444!important;}
          .history-body strong{color:rgba(180,230,225,.9)!important;}
          .history-body p{color:rgba(180,230,225,.6)!important;}
          .status-pill,.brand-pill{background:rgba(62,207,192,.15)!important;border-color:rgba(62,207,192,.4)!important;color:#7be3d6!important;}
          .client-logo-wrap img{height:52px!important;width:auto!important;max-width:240px!important;display:block!important;}
        `,
  caoa: `
          [data-client=caoa] *{font-weight:700!important;}
          [data-client=caoa] .rastrear-btn{box-shadow:0 4px 22px rgba(93,186,141,.35)!important;}
          [data-client=caoa] .rastrear-btn:hover{box-shadow:0 6px 28px rgba(93,186,141,.5)!important;}
          /* caoa-theme-v1 */
          /* card-logo-v1 */
          [data-client=brb] .dest-header-inner::after,[data-client=brb] .client-header-inner::after,[data-client=brbdux] .dest-header-inner::after,[data-client=brbdux] .client-header-inner::after,[data-client=tricard] .dest-header-inner::after,[data-client=tricard] .client-header-inner::after,[data-client=pinbank] .dest-header-inner::after,[data-client=pinbank] .client-header-inner::after{background-image:url('/static/logos/logo-agylog-modern-white.svg?v=20260911')!important;background-size:contain!important;background-repeat:no-repeat!important;background-position:center!important;opacity:1!important;}
          /* caoa-result-white-v1 */
          [data-client=caoa] .info-card,[data-client=caoa] .status-visual-card,[data-client=caoa] .timeline-container,[data-client=caoa] .history-card,[data-client=caoa] .third-party-card{background:#f6f7fb!important;border:1px solid rgba(16,12,90,0.10)!important;box-shadow:0 2px 16px rgba(16,12,90,0.07)!important;color:#0d0d1a!important;}
          [data-client=caoa] .status-visual-media{background:#eef0f6!important;}
          [data-client=caoa] .info-card *,[data-client=caoa] .status-visual-card *,[data-client=caoa] .timeline-container *,[data-client=caoa] .history-card *{color:#0d0d1a!important;}
          [data-client=caoa] .status-title,[data-client=caoa] .status-name{color:#3da870!important;}
          [data-client=caoa] .info-label,[data-client=caoa] .card-label,[data-client=caoa] .section-label{color:rgba(16,12,90,0.50)!important;}
          [data-client=caoa] .status-tag,[data-client=caoa] .tag-item{background:rgba(93,186,141,0.12)!important;color:#3da870!important;border:1px solid rgba(93,186,141,0.30)!important;}
          [data-client=caoa] .timeline-node{background:#e2e4ec!important;border-color:rgba(16,12,90,0.15)!important;}
          [data-client=caoa] .timeline-label,[data-client=caoa] .timeline-desc{color:#3a3a5c!important;}
          [data-client=caoa] .progress-line{background:rgba(16,12,90,0.12)!important;}
          [data-client=caoa] .history-dot{background:#5dba8d!important;}
          [data-client=caoa] .history-date,[data-client=caoa] .history-time{color:rgba(16,12,90,0.45)!important;}
          [data-client=caoa] .bg-glow{display:none!important;}
          /* caoa-divider-v1 */
          [data-client=caoa] .dest-header-inner::before,[data-client=caoa] .client-header-inner::before{content:''!important;display:block!important;width:1px!important;height:36px!important;background:rgba(0,0,0,0.70)!important;align-self:center!important;flex-shrink:0!important;border-radius:1px!important;}
          /* caoa-white-bg-v1 */
          body[data-client=caoa],[data-client=caoa] body,[data-client=caoa]{background:#ffffff!important;color:#0d0d1a!important;}
          [data-client=caoa] .bg-glow,[data-client=caoa] .glow-1,[data-client=caoa] .glow-2,[data-client=caoa] .glow-3{display:none!important;}
          [data-client=caoa] main,[data-client=caoa] .tracking-main,[data-client=caoa] .page-wrap,[data-client=caoa] .content-wrap{background:#ffffff!important;}
          [data-client=caoa] .tracking-card,[data-client=caoa] .search-card{background:#f6f7fb!important;border:1px solid rgba(16,12,90,0.10)!important;box-shadow:0 4px 24px rgba(16,12,90,0.08)!important;}
          [data-client=caoa] .tracking-title,[data-client=caoa] h1,[data-client=caoa] h2,[data-client=caoa] h3{color:#100c5a!important;}
          [data-client=caoa] p,[data-client=caoa] span,[data-client=caoa] label,[data-client=caoa] .subtitle{color:#3a3a5c!important;}
          [data-client=caoa] input[type=text],[data-client=caoa] input[type=search]{background:#ffffff!important;border:1.5px solid rgba(16,12,90,0.18)!important;color:#0d0d1a!important;}
          [data-client=caoa] input::placeholder{color:rgba(16,12,90,0.40)!important;}
          [data-client=caoa] .site-footer{background:#f6f7fb!important;border-top:1px solid rgba(16,12,90,0.10)!important;color:#100c5a!important;}
          [data-client=caoa] .site-footer *{color:#100c5a!important;}
          [data-client=caoa] .colar-btn,[data-client=caoa] .paste-btn{color:#5dba8d!important;}
          /* caoa-agyblack-v1 */
          [data-client=caoa] .dest-header-inner::after,[data-client=caoa] .client-header-inner::after{background-image:url('/static/logos/logo-agylog-modern.svg?v=20260911')!important;background-size:contain!important;background-repeat:no-repeat!important;background-position:center!important;opacity:1!important;}
          [data-client=caoa]{--accent:#5dba8d;--accent-hover:#3da870;}
          [data-client=caoa] .tracking-header{background:#ffffff!important;border-bottom:1px solid rgba(16,12,90,0.10)!important;box-shadow:0 2px 12px rgba(16,12,90,0.08)!important;}
          [data-client=caoa] .tracking-header *{color:#100c5a!important;}
          [data-client=caoa] .client-name{color:#100c5a!important;}
          [data-client=caoa] .tracking-footer{background:#f6f7fb!important;color:#100c5a!important;border-top:1px solid rgba(16,12,90,0.10)!important;}
          [data-client=caoa] .tracking-footer *{color:#100c5a!important;}
          [data-client=caoa] .partner-line{color:#100c5a!important;}
          [data-client=caoa] .status-pill{background:rgba(93,186,141,0.15)!important;color:#3da870!important;border-color:rgba(93,186,141,0.35)!important;}
          [data-client=caoa] .btn-primary,.tracking-btn-primary{background:#5dba8d!important;color:#fff!important;border-color:#5dba8d!important;}
          [data-client=caoa] .btn-primary:hover{background:#3da870!important;}
          [data-client=caoa] .timeline-node-check{color:#ffffff!important;background:#5dba8d!important;box-shadow:0 0 8px rgba(93,186,141,0.5)!important;}
          [data-client=caoa] .timeline-stage.done .timeline-node-check,[data-client=caoa] .timeline-stage.active .timeline-node-check,[data-client=caoa] .timeline-stage.final .timeline-node-check{background:#5dba8d!important;color:#fff!important;}
          [data-client=caoa] .timeline-stage.done .timeline-node-check,[data-client=caoa] .timeline-stage.final .timeline-node-check{box-shadow:0 0 12px rgba(93,186,141,0.55)!important;}
          [data-client=caoa] .timeline-stage.active .timeline-node-check{box-shadow:0 0 16px rgba(93,186,141,0.6)!important;}
          [data-client=caoa] .timeline-track{background:rgba(93,186,141,0.25)!important;}
          [data-client=caoa] .timeline-track-fill{background:#5dba8d!important;}
  `,
  };

    _ts.textContent = _pageThemes[slug] || '';
    document.head.appendChild(_ts);

    // Header
    const header = document.querySelector('.dest-header');
    if (header) {
      const headerTagline = 'Rastreamento de encomenda';
      header.innerHTML = `
        <div class="dest-header-inner client-header-inner">
          <div class="client-logo-wrap">${t.logoSvg}</div>
          <span class="client-header-tagline">${headerTagline}</span>
        </div>
      `;
    }

    // Footer
    const footer = document.querySelector('.site-footer');
    if (footer) {
      footer.innerHTML = `
        <div class="client-footer-inner">
          <p class="client-partner-line">${t.partnerLine}</p>
          <p class="client-footer-copy">&copy; ${new Date().getFullYear()} AGYLOG &middot; Todos os direitos reservados</p>
        </div>
      `;
    }

    // Page title
    document.title = `Rastreio · ${t.name}`;
  }

(function () {
  'use strict';

  const POLL_INTERVAL_MS = 30000;
  const CCXP_POLL_INTERVAL_MS = 30000;

  const codigoInput = document.getElementById('codigoInput');
  const pasteBtn = document.getElementById('pasteBtn');
  const rastrearBtn = document.getElementById('rastrearBtn');
  const alertBox = document.getElementById('alertBox');
  const resultArea = document.getElementById('resultArea');
  const resultCode = document.getElementById('resultCode');
  const resultCliente = document.getElementById('resultCliente');
  const statusText = document.getElementById('statusText');
  const statusPill = document.getElementById('statusPill');
  const currentStageTitle = document.getElementById('currentStageTitle');
  const journeyMessage = document.getElementById('journeyMessage');
  const statusVisualMedia = document.getElementById('statusVisualMedia');
  const visualTags = document.getElementById('visualTags');
  const timeline = document.getElementById('timeline');
  const historyList = document.getElementById('historyList');
  const progressFill = document.getElementById('progressFill');
  const lastUpdateLabel = document.getElementById('lastUpdateLabel');
  const novaBuscaBtn = document.getElementById('novaBuscaBtn');
  const thirdPartyCard = document.getElementById('thirdPartyCard');
  const thirdPartyGrid = document.getElementById('thirdPartyGrid');

  let pollTimer = null;

  const STATUS_THEME = {
    aguardando_postagem: 'violet',
    preparacao_transporte: 'warning',
    transferencia_franquia: 'violet',
    chegada_franquia: '',
    em_rota_entrega: '',
    atencao: 'danger',
    devolucao: 'danger',
    devolvido: 'danger',
    entregue: 'success',
  };

  const STATUS_VISUAL = {
    aguardando_postagem: {
      title: 'Aguardando postagem',
      body: 'O pedido foi recebido e aguarda a confirmação da postagem para entrar na operação.',
      tags: ['Aguardando coleta', 'Pedido confirmado', 'Atualização em breve'],
      media: '/static/assets/waiting.json',
    },
    preparacao_transporte: {
      title: 'Em preparação para transporte',
      body: 'Seu pedido está sendo separado, organizado e preparado para seguir viagem.',
      tags: ['Separação em andamento', 'Conferência ativa', 'Preparando expedição'],
      media: '/static/assets/conveyor.gif',
    },
    transferencia_franquia: {
      title: 'Transferência para franquia distribuidora',
      body: 'A encomenda está em deslocamento entre unidades para chegar ao ponto final de distribuição.',
      tags: ['Transferência ativa', 'Movimento entre unidades', 'Rota confirmada'],
      media: '/static/assets/codex-in-transit.gif',
    },
    chegada_franquia: {
      title: 'Chegada na franquia',
      body: 'O pedido já chegou na unidade responsável pela distribuição final.',
      tags: ['Chegada confirmada', 'Triagem local', 'Última etapa se aproximando'],
      media: '/static/assets/conveyor.gif',
    },
    em_rota_entrega: {
      title: 'Em rota de entrega',
      body: 'Agora sim: o pedido está em rota para o destinatário final.',
      tags: ['Última milha', 'Motorista em rota', 'Entrega em andamento'],
      media: '/static/assets/codex-in-transit.gif',
    },
    atencao: {
      title: 'Entrega malsucedida',
      body: 'Não foi possível concluir a entrega. Uma nova tentativa será realizada em breve. Após 3 tentativas sem sucesso, o objeto retornará à base.',
      tags: ['Nova tentativa agendada', 'Destinatário ausente', 'Até 3 tentativas'],
      media: '/static/assets/codex-in-transit.gif',
      breaking: true,
    },
    devolucao: {
      title: 'Em processo de devolução',
      body: 'Foram realizadas 3 tentativas de entrega sem sucesso. O pedido está em processo de devolução ao remetente.',
      tags: ['Devolução em andamento', '3 tentativas realizadas'],
      media: '/static/assets/codex-in-transit.gif',
      returning: true,
    },
    devolvido: {
        title: 'Devolvido ao remetente',
        body: 'O objeto foi devolvido ao remetente após 3 tentativas de entrega sem sucesso.',
        tags: ['Devolução concluída', 'Retornado ao remetente'],
        media: '/static/assets/box.png',
        returned: true,
    },
    entregue: {
      title: 'Pedido entregue',
      body: 'A entrega foi finalizada com sucesso e o pedido já chegou ao destinatário.',
      tags: ['Recebido', 'Entrega concluída', 'Status final confirmado'],
      media: '/static/assets/check.gif',
      delivered: true,
    },
  };

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function showAlert(message, type) {
    alertBox.textContent = message;
    alertBox.className = `alert-box show ${type || 'danger'}`;
  }

  function hideAlert() {
    alertBox.textContent = '';
    alertBox.className = 'alert-box';
  }

  function renderThirdPartyTracking(tracking) {
    if (!thirdPartyCard || !thirdPartyGrid) return;

    const codigoTerceiro = String(tracking?.codigoTerceiro || '').trim();

    if (!codigoTerceiro) {
      thirdPartyGrid.innerHTML = '';
      thirdPartyCard.classList.add('hidden');
      return;
    }

    thirdPartyGrid.innerHTML = `
      <div class="info-item" style="padding-top:6px;">
        <a href="https://rastreamento.correios.com.br/app/index.php?objetos=${escapeHtml(codigoTerceiro)}" target="_blank" rel="noopener" style="display:flex;align-items:center;justify-content:space-between;width:100%;padding:13px 18px;border-radius:8px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.18);color:inherit;font-size:14px;font-weight:700;text-decoration:none;letter-spacing:1px;cursor:pointer;box-sizing:border-box;"><span style="display:flex;align-items:center;gap:10px;">&#128230; <span><span style="font-size:11px;font-weight:400;opacity:0.6;display:block;letter-spacing:2px;text-transform:uppercase;">C&#243;digo Correios</span>${escapeHtml(codigoTerceiro)}</span></span><span style="font-size:20px;opacity:0.7;">&rarr;</span></a>
      </div>
    `;

    thirdPartyCard.classList.remove('hidden');
  }

  function formatNow() {
    return new Date().toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  function resolveLastUpdate(data, ccxpTreatment) {
    const candidates = [ccxpTreatment?.when, data?.updated_at, data?.updatedAt, data?.ultima_atualizacao, data?.ultimaAtualizacao, data?.ultima_atualizacao_api, data?.ultimaAtualizacaoApi, Array.isArray(data?.history) ? data.history[0]?.when : ''];
    return String(candidates.find((value) => String(value || '').trim()) || '').trim();
  }

  function isCcXpClient() {
    return detectClient() === 'ccxp';
  }

  const CCXP_TREATMENT_STATUSES = new Set([
    'atencao',
    'devolucao',
    'devolvido',
    'ccxp_aguardando_tratativa',
    'ccxp_tratado',
  ]);

  function isCcXpTreatmentStatus(status) {
    return isCcXpClient() && CCXP_TREATMENT_STATUSES.has(status);
  }

  function normalizeCcXpText(value) {
    return String(value ?? '')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .replace(/\s+/g, ' ')
      .trim();
  }

  function resolveCcXpTreatment(data) {
    if (!isCcXpTreatmentStatus(data?.status)) return null;

    const historyText = (Array.isArray(data.history) ? data.history : [])
      .map((entry) => `${entry?.title || ''} ${entry?.desc || ''}`)
      .join(' ');
    const normalizedHistory = normalizeCcXpText(historyText);
    const latestWhen = Array.isArray(data.history) && data.history.length
      ? String(data.history[0]?.when || '').trim()
      : '';
    const hasTreatment = data?.status === 'ccxp_tratado' || data?.kind === 'reenvio' || (normalizedHistory.includes('tratamento de pendencia') && normalizedHistory.includes('reentregar'));

    return hasTreatment
      ? {
          label: 'Tratativa concluída',
          title: 'Tratativa concluída',
          body: 'Nova tentativa de entrega já agendada.',
          timelineDesc: 'Nova tentativa de entrega já agendada.',
          tags: [],
          kind: 'reenvio',
          when: latestWhen,
        }
      : {
          label: 'Insucesso na entrega',
          title: 'Insucesso na entrega',
          body: 'Uma nova tentativa de entrega será realizada em breve.',
          timelineDesc: 'Nova tentativa de entrega em breve.',
          tags: [],
          when: latestWhen,
        };
  }

  function formatCcXpHistoryText(value, field, treatmentLabel) {
    const text = String(value ?? '').trim();
    if (!text) return '';

    const normalized = normalizeCcXpText(text);
    const isTreated = treatmentLabel === 'Tratativa concluída';
    const safeDescription = isTreated
      ? 'Nova tentativa de entrega já agendada.'
      : 'Uma nova tentativa de entrega será realizada em breve.';

    const replacements = {
      'nao entregue por cep incorreto - volume nao entregue': 'Não entregue: CEP incorreto.',
      'nao entregue por numero nao localizado - volume nao entregue': 'Não entregue: número não localizado.',
      'devolucao realizada': '',
      'incesso, aguardando tratativa': 'Insucesso na entrega',
      'insucesso, aguardando tratativa': 'Insucesso na entrega',
      'aguardando tratativa do time ccxp': 'Insucesso na entrega',
      'tratado pelo time ccxp': 'Tratativa concluída',
    };

    if (field === 'title' && ['custodia', 'devolucao', 'devolvido', 'em devolucao'].includes(normalized)) {
      return treatmentLabel || 'Insucesso na entrega';
    }

    if (normalized.includes('tratamento de pendencia')) {
      if (normalized.includes('reentregar')) {
        return field === 'title'
          ? 'Tratativa concluída'
          : 'Nova tentativa de entrega já agendada.';
      }
      return field === 'title'
        ? (treatmentLabel || 'Insucesso na entrega')
        : safeDescription;
    }

    if (
      normalized.includes('devol') ||
      normalized.includes('retorn') ||
      normalized.includes('remetente')
    ) {
      return field === 'title'
        ? (treatmentLabel || 'Insucesso na entrega')
        : safeDescription;
    }

    return replacements[normalized] ?? text;
  }

  function normalizeStageIndex(status, stages) {
    const statusIndex = stages.findIndex((stage) => stage.key === status);
    if (statusIndex >= 0) return statusIndex;

    const doneCount = stages.filter((stage) => stage.done).length;
    return Math.max(0, Math.min(stages.length - 1, doneCount));
  }

  const CCXP_REENVIO_CSS = `
.ccxpre-wrap{width:100%;height:100%;min-height:250px;display:flex;align-items:center;justify-content:center;background:#000;overflow:hidden}
.ccxpre-svg{width:100%;height:100%;max-height:420px;display:block}
.ccxpre-glow{transform-origin:340px 230px;animation:ccxpre-glow 3s ease-in-out infinite}
.ccxpre-spin{transform-origin:340px 230px;animation:ccxpre-spin 8s linear infinite}
.ccxpre-badge{animation:ccxpre-float 3s ease-in-out infinite}
.ccxpre-check{transform-origin:392px 158px;animation:ccxpre-check 8s ease-in-out infinite}
.ccxpre-road{animation:ccxpre-road 1.1s linear infinite}
.ccxpre-truck{animation:ccxpre-drive 8s linear infinite}
.ccxpre-wheel{transform-box:fill-box;transform-origin:center;animation:ccxpre-wheel .7s linear infinite}
@keyframes ccxpre-spin{to{transform:rotate(360deg)}}
@keyframes ccxpre-glow{0%,100%{opacity:.55;transform:scale(.96)}50%{opacity:1;transform:scale(1.04)}}
@keyframes ccxpre-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes ccxpre-check{0%{transform:scale(0);opacity:0}8%{transform:scale(1.2);opacity:1}14%,88%{transform:scale(1);opacity:1}96%,100%{transform:scale(.6);opacity:0}}
@keyframes ccxpre-road{to{stroke-dashoffset:-26}}
@keyframes ccxpre-drive{0%{transform:translateX(-400px)}80%,100%{transform:translateX(1080px)}}
@keyframes ccxpre-wheel{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){
.ccxpre-glow,.ccxpre-spin,.ccxpre-badge,.ccxpre-check,.ccxpre-road,.ccxpre-truck,.ccxpre-wheel{animation:none!important}
.ccxpre-truck{transform:translateX(330px)}
}
`;

  const CCXP_REENVIO_HTML = `
<div class="ccxpre-wrap" role="img" aria-label="Pedido com nova tentativa de entrega em breve.">
<svg class="ccxpre-svg" viewBox="130 55 420 420" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
  <defs>
    <radialGradient id="ccxpre-glow-g" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#E33781" stop-opacity=".32"/>
      <stop offset="1" stop-color="#E33781" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="ccxpre-arc-g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#E33781"/>
      <stop offset="1" stop-color="#F091BA"/>
    </linearGradient>
    <linearGradient id="ccxpre-beam-g" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#F091BA" stop-opacity=".38"/>
      <stop offset="1" stop-color="#F091BA" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <circle class="ccxpre-glow" cx="340" cy="230" r="190" fill="url(#ccxpre-glow-g)"/>

  <circle cx="340" cy="230" r="150" fill="none" stroke="rgba(227,55,129,.20)" stroke-width="5"/>
  <g class="ccxpre-spin">
    <circle cx="340" cy="230" r="150" fill="none" stroke="url(#ccxpre-arc-g)" stroke-width="7" stroke-linecap="round" stroke-dasharray="620 323"/>
    <polygon points="271,96 252,95.5 264,114" fill="#F091BA"/>
  </g>

  <g class="ccxpre-badge">
    <rect x="285" y="155" width="110" height="150" rx="14" fill="#0a0a0c" stroke="rgba(255,255,255,.6)" stroke-width="3"/>
    <rect x="322" y="167" width="36" height="8" rx="4" fill="rgba(255,255,255,.55)"/>
    <circle cx="340" cy="218" r="20" fill="none" stroke="#E33781" stroke-width="4"/>
    <circle cx="340" cy="212" r="6" fill="#E33781"/>
    <path d="M 327 231 a 13 10 0 0 1 26 0 Z" fill="#E33781"/>
    <rect x="304" y="252" width="72" height="8" rx="4" fill="rgba(255,255,255,.55)"/>
    <rect x="316" y="268" width="48" height="8" rx="4" fill="rgba(255,255,255,.28)"/>
    <rect x="304" y="284" width="20" height="8" rx="4" fill="#E33781"/>
    <g class="ccxpre-check">
      <circle cx="392" cy="158" r="20" fill="#E33781" stroke="#000" stroke-width="4"/>
      <path d="M 382 158 L 389 165 L 402 150" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
    </g>
  </g>

  <line class="ccxpre-road" x1="-900" y1="446" x2="1580" y2="446" stroke="rgba(227,55,129,.32)" stroke-width="3" stroke-dasharray="14 12"/>

  <g transform="translate(0 440)">
    <g class="ccxpre-truck">
      <polygon points="40,-20 150,-46 150,2 40,-8" fill="url(#ccxpre-beam-g)"/>
      <rect x="-100" y="-58" width="94" height="52" rx="6" fill="#0a0a0c" stroke="rgba(255,255,255,.75)" stroke-width="3"/>
      <rect x="-84" y="-44" width="30" height="8" rx="4" fill="#E33781"/>
      <path d="M -2 -6 L -2 -42 L 20 -42 L 40 -22 L 40 -6 Z" fill="#0a0a0c" stroke="rgba(255,255,255,.75)" stroke-width="3" stroke-linejoin="round"/>
      <path d="M 6 -35 L 18 -35 L 31 -22 L 6 -22 Z" fill="rgba(227,55,129,.55)"/>
      <circle cx="38" cy="-14" r="3.5" fill="#F091BA"/>
      <g class="ccxpre-wheel">
        <circle cx="-68" cy="-4" r="10" fill="#0a0a0c" stroke="#E33781" stroke-width="3.5"/>
        <line x1="-68" y1="-12" x2="-68" y2="-4" stroke="#E33781" stroke-width="3" stroke-linecap="round"/>
      </g>
      <g class="ccxpre-wheel">
        <circle cx="16" cy="-4" r="10" fill="#0a0a0c" stroke="#E33781" stroke-width="3.5"/>
        <line x1="16" y1="-12" x2="16" y2="-4" stroke="#E33781" stroke-width="3" stroke-linecap="round"/>
      </g>
    </g>
  </g>
</svg>
</div>
`;

  function renderCcXpReenvioAnimation(container) {
    if (!document.getElementById('ccxpre-style')) {
      const style = document.createElement('style');
      style.id = 'ccxpre-style';
      style.textContent = CCXP_REENVIO_CSS;
      document.head.appendChild(style);
    }
    container.innerHTML = CCXP_REENVIO_HTML;
  }

  function renderVisual(status, ccxpTreatment) {
    const visual = ccxpTreatment
      ? { ...ccxpTreatment, media: '/static/assets/waiting.json' }
      : STATUS_VISUAL[status] || STATUS_VISUAL.em_rota_entrega;

    currentStageTitle.textContent = visual.title;
    journeyMessage.textContent = visual.body;
    visualTags.innerHTML = visual.tags
      .map((tag) => `<span class="visual-tag">${escapeHtml(tag)}</span>`)
      .join('');

    if (ccxpTreatment) { renderCcXpReenvioAnimation(statusVisualMedia); return; }

    if (visual.media) {
      const isLottie = visual.media.endsWith('.json');

      if (!visual.delivered) {
        if (visual.breaking) {
          statusVisualMedia.innerHTML = `
            <div class="breaking-wrap">
              <img src="${escapeHtml(visual.media)}" alt="${escapeHtml(visual.title)}" class="breaking-truck" />
              <div class="breaking-overlay"></div>
              <svg class="breaking-x-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <line x1="20" y1="20" x2="80" y2="80" stroke="#ef4444" stroke-width="9" stroke-linecap="round"
                  stroke-dasharray="85" stroke-dashoffset="85">
                  <animate attributeName="stroke-dashoffset"
                    values="85;0;0;85" keyTimes="0;0.18;0.75;1"
                    dur="6s" repeatCount="indefinite" calcMode="spline"
                    keySplines="0.4 0 0.2 1; 0 0 1 1; 0 0 1 1"/>
                </line>
                <line x1="80" y1="20" x2="20" y2="80" stroke="#ef4444" stroke-width="9" stroke-linecap="round"
                  stroke-dasharray="85" stroke-dashoffset="85">
                  <animate attributeName="stroke-dashoffset"
                    values="85;85;0;0;85" keyTimes="0;0.18;0.36;0.75;1"
                    dur="6s" repeatCount="indefinite" calcMode="spline"
                    keySplines="0 0 1 1; 0.4 0 0.2 1; 0 0 1 1; 0 0 1 1"/>
                </line>
              </svg>
            </div>
          `;
          return;
        }
        if (visual.returned) {
        statusVisualMedia.innerHTML = `
          <div class="returned-wrap">
            <img src="${escapeHtml(visual.media)}" alt="${escapeHtml(visual.title)}" class="returned-img" />
            <div class="returned-svg-overlay">
              <svg viewBox="0 0 680 580" xmlns="http://www.w3.org/2000/svg"><defs><style>@keyframes drawLine{0%{stroke-dashoffset:662}70%{stroke-dashoffset:0}88%{stroke-dashoffset:0}96%{stroke-dashoffset:662}100%{stroke-dashoffset:662}}@keyframes showTip{0%{opacity:0}56%{opacity:0}58%{opacity:1}88%{opacity:1}96%{opacity:0}100%{opacity:0}}.ret-line{fill:none;stroke:#E24B4A;stroke-width:65;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:662;stroke-dashoffset:662;animation:drawLine 4.5s ease-in-out infinite}.ret-tip{opacity:0;animation:showTip 4.5s ease-in-out infinite}</style></defs><path class="ret-line" d="M 370,445 A 155,155 0 0,0 370,135 L 230,135"/><polygon class="ret-tip" fill="#E24B4A" points="130,135 230,75 230,195"/></svg>
            </div>
          </div>
        `;
        return;
      }
            if (visual.returning) {
          statusVisualMedia.innerHTML = `
            <div class="returning-wrap">
              <img src="${escapeHtml(visual.media)}" alt="${escapeHtml(visual.title)}" class="returning-truck" />
              <div class="returning-svg-overlay">
                <svg viewBox="0 0 680 580" xmlns="http://www.w3.org/2000/svg"><defs><style>@keyframes drawLine{0%{stroke-dashoffset:662}70%{stroke-dashoffset:0}88%{stroke-dashoffset:0}96%{stroke-dashoffset:662}100%{stroke-dashoffset:662}}@keyframes showTip{0%{opacity:0}56%{opacity:0}58%{opacity:1}88%{opacity:1}96%{opacity:0}100%{opacity:0}}.ret-line{fill:none;stroke:#E24B4A;stroke-width:65;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:662;stroke-dashoffset:662;animation:drawLine 4.5s ease-in-out infinite}.ret-tip{opacity:0;animation:showTip 4.5s ease-in-out infinite}</style></defs><path class="ret-line" d="M 370,445 A 155,155 0 0,0 370,135 L 230,135"/><polygon class="ret-tip" fill="#E24B4A" points="130,135 230,75 230,195"/></svg>
              </div>
            </div>
          `;
          return;
        }
        if (isLottie) {
          statusVisualMedia.innerHTML = `<lottie-player src="${escapeHtml(visual.media)}" background="transparent" speed="1" loop autoplay style="width:100%;height:100%;min-height:250px"></lottie-player>`;
        } else {
          statusVisualMedia.innerHTML = `<img src="${escapeHtml(visual.media)}" alt="${escapeHtml(visual.title)}" />`;
        }
        return;
      }

      statusVisualMedia.innerHTML = `
        <div class="delivered-panel">
          <img src="/static/assets/box.png" alt="Caixa entregue" class="delivered-box" />
          <img src="${escapeHtml(visual.media)}" alt="${escapeHtml(visual.title)}" class="delivered-check" />
        </div>
      `;
      return;
    }

    statusVisualMedia.innerHTML = `
      <div class="status-visual-scene ${escapeHtml(visual.scene || 'waiting')}">
        <div class="scene-ring"></div>
        <div class="scene-track"></div>
        <div class="scene-float-icon">${escapeHtml(visual.emoji || '📦')}</div>
      </div>
    `;
  }

  function renderTimeline(stages, activeStatus, ccxpTreatment) {
  const problemKeys = ['atencao', 'devolucao', 'devolvido'];

  function hasRealDate(stage) {
    const date = String(stage?.date || '').trim().toLowerCase();
    return date && date !== '-' && date !== 'null' && date !== 'undefined';
  }

  function formatCcXpTimelineWhen(value) {
    const text = String(value || '').trim();
    const match = text.match(/^(\d{2}\/\d{2})(?:\/\d{4})?(?:\s+(?:às|·)?\s*(\d{2}:\d{2}))?/i);
    return {
      date: match?.[1] || '-',
      time: match?.[2] || '',
    };
  }

  const isProblemFlow = problemKeys.includes(activeStatus);

  // Mantém a ordem original, mas tira etapas de problema/devolução
  // quando o rastreio atual não está nesse fluxo e elas não têm data real.
  stages = Array.isArray(stages) ? [...stages] : [];

  if (isCcXpTreatmentStatus(activeStatus)) {
    const treatmentWhen = formatCcXpTimelineWhen(ccxpTreatment?.when);
    stages = stages
      .filter((stage) => stage && !problemKeys.includes(stage.key) && stage.key !== 'entregue' && stage.key !== 'ccxp_tratativa')
      .filter((stage) => stage.key !== 'em_rota_entrega' || hasRealDate(stage))
      .map((stage) => stage.key === 'em_rota_entrega'
        ? { ...stage, done: true, attention: false }
        : stage);

    stages.push({
      key: 'ccxp_tratativa',
      title: 'Reenvio',
      desc: ccxpTreatment?.timelineDesc || 'Aguardando tratativa para reenvio.',
      date: treatmentWhen.date,
      time: treatmentWhen.time,
      icon: '✓',
      done: true,
      attention: false,
    });
    activeStatus = 'ccxp_tratativa';
  }

  if (!isProblemFlow) {
    stages = stages.filter((stage) => {
      if (!stage || !problemKeys.includes(stage.key)) return true;
      return stage.done && hasRealDate(stage);
    });
  }

  let activeIndex = normalizeStageIndex(activeStatus, stages);
  const isAtencao = activeStatus === 'atencao';

  if (isAtencao) {
    stages = stages.map((s, i) =>
      i === activeIndex + 1 ? { ...s, done: false, date: '-', time: '' } : s
    );
  }

  stages = stages.filter((s, i) =>
    i <= activeIndex || s.done || (isAtencao && i === activeIndex + 1)
  );

  // Depois de filtrar/remover etapas, recalcula o índice ativo.
  // Esse era o ponto que quebrava: o activeIndex antigo apontava para outra posição.
  activeIndex = stages.findIndex((stage) => stage.key === activeStatus);

  if (activeIndex < 0) {
    activeIndex = normalizeStageIndex(activeStatus, stages);
  }

  activeIndex = Math.max(0, Math.min(stages.length - 1, activeIndex));

  const fillRatio = stages.length > 1 ? activeIndex / (stages.length - 1) : 0;

  const n = stages.length || 1;
  const offset = `calc(100% / ${2 * n})`;
  const progressLine = document.querySelector('.progress-line');
  const progressLineFill = document.querySelector('.progress-line-fill');

  if (progressLine && progressLineFill) {
    progressLine.style.display = '';
    progressLineFill.style.display = '';
    progressLine.style.left = offset;
    progressLine.style.right = offset;
    progressLineFill.style.left = offset;
    progressLineFill.style.right = offset;
  }

  progressFill.style.transform = `scaleX(${fillRatio})`;
  timeline.style.gridTemplateColumns = `repeat(${n}, minmax(0, 1fr))`;

  timeline.innerHTML = stages.map((stage, index) => {
    const classNames = ['timeline-stage'];
    const isDone = index < activeIndex || stage.done;
    const isActive = index === activeIndex;

    if (isDone) classNames.push('done');
    if (isActive) classNames.push('active');
    if (stage.attention) classNames.push('attention');
    if (stage.key === 'entregue') classNames.push('final');
    if (stage.key === 'ccxp_tratativa') classNames.push('ccxp-treatment');

    const timeText = stage.time ? `${stage.date} · ${stage.time}` : stage.date;

    const nodeContent = isDone
      ? '<span class="timeline-node-check">✓</span>'
      : isActive
        ? `<span class="timeline-node-emoji">${escapeHtml(stage.icon)}</span>`
        : '<span class="timeline-node-pending"><span class="pending-ring"></span><span class="pending-ring r2"></span></span>';

    return `
      <article class="${classNames.join(' ')}">
        <div class="timeline-node">${nodeContent}</div>
        <h4>${escapeHtml(stage.title)}</h4>
        <time>${escapeHtml(timeText || '-')}</time>
        <p>${escapeHtml(stage.desc)}</p>
      </article>
    `;
  }).join('');
}

  function renderHistory(history, ccxpTreatment) {
    const shouldFormatCcXp = isCcXpClient();
    const treatmentLabel = ccxpTreatment?.label;

    historyList.innerHTML = history.map((entry) => {
      const title = shouldFormatCcXp ? formatCcXpHistoryText(entry.title, 'title', treatmentLabel) : entry.title;
      const desc = shouldFormatCcXp ? formatCcXpHistoryText(entry.desc, 'desc', treatmentLabel) : entry.desc;

      return `
      <article class="history-item ${escapeHtml(entry.theme || '')}">
        <div class="history-dot"></div>
        <div class="history-body">
          <strong>${escapeHtml(title)}</strong>
          ${desc ? `<p>${escapeHtml(desc)}</p>` : ''}
        </div>
        <time class="history-time">${escapeHtml(entry.when)}</time>
      </article>
    `;
    }).join('');
  }

  function applyStatusVisuals(data) {
    const ccxpTreatment = resolveCcXpTreatment(data);
    statusPill.className = ccxpTreatment
      ? 'status-pill'
      : `status-pill ${STATUS_THEME[data.status] || ''}`.trim();
    statusText.textContent = ccxpTreatment?.label || data.status_label || '-';
    const lastUpdate = resolveLastUpdate(data, ccxpTreatment);
    lastUpdateLabel.textContent = lastUpdate ? "Última atualização: " + lastUpdate : "";
    renderVisual(data.status, ccxpTreatment);
    renderTimeline(data.stages || [], data.status, ccxpTreatment);
    renderHistory(data.history || [], ccxpTreatment);
  }

  function showResult(code, data) {
    resultCode.textContent = code;
    resultCliente.textContent = data.cliente || '-';
    applyStatusVisuals(data);
    renderThirdPartyTracking(data.rastreioTerceiro);
    resultArea.classList.add('show');
    resultArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
    startPolling(code);
  }


  function syncTrackingUrl(code) {
    const cleanCode = String(code || '').trim().toUpperCase();
    if (!cleanCode || !window.history || !window.history.pushState) return;

    const clientSlug = detectClient();
    const nextPath = clientSlug
      ? `/tracking/${clientSlug}/${encodeURIComponent(cleanCode)}`
      : `/tracking/${encodeURIComponent(cleanCode)}`;

    if (window.location.pathname !== nextPath) {
      window.history.pushState({}, '', nextPath);
    }
  }

  async function fetchTracking(code, extraBody) {
    const response = await fetch('/api/rastrear', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        codigo: code,
        ...(isCcXpClient() ? { cliente: 'ccxp' } : {}),
        ...(extraBody || {}),
      }),
    });

    let data = {};
    try {
      data = await response.json();
    } catch {
      data = {};
    }

    return data;
  }

  function startPolling(code) {
    clearInterval(pollTimer);
    pollTimer = setInterval(async () => {
      try {
        const data = await fetchTracking(code, { poll: true });
        if (data.ok) {
          applyStatusVisuals(data);
          renderThirdPartyTracking(data.rastreioTerceiro);
        }
      } catch {
        /* silent */
      }
    }, isCcXpClient() ? CCXP_POLL_INTERVAL_MS : POLL_INTERVAL_MS);
  }

  function stopPolling() {
    clearInterval(pollTimer);
    pollTimer = null;
  }

  function resetResult() {
    stopPolling();
    resultArea.classList.remove('show');
    resultCode.textContent = '-';
    resultCliente.textContent = '-';
    statusText.textContent = '-';
    currentStageTitle.textContent = 'Acompanhamento da entrega';
    journeyMessage.textContent = 'Consulte o código do pedido para visualizar a etapa atual da entrega.';
    statusVisualMedia.innerHTML = '';
    visualTags.innerHTML = '';
    timeline.innerHTML = '';
    historyList.innerHTML = '';
    progressFill.style.transform = 'scaleX(0)';
    lastUpdateLabel.textContent = '';
    statusPill.className = 'status-pill';
    renderThirdPartyTracking(null);
    codigoInput.value = '';
    hideAlert();
    codigoInput.focus();
  }

  pasteBtn.addEventListener('click', async () => {
    try {
      const text = await navigator.clipboard.readText();
      codigoInput.value = text.trim().toUpperCase();
      codigoInput.focus();
    } catch {
      showAlert('Não foi possível acessar a área de transferência. Cole manualmente.', 'warning');
    }
  });

  codigoInput.addEventListener('input', () => {
    codigoInput.value = codigoInput.value.toUpperCase();
    hideAlert();
  });

  codigoInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      rastrearBtn.click();
    }
  });

  rastrearBtn.addEventListener('click', async () => {
    hideAlert();

    const code = codigoInput.value.trim();
    if (!code) {
      showAlert('Digite o código de rastreio antes de continuar.', 'warning');
      codigoInput.focus();
      return;
    }

    if (code.length < 2) {
      showAlert('Código muito curto. Verifique e tente novamente.', 'warning');
      codigoInput.focus();
      return;
    }

    rastrearBtn.disabled = true;
    rastrearBtn.textContent = 'Consultando...';

    try {
      const data = await fetchTracking(code);
      if (!data.ok) {
        showAlert(data.error || 'Código não encontrado. Verifique e tente novamente.', 'danger');
        return;
      }

      syncTrackingUrl(code);
      showResult(code, data);
    } catch {
      showAlert('Falha de conexão. Verifique sua internet e tente novamente.', 'danger');
    } finally {
      rastrearBtn.disabled = false;
      rastrearBtn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        Rastrear encomenda
      `;
    }
  });

  novaBuscaBtn.addEventListener('click', resetResult);

  // ── Apply client theme on load ────────────────────────────────────────
  const _clientSlug = detectClient();
  if (_clientSlug) {
    applyClientTheme(_clientSlug);
    // Pre-fill code from URL: /tracking/SLUG/CODE
    const _urlCode = getTrackingCodeFromURL();
    if (_urlCode && codigoInput && !codigoInput.value) {
      codigoInput.value = _urlCode;
    }
  } else {
    // Existing behaviour: /tracking/CODE
    const _parts = window.location.pathname.split('/').filter(Boolean);
    if (_parts.length >= 2 && _parts[0] === 'tracking' && !codigoInput.value) {
      codigoInput.value = _parts[1].toUpperCase();
    }
  }

})();

/* CODEX TRICARD FINAL HEADER START */
(function () {
  if (typeof detectClient !== 'function' || detectClient() !== 'tricard') return;
  var css = "[data-client=tricard] .dest-header,\n[data-client=tricard] .client-header,\nbody[data-client=tricard] .dest-header,\nbody[data-client=tricard] .client-header {\n  background: linear-gradient(90deg, #0b4691 0%, #083f86 52%, #073676 100%) !important;\n  border-bottom: 1px solid rgba(20, 194, 232, .20) !important;\n  box-shadow: 0 14px 34px rgba(0, 18, 39, .26) !important;\n}\n[data-client=tricard] .dest-header::before,\n[data-client=tricard] .dest-header::after,\n[data-client=tricard] .client-header::before,\n[data-client=tricard] .client-header::after {\n  display: none !important;\n  opacity: 0 !important;\n}\n[data-client=tricard] .client-logo-wrap,\n[data-client=tricard] .client-logo-box {\n  background: transparent !important;\n  box-shadow: none !important;\n  border: 0 !important;\n  border-radius: 0 !important;\n  padding: 0 !important;\n}\n[data-client=tricard] .client-logo-wrap img,\n[data-client=tricard] .client-logo,\n[data-client=tricard] img.client-logo {\n  content: url('/static/logos/logo-tricard-header-white.png?v=1') !important;\n  filter: none !important;\n}\n[data-client=tricard] .dest-header h1,\n[data-client=tricard] .dest-header h2,\n[data-client=tricard] .dest-header p,\n[data-client=tricard] .dest-header span,\n[data-client=tricard] .client-header h1,\n[data-client=tricard] .client-header h2,\n[data-client=tricard] .client-header p,\n[data-client=tricard] .client-header span,\n[data-client=tricard] .client-header-title,\n[data-client=tricard] .client-header-tagline,\n[data-client=tricard] .client-brand-text {\n  color: #ffffff !important;\n  text-shadow: 0 1px 2px rgba(0, 18, 39, .30) !important;\n}";
  ['codex-tricard-light-header', 'codex-tricard-blue-header'].forEach(function(id) {
    var old = document.getElementById(id);
    if (old) old.remove();
  });
  var style = document.getElementById('codex-tricard-final-header');
  if (!style) {
    style = document.createElement('style');
    style.id = 'codex-tricard-final-header';
    document.head.appendChild(style);
  }
  style.textContent = css;
})();
/* CODEX TRICARD FINAL HEADER END */

/* CODEX BRBDUX NO BLUE RESULT START */
(function () {
  if (typeof detectClient !== 'function' || detectClient() !== 'brbdux') return;
  var css = '[data-client=brbdux] .status-visual-media {\n  background: #000 !important;\n  background-image: none !important;\n  border: 1px solid rgba(255,255,255,.14) !important;\n  box-shadow: none !important;\n}\n[data-client=brbdux] .status-visual-media::before,\n[data-client=brbdux] .status-visual-media::after {\n  display: none !important;\n  opacity: 0 !important;\n  background: none !important;\n}\n[data-client=brbdux] .status-visual-media > *,\n[data-client=brbdux] .status-visual-media .returned-wrap,\n[data-client=brbdux] .status-visual-media .delivered-wrap,\n[data-client=brbdux] .status-visual-media .route-wrap,\n[data-client=brbdux] .status-visual-media .default-wrap {\n  background: #000 !important;\n  background-image: none !important;\n}\n[data-client=brbdux] .status-visual-card {\n  background: #000 !important;\n  background-image: none !important;\n  border: 1px solid rgba(255,255,255,.14) !important;\n  box-shadow: 0 24px 70px rgba(0,0,0,.72) !important;\n}\n[data-client=brbdux] .status-visual-copy {\n  background: #000 !important;\n  background-image: none !important;\n  border: 1px solid rgba(255,255,255,.10) !important;\n}\n[data-client=brbdux] .visual-kicker,\n[data-client=brbdux] .timeline-kicker,\n[data-client=brbdux] .status-visual-card .visual-kicker,\n[data-client=brbdux] .status-visual-card .timeline-kicker {\n  color: rgba(255,255,255,.58) !important;\n}\n[data-client=brbdux] .status-visual-media img,\n[data-client=brbdux] .status-visual-media svg,\n[data-client=brbdux] .status-visual-media canvas {\n  filter: none !important;\n  mix-blend-mode: normal !important;\n}';
  var style = document.getElementById('codex-brbdux-no-blue-result');
  if (!style) {
    style = document.createElement('style');
    style.id = 'codex-brbdux-no-blue-result';
    document.head.appendChild(style);
  }
  style.textContent = css;
})();
/* CODEX BRBDUX NO BLUE RESULT END */

/* CODEX MAIN SIMPLE TIMELINE START */
(function () {
  var css = `
    /* Aplica somente no tema principal, sem data-client */
    body:not([data-client]) .progress-line,
    body:not([data-client]) .progress-line-fill {
      display: none !important;
    }

    body:not([data-client]) #timeline {
      display: flex !important;
      flex-direction: column !important;
      gap: 10px !important;
      grid-template-columns: none !important;
    }

    body:not([data-client]) #timeline .timeline-stage {
      display: grid !important;
      grid-template-columns: 32px 1fr auto !important;
      grid-template-areas:
        "node title time"
        "node desc desc" !important;
      align-items: center !important;
      gap: 4px 12px !important;
      padding: 12px 14px !important;
      border-radius: 14px !important;
      background: rgba(255,255,255,0.045) !important;
      border: 1px solid rgba(255,255,255,0.10) !important;
      text-align: left !important;
    }

    body:not([data-client]) #timeline .timeline-node {
      grid-area: node !important;
      width: 28px !important;
      height: 28px !important;
      min-width: 28px !important;
      border-radius: 999px !important;
      box-shadow: none !important;
      filter: none !important;
    }

    body:not([data-client]) #timeline .timeline-stage h4 {
      grid-area: title !important;
      margin: 0 !important;
      font-size: 14px !important;
      line-height: 1.25 !important;
      font-weight: 700 !important;
    }

    body:not([data-client]) #timeline .timeline-stage time {
      grid-area: time !important;
      margin: 0 !important;
      font-size: 11px !important;
      opacity: 0.58 !important;
      white-space: nowrap !important;
    }

    body:not([data-client]) #timeline .timeline-stage p {
      grid-area: desc !important;
      margin: 0 !important;
      font-size: 12px !important;
      line-height: 1.35 !important;
      opacity: 0.62 !important;
    }

    body:not([data-client]) #timeline .timeline-node-pending .pending-ring {
      display: none !important;
    }

    body:not([data-client]) #timeline .timeline-node-check {
      font-size: 13px !important;
      box-shadow: none !important;
    }

    body:not([data-client]) #timeline .timeline-node-emoji {
      font-size: 15px !important;
    }

    body:not([data-client]) #timeline .timeline-stage.active {
      border-color: rgba(255,255,255,0.22) !important;
      background: rgba(255,255,255,0.07) !important;
    }

    body:not([data-client]) #timeline .timeline-stage.done {
      opacity: 0.88 !important;
    }

    body:not([data-client]) #timeline .timeline-stage.attention {
      border-color: rgba(239,68,68,0.35) !important;
      background: rgba(239,68,68,0.07) !important;
    }

    body:not([data-client]) #timeline .timeline-stage.final {
      border-color: rgba(34,197,94,0.35) !important;
      background: rgba(34,197,94,0.07) !important;
    }
  `;

  var style = document.getElementById('codex-main-simple-timeline');
  if (!style) {
    style = document.createElement('style');
    style.id = 'codex-main-simple-timeline';
    document.head.appendChild(style);
  }

  style.textContent = css;
})();
/* CODEX MAIN SIMPLE TIMELINE END */
