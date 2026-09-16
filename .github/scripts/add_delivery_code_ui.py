from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')

old=".select('id,customer_name,order_type,payment_method,payment_status,paid_at,status,total,created_at')"
new=".select('id,customer_name,order_type,payment_method,payment_status,paid_at,status,total,delivery_code,created_at')"
if 'total,delivery_code,created_at' not in s:
    if old not in s: raise SystemExit('orders select anchor not found')
    s=s.replace(old,new,1)

old="paidAt:row.paid_at||null,total:Number(row.total||0),items}"
new="paidAt:row.paid_at||null,deliveryCode:row.delivery_code||null,total:Number(row.total||0),items}"
if 'deliveryCode:row.delivery_code||null' not in s:
    if old not in s: raise SystemExit('normalize order anchor not found')
    s=s.replace(old,new,1)

old="<div class=\"info-line\"><span>Pagamento</span><strong>${order.payment}</strong></div>${confirmable?"
new="<div class=\"info-line\"><span>Pagamento</span><strong>${order.payment}</strong></div>${order.deliveryCode?`<div class=\"info-line\"><span>Código de entrega</span><strong>🔐 ${order.deliveryCode}</strong></div>`:''}${confirmable?"
if '🔐 ${order.deliveryCode}' not in s:
    count=s.count(old)
    if count < 2: raise SystemExit(f'payment anchors found: {count}')
    s=s.replace(old,new,2)

path.write_text(s,encoding='utf-8')
print('Admin delivery code UI applied')
