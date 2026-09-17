from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

# Remove Promoções da navegação principal.
promo_nav = '<button class="nav-item" data-view="promotions"><i data-lucide="badge-percent"></i><span>Promoções</span></button>'
if promo_nav not in s:
    raise SystemExit('promotion nav not found')
s = s.replace(promo_nav, '', 1)

# Extrai o painel de promoções da view separada e remove a view inteira.
promo_view_start = s.index('        <section class="view" id="view-promotions">')
drivers_start = s.index('        <section class="view" id="view-drivers">', promo_view_start)
promo_view = s[promo_view_start:drivers_start]
panel_start = promo_view.index('<section class="promotion-admin-panel">')
panel_end = promo_view.index('</section>', panel_start) + len('</section>')
promo_panel = promo_view[panel_start:panel_end]
s = s[:promo_view_start] + s[drivers_start:]

# Reconstrói a view Cardápio com subtabs Produtos | Promoções.
menu_start = s.index('        <section class="view" id="view-menu">')
drivers_start = s.index('        <section class="view" id="view-drivers">', menu_start)
menu_view = s[menu_start:drivers_start]
open_tag = '        <section class="view" id="view-menu">'
body = menu_view[len(open_tag):]
close_pos = body.rfind('</section>')
if close_pos < 0:
    raise SystemExit('menu closing section not found')
inner = body[:close_pos]
products_marker = '<div class="menu-toolbar">'
products_start = inner.index(products_marker)
header = inner[:products_start]
products = inner[products_start:]

tabs = '''<div class="menu-subtabs" role="tablist" aria-label="Seções do cardápio"><button type="button" class="menu-subtab active" data-menu-subtab="products" role="tab" aria-selected="true"><i data-lucide="book-open"></i><span>Produtos</span></button><button type="button" class="menu-subtab" data-menu-subtab="promotions" role="tab" aria-selected="false"><i data-lucide="badge-percent"></i><span>Promoções</span></button></div>'''
new_menu = open_tag + header + tabs + '<div class="menu-subpanel active" data-menu-subpanel="products">' + products + '</div><div class="menu-subpanel" data-menu-subpanel="promotions">' + promo_panel + '</div></section>\n'
s = s[:menu_start] + new_menu + s[drivers_start:]

# A antiga view Promoções não existe mais; carregar dados apenas ao entrar em Cardápio.
s = s.replace("if(view==='menu'||view==='promotions')loadRealMenu();", "if(view==='menu')loadRealMenu();", 1)

# Estilo das subtabs internas.
css = '''\n  <style id="menu-subtabs-style">\n    .menu-subtabs{display:grid;grid-template-columns:repeat(2,minmax(0,210px));gap:9px;margin:-4px 0 22px;padding:5px;width:max-content;max-width:100%;background:#171412;border:1px solid var(--line);border-radius:13px}\n    .menu-subtab{min-height:45px;display:flex;align-items:center;justify-content:center;gap:9px;padding:0 18px;background:transparent;border:1px solid transparent;border-radius:9px;color:var(--muted);font-size:12px;font-weight:900;transition:.2s}\n    .menu-subtab svg{width:17px;height:17px}.menu-subtab:hover{color:var(--text);border-color:#ffffff12}.menu-subtab.active{background:var(--orange);border-color:var(--orange);color:#1b110b;box-shadow:0 8px 22px #ff5a1620}\n    .menu-subpanel{display:none}.menu-subpanel.active{display:block;animation:view-in .22s ease}\n    #view-menu.menu-tab-promotions>.page-head .head-actions{display:none}\n    #view-menu.menu-tab-promotions .promotion-admin-panel{margin-top:0}\n    @media(max-width:700px){.menu-subtabs{width:100%;grid-template-columns:1fr 1fr;margin-top:-6px;margin-bottom:18px}.menu-subtab{min-height:48px;padding:0 10px;font-size:11px}.menu-subtab span{display:inline!important}}\n  </style>\n'''
if 'id="menu-subtabs-style"' in s:
    raise SystemExit('menu subtabs style already exists')
s = s.replace('</head>', css + '</head>', 1)

# Comportamento: alterna painéis sem rolar uma seção enorme.
js = '''\n<script id="menu-subtabs-script">\n  function switchMenuSubtab(tab){\n    const view=document.querySelector('#view-menu');\n    if(!view)return;\n    const target=tab==='promotions'?'promotions':'products';\n    view.classList.toggle('menu-tab-promotions',target==='promotions');\n    view.querySelectorAll('[data-menu-subtab]').forEach(button=>{const active=button.dataset.menuSubtab===target;button.classList.toggle('active',active);button.setAttribute('aria-selected',active?'true':'false')});\n    view.querySelectorAll('[data-menu-subpanel]').forEach(panel=>panel.classList.toggle('active',panel.dataset.menuSubpanel===target));\n    if(target==='promotions')loadRealMenu();\n    window.scrollTo({top:0,behavior:'smooth'});\n  }\n  document.addEventListener('click',event=>{\n    const tab=event.target.closest('[data-menu-subtab]');\n    if(tab){event.preventDefault();switchMenuSubtab(tab.dataset.menuSubtab);return}\n    const menuNav=event.target.closest('[data-view="menu"]');\n    if(menuNav)setTimeout(()=>switchMenuSubtab('products'),0);\n  });\n</script>\n'''
if 'id="menu-subtabs-script"' in s:
    raise SystemExit('menu subtabs script already exists')
s = s.replace('</body>', js + '</body>', 1)

path.write_text(s, encoding='utf-8')
print('promotions nested inside menu view')
