from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Styles: append late in <head> so the 6-column mobile nav overrides earlier rules.
styles=r'''
  <style>
    .drivers-table{overflow:hidden;background:var(--panel);border:1px solid var(--line);border-radius:12px}
    .drivers-table .driver-head,.drivers-table .driver-row{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr .7fr auto;align-items:center;gap:14px;padding:14px 17px}
    .drivers-table .driver-head{background:#211e1b;color:var(--muted);font-size:10px;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
    .drivers-table .driver-row{border-top:1px solid var(--line);font-size:12px}
    .driver-copy strong{display:block}.driver-copy small{display:block;margin-top:3px;color:var(--muted);font-size:10px}
    .driver-status{display:inline-flex;width:max-content;padding:5px 8px;border-radius:6px;background:#26331e;color:var(--lime);font-size:10px;font-weight:800}.driver-status.off{background:#302b27;color:var(--muted)}
    .driver-edit{width:35px;height:35px;display:grid;place-items:center;border-radius:8px;background:var(--panel-3);border:1px solid var(--line)}.driver-edit:hover{border-color:var(--orange)}.driver-edit svg{width:15px}
    .driver-form-grid{display:grid;grid-template-columns:1fr 1fr;gap:13px}.driver-field{display:grid;gap:6px}.driver-field.full{grid-column:1/-1}.driver-field label{color:var(--muted);font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.06em}.driver-field input,.driver-field select,.driver-field textarea{width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:9px;background:var(--panel-2);color:var(--text);font:inherit}.driver-field textarea{min-height:80px;resize:vertical}.driver-active-row{display:flex;align-items:center;justify-content:space-between;gap:15px;margin-top:16px;padding:13px;background:var(--panel-2);border:1px solid var(--line);border-radius:10px}.driver-active-row strong{display:block;font-size:12px}.driver-active-row small{display:block;margin-top:3px;color:var(--muted);font-size:10px}
    @media(max-width:700px){.nav{grid-template-columns:repeat(6,1fr)}.nav-item{padding:9px 2px}.nav-item span{font-size:7px}.drivers-table{overflow-x:auto}.drivers-table .driver-head,.drivers-table .driver-row{min-width:670px}.driver-form-grid{grid-template-columns:1fr}}
  </style>
'''
if '</head>' not in s: raise SystemExit('head marker not found')
s=s.replace('</head>',styles+'</head>',1)

# Sidebar navigation.
old='<button class="nav-item" data-view="menu"><i data-lucide="book-open"></i><span>Cardápio</span></button><button class="nav-item" data-view="history"><i data-lucide="archive"></i><span>Histórico</span></button>'
new='<button class="nav-item" data-view="menu"><i data-lucide="book-open"></i><span>Cardápio</span></button><button class="nav-item" data-view="drivers"><i data-lucide="bike"></i><span>Entregadores</span></button><button class="nav-item" data-view="history"><i data-lucide="archive"></i><span>Histórico</span></button>'
if old not in s: raise SystemExit('nav marker not found')
s=s.replace(old,new,1)

# Drivers view before history.
history_marker='<section class="view" id="view-history">'
drivers_view='''<section class="view" id="view-drivers"><div class="page-head"><div><span class="eyebrow">Equipe de entrega</span><h1>Entregadores</h1><p>Cadastre e mantenha atualizados os entregadores disponíveis da loja.</p></div><div class="head-actions"><button class="button" data-add-driver type="button"><i data-lucide="user-plus"></i>Adicionar entregador</button><button class="button secondary" data-refresh-drivers type="button"><i data-lucide="refresh-cw"></i>Atualizar</button></div></div><div class="drivers-table" id="drivers-table"><div class="empty-column">Carregando entregadores...</div></div></section>\n        '''
if history_marker not in s: raise SystemExit('history view marker not found')
s=s.replace(history_marker,drivers_view+history_marker,1)

# Driver modal before product modal.
modal_marker='<div class="modal-layer" id="product-edit-modal">'
driver_modal='''<div class="modal-layer" id="driver-modal"><div class="modal"><div class="modal-head"><h2 id="driver-modal-title">Entregador</h2><button class="close" data-close-driver-modal type="button" aria-label="Fechar"><i data-lucide="x"></i></button></div><div id="driver-modal-content"></div></div></div>\n    '''
if modal_marker not in s: raise SystemExit('modal marker not found')
s=s.replace(modal_marker,driver_modal+modal_marker,1)

