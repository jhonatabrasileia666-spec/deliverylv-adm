from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')

# 1) Add Promotions navigation item right after Cardápio.
old_nav='<button class="nav-item" data-view="menu"><i data-lucide="book-open"></i><span>Cardápio</span></button><button class="nav-item" data-view="drivers">'
new_nav='<button class="nav-item" data-view="menu"><i data-lucide="book-open"></i><span>Cardápio</span></button><button class="nav-item" data-view="promotions"><i data-lucide="badge-percent"></i><span>Promoções</span></button><button class="nav-item" data-view="drivers">'
if old_nav not in s: raise SystemExit('nav anchor not found')
s=s.replace(old_nav,new_nav,1)

# 2) Move promotions panel out of Cardápio and into its own view.
promo_panel='<section class="promotion-admin-panel"><div class="promotion-admin-head"><div><span class="eyebrow">Destaques do cardápio</span><h2>Promoções</h2><p>Marque os produtos que entram em oferta e informe o desconto. Eles aparecem antes do cardápio do cliente.</p></div><div class="promotion-admin-actions"><span class="promotion-status" id="promotion-status">Carregando...</span><button class="button small" id="save-promotions" type="button"><i data-lucide="badge-percent"></i>Salvar promoções</button></div></div><div class="promotion-manager" id="promotion-manager"><div class="promotion-empty">Carregando produtos...</div></div></section>'
if promo_panel not in s: raise SystemExit('promotion panel not found')
s=s.replace(promo_panel,'',1)

menu_end='<div class="menu-table"><div class="table-head"><span>Produto</span><span>Categoria</span><span>Preço</span><span>Acréscimo</span><span>Disponibilidade</span><span></span></div></div></section>\n        <section class="view" id="view-drivers">'
promo_view='''<div class="menu-table"><div class="table-head"><span>Produto</span><span>Categoria</span><span>Preço</span><span>Acréscimo</span><span>Disponibilidade</span><span></span></div></div></section>
        <section class="view" id="view-promotions"><div class="page-head"><div><span class="eyebrow">Ofertas e destaques</span><h1>Promoções</h1><p>Escolha os produtos, o tamanho e o desconto que aparecem em destaque no cardápio do cliente.</p></div><div class="head-actions"><button class="button secondary" data-refresh-menu type="button"><i data-lucide="refresh-cw"></i>Atualizar promoções</button></div></div>'''+promo_panel+'''</section>
        <section class="view" id="view-drivers">'''
if menu_end not in s: raise SystemExit('menu end anchor not found')
s=s.replace(menu_end,promo_view,1)

# 3) Load menu data for both the Cardápio and Promoções views.
old_switch="if(view==='orders')renderBoard('orders-board');if(view==='menu')loadRealMenu();if(view==='drivers')loadDrivers();"
new_switch="if(view==='orders')renderBoard('orders-board');if(view==='menu'||view==='promotions')loadRealMenu();if(view==='drivers')loadDrivers();"
if old_switch not in s: raise SystemExit('switchView anchor not found')
s=s.replace(old_switch,new_switch,1)

# 4) Six bottom navigation slots on mobile.
old_mobile='@media(max-width:700px){.nav{grid-template-columns:repeat(5,1fr)}.nav-item{min-width:0}.nav-item span{font-size:8px}}'
new_mobile='@media(max-width:700px){.nav{grid-template-columns:repeat(6,1fr)}.nav-item{min-width:0;padding-left:3px;padding-right:3px}.nav-item span{font-size:7px}}'
if old_mobile not in s: raise SystemExit('mobile nav anchor not found')
s=s.replace(old_mobile,new_mobile,1)

path.write_text(s,encoding='utf-8')
print('separate promotions view applied')
