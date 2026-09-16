from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Admin alert button
old='<div class="top-right"><span class="top-status"><i class="live-dot"></i>Operação ativa</span><button class="button secondary small" id="switch-login-button" type="button"><i data-lucide="log-in"></i>Trocar acesso</button><button class="user" id="account-button" type="button" aria-label="Abrir conta">'
new='<div class="top-right"><span class="top-status"><i class="live-dot"></i>Operação ativa</span><button class="button secondary small lv-alert-toggle" data-enable-alerts type="button"><i data-lucide="bell-ring"></i><span>Ativar alertas</span></button><button class="button secondary small" id="switch-login-button" type="button"><i data-lucide="log-in"></i>Trocar acesso</button><button class="user" id="account-button" type="button" aria-label="Abrir conta">'
if old not in s: raise SystemExit('admin topbar marker not found')
s=s.replace(old,new,1)

# Driver alert button
old='<div class="driver-topbar-copy"><strong>Delivery LV</strong><span id="driver-profile-label">Área do entregador</span></div>\n    <button class="button secondary small" id="driver-logout" type="button"><i data-lucide="arrow-left-right"></i>Trocar acesso</button>'
new='<div class="driver-topbar-copy"><strong>Delivery LV</strong><span id="driver-profile-label">Área do entregador</span></div>\n    <div class="driver-topbar-actions"><button class="button secondary small lv-alert-toggle" data-enable-alerts type="button"><i data-lucide="bell-ring"></i><span>Ativar alertas</span></button><button class="button secondary small" id="driver-logout" type="button"><i data-lucide="arrow-left-right"></i>Trocar acesso</button></div>'
if old not in s: raise SystemExit('driver topbar marker not found')
s=s.replace(old,new,1)

# Driver history section
old='''    <section class="driver-section"><div class="driver-section-head"><h2>Comigo agora</h2><span class="driver-count" id="driver-mine-count">0</span></div><div class="driver-order-list" id="driver-my-orders"></div></section>\n  </main>'''
new='''    <section class="driver-section"><div class="driver-section-head"><h2>Comigo agora</h2><span class="driver-count" id="driver-mine-count">0</span></div><div class="driver-order-list" id="driver-my-orders"></div></section>\n    <section class="driver-section driver-history-section"><div class="driver-section-head"><div><span class="eyebrow">Entregas concluídas</span><h2>Histórico</h2></div><span class="driver-count" id="driver-history-count">0</span></div><div class="driver-order-list" id="driver-history-orders"></div></section>\n  </main>'''
if old not in s: raise SystemExit('driver history marker not found')
s=s.replace(old,new,1)

