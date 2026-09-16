from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='<div class="top-right"><span class="top-status"><i class="live-dot"></i>Operação ativa</span><button class="user" id="account-button" type="button" aria-label="Abrir conta"><span id="account-label">Conta</span><span class="avatar" id="account-avatar">LV</span></button></div>'
new='<div class="top-right"><span class="top-status"><i class="live-dot"></i>Operação ativa</span><button class="button secondary small" id="switch-access-button" type="button"><i data-lucide="repeat-2"></i>Trocar acesso</button><button class="user" id="account-button" type="button" aria-label="Abrir conta"><span id="account-label">Conta</span><span class="avatar" id="account-avatar">LV</span></button></div>'
if old not in s: raise SystemExit('admin topbar marker not found')
s=s.replace(old,new,1)

old='<button class="button secondary small" id="driver-logout" type="button"><i data-lucide="log-out"></i>Sair</button>'
new='<button class="button secondary small" id="driver-logout" type="button"><i data-lucide="repeat-2"></i>Trocar acesso</button>'
if old not in s: raise SystemExit('driver logout marker not found')
s=s.replace(old,new,1)

marker="  document.querySelector('#account-button').onclick=async()=>{"
insert="  document.querySelector('#switch-access-button').onclick=()=>clearPanelSession({serverLogout:true,message:'Escolha o acesso que deseja usar.'});\n\n"
if marker not in s: raise SystemExit('account button marker not found')
s=s.replace(marker,insert+marker,1)

style='''\n  <style id="switch-access-button-styles">\n    #switch-access-button{white-space:nowrap}\n    @media(max-width:700px){\n      #switch-access-button{min-height:36px;padding:0 9px;font-size:9px}\n      #switch-access-button svg{width:14px;height:14px}\n      .top-right{gap:6px}\n    }\n  </style>\n'''
if 'switch-access-button-styles' not in s:
    s=s.replace('</head>',style+'</head>',1)

p.write_text(s,encoding='utf-8')
print('switch access button patched')
