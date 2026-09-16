from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# 1) Store open/closed control UI.
if 'store-control-styles' not in s:
    styles='''\n<style id="store-control-styles">\n  .store-toggle.store-open{border-color:#d9f15c88;color:var(--lime);background:#26311d}\n  .store-toggle.store-closed{border-color:#ff8f7988;color:#ffb2a3;background:#3b211b}\n  @media(max-width:760px){.store-toggle span{display:none}.store-toggle{width:38px;padding:0}}\n</style>\n'''
    s=s.replace('</head>',styles+'</head>',1)

old='<span class="top-status"><i class="live-dot"></i>Operação ativa</span><button class="button secondary small lv-alert-toggle" data-enable-alerts type="button"><i data-lucide="bell-ring"></i><span>Ativar alertas</span></button>'
new='<span class="top-status"><i class="live-dot"></i>Operação ativa</span><button class="button secondary small store-toggle" id="store-toggle-button" type="button" title="Alterar status da loja"><i data-lucide="store"></i><span>Carregando loja...</span></button><button class="button secondary small lv-alert-toggle" data-enable-alerts type="button"><i data-lucide="bell-ring"></i><span>Ativar alertas</span></button>'
if old not in s: raise SystemExit('topbar marker not found')
s=s.replace(old,new,1)

# 2) Escape customer-controlled content in admin HTML.
repls={
'<span class="order-number">#${order.id} · ${order.orderCode||\'Sem código\'}</span>':'<span class="order-number">#${order.id} · ${escapeMenuText(order.orderCode||\'Sem código\')}</span>',
'<div class="customer">${order.customer}</div>':'<div class="customer">${escapeMenuText(order.customer)}</div>',
'<strong>${item.qty}x ${item.name}</strong>${item.detail?`<span>- ${item.detail}</span>`:\'\'}':'<strong>${item.qty}x ${escapeMenuText(item.name)}</strong>${item.detail?`<span>- ${escapeMenuText(item.detail)}</span>`:\'\'}',
'<div class="info-line"><span>Pagamento</span><strong>${order.payment}</strong></div>':'<div class="info-line"><span>Pagamento</span><strong>${escapeMenuText(order.payment)}</strong></div>',
'<strong>Pedido #${order.id} · ${order.orderCode||\'Sem código\'} · ${statusMeta[order.status].label}</strong><span>${order.customer} · ${order.time} · ${order.type}</span>':'<strong>Pedido #${order.id} · ${escapeMenuText(order.orderCode||\'Sem código\')} · ${statusMeta[order.status].label}</strong><span>${escapeMenuText(order.customer)} · ${order.time} · ${escapeMenuText(order.type)}</span>',
'<strong>${text}</strong><span>Central de pedidos</span>':'<strong>${escapeMenuText(text)}</strong><span>Central de pedidos</span>'
}
for old_text,new_text in repls.items():
    if old_text not in s: raise SystemExit('xss marker not found: '+old_text[:80])
    s=s.replace(old_text,new_text)

# 3) Real history dates + escaped customer/code.
marker='  function renderHistory(){'
if marker not in s: raise SystemExit('renderHistory marker not found')
if 'formatHistoryDate' not in s:
    helper="  const formatHistoryDate=value=>{try{return new Intl.DateTimeFormat('pt-BR',{timeZone:'America/Rio_Branco',day:'2-digit',month:'2-digit',year:'numeric'}).format(new Date(value))}catch{return'--/--/----'}};\n"
    s=s.replace(marker,helper+marker,1)

old_hist='<span><strong>#${order.id}</strong><small>${order.orderCode||\'Sem código\'}</small></span><span>${order.customer}</span><span>Hoje<small>${order.time}</small></span>'
new_hist='<span><strong>#${order.id}</strong><small>${escapeMenuText(order.orderCode||\'Sem código\')}</small></span><span>${escapeMenuText(order.customer)}</span><span>${formatHistoryDate(order.createdAt)}<small>${order.time}</small></span>'
if old_hist not in s: raise SystemExit('history row marker not found')
s=s.replace(old_hist,new_hist,1)

old_csv="csv=['Pedido,Cliente,Horário,Total,Status',...rows.map(order=>[order.id,order.customer,order.time,order.total,statusMeta[order.status].label]"
new_csv="csv=['Pedido,Cliente,Data/Horário,Total,Status',...rows.map(order=>[order.id,order.customer,`${formatHistoryDate(order.createdAt)} ${order.time}`,order.total,statusMeta[order.status].label]"
if old_csv not in s: raise SystemExit('history CSV marker not found')
s=s.replace(old_csv,new_csv,1)

# 4) Store status logic tied to authenticated custom panel session.
init_marker='  async function initPanel(){\n'
if init_marker not in s: raise SystemExit('initPanel marker not found')
store_logic='''  let storeIsOpen=false;\n  function renderStoreStatus(){\n    const button=document.querySelector('#store-toggle-button');if(!button)return;\n    button.classList.toggle('store-open',storeIsOpen);button.classList.toggle('store-closed',!storeIsOpen);\n    const span=button.querySelector('span');if(span)span.textContent=storeIsOpen?'Loja aberta':'Loja fechada';\n    button.title=storeIsOpen?'Fechar loja para novos pedidos':'Abrir loja para novos pedidos';\n    if(window.lucide)lucide.createIcons();\n  }\n  async function loadStoreStatus(){\n    const{data,error}=await db.from('store_settings').select('is_open').eq('id',1).single();\n    if(error){console.error('Erro ao carregar status da loja:',error);showToast('Não foi possível ler o status da loja');return false}\n    storeIsOpen=Boolean(data?.is_open);renderStoreStatus();return true;\n  }\n  async function toggleStoreStatus(){\n    const button=document.querySelector('#store-toggle-button');if(!button)return;button.disabled=true;\n    const next=!storeIsOpen;\n    try{\n      const{data,error}=await db.from('store_settings').update({is_open:next,updated_at:new Date().toISOString()}).eq('id',1).select('is_open').single();\n      if(error)throw error;storeIsOpen=Boolean(data?.is_open);renderStoreStatus();showToast(storeIsOpen?'Loja aberta para novos pedidos':'Loja fechada para novos pedidos');\n    }catch(error){console.error('Erro ao alterar status da loja:',error);showToast('Não foi possível alterar o status da loja')}\n    finally{button.disabled=false}\n  }\n  document.querySelector('#store-toggle-button')?.addEventListener('click',toggleStoreStatus);\n\n'''
if 'async function toggleStoreStatus()' not in s:
    s=s.replace(init_marker,store_logic+init_marker,1)

old_init='  async function initPanel(){\n    await loadDailyCosts();'
new_init='  async function initPanel(){\n    await loadStoreStatus();\n    await loadDailyCosts();'
if old_init not in s: raise SystemExit('initPanel load marker not found')
s=s.replace(old_init,new_init,1)

# Final validation.
checks=[
    'id="store-toggle-button"',
    'async function toggleStoreStatus()',
    'escapeMenuText(order.customer)',
    'escapeMenuText(item.detail)',
    'formatHistoryDate(order.createdAt)',
    "db.from('store_settings').update",
]
for check in checks:
    if check not in s: raise SystemExit('missing final marker: '+check)
if '<span>Hoje<small>${order.time}</small></span>' in s:
    raise SystemExit('old fake history date remains')

p.write_text(s,encoding='utf-8')
print('admin production hardening applied')
