from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# 1) History search UI
old='''<section class="view" id="view-history"><div class="page-head"><div><span class="eyebrow">Pedidos concluídos</span><h1>Histórico</h1><p>Consulte rapidamente o que já saiu da operação.</p></div><button class="button secondary" data-export-history><i data-lucide="download"></i>Exportar histórico</button></div><div class="history-table" id="history-table"></div></section>'''
new='''<section class="view" id="view-history"><div class="page-head"><div><span class="eyebrow">Pedidos concluídos</span><h1>Histórico</h1><p>Consulte rapidamente o que já saiu da operação.</p></div><button class="button secondary" data-export-history><i data-lucide="download"></i>Exportar histórico</button></div><div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;padding:0 2px"><i data-lucide="search" style="width:18px;color:var(--muted)"></i><input id="history-search" type="search" autocomplete="off" placeholder="Pesquisar por nome, # do pedido ou código LV-..." aria-label="Pesquisar histórico" style="width:min(520px,100%);height:44px;padding:0 14px;border:1px solid var(--line);border-radius:10px;background:var(--panel);color:var(--text);font:inherit"></div><div class="history-table" id="history-table"></div></section>'''
if old not in s: raise SystemExit('history section marker not found')
s=s.replace(old,new,1)

# 2) History state + text normalization
old="let orders=[];let currentFilter='all';let ordersChannel=null;let ordersRefreshTimer=null;let knownOrderIds=new Set();"
new="let orders=[];let currentFilter='all';let historySearch='';let ordersChannel=null;let ordersRefreshTimer=null;let knownOrderIds=new Set();\n  const normalizeHistorySearch=value=>String(value||'').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().trim();"
if old not in s: raise SystemExit('orders state marker not found')
s=s.replace(old,new,1)

# 3) Bring order_code from Supabase into the normalized order
old="paidAt:row.paid_at||null,deliveryCodeRequired:Boolean(row.delivery_code_required)"
new="paidAt:row.paid_at||null,orderCode:row.order_code||'',deliveryCodeRequired:Boolean(row.delivery_code_required)"
if old not in s: raise SystemExit('normalize order marker not found')
s=s.replace(old,new,1)

old="select('id,customer_name,order_type,payment_method,payment_status,paid_at,status,total,delivery_code_required,delivery_verified_at,created_at')"
new="select('id,order_code,customer_name,order_type,payment_method,payment_status,paid_at,status,total,delivery_code_required,delivery_verified_at,created_at')"
if old not in s: raise SystemExit('orders select marker not found')
s=s.replace(old,new,1)

# 4) Show public order code on active order cards
old='<span class="order-number">#${order.id}</span>'
new='<span class="order-number">#${order.id} · ${order.orderCode||\'Sem código\'}</span>'
if old not in s: raise SystemExit('order card number marker not found')
s=s.replace(old,new,1)

# 5) Searchable history, with order code displayed under the number
history_fn=r'''  function renderHistory(){
    const target=document.querySelector('#history-table');
    const query=normalizeHistorySearch(historySearch).replace(/^#\s*/, '');
    const rows=orders
      .filter(o=>(o.status==='done'&&o.paymentStatus==='paid')||o.status==='cancelled')
      .filter(order=>{
        if(!query)return true;
        const customer=normalizeHistorySearch(order.customer);
        const code=normalizeHistorySearch(order.orderCode);
        const number=String(order.id);
        return customer.includes(query)||code.includes(query)||number.includes(query);
      })
      .sort((a,b)=>b.id-a.id);
    target.innerHTML='<div class="table-head"><span>Pedido</span><span>Cliente</span><span>Data / horário</span><span>Total</span><span>Status</span><span></span></div>'+
      (rows.length?rows.map(order=>`<button class="table-row" data-action="details" data-id="${order.id}"><span><strong>#${order.id}</strong><small>${order.orderCode||'Sem código'}</small></span><span>${order.customer}</span><span>Hoje<small>${order.time}</small></span><span class="table-total">${money(order.total)}</span><span class="status ${order.status==='done'?'done':order.status==='cancelled'?'cancel':''}">${statusMeta[order.status].label}</span><span><i data-lucide="chevron-right"></i></span></button>`).join(''):'<div class="empty-column" style="padding:30px">Nenhum pedido encontrado para esta pesquisa.</div>');
    lucide.createIcons();
  }
'''
pattern=r"  function renderHistory\(\)\{.*?\n  function renderStats"
s,count=re.subn(pattern,lambda m: history_fn+"  function renderStats",s,count=1,flags=re.S)
if count!=1: raise SystemExit('renderHistory replacement failed')

# 6) Details include public order code
old='Pedido #${order.id} · ${statusMeta[order.status].label}'
new='Pedido #${order.id} · ${order.orderCode||\'Sem código\'} · ${statusMeta[order.status].label}'
if old not in s: raise SystemExit('details header marker not found')
s=s.replace(old,new,1)

# 7) New-order notification also surfaces the public code
old='`Pedido #${latest.id} de ${latest.customer} chegou agora.`'
new='`Pedido #${latest.id} · ${latest.orderCode||\'Sem código\'} de ${latest.customer} chegou agora.`'
if old not in s: raise SystemExit('notification marker not found')
s=s.replace(old,new,1)

# 8) Wire the search input
marker="  let expenses=[];"
listener="  document.querySelector('#history-search')?.addEventListener('input',event=>{historySearch=event.target.value;renderHistory()});\n"
if marker not in s: raise SystemExit('history listener marker not found')
s=s.replace(marker,listener+marker,1)

p.write_text(s,encoding='utf-8')
print('admin order-code search patched')
