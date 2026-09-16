from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

head_marker='  <meta name="theme-color" content="#11100f">\n'
head_add='''  <meta name="theme-color" content="#11100f">\n  <meta name="application-name" content="Delivery LV">\n  <meta name="mobile-web-app-capable" content="yes">\n  <meta name="apple-mobile-web-app-capable" content="yes">\n  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n  <meta name="apple-mobile-web-app-title" content="Delivery LV">\n  <link rel="manifest" href="./manifest.webmanifest">\n  <link rel="icon" href="./pwa-icon-192.svg" type="image/svg+xml">\n  <link rel="apple-touch-icon" href="./pwa-icon-192.svg">\n'''
if '<link rel="manifest" href="./manifest.webmanifest">' not in s:
    if head_marker not in s: raise SystemExit('theme meta marker not found')
    s=s.replace(head_marker,head_add,1)

style='''\n<style id="pwa-install-styles">\n  .pwa-install-button{position:fixed;z-index:80;right:16px;bottom:84px;display:none;align-items:center;gap:8px;min-height:44px;padding:0 15px;border:1px solid #ff5a1670;border-radius:11px;background:#ff5a16;color:#1b110b;box-shadow:0 14px 34px #0008;font-size:11px;font-weight:900}\n  .pwa-install-button.show{display:inline-flex}.pwa-install-button svg{width:16px;height:16px}\n  @media(min-width:701px){.pwa-install-button{bottom:22px}}\n</style>\n'''
script='''\n<button class="pwa-install-button" id="pwa-install-button" type="button" aria-label="Instalar aplicativo"><i data-lucide="download"></i><span>Instalar aplicativo</span></button>\n<script id="panel-pwa-module">\n(()=>{\n  const installButton=document.querySelector('#pwa-install-button');\n  let deferredInstallPrompt=null;\n  const standalone=()=>window.matchMedia('(display-mode: standalone)').matches||window.navigator.standalone===true;\n  const refreshInstallButton=()=>{if(!installButton)return;installButton.classList.toggle('show',Boolean(deferredInstallPrompt)&&!standalone());if(window.lucide)lucide.createIcons()};\n\n  if('serviceWorker' in navigator){\n    window.addEventListener('load',()=>{\n      navigator.serviceWorker.register('./notification-sw.js',{scope:'./'}).catch(error=>console.error('Erro ao registrar PWA:',error));\n    });\n  }\n\n  window.addEventListener('beforeinstallprompt',event=>{\n    event.preventDefault();\n    deferredInstallPrompt=event;\n    refreshInstallButton();\n  });\n\n  installButton?.addEventListener('click',async()=>{\n    if(!deferredInstallPrompt)return;\n    installButton.disabled=true;\n    try{\n      await deferredInstallPrompt.prompt();\n      await deferredInstallPrompt.userChoice;\n      deferredInstallPrompt=null;\n      refreshInstallButton();\n    }finally{installButton.disabled=false}\n  });\n\n  window.addEventListener('appinstalled',()=>{deferredInstallPrompt=null;refreshInstallButton()});\n  refreshInstallButton();\n})();\n</script>\n'''

if 'id="pwa-install-styles"' not in s:
    body_marker='</head>'
    if body_marker not in s: raise SystemExit('head close marker not found')
    s=s.replace(body_marker,style+body_marker,1)

if 'id="panel-pwa-module"' not in s:
    end_marker='\n</body>'
    if end_marker not in s: raise SystemExit('body close marker not found')
    s=s.replace(end_marker,script+end_marker,1)

p.write_text(s,encoding='utf-8')
print('PWA metadata and install flow added')
