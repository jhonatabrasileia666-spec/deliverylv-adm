from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'lv-store-control-module' in s:
    raise SystemExit('store control already installed')

# 1) Escape public order data before injecting it into admin innerHTML.
repls={
    '<div class="customer">${order.customer}</div>':'<div class="customer">${escapeMenuText(order.customer)}</div>',
    '<strong>${item.qty}x ${item.name}</strong>${item.detail?`<span>- ${item.detail}</span>`:\'\'}':'<strong>${item.qty}x ${escapeMenuText(item.name)}</strong>${item.detail?`<span>- ${escapeMenuText(item.detail)}</span>`:\'\'}',
    '<div class="info-line"><span>Pagamento</span><strong>${order.payment}</strong></div>':'<div class="info-line"><span>Pagamento</span><strong>${escapeMenuText(order.payment)}</strong></div>',
    '<span>${order.customer}</span><span>Hoje<small>${order.time}</small></span>':'<span>${escapeMenuText(order.customer)}</span><span>${formatHistoryDate(order.createdAt)}<small>${order.time}</small></span>',
    '${order.customer} · ${order.time} · ${order.type}':'${escapeMenuText(order.customer)} · ${order.time} · ${escapeMenuText(order.type)}',
    '<div class="notification-copy"><strong>${text}</strong><span>Central de pedidos</span></div>':'<div class="notification-copy"><strong>${escapeMenuText(text)}</strong><span>Central de pedidos</span></div>'
}
for old,new in repls.items():
    if old in s:
        s=s.replace(old,new)

if '<div class="customer">${order.customer}</div>' in s:
    raise SystemExit('unsafe customer render remains')
if '<strong>${item.qty}x ${item.name}</strong>' in s:
    raise SystemExit('unsafe item name render remains')
if '<span>- ${item.detail}</span>' in s:
    raise SystemExit('unsafe item detail render remains')

# 2) Correct history date and business timezone.
marker='  function renderHistory(){'
if marker not in s:
    raise SystemExit('renderHistory marker not found')
helper="""  function formatHistoryDate(value){
    try{return new Intl.DateTimeFormat('pt-BR',{timeZone:'America/Rio_Branco',day:'2-digit',month:'2-digit',year:'numeric'}).format(new Date(value))}
    catch{return 'Data indisponível'}
  }
"""
s=s.replace(marker,helper+marker,1)
s=s.replace("toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})","toLocaleTimeString('pt-BR',{timeZone:'America/Rio_Branco',hour:'2-digit',minute:'2-digit'})")

# 3) Add authenticated store open/close control.
module=r'''
<style id="lv-store-control-styles">
  .lv-store-toggle{display:none;align-items:center;gap:7px;min-height:36px;padding:0 11px;border:1px solid var(--line);border-radius:9px;background:var(--panel-3);color:var(--text);font-size:10px;font-weight:900;white-space:nowrap}
  .lv-store-toggle.show{display:inline-flex}.lv-store-toggle .dot{width:8px;height:8px;border-radius:50%;background:var(--muted)}
  .lv-store-toggle.open{background:#26331e;color:var(--lime);border-color:#d9f15c55}.lv-store-toggle.open .dot{background:var(--lime);box-shadow:0 0 0 4px #d9f15c14}
  .lv-store-toggle.closed{background:#3c211c;color:#ffb0a0;border-color:#ff8f7955}.lv-store-toggle.closed .dot{background:var(--red)}
  .lv-store-toggle:disabled{opacity:.55;cursor:wait}
  @media(max-width:720px){.lv-store-toggle .label-long{display:none}.lv-store-toggle{padding:0 9px}.top-right{gap:9px}}
</style>
<script id="lv-store-control-module">
(()=>{
  const host=document.querySelector('.top-right')||document.querySelector('.topbar-inner');
  const panel=document.querySelector('#panel-app');
  if(!host||!panel)return;
  const button=document.createElement('button');
  button.type='button';button.className='lv-store-toggle';button.id='lv-store-toggle';
  button.setAttribute('aria-label','Abrir ou fechar loja');
  host.prepend(button);
  let isOpen=null,loading=false;

  const authenticated=()=>panel.classList.contains('authenticated');
  function paint(){
    const visible=authenticated();button.classList.toggle('show',visible);
    if(!visible)return;
    button.classList.toggle('open',isOpen===true);button.classList.toggle('closed',isOpen===false);
    const text=isOpen===true?'Loja aberta':isOpen===false?'Loja fechada':'Verificando loja';
    button.innerHTML=`<span class="dot"></span><span class="label-long">${text}</span><span class="label-short">${isOpen===true?'Aberta':isOpen===false?'Fechada':'...'}</span>`;
  }
  async function refresh(){
    if(!authenticated()){paint();return null}
    const{data,error}=await db.from('store_settings').select('is_open').eq('id',1).single();
    if(error){console.error('Erro ao carregar estado da loja:',error);showToast('Não foi possível verificar se a loja está aberta');return null}
    isOpen=Boolean(data?.is_open);paint();return isOpen;
  }
  async function toggle(){
    if(loading||!authenticated()||isOpen===null)return;
    loading=true;button.disabled=true;
    const next=!isOpen;
    try{
      const{data,error}=await db.from('store_settings').update({is_open:next,updated_at:new Date().toISOString()}).eq('id',1).select('is_open').single();
      if(error)throw error;
      isOpen=Boolean(data?.is_open);paint();showToast(isOpen?'Loja aberta para novos pedidos':'Loja fechada para novos pedidos');
    }catch(error){console.error('Erro ao alterar estado da loja:',error);showToast('Não foi possível alterar o estado da loja')}
    finally{loading=false;button.disabled=false}
  }
  button.addEventListener('click',toggle);
  const observer=new MutationObserver(()=>{paint();if(authenticated())setTimeout(refresh,250)});
  observer.observe(panel,{attributes:true,attributeFilter:['class']});
  window.setInterval(()=>{if(authenticated())refresh()},30000);
  window.LVStoreControl={refresh,toggle,get isOpen(){return isOpen}};
  paint();
})();
</script>
'''
if '</body>' not in s:
    raise SystemExit('body end not found')
s=s.replace('</body>',module+'\n</body>',1)

checks=['formatHistoryDate','escapeMenuText(order.customer)','escapeMenuText(item.detail)','lv-store-control-module',"db.from('store_settings').update"]
for c in checks:
    if c not in s: raise SystemExit('missing marker: '+c)

p.write_text(s,encoding='utf-8')
print('admin prelaunch hardening applied')
