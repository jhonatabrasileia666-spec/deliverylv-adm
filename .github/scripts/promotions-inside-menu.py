from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')

# Remove Promoções from the main navigation.
old_nav='<button class="nav-item" data-view="menu"><i data-lucide="book-open"></i><span>Cardápio</span></button><button class="nav-item" data-view="promotions"><i data-lucide="badge-percent"></i><span>Promoções</span></button><button class="nav-item" data-view="drivers">'
new_nav='<button class="nav-item" data-view="menu"><i data-lucide="book-open"></i><span>Cardápio</span></button><button class="nav-item" data-view="drivers">'
if old_nav not in s: raise SystemExit('main navigation anchor not found')
s=s.replace(old_nav,new_nav,1)

# Replace the separate Cardápio and Promoções views with one Cardápio view containing local tabs.
old_block='''<section class="view" id="view-menu"><div class="page-head"><div><span class="eyebrow">Gestão do cardápio</span><h1>Cardápio</h1><p>Adicione e edite produtos, tamanhos, preços, fotos, acréscimos e disponibilidade.</p></div><div class="head-actions"><button class="button" data-add-product type="button"><i data-lucide="plus"></i>Adicionar produto</button><button class="button secondary" data-refresh-menu type="button"><i data-lucide="refresh-cw"></i>Atualizar cardápio</button></div></div><div class="menu-toolbar"><div><span class="eyebrow">Produtos cadastrados</span></div><span class="menu-help">As alterações salvas aparecem no cardápio do cliente.</span></div><div class="menu-table"><div class="table-head"><span>Produto</span><span>Categoria</span><span>Preço</span><span>Acréscimo</span><span>Disponibilidade</span><span></span></div></div></section>
        <section class="view" id="view-promotions"><div class="page-head"><div><span class="eyebrow">Ofertas e destaques</span><h1>Promoções</h1><p>Escolha os produtos, o tamanho e o desconto que aparecem em destaque no cardápio do cliente.</p></div><div class="head-actions"><button class="button secondary" data-refresh-menu type="button"><i data-lucide="refresh-cw"></i>Atualizar promoções</button></div></div><section class="promotion-admin-panel"><div class="promotion-admin-head"><div><span class="eyebrow">Destaques do cardápio</span><h2>Promoções</h2><p>Marque os produtos que entram em oferta e informe o desconto. Eles aparecem antes do cardápio do cliente.</p></div><div class="promotion-admin-actions"><span class="promotion-status" id="promotion-status">Carregando...</span><button class="button small" id="save-promotions" type="button"><i data-lucide="badge-percent"></i>Salvar promoções</button></div></div><div class="promotion-manager" id="promotion-manager"><div class="promotion-empty">Carregando produtos...</div></div></section></section>'''

new_block='''<section class="view" id="view-menu"><div class="page-head"><div><span class="eyebrow">Gestão do cardápio</span><h1>Cardápio</h1><p>Gerencie produtos e promoções sem misturar as duas áreas.</p></div></div><div class="menu-subtabs" role="tablist" aria-label="Áreas do cardápio"><button class="menu-subtab active" type="button" role="tab" aria-selected="true" data-menu-subview="products"><i data-lucide="book-open"></i><span>Produtos</span></button><button class="menu-subtab" type="button" role="tab" aria-selected="false" data-menu-subview="promotions"><i data-lucide="badge-percent"></i><span>Promoções</span></button></div><div class="menu-subview active" id="menu-subview-products" data-menu-panel="products"><div class="menu-subview-actions"><div><span class="eyebrow">Produtos cadastrados</span><p class="menu-help">Adicione e edite produtos, tamanhos, preços, fotos, acréscimos e disponibilidade.</p></div><div class="head-actions"><button class="button" data-add-product type="button"><i data-lucide="plus"></i>Adicionar produto</button><button class="button secondary" data-refresh-menu type="button"><i data-lucide="refresh-cw"></i>Atualizar cardápio</button></div></div><div class="menu-table"><div class="table-head"><span>Produto</span><span>Categoria</span><span>Preço</span><span>Acréscimo</span><span>Disponibilidade</span><span></span></div></div></div><div class="menu-subview" id="menu-subview-promotions" data-menu-panel="promotions"><div class="menu-subview-actions"><div><span class="eyebrow">Ofertas e destaques</span><p class="menu-help">Escolha produto, tamanho e desconto para destacar no cardápio do cliente.</p></div><button class="button secondary" data-refresh-menu type="button"><i data-lucide="refresh-cw"></i>Atualizar promoções</button></div><section class="promotion-admin-panel"><div class="promotion-admin-head"><div><span class="eyebrow">Destaques do cardápio</span><h2>Promoções</h2><p>Marque os produtos que entram em oferta e informe o desconto. Eles aparecem antes do cardápio do cliente.</p></div><div class="promotion-admin-actions"><span class="promotion-status" id="promotion-status">Carregando...</span><button class="button small" id="save-promotions" type="button"><i data-lucide="badge-percent"></i>Salvar promoções</button></div></div><div class="promotion-manager" id="promotion-manager"><div class="promotion-empty">Carregando produtos...</div></div></section></div></section>'''
if old_block not in s: raise SystemExit('menu/promotions views anchor not found')
s=s.replace(old_block,new_block,1)

