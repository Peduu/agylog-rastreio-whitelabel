(function(){
  const input=document.getElementById('pedidoInput'), button=document.getElementById('consultarBtn'), alertBox=document.getElementById('alertBox'), result=document.getElementById('resultArea'), nameBox=document.getElementById('nameValidation'), nameInput=document.getElementById('nomeInput'), nameHint=document.getElementById('nomeHint');
  const esc=v=>String(v??'-').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function render(data){
    document.getElementById('pedidoCode').textContent=data.pedido||input.value.trim();
    document.getElementById('statusPill').textContent=data.status_label||'-';
    document.getElementById('statusTitle').textContent=data.status_label||'Acompanhamento da entrega';
    document.getElementById('statusMessage').textContent='Confira abaixo as atualizações mais recentes do seu pedido.';
    let stages=Array.isArray(data.stages)?[...data.stages]:[];
    const problemKeys=['atencao','devolucao','devolvido'];
    const isProblemFlow=problemKeys.includes(data.status);
    if(!isProblemFlow) stages=stages.filter(s=>!problemKeys.includes(s.key)||(s.done&&s.date&&s.date!=='-'));
    let activeIndex=stages.findIndex(s=>s.key===data.status);
    if(activeIndex<0){activeIndex=Math.max(0,stages.filter(s=>s.done).length-1)}
    const isAtencao=data.status==='atencao';
    if(isAtencao&&stages[activeIndex+1]) stages[activeIndex+1]={...stages[activeIndex+1],done:false,date:'-',time:''};
    stages=stages.filter((s,i)=>i<=activeIndex||s.done||(isAtencao&&i===activeIndex+1));
    activeIndex=Math.max(0,stages.findIndex(s=>s.key===data.status));
    const timeline=document.getElementById('timeline'), fill=document.getElementById('progressFill');
    timeline.style.gridTemplateColumns=`repeat(${Math.max(stages.length,1)},minmax(105px,1fr))`;
    fill.style.transform=`scaleX(${stages.length>1?activeIndex/(stages.length-1):0})`;
    timeline.innerHTML=stages.map((s,i)=>{const done=Boolean(s.done)||i<activeIndex, active=i===activeIndex;return `<article class="timeline-stage ${done?'done':''} ${active?'active':''} ${s.key==='entregue'?'final':''}"><div class="timeline-node">${done?'<span class="timeline-node-check">✓</span>':active?`<span class="timeline-node-emoji">${esc(s.icon||'•')}</span>`:'<span class="timeline-node-pending">•</span>'}</div><h4>${esc(s.title||'Etapa')}</h4><time>${esc(s.time?`${s.date} · ${s.time}`:(s.date||'-'))}</time><p>${esc(s.desc||'')}</p></article>`}).join('');
    document.getElementById('historyList').innerHTML=(data.history||[]).map(h=>`<div class="history-item"><strong>${esc(h.title||h.status||'Atualização')}</strong><p>${esc(h.desc||h.description||h.when||h.date||'')}</p></div>`).join('')||'<p>Sem atualizações adicionais.</p>';
    result.classList.remove('hidden'); result.scrollIntoView({behavior:'smooth',block:'start'});
  }
  async function carregarDica(){
    const codigo=input.value.trim(); nameBox.classList.add('hidden'); nameHint.textContent='-';
    if(!codigo) return;
    try{const r=await fetch(`/api/rastrear/simplecompany/dica?codigo=${encodeURIComponent(codigo)}`);const data=await r.json();if(!r.ok)throw new Error(data.error||'Pedido não encontrado.');nameHint.textContent=data.nome_mascarado;nameBox.classList.remove('hidden');nameInput.focus()}catch(e){alertBox.textContent=e.message}
  }
  async function consultar(){
    const codigo=input.value.trim(), nome=nameInput.value.trim(); alertBox.textContent=''; if(!codigo){alertBox.textContent='Informe o número do pedido.';return}
    if(nameBox.classList.contains('hidden')){await carregarDica();return}
    if(!nome){alertBox.textContent='Digite o nome completo do destinatário.';nameInput.focus();return}
    button.disabled=true; button.textContent='Consultando...'; result.classList.add('hidden');
    try{const r=await fetch('/api/rastrear/simplecompany',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({codigo,nome})});const data=await r.json();if(!r.ok)throw new Error(data.error||'Pedido não encontrado.');render(data)}catch(e){alertBox.textContent=e.message}finally{button.disabled=false;button.textContent='Consultar pedido'}
  }
  button.addEventListener('click',consultar); input.addEventListener('blur',carregarDica); input.addEventListener('keydown',e=>{if(e.key==='Enter')consultar()}); document.getElementById('novaBuscaBtn').addEventListener('click',()=>{input.value='';nameInput.value='';nameBox.classList.add('hidden');input.focus();result.classList.add('hidden')});
  if(input.value.trim()) carregarDica();
})();
