const CACHE_NAME='deliverylv-panel-v1';
const APP_SHELL=['./','./index.html','./manifest.webmanifest','./pwa-icon-192.svg','./pwa-icon-512.svg'];

self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE_NAME).then(cache=>cache.addAll(APP_SHELL)).then(()=>self.skipWaiting()));
});

self.addEventListener('activate',event=>{
  event.waitUntil((async()=>{
    const keys=await caches.keys();
    await Promise.all(keys.filter(key=>key!==CACHE_NAME).map(key=>caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch',event=>{
  const request=event.request;
  if(request.method!=='GET')return;
  const url=new URL(request.url);

  if(url.hostname.includes('supabase.co'))return;

  if(request.mode==='navigate'){
    event.respondWith((async()=>{
      try{
        const fresh=await fetch(request);
        const cache=await caches.open(CACHE_NAME);
        cache.put('./index.html',fresh.clone());
        return fresh;
      }catch(error){
        return (await caches.match('./index.html'))||(await caches.match('./'));
      }
    })());
    return;
  }

  if(['script','style','font','image'].includes(request.destination)||url.origin===self.location.origin){
    event.respondWith((async()=>{
      const cached=await caches.match(request);
      const network=fetch(request).then(async response=>{
        if(response&&response.status<400){
          const cache=await caches.open(CACHE_NAME);
          cache.put(request,response.clone());
        }
        return response;
      }).catch(()=>null);
      return cached||(await network)||Response.error();
    })());
  }
});

self.addEventListener('notificationclick',event=>{
  event.notification.close();
  event.waitUntil((async()=>{
    const windows=await self.clients.matchAll({type:'window',includeUncontrolled:true});
    if(windows.length){await windows[0].focus();return}
    await self.clients.openWindow('./');
  })());
});
