from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

# 1) Cardápio: botão de adicionar produto.
menu_pattern = re.compile(r'<section class="view" id="view-menu">.*?</section>\n        <section class="view" id="view-history">', re.S)
menu_replacement = '''<section class="view" id="view-menu"><div class="page-head"><div><span class="eyebrow">Gestão do cardápio</span><h1>Cardápio</h1><p>Adicione e edite produtos, tamanhos, preços, fotos, acréscimos e disponibilidade.</p></div><div class="head-actions"><button class="button" data-add-product type="button"><i data-lucide="plus"></i>Adicionar produto</button><button class="button secondary" data-refresh-menu type="button"><i data-lucide="refresh-cw"></i>Atualizar cardápio</button></div></div><div class="menu-toolbar"><div><span class="eyebrow">Produtos cadastrados</span></div><span class="menu-help">As alterações salvas aparecem no cardápio do cliente.</span></div><div class="menu-table"><div class="table-head"><span>Produto</span><span>Categoria</span><span>Preço</span><span>Acréscimo</span><span>Disponibilidade</span><span></span></div></div></section>
        <section class="view" id="view-history">'''
text, count = menu_pattern.subn(menu_replacement, text, count=1)
if count != 1:
    raise SystemExit('view-menu marker not found')

# 2) Modal compartilhado para criar/editar.
old_modal = '<div class="modal-layer" id="product-edit-modal"><div class="modal"><div class="modal-head"><h2>Editar produto</h2><button class="close" data-close-product-editor type="button" aria-label="Fechar"><i data-lucide="x"></i></button></div><div id="product-edit-content"></div></div></div>'
new_modal = '<div class="modal-layer" id="product-edit-modal"><div class="modal product-manager-modal"><div class="modal-head"><h2 id="product-modal-title">Produto</h2><button class="close" data-close-product-editor type="button" aria-label="Fechar"><i data-lucide="x"></i></button></div><div id="product-edit-content"></div></div></div>'
if old_modal not in text:
    raise SystemExit('product modal marker not found')
text = text.replace(old_modal, new_modal, 1)

# 3) Estilos do cadastro flexível.
css_marker = '    @media(max-width:700px){.menu-help{display:block;margin-top:5px}.menu-table .table-row>*{display:none!important}.menu-table .table-row>*:first-child,.menu-table .table-row>*:last-child{display:flex!important}.menu-table .table-row>*:last-child{justify-content:flex-end}.product-edit-grid{grid-template-columns:1fr}.product-edit-field.full{grid-column:auto}}\n'
extra_css = r'''    .product-manager-modal{width:min(680px,100%)}
    .product-edit-field select{width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:9px;background:#141210;color:var(--text);font:inherit}
    .product-edit-field select:focus{border-color:var(--orange);outline:none}
    .product-form-section{display:grid;gap:10px;padding:13px;border:1px solid var(--line);border-radius:10px;background:var(--panel-2)}
    .product-form-section>strong{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--orange-soft)}
    .product-form-note{margin:0;color:var(--muted);font-size:10px;line-height:1.5}
    .image-source-tabs{display:grid;grid-template-columns:1fr 1fr;gap:7px}.image-source-tab{padding:10px;border:1px solid var(--line);border-radius:8px;background:var(--panel-3);color:var(--muted);font-size:11px;font-weight:800}.image-source-tab.active{border-color:var(--orange);background:#342016;color:var(--orange-soft)}
    .image-source-panel{display:none}.image-source-panel.active{display:grid;gap:7px}.gallery-picker{display:flex;align-items:center;justify-content:center;gap:8px;min-height:46px;padding:10px;border:1px dashed #6c5b50;border-radius:9px;background:#171411;color:var(--text);font-size:11px;font-weight:800;cursor:pointer}.gallery-picker input{display:none}.gallery-picker svg{width:16px;color:var(--orange-soft)}
    .size-builder{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.size-option{display:grid;gap:7px;padding:10px;border:1px solid var(--line);border-radius:9px;background:#171411}.size-option-head{display:flex;align-items:center;gap:7px;font-size:11px;font-weight:900}.size-option-head input{width:17px;height:17px;accent-color:var(--orange)}.size-option input[type=number]{width:100%;padding:9px 10px;border:1px solid var(--line);border-radius:8px;background:#0f0e0d;color:var(--text);font:inherit}.size-option.disabled{opacity:.55}.size-option.disabled input[type=number]{pointer-events:none}
    .product-toggle-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:11px 12px;border:1px solid var(--line);border-radius:9px;background:#171411}.product-toggle-row strong{font-size:11px}.product-toggle-row small{display:block;margin-top:2px;color:var(--muted);font-size:9px}.product-toggle-row input{width:19px;height:19px;accent-color:var(--orange)}
    @media(max-width:700px){.size-builder{grid-template-columns:1fr}.product-manager-modal{padding:17px}.image-source-tabs{grid-template-columns:1fr 1fr}}
'''
if css_marker not in text:
    raise SystemExit('menu css marker not found')
