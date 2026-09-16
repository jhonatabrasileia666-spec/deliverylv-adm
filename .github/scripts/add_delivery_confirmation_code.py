from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="function canConfirmPayment(order){return order.paymentStatus!=='paid'&&(order.status==='delivery'||(order.status==='ready'&&(order.type==='Retirada no balcão'||order.type==='Comer no local')))}"
new="function needsDeliveryConfirmation(order){return order.status==='delivery'&&order.type==='Entrega'&&order.deliveryCodeRequired&&!order.deliveryVerifiedAt}\n  function canConfirmPayment(order){return order.paymentStatus!=='paid'&&((order.status==='delivery'&&(!order.deliveryCodeRequired||!!order.deliveryVerifiedAt))||(order.status==='ready'&&(order.type==='Retirada no balcão'||order.type==='Comer no local')))}"
if old not in s: raise SystemExit('canConfirmPayment marker not found')
s=s.replace(old,new,1)

old="total:Number(row.total||0),items}}"
new="total:Number(row.total||0),deliveryCodeRequired:Boolean(row.delivery_code_required),deliveryVerifiedAt:row.delivery_verified_at||null,items}}"
if old not in s: raise SystemExit('normalize marker not found')
s=s.replace(old,new,1)

old=".select('id,customer_name,order_type,payment_method,payment_status,paid_at,status,total,created_at')"
new=".select('id,customer_name,order_type,payment_method,payment_status,paid_at,status,total,created_at,delivery_code_required,delivery_verified_at')"
if old not in s: raise SystemExit('orders select marker not found')
s=s.replace(old,new,1)

order_card=r'''  function orderCard(order){
    const meta=orderStatusMeta(order),deliveryCheck=needsDeliveryConfirmation(order),confirmable=canConfirmPayment(order);
    return `<article class="order-card ${statusClass(order.status)}" data-order="${order.id}"><div class="order-card-top"><span class="order-number">#${order.id}</span><span class="order-time">há ${order.minutes} min</span></div><div class="customer">${order.customer}</div><div class="order-meta"><i data-lucide="clock"></i>${order.time} · ${order.type}</div><div class="item-list">${order.items.map(item=>`<div class="item"><strong>${item.qty}x ${item.name}</strong>${item.detail?`<span>- ${item.detail}</span>`:''}</div>`).join('')}</div><div class="order-info"><div class="info-line"><span>Pagamento</span><strong>${order.payment}</strong></div>${deliveryCheck?`<div class="info-line"><span>Código de entrega</span><strong>Aguardando validação</strong></div>`:order.deliveryCodeRequired&&order.deliveryVerifiedAt?`<div class="info-line"><span>Código de entrega</span><strong>Validado</strong></div>`:''}${confirmable?`<div class="info-line"><span>Status do pagamento</span><strong>Pendente</strong></div>`:order.status==='done'?`<div class="info-line"><span>Status do pagamento</span><strong>Confirmado</strong></div>`:''}<div class="info-line"><span>Entrega</span><strong>${order.type}</strong></div></div><div class="total-line"><span>Total</span><strong>${money(order.total)}</strong></div><div class="card-actions">${order.status==='new'?`<button class="button small" data-action="accept" data-id="${order.id}"><i data-lucide="arrow-right"></i>${meta.nextLabel}</button><button class="mini-action" data-action="reject" data-id="${order.id}" aria-label="Recusar pedido"><i data-lucide="x"></i></button>`:deliveryCheck?`<button class="button small" data-action="validate-delivery-code" data-id="${order.id}"><i data-lucide="key-round"></i>Validar código de entrega</button><button class="mini-action" data-action="details" data-id="${order.id}" aria-label="Ver detalhes"><i data-lucide="eye"></i></button>`:confirmable?`<button class="button small" data-action="confirm-payment" data-id="${order.id}"><i data-lucide="badge-check"></i>Confirmar pagamento</button><button class="mini-action" data-action="details" data-id="${order.id}" aria-label="Ver detalhes"><i data-lucide="eye"></i></button>`:order.status==='done'||order.status==='cancelled'?`<button class="button small secondary" data-action="details" data-id="${order.id}"><i data-lucide="eye"></i>Ver detalhes</button>`:`<button class="button small" data-action="advance" data-id="${order.id}">${meta.nextLabel}<i data-lucide="arrow-right"></i></button><button class="mini-action" data-action="details" data-id="${order.id}" aria-label="Ver detalhes"><i data-lucide="eye"></i></button>`}</div></article>`;
  }
'''
s,count=re.subn(r"  function orderCard\(order\)\{.*?\n  function boardColumn",order_card+"  function boardColumn",s,count=1,flags=re.S)
if count!=1: raise SystemExit('orderCard replacement failed')

