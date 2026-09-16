from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'id="driver-login-module"' in s:
    raise SystemExit('driver login module already present')

module=r'''
<style id="driver-login-styles">
  .driver-app{display:none;min-height:100vh;background:var(--bg);color:var(--text)}.driver-app.authenticated{display:block}
  .driver-topbar{position:sticky;top:0;z-index:25;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:13px 18px;background:#11100ff2;border-bottom:1px solid #ffffff12;backdrop-filter:blur(18px)}
  .driver-topbar-copy strong{display:block;font:800 22px/1 "Barlow Condensed";text-transform:uppercase}.driver-topbar-copy span{display:block;margin-top:4px;color:var(--muted);font-size:10px}
  .driver-main{width:min(920px,100%);margin:auto;padding:24px 16px 80px}.driver-hero{display:flex;align-items:flex-end;justify-content:space-between;gap:14px;margin-bottom:22px}.driver-hero h1{margin:6px 0 5px;font:800 42px/.92 "Barlow Condensed";text-transform:uppercase}.driver-hero p{margin:0;color:var(--muted);font-size:11px}
  .driver-section{margin-top:22px}.driver-section-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:10px}.driver-section-head h2{margin:0;font:800 25px/1 "Barlow Condensed";text-transform:uppercase}.driver-count{min-width:24px;height:24px;display:grid;place-items:center;border-radius:7px;background:var(--panel-3);color:var(--orange-soft);font-size:10px;font-weight:900}
  .driver-order-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.driver-delivery-card{padding:15px;background:var(--panel);border:1px solid var(--line);border-radius:12px}.driver-delivery-card.mine{border-color:#d9f15c50;box-shadow:inset 3px 0 var(--lime)}
  .driver-delivery-top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}.driver-delivery-top strong{color:var(--orange-soft);font-size:12px}.driver-delivery-top span{color:var(--muted);font-size:9px}.driver-customer{margin-top:10px;font-size:15px;font-weight:900}.driver-address{margin-top:5px;color:#d2c7bd;font-size:11px;line-height:1.45}.driver-order-code{margin-top:5px;color:var(--muted);font-size:10px}.driver-delivery-info{display:grid;gap:7px;margin-top:13px;padding-top:12px;border-top:1px solid var(--line);font-size:10px}.driver-delivery-info div{display:flex;justify-content:space-between;gap:10px}.driver-delivery-info span{color:var(--muted)}.driver-delivery-info strong{text-align:right}.driver-delivery-actions{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:13px}.driver-delivery-actions .button{min-width:0;padding:0 9px}.driver-call{display:flex;align-items:center;justify-content:center;gap:7px;min-height:42px;border:1px solid var(--line);border-radius:9px;background:var(--panel-3);font-size:11px;font-weight:900}.driver-call svg{width:14px}.driver-empty{padding:26px 12px;border:1px dashed var(--line);border-radius:11px;color:var(--muted);text-align:center;font-size:11px}
  .driver-pin-help{display:block;margin-top:5px;color:var(--muted);font-size:9px;line-height:1.4}
  @media(max-width:700px){.driver-main{padding:18px 12px 70px}.driver-hero{align-items:flex-start;flex-direction:column}.driver-hero h1{font-size:37px}.driver-hero .button{width:100%}.driver-order-list{grid-template-columns:1fr}.driver-delivery-actions{grid-template-columns:1fr}.driver-topbar{padding:11px 12px}.driver-topbar .button{min-height:38px;padding:0 11px;font-size:10px}}
</style>

<section class="driver-app" id="driver-app">
  <header class="driver-topbar">
    <div class="driver-topbar-copy"><strong>Delivery LV</strong><span id="driver-profile-label">Área do entregador</span></div>
    <button class="button secondary small" id="driver-logout" type="button"><i data-lucide="log-out"></i>Sair</button>
  </header>
  <main class="driver-main">
    <div class="driver-hero"><div><span class="eyebrow">Central de entregas</span><h1>Minhas entregas</h1><p>Veja pedidos disponíveis e acompanhe as entregas que você pegou.</p></div><button class="button secondary" id="driver-refresh" type="button"><i data-lucide="refresh-cw"></i>Atualizar</button></div>
    <section class="driver-section"><div class="driver-section-head"><h2>Disponíveis</h2><span class="driver-count" id="driver-available-count">0</span></div><div class="driver-order-list" id="driver-available-orders"></div></section>
    <section class="driver-section"><div class="driver-section-head"><h2>Comigo agora</h2><span class="driver-count" id="driver-mine-count">0</span></div><div class="driver-order-list" id="driver-my-orders"></div></section>
  </main>
</section>

<script id="driver-login-module">
(()=>{
  const DRIVER_SESSION_KEY='deliverylv_driver_session';
  let loginMode='admin';
  let driverToken=localStorage.getItem(DRIVER_SESSION_KEY)||'';
  let driverProfile=null;
  let driverOrders=[];
  let driverRefreshTimer=null;
  const createDriverClient=token=>window.supabase.createClient(SUPABASE_URL,SUPABASE_PUBLISHABLE_KEY,token?{global:{headers:{'x-driver-session':token}}}:{});
  let driverDb=createDriverClient(driverToken);
  const publicDriverDb=createDriverClient('');
  async function driverAuth(action,{login=null,pin=null}={}){
    const client=action==='login'?publicDriverDb:driverDb;
    const{data,error}=await client.rpc('lv_driver_auth',{p_action:action,p_login:login,p_pin:pin});
    if(error)throw error;return data;
  }

  const loginForm=document.querySelector('#login-form');
  const loginCard=document.querySelector('.login-card');
  const modeBar=document.createElement('div');
  modeBar.className='login-mode';
  modeBar.innerHTML='<button class="login-mode-button active" type="button" data-login-mode="admin">Admin</button><button class="login-mode-button" type="button" data-login-mode="driver">Entregador</button>';
  loginForm.insertAdjacentElement('beforebegin',modeBar);
  const loginTitle=loginCard.querySelector('h1'),loginIntro=loginCard.querySelector('p'),userLabel=document.querySelector('#login-user-field label'),userInput=document.querySelector('#login-user'),passwordLabel=document.querySelector('#login-password-label'),passwordInput=document.querySelector('#login-password'),help=loginCard.querySelector('.login-help');
  loginCard.querySelector('.login-brand small').textContent='CENTRAL DE ACESSO';

  function setLoginMode(mode){
    loginMode=mode;
    modeBar.querySelectorAll('[data-login-mode]').forEach(button=>button.classList.toggle('active',button.dataset.loginMode===mode));
    const driver=mode==='driver';
    loginTitle.textContent=driver?'Entrar como entregador':'Entrar no painel';
    loginIntro.textContent=driver?'Use seu telefone cadastrado e o PIN fornecido pela loja.':'Entre com o e-mail e a senha cadastrados.';
    userLabel.textContent=driver?'Telefone':'E-mail';
    userInput.type=driver?'tel':'email';userInput.inputMode=driver?'tel':'email';userInput.placeholder=driver?'(68) 99999-9999':'Digite o e-mail cadastrado';
    passwordLabel.textContent=driver?'PIN de acesso':'Senha';
    passwordInput.inputMode=driver?'numeric':'';passwordInput.placeholder=driver?'Digite seu PIN':'Digite sua senha';
    help.textContent=driver?'Seu acesso mostra somente as entregas. O PIN é cadastrado pela administração da loja.':'Por segurança, a senha não fica gravada no código do site. Após tentativas incorretas repetidas, o acesso é temporariamente bloqueado.';
    userInput.value='';passwordInput.value='';document.querySelector('#login-message').textContent='';
  }
  modeBar.addEventListener('click',event=>{const button=event.target.closest('[data-login-mode]');if(button)setLoginMode(button.dataset.loginMode)});

  const originalOpenDriverEditor=openDriverEditor;
  openDriverEditor=function(id=null){
    originalOpenDriverEditor(id);
    const form=document.querySelector('#driver-form');if(!form)return;
    const phone=document.querySelector('#driver-phone');phone.required=true;
    const anchor=document.querySelector('.driver-active-row');
    const field=document.createElement('div');field.className='driver-field full';
    field.innerHTML=`<label for="driver-pin">PIN de acesso ${id?'(opcional para trocar)':''}</label><input id="driver-pin" type="password" inputmode="numeric" pattern="[0-9]{4,8}" ${id?'':'required'} placeholder="${id?'Deixe vazio para manter o PIN':'4 a 8 números'}"><small class="driver-pin-help">O entregador entra usando o telefone cadastrado + este PIN. Para trocar o PIN depois, preencha um novo.</small>`;
    anchor.insertAdjacentElement('beforebegin',field);
  };

  saveDriver=async function(event,id=null){
    event.preventDefault();
    const name=document.querySelector('#driver-name').value.trim(),phone=document.querySelector('#driver-phone').value.trim(),pin=document.querySelector('#driver-pin')?.value.trim()||'';
    const digits=phone.replace(/\D/g,'');
    if(name.length<2){showToast('Informe o nome do entregador');return}
    if(digits.length<8||digits.length>15){showToast('Informe um telefone válido');return}
    if(!id&&!/^\d{4,8}$/.test(pin)){showToast('Crie um PIN de 4 a 8 números');return}
    if(pin&&!/^\d{4,8}$/.test(pin)){showToast('O PIN deve ter de 4 a 8 números');return}
    const payload={name,phone,vehicle_type:document.querySelector('#driver-vehicle').value,vehicle_identification:document.querySelector('#driver-identification').value.trim()||null,notes:document.querySelector('#driver-notes').value.trim()||null,active:document.querySelector('#driver-active').checked,updated_at:new Date().toISOString()};
    const button=event.submitter;button.disabled=true;button.textContent='Salvando...';
    try{
      let savedId=id;
      if(id){const{data,error}=await db.from('delivery_drivers').update(payload).eq('id',id).select('id').single();if(error)throw error;savedId=data.id}
      else{const{data,error}=await db.from('delivery_drivers').insert(payload).select('id').single();if(error)throw error;savedId=data.id}
      const{data:access,error:accessError}=await db.rpc('lv_driver_access',{p_driver_id:savedId,p_pin:pin||null});
      if(accessError)throw accessError;if(!access?.ok)throw new Error(access?.message||'Não foi possível configurar o acesso do entregador');
      document.querySelector('#driver-modal').classList.remove('show');await loadDrivers();showToast(id?'Entregador atualizado':'Entregador cadastrado e acesso liberado');
    }catch(error){console.error('Erro ao salvar entregador:',error);showToast(error?.message||'Não foi possível salvar o entregador')}
    finally{button.disabled=false;button.innerHTML=id?'<i data-lucide="save"></i>Salvar alterações':'<i data-lucide="save"></i>Cadastrar entregador';lucide.createIcons()}
  };

  const escapeDriver=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const driverStatusLabel=status=>['delivered','out_for_delivery','delivery'].includes(String(status))?'Saiu para entrega':status==='ready'?'Pronto para sair':status==='completed'?'Finalizado':'Em andamento';
  function driverCard(order,mine=false){
    const phoneDigits=String(order.customer_phone||'').replace(/\D/g,'');
    const needsCode=Boolean(order.delivery_code_required)&&!order.delivery_verified_at;
    const canFinish=mine&&(!order.delivery_code_required||order.delivery_verified_at)&&order.payment_status!=='paid';
    return `<article class="driver-delivery-card ${mine?'mine':''}"><div class="driver-delivery-top"><strong>#${order.id} · ${escapeDriver(order.order_code||'')}</strong><span>${new Date(order.created_at).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}</span></div><div class="driver-customer">${escapeDriver(order.customer_name||'Cliente')}</div><div class="driver-address">${escapeDriver(order.address||'Endereço não informado')}</div><div class="driver-order-code">${driverStatusLabel(order.status)}</div><div class="driver-delivery-info"><div><span>Pagamento</span><strong>${escapeDriver(order.payment_method||'A confirmar')}</strong></div><div><span>Total</span><strong>${money(Number(order.total||0))}</strong></div>${mine?`<div><span>Código</span><strong>${needsCode?'Aguardando cliente':order.delivery_code_required?'Validado':'Não exigido'}</strong></div>`:''}</div><div class="driver-delivery-actions">${mine?(needsCode?`<button class="button" data-driver-action="validate" data-order-id="${order.id}"><i data-lucide="key-round"></i>Validar código</button>`:canFinish?`<button class="button" data-driver-action="finish" data-order-id="${order.id}"><i data-lucide="badge-check"></i>Confirmar pagamento</button>`:''):`<button class="button" data-driver-action="claim" data-order-id="${order.id}"><i data-lucide="bike"></i>Pegar entrega</button>`}${phoneDigits?`<a class="driver-call" href="tel:${phoneDigits}"><i data-lucide="phone"></i>Ligar para cliente</a>`:''}</div></article>`;
  }
  function renderDriverOrders(){
    const mine=driverOrders.filter(order=>String(order.driver_id)===String(driverProfile?.driver_id)&&order.payment_status!=='paid'&&order.status!=='completed');
    const available=driverOrders.filter(order=>!order.driver_id&&['ready','delivered','out_for_delivery','delivery'].includes(String(order.status)));
    document.querySelector('#driver-available-count').textContent=available.length;document.querySelector('#driver-mine-count').textContent=mine.length;
    document.querySelector('#driver-available-orders').innerHTML=available.length?available.map(order=>driverCard(order,false)).join(''):'<div class="driver-empty">Nenhuma entrega disponível agora.</div>';
    document.querySelector('#driver-my-orders').innerHTML=mine.length?mine.map(order=>driverCard(order,true)).join(''):'<div class="driver-empty">Você não está com nenhuma entrega no momento.</div>';
    lucide.createIcons();
  }
  async function loadDriverOrders(){
    const{data,error}=await driverDb.from('orders').select('id,order_code,customer_name,customer_phone,address,payment_method,payment_status,status,total,delivery_code_required,delivery_verified_at,driver_id,driver_assigned_at,created_at').order('created_at',{ascending:false}).order('id',{ascending:false});
    if(error){console.error('Erro ao carregar entregas:',error);if(error.code==='PGRST301')clearDriverSession('Sua sessão terminou.');return}
    const previousAvailable=driverOrders.filter(order=>!order.driver_id).length;driverOrders=data||[];renderDriverOrders();
    const currentAvailable=driverOrders.filter(order=>!order.driver_id).length;if(currentAvailable>previousAvailable&&previousAvailable>=0){try{navigator.vibrate?.(150)}catch(error){}}
  }
  async function enterDriver(profile){
    driverProfile=profile;document.querySelector('#panel-app').classList.remove('authenticated');document.querySelector('#login-screen').style.display='none';document.querySelector('#driver-app').classList.add('authenticated');document.querySelector('#driver-profile-label').textContent=`${profile.name} · ${profile.vehicle_type||'Entregador'}`;
    await loadDriverOrders();if(driverRefreshTimer)clearInterval(driverRefreshTimer);driverRefreshTimer=setInterval(loadDriverOrders,10000);lucide.createIcons();
  }
  async function clearDriverSession(message=''){
    if(driverToken){try{await driverAuth('logout')}catch(error){}}
    if(driverRefreshTimer){clearInterval(driverRefreshTimer);driverRefreshTimer=null}driverToken='';driverProfile=null;driverOrders=[];localStorage.removeItem(DRIVER_SESSION_KEY);driverDb=createDriverClient('');document.querySelector('#driver-app').classList.remove('authenticated');showLogin(message);setLoginMode('driver');
  }
  document.querySelector('#driver-logout').onclick=()=>clearDriverSession();document.querySelector('#driver-refresh').onclick=()=>loadDriverOrders();
  document.querySelector('#driver-app').addEventListener('click',async event=>{
    const button=event.target.closest('[data-driver-action]');if(!button)return;const orderId=Number(button.dataset.orderId);button.disabled=true;
    try{
      if(button.dataset.driverAction==='claim'){
        const{data,error}=await driverDb.rpc('lv_driver_claim_order',{p_order_id:orderId});if(error)throw error;if(!data?.ok)throw new Error(data?.message||'Não foi possível pegar esta entrega');showToast('Entrega adicionada à sua rota');
      }else if(button.dataset.driverAction==='validate'){
        const raw=prompt(`Pedido #${orderId}\nDigite o código de 4 dígitos informado pelo cliente:`);if(raw===null)return;const code=String(raw).trim();if(!/^\d{4}$/.test(code))throw new Error('O código deve ter exatamente 4 dígitos');
        const{data,error}=await driverDb.rpc('lv_driver_confirm_delivery_code',{p_order_id:orderId,p_code:code});if(error)throw error;if(!data?.ok)throw new Error(data?.message||'Código incorreto');showToast('Código de entrega validado');
      }else if(button.dataset.driverAction==='finish'){
        if(!confirm('Confirmar que o pagamento foi recebido e finalizar esta entrega?'))return;
        const{data,error}=await driverDb.rpc('lv_driver_confirm_payment',{p_order_id:orderId});if(error)throw error;if(!data?.ok)throw new Error(data?.message||'Não foi possível finalizar');showToast('Entrega finalizada');
      }
      await loadDriverOrders();
    }catch(error){console.error(error);showToast(error?.message||'Não foi possível concluir a ação')}
    finally{button.disabled=false}
  });

  loginForm.onsubmit=async event=>{
    event.preventDefault();const typedLogin=userInput.value.trim(),secret=passwordInput.value,button=document.querySelector('#login-submit'),status=document.querySelector('#login-message');if(!secret)return;button.disabled=true;status.textContent='Verificando acesso...';status.className='auth-message';
    try{
      if(loginMode==='driver'){
        const result=await driverAuth('login',{login:typedLogin,pin:secret});if(!result?.ok){status.textContent=result?.message||'Telefone ou PIN inválidos.';return}
        driverToken=result.token;localStorage.setItem(DRIVER_SESSION_KEY,driverToken);driverDb=createDriverClient(driverToken);const me=await driverAuth('me');if(!me?.ok)throw new Error(me?.message||'Não foi possível validar a sessão.');status.textContent='';await enterDriver(me);
      }else{
        const login=typedLogin||'jhonata';const result=await panelAuth('login',{login,password:secret});if(!result?.ok){status.textContent=result?.message||'Usuário ou senha inválidos.';return}
        panelToken=result.token;localStorage.setItem(PANEL_SESSION_KEY,panelToken);db=createPanelClient(panelToken);const me=await panelAuth('me');if(!me?.ok)throw new Error(me?.message||'Não foi possível validar a sessão.');status.textContent='';await enterPanel(me);
      }
    }catch(error){console.error('Erro no login:',error);status.textContent='Não foi possível entrar agora. Verifique sua conexão e tente novamente.'}
    finally{button.disabled=false}
  };

  async function restoreDriver(){
    if(panelToken||!driverToken)return;
    try{driverDb=createDriverClient(driverToken);const me=await driverAuth('me');if(!me?.ok){await clearDriverSession('Entre novamente para acessar suas entregas.');return}await enterDriver(me)}catch(error){console.error('Erro ao restaurar entregador:',error);await clearDriverSession('Entre novamente para acessar suas entregas.')}
  }
  restoreDriver();
})();
</script>
'''

s=s.replace('</body>',module+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('driver login module appended')