# Add alert module before main app script
marker="\n<script>\n  const SUPABASE_URL="
if marker not in s: raise SystemExit('main script marker not found')
alert_module=r'''
<style id="lv-alert-styles">
  .notification.show{pointer-events:auto}
  .lv-alert-toggle{white-space:nowrap}
  .lv-alert-toggle.alerts-on{border-color:#d9f15c66;color:var(--lime)}
  .lv-urgent-alert{position:fixed;z-index:120;left:50%;top:14px;transform:translateX(-50%);width:min(520px,calc(100vw - 24px));display:flex;align-items:center;gap:12px;padding:14px 15px;background:#2b190f;border:1px solid #ff5a16aa;border-radius:13px;box-shadow:0 18px 55px #000a;animation:lv-alert-in .24s ease}
  .lv-urgent-alert-icon{width:40px;height:40px;flex:none;display:grid;place-items:center;border-radius:10px;background:var(--orange);color:#1b110b}.lv-urgent-alert-icon svg{width:20px}
  .lv-urgent-alert-copy{min-width:0;flex:1}.lv-urgent-alert-copy strong{display:block;font-size:13px}.lv-urgent-alert-copy span{display:block;margin-top:3px;color:#d4c5b9;font-size:10px;line-height:1.4}
  .lv-urgent-alert button{min-height:34px;padding:0 11px;border-radius:8px;background:var(--panel-3);border:1px solid var(--line);font-size:10px;font-weight:900}
  .driver-topbar-actions{display:flex;align-items:center;gap:7px}.driver-history-section{padding-top:6px;border-top:1px solid #ffffff10}.driver-history-section .driver-section-head{align-items:flex-end}
  .driver-delivery-card.history{opacity:.92;border-color:#ffffff12;box-shadow:none}.driver-delivery-card.history .driver-customer{margin-top:8px}.driver-history-date{margin-top:5px;color:var(--muted);font-size:9px}
  @keyframes lv-alert-in{from{opacity:0;transform:translate(-50%,-10px)}to{opacity:1;transform:translate(-50%,0)}}
  @media(max-width:700px){.lv-alert-toggle span{display:none}.lv-alert-toggle{min-width:38px;padding:0 9px}.driver-topbar-actions{gap:5px}.lv-urgent-alert{top:8px}.lv-urgent-alert button{padding:0 9px}}
</style>
<script id="lv-alert-module">
window.LVAlerts=(()=>{
  const timers=new Map();let audioCtx=null;let swRegistration=null;
  const getAudio=()=>{try{const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return null;if(!audioCtx)audioCtx=new AC();if(audioCtx.state==='suspended')audioCtx.resume().catch(()=>{});return audioCtx}catch(error){return null}};
  function beep(){const ctx=getAudio();if(!ctx)return;try{const now=ctx.currentTime;[0,.18].forEach((offset,index)=>{const osc=ctx.createOscillator(),gain=ctx.createGain();osc.type='sine';osc.frequency.value=index?720:920;gain.gain.setValueAtTime(.0001,now+offset);gain.gain.exponentialRampToValueAtTime(.18,now+offset+.02);gain.gain.exponentialRampToValueAtTime(.0001,now+offset+.16);osc.connect(gain);gain.connect(ctx.destination);osc.start(now+offset);osc.stop(now+offset+.18)})}catch(error){}}
  function vibrate(){try{navigator.vibrate?.([260,120,260,120,420])}catch(error){}}
  async function ensureSw(){if(swRegistration)return swRegistration;if(!('serviceWorker' in navigator))return null;try{swRegistration=await navigator.serviceWorker.register('./notification-sw.js',{scope:'./'});return swRegistration}catch(error){console.warn('Service Worker de alerta indisponível',error);return null}}
  async function systemNotify(title,body,tag){if(!('Notification' in window)||Notification.permission!=='granted')return;try{const reg=await ensureSw();if(reg?.showNotification){await reg.showNotification(title,{body,tag,renotify:true,vibrate:[250,120,250],icon:'./icon-192.png'});return}new Notification(title,{body,tag})}catch(error){console.warn('Notificação do sistema indisponível',error)}}
  function banner(key,title,body){document.querySelectorAll('.lv-urgent-alert').forEach(node=>node.remove());const node=document.createElement('div');node.className='lv-urgent-alert';node.dataset.alertKey=key;node.innerHTML=`<div class="lv-urgent-alert-icon"><i data-lucide="bell-ring"></i></div><div class="lv-urgent-alert-copy"><strong>${String(title).replace(/[<>]/g,'')}</strong><span>${String(body).replace(/[<>]/g,'')}</span></div><button type="button" data-lv-alert-dismiss="${key}">OK</button>`;document.body.appendChild(node);window.lucide?.createIcons()}
  function pulse(title,body,tag,withSystem=false){beep();vibrate();if(withSystem)systemNotify(title,body,tag)}
  function stop(key){const timer=timers.get(key);if(timer)clearInterval(timer);timers.delete(key);document.querySelector(`.lv-urgent-alert[data-alert-key="${CSS.escape(key)}"]`)?.remove()}
  function start(key,title,body,{repeats=8,interval=6000}={}){stop(key);banner(key,title,body);pulse(title,body,key,true);let count=1;const timer=setInterval(()=>{count+=1;if(count>repeats){stop(key);return}pulse(title,body,key,false)},interval);timers.set(key,timer)}
  function updateButtons(){const granted=('Notification' in window)&&Notification.permission==='granted';document.querySelectorAll('[data-enable-alerts]').forEach(button=>{button.classList.toggle('alerts-on',granted);const span=button.querySelector('span');if(span)span.textContent=granted?'Alertas ativos':'Ativar alertas';button.title=granted?'Som, vibração e notificações ativados':'Ativar som, vibração e notificações'})}
  async function enable(){getAudio();await ensureSw();if('Notification' in window&&Notification.permission==='default'){try{await Notification.requestPermission()}catch(error){}}updateButtons();beep();vibrate()}
  document.addEventListener('pointerdown',()=>getAudio(),{once:true,capture:true});
  document.addEventListener('click',event=>{const enableButton=event.target.closest('[data-enable-alerts]');if(enableButton){enable();return}const dismiss=event.target.closest('[data-lv-alert-dismiss]');if(dismiss)stop(dismiss.dataset.lvAlertDismiss)});
  window.addEventListener('load',()=>{ensureSw();updateButtons()});
  return{start,stop,enable,prime:getAudio,updateButtons};
})();
</script>
'''
s=s.replace(marker,"\n"+alert_module+marker,1)