text = text.replace(css_marker, css_marker + extra_css, 1)

# 4) Substitui apenas a gestão do cardápio; pedidos/financeiro ficam intactos.
start = text.find('  let menuProducts=[],menuCategories=[];')
end = text.find('  function orderCard(order){', start)
if start < 0 or end < 0:
    raise SystemExit('menu javascript block not found')

new_block = r'''  let menuProducts=[],menuCategories=[],menuProductSizes=[],menuPizzaSizes=[];
  const escapeMenuText=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  function safeProductImage(value){const raw=String(value||'').trim();if(!raw)return'';try{const url=new URL(raw);return ['http:','https:'].includes(url.protocol)?url.href:''}catch(error){return''}}
  const sizeCode=name=>{const normalized=String(name||'').trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');if(['p','pequena','pequeno'].includes(normalized))return'P';if(['m','media','medio'].includes(normalized))return'M';if(['g','grande'].includes(normalized))return'G';return String(name||'').trim().toUpperCase()};
  const productSizesFor=id=>menuProductSizes.filter(size=>String(size.product_id)===String(id)&&size.active!==false).sort((a,b)=>Number(a.sort_order||0)-Number(b.sort_order||0));
  async function loadRealMenu(){
    const target=document.querySelector('.menu-table');if(!target)return;
    const[{data:products,error:productsError},{data:categories,error:categoriesError},{data:sizeRows,error:sizesError},{data:pizzaSizeRows,error:pizzaSizesError}]=await Promise.all([
      db.from('products').select('id,name,description,base_price,price_addition,image_url,category_id,active,pricing_mode,allow_edges,sort_order').order('name'),
      db.from('categories').select('id,slug,name').eq('active',true).order('sort_order'),
      db.from('product_sizes').select('id,product_id,name,price,active,sort_order').order('sort_order'),
      db.from('pizza_sizes').select('id,name,price,active,sort_order').eq('active',true).order('sort_order')
    ]);
    if(productsError||categoriesError||sizesError||pizzaSizesError){console.error(productsError||categoriesError||sizesError||pizzaSizesError);showToast('Erro ao carregar cardápio');return}
    menuProducts=products||[];menuCategories=categories||[];menuProductSizes=sizeRows||[];menuPizzaSizes=pizzaSizeRows||[];
    const categoryMap=new Map(menuCategories.map(category=>[category.id,category.name||category.slug]));
    target.innerHTML='<div class="table-head"><span>Produto</span><span>Categoria</span><span>Preço</span><span>Acréscimo</span><span>Disponibilidade</span><span></span></div>'+menuProducts.map(item=>{
      const image=safeProductImage(item.image_url);
      const thumb=image?`<img class="menu-thumb" src="${escapeMenuText(image)}" alt="">`:'<span class="menu-thumb menu-thumb-placeholder"><i data-lucide="image"></i></span>';
      const addition=Number(item.price_addition||0);
      const ownSizes=productSizesFor(item.id);
      const category=menuCategories.find(entry=>entry.id===item.category_id);
      const fallbackSizes=String(category?.slug||'').toLowerCase()==='pizzas'?menuPizzaSizes:[];
      const pricedSizes=ownSizes.length?ownSizes:fallbackSizes;
      const base=item.pricing_mode==='sizes'&&pricedSizes.length?Math.min(...pricedSizes.map(size=>Number(size.price||0))):Number(item.base_price||0);
      const priceText=item.pricing_mode==='sizes'?'A partir de '+money(base):money(base);
      return `<div class="table-row" data-product-row="${item.id}"><div class="menu-product">${thumb}<div class="menu-product-copy"><strong>${escapeMenuText(item.name||'')}</strong><small>${escapeMenuText(item.description||'Sem descrição')}</small></div></div><span>${escapeMenuText(categoryMap.get(item.category_id)||'-')}</span><span class="table-total">${priceText}</span><span class="addition-value ${addition>0?'':'none'}">${addition>0?'+ '+money(addition):'Sem acréscimo'}</span><span class="availability ${item.active===false?'off':''}">${item.active===false?'Indisponível':'Disponível'}</span><button class="menu-edit" data-edit-product="${item.id}" type="button" aria-label="Editar ${escapeMenuText(item.name||'produto')}"><i data-lucide="pencil"></i></button></div>`
    }).join('');
    lucide.createIcons();
  }
  function formSizesFor(item){
    if(!item)return {P:{enabled:true,price:''},M:{enabled:true,price:''},G:{enabled:true,price:''}};
    const category=menuCategories.find(entry=>entry.id===item.category_id);
    let rows=productSizesFor(item.id);
    if(!rows.length&&String(category?.slug||'').toLowerCase()==='pizzas')rows=menuPizzaSizes;
    const result={P:{enabled:false,price:''},M:{enabled:false,price:''},G:{enabled:false,price:''}};
    rows.forEach(row=>{const code=sizeCode(row.name);if(result[code])result[code]={enabled:row.active!==false,price:Number(row.price||0).toFixed(2)}});
    if(!rows.length&&item.pricing_mode==='sizes'){result.P.enabled=true;result.M.enabled=true;}
    return result;
  }
  function productFormHtml(item=null){
    const category=menuCategories.find(entry=>entry.id===item?.category_id);
    const defaultMode=item?.pricing_mode||((category?.slug||menuCategories[0]?.slug)==='pizzas'?'sizes':'fixed');
    const sizesState=formSizesFor(item);
    const image=safeProductImage(item?.image_url);
    const categoryOptions=menuCategories.map(entry=>`<option value="${entry.id}" ${entry.id===item?.category_id?'selected':''}>${escapeMenuText(entry.name||entry.slug)}</option>`).join('');
    const sizeCard=code=>`<label class="size-option ${sizesState[code].enabled?'':'disabled'}" data-size-card="${code}"><span class="size-option-head"><input type="checkbox" data-size-enabled="${code}" ${sizesState[code].enabled?'checked':''}>Tamanho ${code}</span><input type="number" min="0" max="999999.99" step="0.01" data-size-price="${code}" placeholder="Preço do ${code}" value="${sizesState[code].price}" ${sizesState[code].enabled?'':'disabled'}></label>`;
    return `<form class="product-edit-form" id="product-edit-form"><div class="product-image-preview"><img id="product-image-preview" src="${escapeMenuText(image||'https://placehold.co/160x120?text=Sem+foto')}" alt="Prévia da foto"><span>Escolha uma foto da galeria ou use um link da internet. JPG, PNG ou WebP, até 5 MB.</span></div><div class="product-edit-grid"><div class="product-edit-field"><label for="edit-product-category">Categoria</label><select id="edit-product-category" required>${categoryOptions}</select></div><div class="product-edit-field"><label for="edit-product-pricing">Como é o preço?</label><select id="edit-product-pricing"><option value="fixed" ${defaultMode==='fixed'?'selected':''}>Preço único</option><option value="sizes" ${defaultMode==='sizes'?'selected':''}>Preço por tamanho</option></select></div><div class="product-edit-field full"><label for="edit-product-name">Nome</label><input id="edit-product-name" required maxlength="120" value="${escapeMenuText(item?.name||'')}"></div><div class="product-edit-field full"><label for="edit-product-description">Descrição</label><textarea id="edit-product-description" maxlength="600">${escapeMenuText(item?.description||'')}</textarea></div><div class="product-edit-field" id="fixed-price-field"><label for="edit-product-price">Preço (R$)</label><input id="edit-product-price" type="number" min="0" max="999999.99" step="0.01" value="${Number(item?.base_price||0).toFixed(2)}"></div><div class="product-edit-field"><label for="edit-product-addition">Acréscimo opcional (R$)</label><input id="edit-product-addition" type="number" min="0" max="999999.99" step="0.01" value="${Number(item?.price_addition||0).toFixed(2)}"></div></div><div class="product-form-section" id="sizes-section"><strong>Tamanhos deste produto</strong><p class="product-form-note">Marque só os tamanhos que esse item vende. Pode ser P/M, P/M/G ou apenas um deles.</p><div class="size-builder">${sizeCard('P')}${sizeCard('M')}${sizeCard('G')}</div></div><div class="product-form-section"><strong>Foto do produto</strong><div class="image-source-tabs"><button class="image-source-tab active" data-image-source="gallery" type="button"><i data-lucide="image-up"></i> Galeria</button><button class="image-source-tab" data-image-source="url" type="button"><i data-lucide="link"></i> Internet</button></div><div class="image-source-panel active" data-image-panel="gallery"><label class="gallery-picker"><i data-lucide="image-plus"></i><span id="gallery-file-label">Escolher foto da galeria</span><input id="edit-product-file" type="file" accept="image/jpeg,image/png,image/webp"></label></div><div class="image-source-panel" data-image-panel="url"><div class="product-edit-field"><label for="edit-product-image">Link da foto</label><input id="edit-product-image" type="url" inputmode="url" placeholder="https://..." value="${escapeMenuText(item?.image_url||'')}"></div></div></div><label class="product-toggle-row" for="edit-product-edges"><span><strong>Permitir borda</strong><small>Use em pizzas ou outros itens que aceitem borda.</small></span><input id="edit-product-edges" type="checkbox" ${item?.allow_edges?'checked':''}></label><label class="product-active-row" for="edit-product-active"><span><strong>Produto disponível</strong><small>Desative para esconder do cardápio do cliente.</small></span><input id="edit-product-active" type="checkbox" ${item?.active===false?'':'checked'}></label><div class="modal-actions"><button class="button" type="submit"><i data-lucide="save"></i>${item?'Salvar alterações':'Adicionar produto'}</button><button class="button secondary" type="button" data-close-product-editor>Cancelar</button></div></form>`;
  }
  function bindProductForm(item=null){
    const pricing=document.querySelector('#edit-product-pricing');
    const fixedField=document.querySelector('#fixed-price-field');
    const sizesSection=document.querySelector('#sizes-section');
    const syncPricing=()=>{const usesSizes=pricing.value==='sizes';fixedField.style.display=usesSizes?'none':'grid';sizesSection.style.display=usesSizes?'grid':'none'};
    pricing.addEventListener('change',syncPricing);syncPricing();
    document.querySelectorAll('[data-size-enabled]').forEach(check=>check.addEventListener('change',()=>{const code=check.dataset.sizeEnabled;const input=document.querySelector(`[data-size-price="${code}"]`);const card=document.querySelector(`[data-size-card="${code}"]`);input.disabled=!check.checked;card.classList.toggle('disabled',!check.checked);if(check.checked&&!input.value)input.focus()}));
    const preview=document.querySelector('#product-image-preview'),urlInput=document.querySelector('#edit-product-image'),fileInput=document.querySelector('#edit-product-file'),fileLabel=document.querySelector('#gallery-file-label');
    document.querySelectorAll('[data-image-source]').forEach(tab=>tab.addEventListener('click',()=>{const source=tab.dataset.imageSource;document.querySelectorAll('[data-image-source]').forEach(button=>button.classList.toggle('active',button===tab));document.querySelectorAll('[data-image-panel]').forEach(panel=>panel.classList.toggle('active',panel.dataset.imagePanel===source))}));
    urlInput?.addEventListener('input',()=>{preview.src=safeProductImage(urlInput.value)||'https://placehold.co/160x120?text=Sem+foto'});
    fileInput?.addEventListener('change',()=>{const file=fileInput.files?.[0];if(!file)return;fileLabel.textContent=file.name;preview.src=URL.createObjectURL(file)});
    document.querySelector('#product-edit-form').onsubmit=event=>saveProductForm(event,item?.id||null);
  }
  function openProductCreator(){document.querySelector('#product-modal-title').textContent='Adicionar produto';document.querySelector('#product-edit-content').innerHTML=productFormHtml();document.querySelector('#product-edit-modal').classList.add('show');lucide.createIcons();bindProductForm()}
  function openProductEditor(id){const item=menuProducts.find(product=>String(product.id)===String(id));if(!item)return;document.querySelector('#product-modal-title').textContent='Editar produto';document.querySelector('#product-edit-content').innerHTML=productFormHtml(item);document.querySelector('#product-edit-modal').classList.add('show');lucide.createIcons();bindProductForm(item)}
  async function uploadProductImage(file){
    if(!file)return'';
    if(!['image/jpeg','image/png','image/webp'].includes(file.type))throw new Error('Use uma foto JPG, PNG ou WebP');
    if(file.size>5*1024*1024)throw new Error('A foto deve ter no máximo 5 MB');
    const extension=(file.name.split('.').pop()||'jpg').toLowerCase().replace(/[^a-z0-9]/g,'');
    const unique=(crypto.randomUUID?crypto.randomUUID():String(Date.now()));
    const objectPath=`products/${unique}.${extension||'jpg'}`;
    const{error}=await db.storage.from('product-images').upload(objectPath,file,{cacheControl:'3600',upsert:false,contentType:file.type});
    if(error)throw error;
    const{data}=db.storage.from('product-images').getPublicUrl(objectPath);
    return data?.publicUrl||'';
  }
  function collectProductSizes(){
    return ['P','M','G'].filter(code=>document.querySelector(`[data-size-enabled="${code}"]`)?.checked).map((code,index)=>({name:code,price:Number(document.querySelector(`[data-size-price="${code}"]`).value),active:true,sort_order:index+1}));
  }
  async function saveProductForm(event,id=null){
    event.preventDefault();
    const form=event.currentTarget,button=form.querySelector('button[type="submit"]');
    const categoryId=Number(document.querySelector('#edit-product-category').value);
    const name=document.querySelector('#edit-product-name').value.trim();
    const description=document.querySelector('#edit-product-description').value.trim();
    const pricingMode=document.querySelector('#edit-product-pricing').value;
    const sizes=collectProductSizes();
    const fixedPrice=Number(document.querySelector('#edit-product-price').value||0);
    const priceAddition=Number(document.querySelector('#edit-product-addition').value||0);
    const allowEdges=document.querySelector('#edit-product-edges').checked;
    const active=document.querySelector('#edit-product-active').checked;
    const file=document.querySelector('#edit-product-file').files?.[0]||null;
    const rawImage=document.querySelector('#edit-product-image').value.trim();
    if(!categoryId||!name){showToast('Informe categoria e nome do produto');return}
    if(pricingMode==='fixed'&&(!Number.isFinite(fixedPrice)||fixedPrice<0)){showToast('Confira o preço do produto');return}
    if(pricingMode==='sizes'&&(!sizes.length||sizes.some(size=>!Number.isFinite(size.price)||size.price<0))){showToast('Marque pelo menos um tamanho e informe seus preços');return}
    if(!Number.isFinite(priceAddition)||priceAddition<0){showToast('Confira o valor do acréscimo');return}
    if(rawImage&&!safeProductImage(rawImage)&&!file){showToast('Use um link de foto válido começando com http ou https');return}
    button.disabled=true;button.textContent='Salvando...';
    let createdId=id;
    try{
      let imageUrl=rawImage?safeProductImage(rawImage):'';
      if(file)imageUrl=await uploadProductImage(file);
      if(!imageUrl&&id)imageUrl=menuProducts.find(product=>String(product.id)===String(id))?.image_url||'';
      const basePrice=pricingMode==='sizes'?Math.min(...sizes.map(size=>size.price)):fixedPrice;
      const payload={category_id:categoryId,name,description:description||null,base_price:basePrice,price_addition:priceAddition,image_url:imageUrl||null,active,pricing_mode:pricingMode,allow_edges:allowEdges};
      if(id){
        const{data,error}=await db.from('products').update(payload).eq('id',id).select('id');
        if(error||!data?.length)throw error||new Error('Produto não encontrado');
      }else{
        const{data,error}=await db.from('products').insert(payload).select('id').single();
        if(error||!data?.id)throw error||new Error('Não foi possível criar o produto');
        createdId=data.id;
      }
      const{error:deleteSizesError}=await db.from('product_sizes').delete().eq('product_id',createdId);
      if(deleteSizesError)throw deleteSizesError;
      if(pricingMode==='sizes'){
        const rows=sizes.map(size=>({...size,product_id:createdId}));
        const{error:sizeError}=await db.from('product_sizes').insert(rows);
        if(sizeError)throw sizeError;
      }
      document.querySelector('#product-edit-modal').classList.remove('show');
      await loadRealMenu();
      await loadRealOrders({notify:false});
      showToast(id?'Produto atualizado no cardápio':'Produto adicionado ao cardápio');
    }catch(error){
      console.error('Erro ao salvar produto:',error);
      if(!id&&createdId){try{await db.from('products').delete().eq('id',createdId)}catch(cleanupError){console.error(cleanupError)}}
      showToast(error?.message||'Não foi possível salvar o produto');
      button.disabled=false;button.textContent=id?'Salvar alterações':'Adicionar produto';
    }
  }
'''
text = text[:start] + new_block + text[end:]

# 5) Eventos: abrir cadastro novo sem tocar nos outros fluxos.
old_click = "    const editProduct=event.target.closest('[data-edit-product]');if(editProduct){openProductEditor(editProduct.dataset.editProduct);return}\n    if(event.target.closest('[data-refresh-menu]')){loadRealMenu();return}"
new_click = "    const addProduct=event.target.closest('[data-add-product]');if(addProduct){openProductCreator();return}\n    const editProduct=event.target.closest('[data-edit-product]');if(editProduct){openProductEditor(editProduct.dataset.editProduct);return}\n    if(event.target.closest('[data-refresh-menu]')){loadRealMenu();return}"
if old_click not in text:
    raise SystemExit('menu click handler marker not found')
text = text.replace(old_click, new_click, 1)

# Sanity checks.
for marker in ['data-add-product','function openProductCreator','function uploadProductImage','product_sizes','pricing_mode','data-size-enabled','product-images']:
    if marker not in text:
        raise SystemExit(f'missing expected marker: {marker}')

path.write_text(text, encoding='utf-8')