# Restore five main navigation buttons on mobile.
old_mobile='@media(max-width:700px){.nav{grid-template-columns:repeat(6,1fr)}.nav-item{min-width:0;padding-left:3px;padding-right:3px}.nav-item span{font-size:7px}}'
new_mobile='@media(max-width:700px){.nav{grid-template-columns:repeat(5,1fr)}.nav-item{min-width:0}.nav-item span{font-size:8px}}'
if old_mobile not in s: raise SystemExit('mobile navigation anchor not found')
s=s.replace(old_mobile,new_mobile,1)

# Add local Cardápio tab styling before the existing promotion styles.
css_anchor='  .promotion-admin-panel{margin:0 0 26px;'
css='''  .menu-subtabs{display:grid;grid-template-columns:repeat(2,minmax(0,220px));gap:10px;margin:-6px 0 24px;padding-bottom:18px;border-bottom:1px solid var(--line)}
  .menu-subtab{min-height:48px;display:flex;align-items:center;justify-content:center;gap:9px;padding:0 18px;border:1px solid var(--line);border-radius:11px;background:var(--panel);color:var(--muted);font-size:12px;font-weight:900;transition:.2s}.menu-subtab svg{width:17px}.menu-subtab:hover{border-color:#ff5a1670;color:var(--text)}.menu-subtab.active{background:var(--orange);border-color:var(--orange);color:#1b110b;box-shadow:0 8px 24px #ff5a1620}.menu-subview{display:none}.menu-subview.active{display:block;animation:view-in .22s ease}.menu-subview-actions{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:15px}.menu-subview-actions .menu-help{margin:5px 0 0}
  @media(max-width:700px){.menu-subtabs{grid-template-columns:1fr 1fr;gap:8px;margin-top:-4px}.menu-subtab{min-height:46px;padding:0 10px}.menu-subview-actions{align-items:stretch;flex-direction:column}.menu-subview-actions .head-actions{display:grid;grid-template-columns:1fr 1fr;width:100%}.menu-subview-actions>.button{width:100%}}
'''
if css_anchor not in s: raise SystemExit('promotion css anchor not found')
s=s.replace(css_anchor,css+css_anchor,1)

# Cardápio is now the only main view that loads menu data.
old_switch="if(view==='orders')renderBoard('orders-board');if(view==='menu'||view==='promotions')loadRealMenu();if(view==='drivers')loadDrivers();"
new_switch="if(view==='orders')renderBoard('orders-board');if(view==='menu'){switchMenuSubview('products');loadRealMenu()}if(view==='drivers')loadDrivers();"
if old_switch not in s: raise SystemExit('switch view anchor not found')
s=s.replace(old_switch,new_switch,1)

# Add local tab switching helper before switchView.
anchor='  function switchView(view){'
helper='''  function switchMenuSubview(name){
    const target=name==='promotions'?'promotions':'products';
    document.querySelectorAll('[data-menu-subview]').forEach(button=>{const active=button.dataset.menuSubview===target;button.classList.toggle('active',active);button.setAttribute('aria-selected',active?'true':'false')});
    document.querySelectorAll('[data-menu-panel]').forEach(panel=>panel.classList.toggle('active',panel.dataset.menuPanel===target));
    if(target==='promotions')loadRealMenu();
  }
'''
if anchor not in s: raise SystemExit('switchView function anchor not found')
s=s.replace(anchor,helper+anchor,1)

# Handle clicks on Products/Promoções local tabs.
old_click="document.addEventListener('click',event=>{const nav=event.target.closest('[data-view]');if(nav)switchView(nav.dataset.view);const jump=event.target.closest('[data-view-jump]');"
new_click="document.addEventListener('click',event=>{const menuSubtab=event.target.closest('[data-menu-subview]');if(menuSubtab){switchMenuSubview(menuSubtab.dataset.menuSubview);return}const nav=event.target.closest('[data-view]');if(nav)switchView(nav.dataset.view);const jump=event.target.closest('[data-view-jump]');"
if old_click not in s: raise SystemExit('document click anchor not found')
s=s.replace(old_click,new_click,1)

path.write_text(s,encoding='utf-8')
print('promotions moved inside Cardapio tabs')