# Strong admin alert when a fresh order arrives
old="notice.classList.add('show');}}"
new="notice.classList.add('show');window.LVAlerts?.start('admin-new-order','Novo pedido recebido',`Pedido #${latest.id} · ${latest.orderCode||'Sem código'} de ${latest.customer}`,{repeats:8,interval:6000});}}"
if old not in s: raise SystemExit('admin fresh alert marker not found')
s=s.replace(old,new,1)

# Stop admin alert when notice is acknowledged
old="document.querySelector('#close-notice').onclick=()=>document.querySelector('#notification').classList.remove('show');"
new="document.querySelector('#close-notice').onclick=()=>{document.querySelector('#notification').classList.remove('show');window.LVAlerts?.stop('admin-new-order')};"
if old not in s: raise SystemExit('close notice marker not found')
s=s.replace(old,new,1)

# Faster fallback polling for admin
s=s.replace("window.setInterval(()=>loadRealOrders(),10000)","window.setInterval(()=>loadRealOrders(),5000)",1)

# Driver state for alerts
old="let driverOrders=[];\n  let driverRefreshTimer=null;"
new="let driverOrders=[];\n  let driverRefreshTimer=null;\n  let driverKnownAvailableIds=new Set();\n  let driverAlertsReady=false;"
if old not in s: raise SystemExit('driver state marker not found')
s=s.replace(old,new,1)

# Replace driver rendering with history support
pattern=r"  function renderDriverOrders\(\)\{.*?\n  async function loadDriverOrders\(\)\{"
replacement=r'''  function driverHistoryCard(order){
    const when=order.finished_at||order.paid_at||order.created_at;
    const date=when?new Date(when).toLocaleString('pt-BR',{day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'}):'Data não informada';
    return `<article class="driver-delivery-card history"><div class="driver-delivery-top"><strong>#${order.id} · ${escapeDriver(order.order_code||'')}</strong><span>Finalizada</span></div><div class="driver-customer">${escapeDriver(order.customer_name||'Cliente')}</div><div class="driver-history-date">${date}</div><div class="driver-delivery-info"><div><span>Pagamento</span><strong>${escapeDriver(order.payment_method||'')}</strong></div><div><span>Total</span><strong>${money(Number(order.total||0))}</strong></div></div></article>`;
  }
  function renderDriverOrders(){
    const mine=driverOrders.filter(order=>String(order.driver_id)===String(driverProfile?.driver_id)&&order.payment_status!=='paid'&&order.status!=='completed');
    const available=driverOrders.filter(order=>!order.driver_id&&['ready','delivered','out_for_delivery','delivery'].includes(String(order.status)));
    const history=driverOrders.filter(order=>String(order.driver_id)===String(driverProfile?.driver_id)&&(order.payment_status==='paid'||order.status==='completed')).sort((a,b)=>new Date(b.finished_at||b.paid_at||b.created_at)-new Date(a.finished_at||a.paid_at||a.created_at));
    document.querySelector('#driver-available-count').textContent=available.length;document.querySelector('#driver-mine-count').textContent=mine.length;document.querySelector('#driver-history-count').textContent=history.length;
    document.querySelector('#driver-available-orders').innerHTML=available.length?available.map(order=>driverCard(order,false)).join(''):'<div class="driver-empty">Nenhuma entrega disponível agora.</div>';
    document.querySelector('#driver-my-orders').innerHTML=mine.length?mine.map(order=>driverCard(order,true)).join(''):'<div class="driver-empty">Você não está com nenhuma entrega no momento.</div>';
    document.querySelector('#driver-history-orders').innerHTML=history.length?history.map(driverHistoryCard).join(''):'<div class="driver-empty">Nenhuma entrega concluída por você ainda.</div>';
    lucide.createIcons();
  }
  async function loadDriverOrders(){'''
