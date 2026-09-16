from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'data-lv-delivery-address' in s:
    raise SystemExit('delivery address display already present')

old_card = "<div class=\"info-line\"><span>Entrega</span><strong>${order.type}</strong></div></div><div class=\"total-line\">"
new_card = "<div class=\"info-line\"><span>Entrega</span><strong>${order.type}</strong></div>${order.type==='Entrega'?`<div class=\"info-line\" data-lv-delivery-address><span>Endereço</span><strong>${escapeMenuText(order.address||'Não informado')}</strong></div>`:''}</div><div class=\"total-line\">"
if old_card not in s:
    raise SystemExit('order card marker not found')
s = s.replace(old_card, new_card, 1)

old_detail = "${confirmable?`<div class=\"info-line\"><span>Status do pagamento</span><strong>Pendente</strong></div>`:order.status==='done'?`<div class=\"info-line\"><span>Status do pagamento</span><strong>Confirmado</strong></div>`:''}<div class=\"total-line\">"
new_detail = "${confirmable?`<div class=\"info-line\"><span>Status do pagamento</span><strong>Pendente</strong></div>`:order.status==='done'?`<div class=\"info-line\"><span>Status do pagamento</span><strong>Confirmado</strong></div>`:''}${order.type==='Entrega'?`<div class=\"info-line\" data-lv-delivery-address><span>Endereço</span><strong>${escapeMenuText(order.address||'Não informado')}</strong></div>`:''}<div class=\"total-line\">"
if old_detail not in s:
    raise SystemExit('order details marker not found')
s = s.replace(old_detail, new_detail, 1)

if s.count('data-lv-delivery-address') != 2:
    raise SystemExit('expected two delivery address displays')
if "order.type==='Entrega'" not in s or "escapeMenuText(order.address||'Não informado')" not in s:
    raise SystemExit('final validation markers missing')

p.write_text(s, encoding='utf-8')
print('delivery address display added to cards and details')
