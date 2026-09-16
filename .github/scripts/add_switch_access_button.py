from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# The admin header already has switch-login-button and the driver header already has Trocar acesso.
# Only wire the admin button to close its current session and return to the central login screen.
if 'id="switch-login-button"' not in s:
    raise SystemExit('existing admin switch-login-button not found')
if 'id="driver-logout"' not in s:
    raise SystemExit('driver switch button not found')

marker="  modeBar.addEventListener('click',event=>{const button=event.target.closest('[data-login-mode]');if(button)setLoginMode(button.dataset.loginMode)});"
insert="""  modeBar.addEventListener('click',event=>{const button=event.target.closest('[data-login-mode]');if(button)setLoginMode(button.dataset.loginMode)});\n  const switchLoginButton=document.querySelector('#switch-login-button');\n  if(switchLoginButton){\n    switchLoginButton.onclick=async()=>{\n      await clearPanelSession({serverLogout:true,message:'Escolha como deseja entrar.'});\n      setLoginMode('admin');\n    };\n  }"""
if marker not in s:
    raise SystemExit('login mode marker not found')
s=s.replace(marker,insert,1)

style='''\n  <style id="switch-access-button-styles">\n    #switch-login-button{white-space:nowrap}\n    @media(max-width:700px){\n      #switch-login-button{min-height:36px;padding:0 9px;font-size:9px}\n      #switch-login-button svg{width:14px;height:14px}\n      .top-right{gap:6px}\n    }\n  </style>\n'''
if 'switch-access-button-styles' not in s:
    s=s.replace('</head>',style+'</head>',1)

p.write_text(s,encoding='utf-8')
print('existing switch access button wired')
