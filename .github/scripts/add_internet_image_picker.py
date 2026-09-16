from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

if 'internet-image-picker-upgrade' in s:
    print('internet image picker already installed')
    raise SystemExit(0)

css = r'''
<style id="internet-image-picker-styles">
  .internet-image-search{display:grid;gap:10px}
  .internet-image-search-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px}
  .internet-image-search-row input{min-width:0;width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:9px;background:#141210;color:var(--text);font:inherit}
  .internet-image-search-row input:focus{border-color:var(--orange);outline:none}
  .internet-image-search-row button{min-width:92px;padding:0 13px;border-radius:9px;background:var(--orange);color:#1b110b;font-size:11px;font-weight:900}
  .internet-image-status{min-height:16px;color:var(--muted);font-size:10px;line-height:1.45}
  .internet-image-results{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;max-height:360px;overflow:auto;padding-right:2px}
  .internet-image-card{position:relative;display:block;min-width:0;padding:0;overflow:hidden;border:2px solid transparent;border-radius:10px;background:#171411;aspect-ratio:1/1}
  .internet-image-card:hover{border-color:#ff5a1680}
  .internet-image-card.selected{border-color:var(--lime);box-shadow:0 0 0 2px #d9f15c25}
  .internet-image-card img{width:100%;height:100%;object-fit:cover}
  .internet-image-card span{position:absolute;right:0;bottom:0;left:0;padding:22px 7px 6px;background:linear-gradient(transparent,#000c);color:#fff;font-size:9px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:left}
  .internet-image-card.selected:after{content:'✓';position:absolute;top:6px;right:6px;width:24px;height:24px;display:grid;place-items:center;border-radius:50%;background:var(--lime);color:#111;font-weight:900}
  .internet-image-note{margin:0;color:#81776f;font-size:9px;line-height:1.45}
  @media(max-width:700px){.internet-image-results{grid-template-columns:repeat(2,minmax(0,1fr));max-height:330px}.internet-image-search-row{grid-template-columns:1fr}.internet-image-search-row button{min-height:42px}}
</style>
'''

js = r'''
<script id="internet-image-picker-upgrade">
(()=>{
  const previousBindProductForm=bindProductForm;
  bindProductForm=function(item=null){
    previousBindProductForm(item);

    const panel=document.querySelector('[data-image-panel="url"]');
    const tab=document.querySelector('[data-image-source="url"]');
    const hidden=document.querySelector('#edit-product-image');
    const preview=document.querySelector('#product-image-preview');
    const fileInput=document.querySelector('#edit-product-file');
    const nameInput=document.querySelector('#edit-product-name');
    const helper=document.querySelector('.product-image-preview span');
    if(!panel||!tab||!hidden||!preview)return;

    if(helper)helper.textContent='Escolha uma foto da galeria ou pesquise e selecione uma imagem da internet.';
    tab.innerHTML='<i data-lucide="search"></i> Internet';

    hidden.type='hidden';
    hidden.removeAttribute('inputmode');
    hidden.removeAttribute('placeholder');
    panel.innerHTML='';
    panel.appendChild(hidden);

    const searchBox=document.createElement('div');
    searchBox.className='internet-image-search';

    const row=document.createElement('div');
    row.className='internet-image-search-row';

    const queryInput=document.createElement('input');
    queryInput.id='internet-image-query';
    queryInput.type='search';
    queryInput.autocomplete='off';
    queryInput.placeholder='Ex.: pizza calabresa, esfirra de carne...';

    const searchButton=document.createElement('button');
    searchButton.type='button';
    searchButton.innerHTML='<i data-lucide="search"></i> Buscar';

    const status=document.createElement('div');
    status.className='internet-image-status';
    status.textContent='Digite o que deseja e toque em Buscar.';

    const results=document.createElement('div');
    results.className='internet-image-results';

    const note=document.createElement('p');
    note.className='internet-image-note';
    note.textContent='Busca feita no Wikimedia Commons. As imagens possuem licenças próprias; confira a licença/origem antes do uso comercial.';

    row.append(queryInput,searchButton);
    searchBox.append(row,status,results,note);
    panel.appendChild(searchBox);

    const setSelected=(button,url)=>{
      if(!url)return;
      hidden.value=url;
      preview.src=url;
      if(fileInput)fileInput.value='';
      results.querySelectorAll('.internet-image-card').forEach(card=>card.classList.toggle('selected',card===button));
      status.textContent='Imagem selecionada. Agora é só salvar o produto.';
    };

    const renderResults=pages=>{
      results.innerHTML='';
      const usable=pages
        .map(page=>({page,info:page.imageinfo?.[0]}))
        .filter(entry=>entry.info&&String(entry.info.mime||'').startsWith('image/')&&(entry.info.thumburl||entry.info.url))
        .slice(0,12);
      if(!usable.length){
        status.textContent='Não encontrei imagens para essa busca. Tente outras palavras.';
        return;
      }
      status.textContent=`${usable.length} imagens encontradas. Toque em uma para escolher.`;
      usable.forEach(({page,info})=>{
        const button=document.createElement('button');
        button.type='button';
        button.className='internet-image-card';
        const imageUrl=info.thumburl||info.url;
        const img=document.createElement('img');
        img.loading='lazy';
        img.alt=String(page.title||'Imagem encontrada').replace(/^File:/i,'');
        img.src=imageUrl;
        const label=document.createElement('span');
        label.textContent=img.alt;
        button.append(img,label);
        button.addEventListener('click',()=>setSelected(button,imageUrl));
        results.appendChild(button);
      });
    };

    const searchImages=async()=>{
      const term=(queryInput.value||nameInput?.value||'').trim();
      if(!term){
        status.textContent='Digite o nome do produto ou o tipo de imagem que deseja buscar.';
        queryInput.focus();
        return;
      }
      searchButton.disabled=true;
      searchButton.textContent='Buscando...';
      status.textContent='Buscando imagens na internet...';
      results.innerHTML='';
      try{
        const params=new URLSearchParams({
          action:'query',
          generator:'search',
          gsrsearch:term,
          gsrnamespace:'6',
          gsrlimit:'24',
          prop:'imageinfo',
          iiprop:'url|mime',
          iiurlwidth:'900',
          format:'json',
          formatversion:'2',
          origin:'*'
        });
        const response=await fetch(`https://commons.wikimedia.org/w/api.php?${params.toString()}`);
        if(!response.ok)throw new Error(`HTTP ${response.status}`);
        const data=await response.json();
        const pages=Array.isArray(data?.query?.pages)?data.query.pages.slice().sort((a,b)=>(a.index??999)-(b.index??999)):[];
        renderResults(pages);
      }catch(error){
        console.error('Erro ao buscar imagens:',error);
        status.textContent='Não foi possível buscar imagens agora. Tente novamente.';
      }finally{
        searchButton.disabled=false;
        searchButton.innerHTML='<i data-lucide="search"></i> Buscar';
        if(window.lucide)lucide.createIcons();
      }
    };

    searchButton.addEventListener('click',searchImages);
    queryInput.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();searchImages()}});
    tab.addEventListener('click',()=>{
      if(!queryInput.value&&nameInput?.value)queryInput.value=nameInput.value;
      setTimeout(()=>queryInput.focus(),50);
    });

    if(window.lucide)lucide.createIcons();
  };
})();
</script>
'''

if '</head>' not in s or '</body>' not in s:
    raise SystemExit('HTML closing tags not found')

s=s.replace('</head>', css+'\n</head>', 1)
s=s.replace('</body>', js+'\n</body>', 1)
path.write_text(s,encoding='utf-8')
print('internet image picker installed')