old="async function confirmPayment(id){"
validate=r'''async function validateDeliveryCode(id){
    const order=orders.find(item=>item.id===id);if(!order||!needsDeliveryConfirmation(order))return;
    const raw=window.prompt(`Pedido #${id}\nDigite o código de entrega de 4 dígitos informado pelo cliente:`);
    if(raw===null)return;
    const code=String(raw).trim();
    if(!/^\d{4}$/.test(code)){showToast('O código deve ter exatamente 4 dígitos');return}
    const{data,error}=await db.rpc('confirmar_codigo_entrega',{p_order_id:id,p_codigo:code});
    if(error){console.error('Erro ao validar código de entrega:',error);showToast(error.message||'Não foi possível validar o código');return}
    if(!data){showToast('Código de entrega incorreto');return}
    await loadRealOrders({notify:false});
    document.querySelector('#detail-modal').classList.remove('show');
    showToast('Código confirmado. Entrega validada!');
  }
  async function confirmPayment(id){'''
if old not in s: raise SystemExit('confirmPayment marker not found')
s=s.replace(old,validate,1)

open_details=r'''  function openDetails(id){
    const order=orders.find(item=>item.id===id);if(!order)return;
    const meta=orderStatusMeta(order),deliveryCheck=needsDeliveryConfirmation(order),confirmable=canConfirmPayment(order);
    document.querySelector('#modal-content').innerHTML=`<div class="detail-summary"><strong>Pedido #${order.id} · ${statusMeta[order.status].label}</strong><span>${order.customer} · ${order.time} · ${order.type}</span><div class="item-list">${order.items.map(item=>`<div class="item"><strong>${item.qty}x ${item.name}</strong>${item.detail?`<span>- ${item.detail}</span>`:''}</div>`).join('')}</div><div class="info-line"><span>Pagamento</span><strong>${order.payment}</strong></div>${deliveryCheck?`<div class="info-line"><span>Código de entrega</span><strong>Aguardando validação</strong></div>`:order.deliveryCodeRequired&&order.deliveryVerifiedAt?`<div class="info-line"><span>Código de entrega</span><strong>Validado</strong></div>`:''}${confirmable?`<div class="info-line"><span>Status do pagamento</span><strong>Pendente</strong></div>`:order.status==='done'?`<div class="info-line"><span>Status do pagamento</span><strong>Confirmado</strong></div>`:''}<div class="total-line"><span>Total</span><strong>${money(order.total)}</strong></div></div><div class="modal-actions">${order.status==='new'?`<button class="button" data-action="accept" data-id="${order.id}">${meta.nextLabel}</button>`:deliveryCheck?`<button class="button" data-action="validate-delivery-code" data-id="${order.id}">Validar código de entrega</button>`:confirmable?`<button class="button" data-action="confirm-payment" data-id="${order.id}">Confirmar pagamento</button>`:!['done','cancelled'].includes(order.status)&&meta.next?`<button class="button" data-action="advance" data-id="${order.id}">${meta.nextLabel}</button>`:''}<button class="button secondary" data-close-modal>Fechar</button></div>`;
    document.querySelector('#detail-modal').classList.add('show');lucide.createIcons();
  }
'''
s,count=re.subn(r"  function openDetails\(id\)\{.*?\n  function showToast",open_details+"  function showToast",s,count=1,flags=re.S)
if count!=1: raise SystemExit('openDetails replacement failed')

old="if(action.dataset.action==='confirm-payment')confirmPayment(id);"
new="if(action.dataset.action==='validate-delivery-code')validateDeliveryCode(id);if(action.dataset.action==='confirm-payment')confirmPayment(id);"
if old not in s: raise SystemExit('action marker not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('admin patched')
