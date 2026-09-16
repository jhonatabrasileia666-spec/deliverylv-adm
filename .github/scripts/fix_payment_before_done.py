from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def replace_line(prefix, new_line, label):
    global text
    pattern = rf'^  {re.escape(prefix)}.*$'
    text, count = re.subn(pattern, '  ' + new_line, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit(f'Expected code not found: {label}')

replace_line(
    'const statusMeta=',
    "const statusMeta={new:{label:'Novo pedido',next:'prep',nextLabel:'Mandar para preparo'},accepted:{label:'Aceito',next:'prep',nextLabel:'Enviar para preparo'},prep:{label:'Em preparo',next:'ready',nextLabel:'Marcar como pronto'},ready:{label:'Pronto',next:'delivery',nextLabel:'Saiu para entrega'},delivery:{label:'Saiu para entrega',next:null,nextLabel:'Confirmar pagamento'},done:{label:'Finalizado',next:null,nextLabel:'Finalizado'},cancelled:{label:'Recusado',next:null,nextLabel:'Recusado'}};",
    'statusMeta'
)

replace_line(
    'function orderStatusMeta(order)',
    "function orderStatusMeta(order){if(order.status==='ready'){if(order.type==='Retirada no balcão'||order.type==='Comer no local')return{...statusMeta.ready,next:null,nextLabel:'Confirmar pagamento'}}return statusMeta[order.status]}",
    'orderStatusMeta'
)

# Insert helper right after orderStatusMeta.
marker = "  function orderStatusMeta(order){if(order.status==='ready'){if(order.type==='Retirada no balcão'||order.type==='Comer no local')return{...statusMeta.ready,next:null,nextLabel:'Confirmar pagamento'}}return statusMeta[order.status]}\n"
helper = marker + "  function canConfirmPayment(order){return order.paymentStatus!=='paid'&&(order.status==='delivery'||(order.status==='ready'&&(order.type==='Retirada no balcão'||order.type==='Comer no local')))}\n"
if marker not in text:
    raise SystemExit('Expected code not found: helper marker')
text = text.replace(marker, helper, 1)

replace_line(
    'function normalizeOrder(row,items=[])',
    "function normalizeOrder(row,items=[]){const type=normalizeOrderType(row.order_type),paymentStatus=String(row.payment_status||'pending').toLowerCase(),rawStatus=normalizeStatus(row.status);let status=rawStatus;if(rawStatus==='done'&&paymentStatus!=='paid')status=type==='Entrega'?'delivery':'ready';return{id:row.id,customer:row.customer_name||'Cliente não informado',createdAt:row.created_at||Date.now(),minutes:Math.max(0,Math.floor((Date.now()-new Date(row.created_at||Date.now()).getTime())/60000)),status,rawStatus,time:new Date(row.created_at||Date.now()).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}),type,payment:row.payment_method||'A confirmar',paymentStatus,paidAt:row.paid_at||null,total:Number(row.total||0),items}}",
    'normalizeOrder'
)

replace_line(
    'function orderCard(order)',
    "function orderCard(order){const meta=orderStatusMeta(order),confirmable=canConfirmPayment(order);return `<article class=\"order-card ${statusClass(order.status)}\" data-order=\"${order.id}\"><div class=\"order-card-top\"><span class=\"order-number\">#${order.id}</span><span class=\"order-time\">há ${order.minutes} min</span></div><div class=\"customer\">${order.customer}</div><div class=\"order-meta\"><i data-lucide=\"clock\"></i>${order.time} · ${order.type}</div><div class=\"item-list\">${order.items.map(item=>`<div class=\"item\"><strong>${item.qty}x ${item.name}</strong>${item.detail?`<span>- ${item.detail}</span>`:''}</div>`).join('')}</div><div class=\"order-info\"><div class=\"info-line\"><span>Pagamento</span><strong>${order.payment}</strong></div>${confirmable?`<div class=\"info-line\"><span>Status do pagamento</span><strong>Pendente</strong></div>`:order.status==='done'?`<div class=\"info-line\"><span>Status do pagamento</span><strong>Confirmado</strong></div>`:''}<div class=\"info-line\"><span>Entrega</span><strong>${order.type}</strong></div></div><div class=\"total-line\"><span>Total</span><strong>${money(order.total)}</strong></div><div class=\"card-actions\">${order.status==='new'?`<button class=\"button small\" data-action=\"accept\" data-id=\"${order.id}\"><i data-lucide=\"arrow-right\"></i>${meta.nextLabel}</button><button class=\"mini-action\" data-action=\"reject\" data-id=\"${order.id}\" aria-label=\"Recusar pedido\"><i data-lucide=\"x\"></i></button>`:confirmable?`<button class=\"button small\" data-action=\"confirm-payment\" data-id=\"${order.id}\"><i data-lucide=\"badge-check\"></i>Confirmar pagamento</button><button class=\"mini-action\" data-action=\"details\" data-id=\"${order.id}\" aria-label=\"Ver detalhes\"><i data-lucide=\"eye\"></i></button>`:order.status==='done'||order.status==='cancelled'?`<button class=\"button small secondary\" data-action=\"details\" data-id=\"${order.id}\"><i data-lucide=\"eye\"></i>Ver detalhes</button>`:`<button class=\"button small\" data-action=\"advance\" data-id=\"${order.id}\">${meta.nextLabel}<i data-lucide=\"arrow-right\"></i></button><button class=\"mini-action\" data-action=\"details\" data-id=\"${order.id}\" aria-label=\"Ver detalhes\"><i data-lucide=\"eye\"></i></button>`}</div></article>`}",
    'orderCard'
)

replace_line(
    'function renderBoard(targetId,overview=false)',
    "function renderBoard(targetId,overview=false){const target=document.querySelector('#'+targetId);const active=orders;const prepOrders=active.filter(order=>['accepted','prep'].includes(order.status));const source=currentFilter==='all'?active:active.filter(order=>currentFilter==='new'?order.status==='new':currentFilter==='prep'?['accepted','prep'].includes(order.status):currentFilter==='ready'?order.status==='ready':currentFilter==='delivery'?order.status==='delivery':currentFilter==='done'?order.status==='done'&&order.paymentStatus==='paid':true);const columns=[['new','Novos',active.filter(o=>o.status==='new')],['prep','Em preparo',prepOrders],['ready','Prontos',active.filter(o=>o.status==='ready')],['delivery','Saiu para entrega',active.filter(o=>o.status==='delivery')],['done','Finalizados',active.filter(o=>o.status==='done'&&o.paymentStatus==='paid')]];if(overview){target.innerHTML=columns.slice(0,3).map(([status,title,list])=>boardColumn(status,title,list)).join('');lucide.createIcons();return}const selected=currentFilter==='all'?'new':currentFilter;const selectedColumn=columns.find(column=>column[0]===selected)||columns[0];const selectedOrders=selectedColumn[0]==='prep'?source.filter(order=>['accepted','prep'].includes(order.status)):source.filter(order=>order.status===selectedColumn[0]&&(selectedColumn[0]!=='done'||order.paymentStatus==='paid'));target.innerHTML=`<div class=\"status-tabs-layout\"><div class=\"status-tabs\">${columns.map(([status,title,list])=>`<button class=\"status-tab ${status===selected?'active':''}\" data-status-tab=\"${status}\"><span>${title}</span><b class=\"status-tab-count\">${list.length}</b></button>`).join('')}</div><div class=\"status-board\"><div class=\"order-grid\">${boardColumn(selectedColumn[0],selectedColumn[1],selectedOrders)}</div></div></div>`;lucide.createIcons();}",
    'renderBoard'
)

replace_line(
    'async function updateStatus(id,next)',
    "async function updateStatus(id,next){const status={accepted:'accepted',prep:'prep',ready:'ready',delivery:'delivered',cancelled:'cancelled'}[next];if(!status)return;const{error}=await db.from('orders').update({status}).eq('id',id);if(error){console.error('Erro ao atualizar pedido:',error);showToast(`Erro ao atualizar pedido: ${error.message||'verifique as permissões'}`);return}await loadRealOrders({notify:false});showToast(next==='cancelled'?'Pedido recusado':'Pedido atualizado')}",
    'updateStatus'
)

replace_line(
    'async function confirmPayment(id)',
    "async function confirmPayment(id){const order=orders.find(item=>item.id===id);if(!order||!canConfirmPayment(order))return;const now=new Date().toISOString();const{error}=await db.from('orders').update({payment_status:'paid',paid_at:now,status:'completed',finished_at:now}).eq('id',id).neq('payment_status','paid');if(error){console.error('Erro ao confirmar pagamento:',error);showToast(`Erro ao confirmar pagamento: ${error.message||'verifique as permissões'}`);return}await loadRealOrders({notify:false});document.querySelector('#detail-modal').classList.remove('show');showToast('Pagamento confirmado e pedido finalizado')}",
    'confirmPayment'
)

replace_line(
    'function openDetails(id)',
    "function openDetails(id){const order=orders.find(item=>item.id===id);if(!order)return;const meta=orderStatusMeta(order),confirmable=canConfirmPayment(order);document.querySelector('#modal-content').innerHTML=`<div class=\"detail-summary\"><strong>Pedido #${order.id} · ${statusMeta[order.status].label}</strong><span>${order.customer} · ${order.time} · ${order.type}</span><div class=\"item-list\">${order.items.map(item=>`<div class=\"item\"><strong>${item.qty}x ${item.name}</strong>${item.detail?`<span>- ${item.detail}</span>`:''}</div>`).join('')}</div><div class=\"info-line\"><span>Pagamento</span><strong>${order.payment}</strong></div>${confirmable?`<div class=\"info-line\"><span>Status do pagamento</span><strong>Pendente</strong></div>`:order.status==='done'?`<div class=\"info-line\"><span>Status do pagamento</span><strong>Confirmado</strong></div>`:''}<div class=\"total-line\"><span>Total</span><strong>${money(order.total)}</strong></div></div><div class=\"modal-actions\">${order.status==='new'?`<button class=\"button\" data-action=\"accept\" data-id=\"${order.id}\">${meta.nextLabel}</button>`:confirmable?`<button class=\"button\" data-action=\"confirm-payment\" data-id=\"${order.id}\">Confirmar pagamento</button>`:!['done','cancelled'].includes(order.status)&&meta.next?`<button class=\"button\" data-action=\"advance\" data-id=\"${order.id}\">${meta.nextLabel}</button>`:''}<button class=\"button secondary\" data-close-modal>Fechar</button></div>`;document.querySelector('#detail-modal').classList.add('show');lucide.createIcons()}",
    'openDetails'
)

required = [
    "function canConfirmPayment(order)",
    "status:'completed',finished_at:now",
    "active.filter(o=>o.status==='done'&&o.paymentStatus==='paid')",
    "rawStatus==='done'&&paymentStatus!=='paid'",
    "delivery:{label:'Saiu para entrega',next:null,nextLabel:'Confirmar pagamento'}"
]
for item in required:
    if item not in text:
        raise SystemExit(f'Missing expected marker after patch: {item}')

path.write_text(text, encoding='utf-8', newline='')