# Driver CRUD logic.
js=r'''
  let deliveryDrivers=[];
  async function loadDrivers(){
    const target=document.querySelector('#drivers-table');if(!target)return;
    const{data,error}=await db.from('delivery_drivers').select('id,name,phone,vehicle_type,vehicle_identification,notes,active,created_at,updated_at').order('active',{ascending:false}).order('name');
    if(error){console.error('Erro ao carregar entregadores:',error);target.innerHTML='<div class="empty-column">Não foi possível carregar os entregadores.</div>';showToast('Erro ao carregar entregadores');return}
    deliveryDrivers=data||[];renderDrivers();
  }
  function renderDrivers(){
    const target=document.querySelector('#drivers-table');if(!target)return;
    target.innerHTML='<div class="driver-head"><span>Entregador</span><span>Telefone</span><span>Veículo</span><span>Identificação</span><span>Status</span><span></span></div>'+
      (deliveryDrivers.length?deliveryDrivers.map(driver=>`<div class="driver-row"><div class="driver-copy"><strong>${escapeMenuText(driver.name||'')}</strong><small>${driver.notes?escapeMenuText(driver.notes):'Sem observação'}</small></div><span>${escapeMenuText(driver.phone||'-')}</span><span>${escapeMenuText(driver.vehicle_type||'-')}</span><span>${escapeMenuText(driver.vehicle_identification||'-')}</span><span class="driver-status ${driver.active===false?'off':''}">${driver.active===false?'Inativo':'Ativo'}</span><button class="driver-edit" type="button" data-edit-driver="${driver.id}" aria-label="Editar entregador"><i data-lucide="pencil"></i></button></div>`).join(''):'<div class="empty-column" style="padding:30px">Nenhum entregador cadastrado ainda.</div>');
    lucide.createIcons();
  }
  function openDriverEditor(id=null){
    const driver=id?deliveryDrivers.find(item=>String(item.id)===String(id)):null;
    document.querySelector('#driver-modal-title').textContent=driver?'Editar entregador':'Adicionar entregador';
    document.querySelector('#driver-modal-content').innerHTML=`<form id="driver-form"><div class="driver-form-grid"><div class="driver-field full"><label for="driver-name">Nome</label><input id="driver-name" maxlength="120" required value="${escapeMenuText(driver?.name||'')}" placeholder="Nome do entregador"></div><div class="driver-field"><label for="driver-phone">Telefone</label><input id="driver-phone" maxlength="30" inputmode="tel" value="${escapeMenuText(driver?.phone||'')}" placeholder="(68) 99999-9999"></div><div class="driver-field"><label for="driver-vehicle">Veículo</label><select id="driver-vehicle"><option ${driver?.vehicle_type==='Moto'?'selected':''}>Moto</option><option ${driver?.vehicle_type==='Carro'?'selected':''}>Carro</option><option ${driver?.vehicle_type==='Bicicleta'?'selected':''}>Bicicleta</option><option ${driver?.vehicle_type==='Outro'?'selected':''}>Outro</option></select></div><div class="driver-field full"><label for="driver-identification">Placa / identificação</label><input id="driver-identification" maxlength="80" value="${escapeMenuText(driver?.vehicle_identification||'')}" placeholder="Ex.: ABC1D23, Moto preta, Bike 02"></div><div class="driver-field full"><label for="driver-notes">Observações</label><textarea id="driver-notes" maxlength="500" placeholder="Informação opcional">${escapeMenuText(driver?.notes||'')}</textarea></div></div><label class="driver-active-row" for="driver-active"><span><strong>Entregador ativo</strong><small>Desative quando ele não trabalhar mais com a loja.</small></span><input id="driver-active" type="checkbox" ${driver?.active===false?'':'checked'}></label><div class="modal-actions"><button class="button" type="submit"><i data-lucide="save"></i>${driver?'Salvar alterações':'Cadastrar entregador'}</button><button class="button secondary" type="button" data-close-driver-modal>Cancelar</button></div></form>`;
    document.querySelector('#driver-form').onsubmit=event=>saveDriver(event,driver?.id||null);
    document.querySelector('#driver-modal').classList.add('show');lucide.createIcons();
  }
  async function saveDriver(event,id=null){
    event.preventDefault();
    const name=document.querySelector('#driver-name').value.trim();
    if(name.length<2){showToast('Informe o nome do entregador');return}
    const payload={name,phone:document.querySelector('#driver-phone').value.trim()||null,vehicle_type:document.querySelector('#driver-vehicle').value,vehicle_identification:document.querySelector('#driver-identification').value.trim()||null,notes:document.querySelector('#driver-notes').value.trim()||null,active:document.querySelector('#driver-active').checked,updated_at:new Date().toISOString()};
    const button=event.submitter;button.disabled=true;
    const result=id?await db.from('delivery_drivers').update(payload).eq('id',id):await db.from('delivery_drivers').insert(payload);
    if(result.error){console.error('Erro ao salvar entregador:',result.error);showToast(result.error.message||'Não foi possível salvar o entregador');button.disabled=false;return}
    document.querySelector('#driver-modal').classList.remove('show');await loadDrivers();showToast(id?'Entregador atualizado':'Entregador cadastrado');
  }
'''
marker='  function orderCard(order){'
if marker not in s: raise SystemExit('orderCard marker not found')
s=s.replace(marker,js+marker,1)

# Load driver data when opening the view.
old="if(view==='orders')renderBoard('orders-board');if(view==='menu')loadRealMenu();window.scrollTo"
new="if(view==='orders')renderBoard('orders-board');if(view==='menu')loadRealMenu();if(view==='drivers')loadDrivers();window.scrollTo"
if old not in s: raise SystemExit('switchView marker not found')
s=s.replace(old,new,1)

# Driver view events, inserted after the product editor listener.
old="  document.querySelector('#history-search')?.addEventListener('input',event=>{historySearch=event.target.value;renderHistory()});"
new="""  document.addEventListener('click',event=>{\n    const addDriver=event.target.closest('[data-add-driver]');if(addDriver){openDriverEditor();return}\n    const editDriver=event.target.closest('[data-edit-driver]');if(editDriver){openDriverEditor(editDriver.dataset.editDriver);return}\n    if(event.target.closest('[data-refresh-drivers]')){loadDrivers();return}\n    if(event.target.closest('[data-close-driver-modal]')||event.target.id==='driver-modal')document.querySelector('#driver-modal').classList.remove('show');\n  });\n  document.querySelector('#history-search')?.addEventListener('input',event=>{historySearch=event.target.value;renderHistory()});"""
if old not in s: raise SystemExit('history listener marker not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('drivers tab patched')