s,count=re.subn(pattern,lambda m:replacement,s,count=1,flags=re.S)
if count!=1: raise SystemExit('driver render replacement failed')

# Replace driver load function body up to enterDriver
pattern=r"  async function loadDriverOrders\(\)\{.*?\n  async function enterDriver\(profile\)\{"
replacement=r'''  async function loadDriverOrders(){
    const{data,error}=await driverDb.from('orders').select('id,order_code,customer_name,customer_phone,address,payment_method,payment_status,paid_at,status,total,delivery_code_required,delivery_verified_at,driver_id,driver_assigned_at,finished_at,created_at').order('created_at',{ascending:false}).order('id',{ascending:false});
    if(error){console.error('Erro ao carregar entregas:',error);if(error.code==='PGRST301')clearDriverSession('Sua sessão terminou.');return}
    const rows=data||[];
    const availableRows=rows.filter(order=>!order.driver_id&&['ready','delivered','out_for_delivery','delivery'].includes(String(order.status)));
    const freshAvailable=availableRows.filter(order=>!driverKnownAvailableIds.has(String(order.id)));
    driverOrders=rows;renderDriverOrders();driverKnownAvailableIds=new Set(availableRows.map(order=>String(order.id)));
    if((driverAlertsReady||freshAvailable.length)&&freshAvailable.length){const latest=freshAvailable[0];window.LVAlerts?.start('driver-new-delivery','Nova entrega disponível',`Pedido #${latest.id} · ${latest.order_code||''} · ${latest.customer_name||'Cliente'}`,{repeats:10,interval:6000})}
    driverAlertsReady=true;
  }
  async function enterDriver(profile){'''
s,count=re.subn(pattern,lambda m:replacement,s,count=1,flags=re.S)
if count!=1: raise SystemExit('driver load replacement failed')

# Reset alerts when entering/clearing driver session and use 5s fallback refresh
old="driverProfile=profile;document.querySelector('#panel-app').classList.remove('authenticated');"
new="driverProfile=profile;driverKnownAvailableIds=new Set();driverAlertsReady=false;window.LVAlerts?.stop('driver-new-delivery');document.querySelector('#panel-app').classList.remove('authenticated');"
if old not in s: raise SystemExit('enter driver marker not found')
s=s.replace(old,new,1)
s=s.replace("driverRefreshTimer=setInterval(loadDriverOrders,10000)","driverRefreshTimer=setInterval(loadDriverOrders,5000)",1)
old="if(driverRefreshTimer){clearInterval(driverRefreshTimer);driverRefreshTimer=null}driverToken='';driverProfile=null;driverOrders=[];"
new="if(driverRefreshTimer){clearInterval(driverRefreshTimer);driverRefreshTimer=null}window.LVAlerts?.stop('driver-new-delivery');driverKnownAvailableIds=new Set();driverAlertsReady=false;driverToken='';driverProfile=null;driverOrders=[];"
if old not in s: raise SystemExit('clear driver marker not found')
s=s.replace(old,new,1)

# Stop repeating driver alert as soon as a delivery is claimed
old="if(error)throw error;if(!data?.ok)throw new Error(data?.message||'Não foi possível pegar esta entrega');showToast('Entrega adicionada à sua rota');"
new="if(error)throw error;if(!data?.ok)throw new Error(data?.message||'Não foi possível pegar esta entrega');window.LVAlerts?.stop('driver-new-delivery');showToast('Entrega adicionada à sua rota');"
if old not in s: raise SystemExit('driver claim marker not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('driver history and alert system patched')
