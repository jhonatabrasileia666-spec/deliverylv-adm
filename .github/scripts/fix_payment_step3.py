from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

replacements = [
    ("payment:row.payment_method||'A confirmar',total:Number(row.total||0),items", "payment:row.payment_method||'A confirmar',paymentStatus:String(row.payment_status||'pending').toLowerCase(),paidAt:row.paid_at||null,total:Number(row.total||0),items"),
    (".select('id,customer_name,order_type,payment_method,status,total,created_at')", ".select('id,customer_name,order_type,payment_method,payment_status,paid_at,status,total,created_at')"),
    ("const sales=orders.filter(o=>o.status==='done'&&isToday(o.createdAt)).reduce((sum,o)=>sum+o.total,0);", "const sales=orders.filter(o=>o.status==='done'&&o.paymentStatus==='paid'&&o.paidAt&&isToday(o.paidAt)).reduce((sum,o)=>sum+o.total,0);"),
    ("const date=dateKey(year,month,day),dayOrders=orders.filter(order=>order.status==='done'&&businessDate(order.createdAt)===date),sales=dayOrders.reduce((sum,order)=>sum+order.total,0)", "const date=dateKey(year,month,day),dayOrders=orders.filter(order=>order.status==='done'&&order.paymentStatus==='paid'&&order.paidAt&&businessDate(order.paidAt)===date),sales=dayOrders.reduce((sum,order)=>sum+order.total,0)"),
    ("const finalized=orders.filter(order=>order.status==='done'&&businessDate(order.createdAt)===today);", "const finalized=orders.filter(order=>order.status==='done'&&order.paymentStatus==='paid'&&order.paidAt&&businessDate(order.paidAt)===today);"),
    ("<div class=\"finance-note\">pedidos finalizados</div>", "<div class=\"finance-note\">pagamentos confirmados</div>"),
    ("<div class=\"finance-line\"><span>Pedidos concluídos</span><strong id=\"finance-order-count\">0</strong></div>", "<div class=\"finance-line\"><span>Pagamentos confirmados</span><strong id=\"finance-order-count\">0</strong></div>"),
    ("Resultado = vendas finalizadas − custo diário informado − outros gastos do dia.", "Resultado = pagamentos confirmados − custo diário informado − outros gastos do dia."),
    ("pedido${data.orders>1?'s':''} finalizado${data.orders>1?'s':''} neste dia.", "pagamento${data.orders>1?'s':''} confirmado${data.orders>1?'s':''} neste dia."),
    ("'Nenhum pedido finalizado neste dia.'", "'Nenhum pagamento confirmado neste dia.'"),
]

for old, new in replacements:
    if old not in text:
        raise SystemExit(f'Expected code not found: {old[:120]!r}')
    text = text.replace(old, new, 1)

order_card_pattern = r"  function orderCard\(order\)\{.*?\n  function boardColumn"
order_card_replacement = '''  function orderCard(order){const meta=orderStatusMeta(order);const completedActions=order.paymentStatus==='paid'?`<button class="button small secondary" data-action="details" data-id="${order.id}"><i data-lucide="eye"></i>Ver detalhes</button>`:`<button class="button small" data-action="confirm-payment" data-id="${order.id}"><i data-lucide="badge-check"></i>Confirmar pagamento</button><button class="mini-action" data-action="details" data-id="${order.id}" aria-label="Ver detalhes"><i data-lucide="eye"></i></button>`;return `<article class="order-card ${statusClass(order.status)}" data-order="${order.id}"><div class="order-card-top"><span class="order-number">#${order.id}</span><span class="order-time">há ${order.minutes} min</span></div><div class="customer">${order.customer}</div><div class="order-meta"><i data-lucide="clock"></i>${order.time} · ${order.type}</div><div class="item-list">${order.items.map(item=>`<div class="item"><strong>${item.qty}x ${item.name}</strong>${item.detail?`<span>- ${item.detail}</span>`:''}</div>`).join('')}</div><div class="order-info"><div class="info-line"><span>Pagamento</span><strong>${order.payment}</strong></div>${order.status==='done'?`<div class="info-line"><span>Status do pagamento</span><strong>${order.paymentStatus==='paid'?'Confirmado':'Pendente'}</strong></div>`:''}<div class="info-line"><span>Entrega</span><strong>${order.type}</strong></div></div><div class="total-line"><span>Total</span><strong>${money(order.total)}</strong></div><div class="card-actions">${order.status==='new'?`<button class="button small" data-action="accept" data-id="${order.id}"><i data-lucide="arrow-right"></i>${meta.nextLabel}</button><button class="mini-action" data-action="reject" data-id="${order.id}" aria-label="Recusar pedido"><i data-lucide="x"></i></button>`:order.status==='done'?completedActions:order.status==='cancelled'?`<button class="button small secondary" data-action="details" data-id="${order.id}"><i data-lucide="eye"></i>Ver detalhes</button>`:`<button class="button small" data-action="advance" data-id="${order.id}">${meta.nextLabel}<i data-lucide="arrow-right"></i></button><button class="mini-action" data-action="details" data-id="${order.id}" aria-label="Ver detalhes"><i data-lucide="eye"></i></button>`}</div></article>`}
  function boardColumn'''
