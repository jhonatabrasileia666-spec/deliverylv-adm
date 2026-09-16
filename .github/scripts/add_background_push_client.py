from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
if 'id="lv-background-push-module"' in s:
    raise SystemExit('background push module already exists')

module=r'''
<style id="lv-background-push-styles">
  .lv-server-alert{position:fixed;z-index:120;left:50%;top:16px;transform:translate(-50%,-16px);width:min(560px,calc(100vw - 24px));display:none;align-items:center;gap:12px;padding:13px 14px;background:#35170d;border:2px solid var(--orange);border-radius:14px;box-shadow:0 22px 70px #000c;color:var(--text)}
  .lv-server-alert.show{display:flex;animation:lv-alert-in .25s ease forwards}.lv-server-alert-icon{width:42px;height:42px;flex:none;display:grid;place-items:center;border-radius:11px;background:var(--orange);color:#160b06}.lv-server-alert-copy{min-width:0;flex:1}.lv-server-alert-copy strong{display:block;font-size:13px}.lv-server-alert-copy span{display:block;margin-top:3px;color:#d8c6b9;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.lv-server-alert-stop{min-height:40px;padding:0 13px;border-radius:9px;background:var(--lime);color:#111;font-weight:900;font-size:11px}.lv-server-alert-status{display:block;margin-top:3px;color:var(--lime);font-size:9px}
  @keyframes lv-alert-in{to{transform:translate(-50%,0)}}
  @media(max-width:600px){.lv-server-alert{top:8px;align-items:flex-start}.lv-server-alert-icon{width:36px;height:36px}.lv-server-alert-stop{padding:0 9px}.lv-server-alert-copy span{max-width:45vw}}
</style>
<div class="lv-server-alert" id="lv-server-alert" role="alert" aria-live="assertive">
  <div class="lv-server-alert-icon"><i data-lucide="bell-ring"></i></div>
  <div class="lv-server-alert-copy"><strong id="lv-server-alert-title">Novo alerta</strong><span id="lv-server-alert-body">Existe uma atualização.</span><small class="lv-server-alert-status">O aviso continua até você parar.</small></div>
  <button class="lv-server-alert-stop" id="lv-server-alert-stop" type="button">Parar alerta</button>
</div>
<script id="lv-background-push-module">
(()=>{
  const VAPID_PUBLIC='BPGBg5ZSyN1I9D76RucxYKyYeWQU--jfQDpePfIpChaHj51ZV_GkQhgScvKaXIHHKYsVpZIjkWfBoDEi9tIqNp8';
  const ACK_URL='https://nhvarlrbqbryrurpdwvp.supabase.co/functions/v1/lv-web-push';
  const PANEL_KEY='deliverylv_panel_session';
  const DRIVER_KEY='deliverylv_driver_session';
  const banner=document.querySelector('#lv-server-alert');
  let currentAlert=null;
  let syncedAudience='';
  let syncing=false;

  function applicationServerKey(value){
    const padding='='.repeat((4-value.length%4)%4),base64=(value+padding).replace(/-/g,'+').replace(/_/g,'/'),raw=atob(base64),out=new Uint8Array(raw.length);
    for(let i=0;i<raw.length;i++)out[i]=raw.charCodeAt(i);
    return out;
  }
  function audience(){
    if(document.querySelector('#driver-app')?.classList.contains('authenticated'))return'driver';
    if(document.querySelector('#panel-app')?.classList.contains('authenticated'))return'admin';
    return'';
  }
  function clientFor(role){
    const token=localStorage.getItem(role==='driver'?DRIVER_KEY:PANEL_KEY)||'';
    if(!token)return null;
    const header=role==='driver'?'x-driver-session':'x-panel-session';
    return window.supabase.createClient(SUPABASE_URL,SUPABASE_PUBLISHABLE_KEY,{global:{headers:{[header]:token}}});
  }
  function markButtons(active,text='Alertas ativos'){
    document.querySelectorAll('[data-enable-alerts]').forEach(button=>{
      button.classList.toggle('push-active',active);
      const span=button.querySelector('span');if(span&&active)span.textContent=text;
    });
  }
  async function registerPush(role,{ask=false}={}){
    if(syncing||!role||!('serviceWorker'in navigator)||!('PushManager'in window)||!('Notification'in window))return false;
    syncing=true;
    try{
      let permission=Notification.permission;
      if(permission==='default'&&ask)permission=await Notification.requestPermission();
      if(permission!=='granted')return false;
      const registration=await navigator.serviceWorker.ready;
      let subscription=await registration.pushManager.getSubscription();
      if(!subscription){
        subscription=await registration.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:applicationServerKey(VAPID_PUBLIC)});
      }
      const client=clientFor(role);if(!client)return false;
      const{data,error}=await client.rpc('lv_push_subscribe',{p_audience:role,p_subscription:subscription.toJSON()});
      if(error)throw error;
      if(!data?.ok)throw new Error(data?.message||'Não foi possível ativar as notificações em segundo plano');
      syncedAudience=role;markButtons(true);
      return true;
    }catch(error){
      console.error('Erro ao registrar Web Push:',error);
      if(ask&&typeof showToast==='function')showToast(error?.message||'Não foi possível ativar as notificações em segundo plano');
      return false;
    }finally{syncing=false}
  }
  async function ackAlert(data){
    if(!data?.alertId||!data?.ackToken)return false;
    try{
      const response=await fetch(ACK_URL,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:'ack',alertId:data.alertId,ackToken:data.ackToken})});
      return response.ok;
    }catch(error){console.error('Erro ao parar alerta:',error);return false}
  }
  function hideBanner(){banner?.classList.remove('show');window.LVAlerts?.stop?.('server-push');currentAlert=null}
  function showBanner(data){
    if(!data?.alertId)return;
    const same=String(currentAlert?.alertId||'')===String(data.alertId);
    currentAlert=data;
    document.querySelector('#lv-server-alert-title').textContent=data.title||'Delivery LV';
    document.querySelector('#lv-server-alert-body').textContent=data.body||'Existe um alerta que precisa de atenção.';
    banner?.classList.add('show');
    if(!same)window.LVAlerts?.start?.('server-push',data.title||'Novo alerta',data.body||'Delivery LV',{repeats:120,interval:5000});
    if(window.lucide)lucide.createIcons();
  }
  async function stopCurrent(){
    const data=currentAlert;if(!data)return;
    const button=document.querySelector('#lv-server-alert-stop');if(button){button.disabled=true;button.textContent='Parando...'}
    const ok=await ackAlert(data);
    if(ok){hideBanner();if(typeof showToast==='function')showToast('Alerta encerrado')}
    else if(typeof showToast==='function')showToast('Não foi possível parar o alerta. Verifique a conexão.');
    if(button){button.disabled=false;button.textContent='Parar alerta'}
  }

  document.querySelector('#lv-server-alert-stop')?.addEventListener('click',stopCurrent);
  document.addEventListener('click',event=>{
    const button=event.target.closest('[data-enable-alerts]');if(!button)return;
    const role=audience();
    if(role)registerPush(role,{ask:true}).then(ok=>{if(ok&&typeof showToast==='function')showToast('Notificações em segundo plano ativadas')});
  },true);

  navigator.serviceWorker?.addEventListener('message',event=>{
    const message=event.data||{};
    if(message.type==='lv-push-alert')showBanner(message.payload||{});
    if(message.type==='lv-push-stopped'&&String(currentAlert?.alertId||'')===String(message.payload?.alertId||''))hideBanner();
  });

  const sync=()=>{
    const role=audience();
    if(role&&Notification.permission==='granted'&&role!==syncedAudience)registerPush(role);
  };
  const observer=new MutationObserver(sync);
  ['panel-app','driver-app'].forEach(id=>{const el=document.getElementById(id);if(el)observer.observe(el,{attributes:true,attributeFilter:['class']})});
  window.addEventListener('load',()=>setTimeout(sync,1200));
  window.LVBackgroundPush={register:registerPush,stopCurrent};
})();
</script>
'''

if '</body>' not in s:
    raise SystemExit('body close marker not found')
s=s.replace('</body>',module+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('background push client added')
