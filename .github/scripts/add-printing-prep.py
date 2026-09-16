from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'id="lv-printing-module"' in s:
    raise SystemExit('printing module already exists')

# 1) Make room for a visible manual print icon in order cards.
s = s.replace(
    '.card-actions{display:grid;grid-template-columns:1fr auto;gap:7px;margin-top:13px}',
    '.card-actions{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:7px;margin-top:13px}',
    1
)

# 2) Print-only receipt surface. Hidden in normal use.
print_css = r'''
  <style id="lv-printing-style">
    #lv-print-sheet{display:none}
    @media print{
      @page{margin:4mm}
      body.lv-printing{background:#fff!important;color:#000!important}
      body.lv-printing>*:not(#lv-print-sheet){display:none!important}
      body.lv-printing #lv-print-sheet{display:block!important;position:static!important;width:72mm;max-width:100%;margin:0 auto;padding:0;background:#fff!important;color:#000!important}
      body.lv-printing #lv-print-sheet pre{margin:0;white-space:pre-wrap;overflow-wrap:anywhere;color:#000!important;background:#fff!important;font:600 12px/1.35 ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}
    }
  </style>
'''
if '</head>' not in s:
    raise SystemExit('head end not found')
s = s.replace('</head>', print_css + '</head>', 1)

# 3) Use the real order_items columns. This is required so printed quantities/prices
#    match the persisted order, while keeping backwards-compatible fallbacks.
old_item_map = "return{qty:Number(item.qty||1),name:product.name||'Item',detail:[item.size,item.edge,item.note,item.detail].filter(Boolean).join(' · '),price:Number(product.base_price||0)}"
new_item_map = "return{qty:Number(item.quantity||item.qty||1),name:item.product_name||product.name||'Item',detail:item.detail||[item.size,item.edge,item.note].filter(Boolean).join(' · '),price:Number(item.unit_price||product.base_price||0)}"
if old_item_map not in s:
    raise SystemExit('order item mapping marker not found')
s = s.replace(old_item_map, new_item_map, 1)

# 4) Load address/phone too, so the receipt is ready for delivery orders.
old_select = ".select('id,order_code,customer_name,order_type,payment_method,payment_status,paid_at,status,total,delivery_code_required,delivery_verified_at,created_at')"
new_select = ".select('id,order_code,customer_name,customer_phone,address,order_type,payment_method,payment_status,paid_at,status,total,delivery_code_required,delivery_verified_at,created_at')"
if old_select not in s:
    raise SystemExit('orders select marker not found')
s = s.replace(old_select, new_select, 1)

old_norm = "return{id:row.id,customer:row.customer_name||'Cliente não informado',createdAt:row.created_at||Date.now()"
new_norm = "return{id:row.id,customer:row.customer_name||'Cliente não informado',phone:row.customer_phone||'',address:row.address||'',createdAt:row.created_at||Date.now()"
if old_norm not in s:
    raise SystemExit('normalizeOrder marker not found')
s = s.replace(old_norm, new_norm, 1)

# 5) Add a print button to every order card without altering status actions.
start = s.find('  function orderCard(order){')
end = s.find('\n  function boardColumn', start)
if start < 0 or end < 0:
    raise SystemExit('orderCard block not found')
block = s[start:end]
block = block.replace(
    "const meta=orderStatusMeta(order),deliveryCheck=needsDeliveryConfirmation(order),confirmable=canConfirmPayment(order);",
    "const meta=orderStatusMeta(order),deliveryCheck=needsDeliveryConfirmation(order),confirmable=canConfirmPayment(order),printAction=`<button class=\"mini-action\" data-action=\"print-order\" data-id=\"${order.id}\" aria-label=\"Imprimir pedido\" title=\"Imprimir pedido\"><i data-lucide=\"printer\"></i></button>`;",
    1
)
needle = "}</div></article>`;"
if needle not in block:
    raise SystemExit('orderCard closing marker not found')
block = block.replace(needle, "}${printAction}</div></article>`;", 1)
s = s[:start] + block + s[end:]

# 6) Visible manual print button in details modal.
old_close = '<button class=\\"button secondary\\" data-close-modal>Fechar</button>'
new_close = '<button class=\\"button secondary\\" data-action=\\"print-order\\" data-id=\\"${order.id}\\"><i data-lucide=\\"printer\\"></i>Imprimir pedido</button><button class=\\"button secondary\\" data-close-modal>Fechar</button>'
if old_close not in s:
    raise SystemExit('details close button marker not found')
s = s.replace(old_close, new_close, 1)

