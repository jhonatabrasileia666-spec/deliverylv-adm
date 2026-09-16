from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Correct local system-notification icon.
old="icon:'./icon-192.png'"
if old not in s: raise SystemExit('old notification icon marker not found')
s=s.replace(old,"icon:'./pwa-icon-192.svg'",1)

# Add a single way to stop every local siren/timer.
old="function stop(key){const timer=timers.get(key);if(timer)clearInterval(timer);timers.delete(key);document.querySelector(`.lv-urgent-alert[data-alert-key=\"${CSS.escape(key)}\"]`)?.remove()}\n  function start(key,title,body,{repeats=1200,interval=3000}={})"
new="function stop(key){const timer=timers.get(key);if(timer)clearInterval(timer);timers.delete(key);document.querySelector(`.lv-urgent-alert[data-alert-key=\"${CSS.escape(key)}\"]`)?.remove()}\n  function stopAll(){[...timers.keys()].forEach(stop);document.querySelectorAll('.lv-urgent-alert').forEach(node=>node.remove())}\n  function start(key,title,body,{repeats=1200,interval=3000}={})"
if old not in s: raise SystemExit('LVAlerts stop marker not found')
s=s.replace(old,new,1)

old="return{start,stop,enable,prime:getAudio,updateButtons};"
new="return{start,stop,stopAll,enable,prime:getAudio,updateButtons};"
if old not in s: raise SystemExit('LVAlerts export marker not found')
s=s.replace(old,new,1)

# When Web Push is stopped/acknowledged, stop ALL local sirens too.
old="function hideBanner(){banner?.classList.remove('show');window.LVAlerts?.stop?.('server-push');currentAlert=null}"
new="function hideBanner(){banner?.classList.remove('show');window.LVAlerts?.stopAll?.();currentAlert=null}"
if old not in s: raise SystemExit('hideBanner marker not found')
s=s.replace(old,new,1)

# Closing the admin new-order notice also acknowledges an active server push.
old="document.querySelector('#close-notice').onclick=()=>{document.querySelector('#notification').classList.remove('show');window.LVAlerts?.stop('admin-new-order')};"
new="document.querySelector('#close-notice').onclick=async()=>{document.querySelector('#notification').classList.remove('show');window.LVAlerts?.stopAll?.();await window.LVBackgroundPush?.stopCurrent?.()};"
if old not in s: raise SystemExit('close notice marker not found')
s=s.replace(old,new,1)

checks=["icon:'./pwa-icon-192.svg'","function stopAll()","stopAll,enable","window.LVAlerts?.stopAll?.()","await window.LVBackgroundPush?.stopCurrent?.()"]
for marker in checks:
    if marker not in s: raise SystemExit('missing final marker: '+marker)
if "icon:'./icon-192.png'" in s: raise SystemExit('old icon remains')

p.write_text(s,encoding='utf-8')
print('alert stop unified and notification icon corrected')
