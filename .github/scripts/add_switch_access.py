from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='<div class="top-right"><span class="top-status"><i class="live-dot"></i>Operação ativa</span><button class="user" id="account-button" type="button" aria-label="Abrir conta">'
new='<div class="top-right"><span class="top-status"><i class="live-dot"></i>Operação ativa</span><button class="button secondary small" id="switch-login-button" type="button"><i data-lucide="log-in"></i>Trocar acesso</button><button class="user" id="account-button" type="button" aria-label="Abrir conta">'
if old not in s: raise SystemExit('admin topbar marker not found')
s=s.replace(old,new,1)

old='<button class="button secondary small" id="driver-logout" type="button"><i data-lucide="log-out"></i>Sair</button>'
new='<button class="button secondary small" id="driver-logout" type="button"><i data-lucide="arrow-left-right"></i>Trocar acesso</button>'
if old not in s: raise SystemExit('driver logout marker not found')
s=s.replace(old,new,1)

old="document.querySelector('#logout-button').onclick=()=>clearPanelSession({serverLogout:true});"
new="document.querySelector('#logout-button').onclick=()=>clearPanelSession({serverLogout:true});\n  document.querySelector('#switch-login-button').onclick=async()=>{await clearPanelSession({serverLogout:true,message:'Escolha como deseja entrar.'});document.querySelector('[data-login-mode=\"admin\"]')?.click();};"
if old not in s: raise SystemExit('admin logout handler marker not found')
s=s.replace(old,new,1)

old="document.querySelector('#driver-logout').onclick=()=>clearDriverSession();document.querySelector('#driver-refresh').onclick=()=>loadDriverOrders();"
new="document.querySelector('#driver-logout').onclick=async()=>{await clearDriverSession('Escolha como deseja entrar.');document.querySelector('[data-login-mode=\"admin\"]')?.click();};document.querySelector('#driver-refresh').onclick=()=>loadDriverOrders();"
if old not in s: raise SystemExit('driver handler marker not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('switch access buttons patched')