# 7) Let the existing action dispatcher call the printing bridge.
old_actions = "if(action.dataset.action==='details')openDetails(id)}"
new_actions = "if(action.dataset.action==='details')openDetails(id);if(action.dataset.action==='print-order')window.LVPrinting?.printNormal(id)}"
if old_actions not in s:
    raise SystemExit('action dispatcher marker not found')
s = s.replace(old_actions, new_actions, 1)

# 8) Hidden print bridge. Automatic modes intentionally default OFF.
module = r'''
<section id="lv-print-sheet" aria-hidden="true"></section>
<script id="lv-printing-module">
(()=>{
  // ---------------------------------------------------------
  // DELIVERY LV — IMPRESSÃO
  // MODO ENTREGUE AO CLIENTE: impressão normal/manual.
  // AutoPrint/RawBT ficam preparados, ocultos e DESLIGADOS
  // até o modelo da impressora ser confirmado.
  // ---------------------------------------------------------
  const CONFIG=Object.freeze({
    autoPrintEnabled:false,
    autoPrintMode:'download', // 'download' (AutoPrint watcher) ou 'rawbt'
    rawBtEnabled:false,
    rawBtPackage:'ru.a402d.rawbtprinter',
    receiptWidth:32,
    skipLocalOrders:true
  });
  const SENT_KEY='deliverylv_autoprint_sent_v1';
  const queue=[];

  const clean=value=>String(value??'').replace(/[\r\n\t]+/g,' ').replace(/\s{2,}/g,' ').trim();
  const moneyText=value=>Number(value||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
  const sep=()=>'-'.repeat(CONFIG.receiptWidth);
  const center=value=>{const text=clean(value).slice(0,CONFIG.receiptWidth);const left=Math.max(0,Math.floor((CONFIG.receiptWidth-text.length)/2));return ' '.repeat(left)+text};
  const formatDate=value=>{try{return new Intl.DateTimeFormat('pt-BR',{timeZone:'America/Rio_Branco',day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'}).format(new Date(value))}catch{return''}};

  function orderById(id){return Array.isArray(orders)?orders.find(order=>Number(order.id)===Number(id)):null}
  function buildReceipt(order){
    if(!order)return'';
    const lines=[center('DELIVERY LV'),sep(),`PEDIDO #${order.id}`];
    if(order.orderCode)lines.push(`CODIGO: ${clean(order.orderCode)}`);
    lines.push(`DATA: ${formatDate(order.createdAt)}`);
    lines.push(`CLIENTE: ${clean(order.customer||'Cliente')}`);
    if(order.phone)lines.push(`TELEFONE: ${clean(order.phone)}`);
    lines.push(`TIPO: ${clean(order.type||'')}`);
    if(order.address&&String(order.type).toLowerCase().includes('entrega'))lines.push(`ENDERECO: ${clean(order.address)}`);
    lines.push(`PAGAMENTO: ${clean(order.payment||'A confirmar')}`,sep(),'ITENS');
    (order.items||[]).forEach(item=>{
      const qty=Math.max(1,Number(item.qty||1));
      lines.push(`${qty}x ${clean(item.name||'Item')}`);
      if(item.detail)lines.push(`  ${clean(item.detail)}`);
      const unit=Number(item.price||0);
      if(Number.isFinite(unit)&&unit>0)lines.push(`  ${moneyText(unit)} x ${qty} = ${moneyText(unit*qty)}`);
    });
    lines.push(sep(),`TOTAL: ${moneyText(order.total)}`,sep(),center('OBRIGADO!'),'');
    return lines.join('\n');
  }

  function escapeHtml(value){return String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]))}
  function printNormal(id){
    const order=orderById(id);if(!order){showToast?.('Pedido não encontrado');return false}
    const sheet=document.querySelector('#lv-print-sheet');if(!sheet)return false;
    sheet.innerHTML=`<pre>${escapeHtml(buildReceipt(order))}</pre>`;
    document.body.classList.add('lv-printing');
    const cleanup=()=>{document.body.classList.remove('lv-printing');sheet.innerHTML='';window.removeEventListener('afterprint',cleanup)};
    window.addEventListener('afterprint',cleanup);
    try{window.print();window.setTimeout(()=>{if(document.body.classList.contains('lv-printing'))cleanup()},2500);return true}catch(error){cleanup();console.error('Impressão normal indisponível',error);showToast?.('Não foi possível abrir a impressão');return false}
  }

  function sentIds(){try{return new Set(JSON.parse(sessionStorage.getItem(SENT_KEY)||'[]').map(String))}catch{return new Set()}}
  function wasSent(id){return sentIds().has(String(id))}
  function markSent(id){try{const ids=sentIds();ids.add(String(id));sessionStorage.setItem(SENT_KEY,JSON.stringify([...ids].slice(-200)))}catch(error){console.warn('Deduplicação de AutoPrint limitada à sessão atual',error)}}

  function saveAutoPrintFile(order){
    if(!order||wasSent(order.id))return true;
    const text=buildReceipt(order).replace(/\r?\n/g,'\r\n');
    const blob=new Blob([text],{type:'text/plain;charset=utf-8'});
    const url=URL.createObjectURL(blob);
    const link=document.createElement('a');
    link.href=url;link.download=`DELIVERY_LV_PEDIDO_${String(order.id).padStart(4,'0')}.txt`;link.style.display='none';
    document.body.appendChild(link);link.click();link.remove();window.setTimeout(()=>URL.revokeObjectURL(url),10000);
    markSent(order.id);return true;
  }

  function utf8Base64(text){const bytes=new TextEncoder().encode(text);let binary='';bytes.forEach(byte=>binary+=String.fromCharCode(byte));return btoa(binary)}
  function rawBtIntent(order){
    const base64=utf8Base64(buildReceipt(order));
    const dataUri='data:text/plain;base64,'+base64;
    return 'intent:'+encodeURI(dataUri)+'#Intent;scheme=rawbt;package='+CONFIG.rawBtPackage+';end;';
  }
  function rawBtDirect(order){return 'rawbt:data:text/plain;base64,'+utf8Base64(buildReceipt(order))}
  function sendRawBt(order){
    if(!CONFIG.rawBtEnabled||!order||wasSent(order.id))return false;
    if(!/Android/i.test(navigator.userAgent))return false;
    const intent=rawBtIntent(order);
    try{window.location.href=intent;markSent(order.id);return true}catch(error){console.warn('RawBT intent falhou',error);try{window.location.href=rawBtDirect(order);markSent(order.id);return true}catch{return false}}
  }

  function eligible(order){
    if(!order||order.status!=='new')return false;
    if(CONFIG.skipLocalOrders&&String(order.type||'').toLowerCase().includes('local'))return false;
    return !wasSent(order.id);
  }
  function auto(order){
    if(!CONFIG.autoPrintEnabled||!eligible(order))return false;
    try{
      const ok=CONFIG.autoPrintMode==='rawbt'?sendRawBt(order):saveAutoPrintFile(order);
      if(!ok&&!queue.some(item=>Number(item.id)===Number(order.id)))queue.push(order);
      return ok;
    }catch(error){console.error('Falha no AutoPrint',error);if(!queue.some(item=>Number(item.id)===Number(order.id)))queue.push(order);return false}
  }
  function retryQueue(){if(!CONFIG.autoPrintEnabled||!queue.length)return false;const order=queue.shift();return auto(order)}
  function testHidden(){
    const fake={id:'TESTE',orderCode:'TESTE',createdAt:new Date().toISOString(),customer:'Teste de impressao',phone:'',address:'',type:'Retirada no balcão',payment:'Teste',total:0,items:[{qty:1,name:'TESTE DE IMPRESSAO',detail:'Configuracao oculta',price:0}],status:'new'};
    if(CONFIG.autoPrintMode==='rawbt')return sendRawBt(fake);return saveAutoPrintFile(fake);
  }

  // Detect only genuinely new orders after the first panel load.
  const originalLoad=loadRealOrders;
  loadRealOrders=async function(options={}){
    const before=new Set((orders||[]).map(order=>String(order.id)));
    const detect=CONFIG.autoPrintEnabled&&options?.notify!==false;
    const result=await originalLoad(options);
    if(detect)(orders||[]).filter(order=>!before.has(String(order.id))).forEach(auto);
    return result;
  };

  window.LVPrinting={config:CONFIG,printNormal,buildReceipt,retryQueue,testHidden,_queue:queue};
})();
</script>
'''
if '</body>' not in s:
    raise SystemExit('body end not found')
s = s.replace('</body>', module + '\n</body>', 1)

# Sanity checks: hidden automatic features must remain disabled.
checks = [
    'autoPrintEnabled:false',
    'rawBtEnabled:false',
    "rawBtPackage:'ru.a402d.rawbtprinter'",
    'data-action=\\"print-order\\"',
    'id="lv-printing-module"',
    "item.quantity||item.qty||1",
]
for marker in checks:
    if marker not in s:
        raise SystemExit(f'missing final marker: {marker}')

p.write_text(s,encoding='utf-8')
print('printing preparation added; auto modes remain hidden/off')