text, count = re.subn(order_card_pattern, order_card_replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit('Could not replace orderCard')

marker = "  function openDetails(id){"
confirm_fn = "  async function confirmPayment(id){const order=orders.find(item=>item.id===id);if(!order||order.status!=='done'||order.paymentStatus==='paid')return;const{error}=await db.from('orders').update({payment_status:'paid',paid_at:new Date().toISOString()}).eq('id',id).eq('status','completed');if(error){console.error('Erro ao confirmar pagamento:',error);showToast(`Erro ao confirmar pagamento: ${error.message||'verifique as permissões'}`);return}await loadRealOrders({notify:false});document.querySelector('#detail-modal').classList.remove('show');showToast('Pagamento confirmado e lançado no financeiro')}\n"
if marker not in text:
    raise SystemExit('openDetails marker not found')
text = text.replace(marker, confirm_fn + marker, 1)

open_details_pattern = r"  function openDetails\(id\)\{.*?\n  function showToast"
open_details_replacement = '''  function openDetails(id){const order=orders.find(item=>item.id===id);if(!order)return;const meta=orderStatusMeta(order);const paymentAction=order.status==='done'&&order.paymentStatus!=='paid'?`<button class="button" data-action="confirm-payment" data-id="${order.id}">Confirmar pagamento</button>`:'';document.querySelector('#modal-content').innerHTML=`<div class="detail-summary"><strong>Pedido #${order.id} · ${statusMeta[order.status].label}</strong><span>${order.customer} · ${order.time} · ${order.type}</span><div class="item-list">${order.items.map(item=>`<div class="item"><strong>${item.qty}x ${item.name}</strong>${item.detail?`<span>- ${item.detail}</span>`:''}</div>`).join('')}</div><div class="info-line"><span>Pagamento</span><strong>${order.payment}</strong></div>${order.status==='done'?`<div class="info-line"><span>Status do pagamento</span><strong>${order.paymentStatus==='paid'?'Confirmado':'Pendente'}</strong></div>`:''}<div class="total-line"><span>Total</span><strong>${money(order.total)}</strong></div></div><div class="modal-actions">${order.status==='new'?`<button class="button" data-action="accept" data-id="${order.id}">${meta.nextLabel}</button>`:!['done','cancelled'].includes(order.status)?`<button class="button" data-action="advance" data-id="${order.id}">${meta.nextLabel}</button>`:''}${paymentAction}<button class="button secondary" data-close-modal>Fechar</button></div>`;document.querySelector('#detail-modal').classList.add('show');lucide.createIcons()}
  function showToast'''
text, count = re.subn(open_details_pattern, open_details_replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit('Could not replace openDetails')

old_click = "if(action.dataset.action==='reject'){updateStatus(id,'cancelled')}if(action.dataset.action==='details')openDetails(id)"
new_click = "if(action.dataset.action==='reject'){updateStatus(id,'cancelled')}if(action.dataset.action==='confirm-payment')confirmPayment(id);if(action.dataset.action==='details')openDetails(id)"
if old_click not in text:
    raise SystemExit('Click handler marker not found')
text = text.replace(old_click, new_click, 1)

for required in ["payment_status,paid_at", "data-action=\"confirm-payment\"", "payment_status:'paid'", "o.paymentStatus==='paid'", "businessDate(order.paidAt)===date"]:
    if required not in text:
        raise SystemExit(f'Missing expected marker after patch: {required}')

path.write_text(text, encoding='utf-8', newline='')
