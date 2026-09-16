from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

if 'id="product-edit-modal"' in text:
    raise SystemExit('Product editor already installed')

# 1) Make the menu section a real management surface.
menu_start = text.index('        <section class="view" id="view-menu">')
history_start = text.index('        <section class="view" id="view-history">', menu_start)
new_menu = '''        <section class="view" id="view-menu"><div class="page-head"><div><span class="eyebrow">Gestão do cardápio</span><h1>Cardápio</h1><p>Edite produtos, preços, fotos, acréscimos e disponibilidade.</p></div><button class="button secondary" data-refresh-menu><i data-lucide="refresh-cw"></i>Atualizar cardápio</button></div><div class="menu-toolbar"><div><span class="eyebrow">Produtos cadastrados</span></div><span class="menu-help">As alterações salvas aparecem no cardápio do cliente.</span></div><div class="menu-table"><div class="table-head"><span>Produto</span><span>Categoria</span><span>Preço</span><span>Acréscimo</span><span>Disponibilidade</span><span></span></div></div></section>\n'''
text = text[:menu_start] + new_menu + text[history_start:]

# 2) Add editor-specific styling without touching unrelated styles.
style_marker = '  </style>'
menu_css = r'''
    /* Cardápio editável */
    .menu-table .table-head,.menu-table .table-row{grid-template-columns:minmax(230px,2fr) 1fr .8fr .8fr 1fr auto}
    .menu-product{display:flex;align-items:center;gap:11px;min-width:0}.menu-product-copy{min-width:0}.menu-product-copy strong,.menu-product-copy small{overflow:hidden;text-overflow:ellipsis}.menu-thumb{width:48px;height:48px;flex:none;object-fit:cover;border:1px solid var(--line);border-radius:10px;background:var(--panel-3)}.menu-thumb-placeholder{display:grid;place-items:center;color:var(--muted)}.menu-thumb-placeholder svg{width:18px}.menu-help{color:var(--muted);font-size:11px}.menu-edit{min-width:36px;height:36px;display:grid;place-items:center;border:1px solid var(--line);border-radius:9px;background:var(--panel-3)}.menu-edit:hover{border-color:var(--orange);color:var(--orange-soft)}.menu-edit svg{width:15px}.addition-value{color:var(--orange-soft);font-weight:800}.addition-value.none{color:var(--muted);font-weight:600}
    .product-edit-form{display:grid;gap:14px}.product-edit-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.product-edit-field{display:grid;gap:7px}.product-edit-field.full{grid-column:1/-1}.product-edit-field label{color:var(--muted);font-size:10px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}.product-edit-field input,.product-edit-field textarea{width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:9px;background:#141210;color:var(--text);font:inherit}.product-edit-field textarea{min-height:82px;resize:vertical}.product-edit-field input:focus,.product-edit-field textarea:focus{border-color:var(--orange);outline:none}.product-image-preview{display:flex;align-items:center;gap:12px;padding:10px;border:1px solid var(--line);border-radius:10px;background:var(--panel-2)}.product-image-preview img{width:76px;height:64px;object-fit:cover;border-radius:8px;background:var(--panel-3)}.product-image-preview span{color:var(--muted);font-size:10px;line-height:1.5}.product-active-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px;border:1px solid var(--line);border-radius:10px;background:var(--panel-2)}.product-active-row strong{font-size:12px}.product-active-row small{display:block;margin-top:3px;color:var(--muted);font-size:10px}.product-active-row input{width:20px;height:20px;accent-color:var(--orange)}
    @media(max-width:700px){.menu-help{display:block;margin-top:5px}.menu-table .table-row>*{display:none!important}.menu-table .table-row>*:first-child,.menu-table .table-row>*:last-child{display:flex!important}.menu-table .table-row>*:last-child{justify-content:flex-end}.product-edit-grid{grid-template-columns:1fr}.product-edit-field.full{grid-column:auto}}
'''
text = text.replace(style_marker, menu_css + '\n' + style_marker, 1)

# 3) Add the product editor modal.
modal_marker = '    <div class="modal-layer" id="detail-modal">'
product_modal = '''    <div class="modal-layer" id="product-edit-modal"><div class="modal"><div class="modal-head"><h2>Editar produto</h2><button class="close" data-close-product-editor type="button" aria-label="Fechar"><i data-lucide="x"></i></button></div><div id="product-edit-content"></div></div></div>\n'''
text = text.replace(modal_marker, product_modal + modal_marker, 1)

# 4) Replace the read-only menu loader with an editable version and editor functions.
fn_start = text.index('  async function loadRealMenu(){')
fn_end = text.index('  function orderCard(order)', fn_start)
new_functions = r'''  let menuProducts=[],menuCategories=[];
  const escapeMenuText=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  function safeProductImage(value){const raw=String(value||'').trim();if(!raw)return'';try{const url=new URL(raw);return ['http:','https:'].includes(url.protocol)?url.href:''}catch(error){return''}}
  async function loadRealMenu(){
    const target=document.querySelector('.menu-table');if(!target)return;
    const[{data:products,error:productsError},{data:categories,error:categoriesError}]=await Promise.all([
      db.from('products').select('id,name,description,base_price,price_addition,image_url,category_id,active').order('name'),
      db.from('categories').select('id,slug,name').eq('active',true).order('sort_order')
    ]);
    if(productsError||categoriesError){console.error(productsError||categoriesError);showToast('Erro ao carregar cardápio');return}
    menuProducts=products||[];menuCategories=categories||[];
    const categoryMap=new Map(menuCategories.map(category=>[category.id,category.name||category.slug]));
    target.innerHTML='<div class="table-head"><span>Produto</span><span>Categoria</span><span>Preço</span><span>Acréscimo</span><span>Disponibilidade</span><span></span></div>'+menuProducts.map(item=>{
      const image=safeProductImage(item.image_url);
      const thumb=image?`<img class="menu-thumb" src="${escapeMenuText(image)}" alt="">`:'<span class="menu-thumb menu-thumb-placeholder"><i data-lucide="image"></i></span>';
      const addition=Number(item.price_addition||0);
      return `<div class="table-row" data-product-row="${item.id}"><div class="menu-product">${thumb}<div class="menu-product-copy"><strong>${escapeMenuText(item.name||'')}</strong><small>${escapeMenuText(item.description||'Sem descrição')}</small></div></div><span>${escapeMenuText(categoryMap.get(item.category_id)||'-')}</span><span class="table-total">${money(Number(item.base_price||0))}</span><span class="addition-value ${addition>0?'':'none'}">${addition>0?'+ '+money(addition):'Sem acréscimo'}</span><span class="availability ${item.active===false?'off':''}">${item.active===false?'Indisponível':'Disponível'}</span><button class="menu-edit" data-edit-product="${item.id}" type="button" aria-label="Editar ${escapeMenuText(item.name||'produto')}"><i data-lucide="pencil"></i></button></div>`
    }).join('');
    lucide.createIcons();
  }
  function openProductEditor(id){
    const item=menuProducts.find(product=>String(product.id)===String(id));if(!item)return;
    const category=menuCategories.find(entry=>entry.id===item.category_id);
    const image=safeProductImage(item.image_url);
    const isPizza=String(category?.slug||'').toLowerCase()==='pizzas';
    document.querySelector('#product-edit-content').innerHTML=`<form class="product-edit-form" id="product-edit-form"><div class="product-image-preview"><img id="product-image-preview" src="${escapeMenuText(image||'https://placehold.co/160x120?text=Sem+foto')}" alt="Prévia da foto"><span>${isPizza?'Nas pizzas, o preço por tamanho continua definido pela tabela de tamanhos. Use o acréscimo para cobrar a mais neste sabor.':'A foto é atualizada pelo link informado abaixo.'}</span></div><div class="product-edit-grid"><div class="product-edit-field full"><label for="edit-product-name">Nome</label><input id="edit-product-name" required maxlength="120" value="${escapeMenuText(item.name||'')}"></div><div class="product-edit-field full"><label for="edit-product-description">Descrição</label><textarea id="edit-product-description" maxlength="600">${escapeMenuText(item.description||'')}</textarea></div><div class="product-edit-field"><label for="edit-product-price">Preço base (R$)</label><input id="edit-product-price" type="number" min="0" max="999999.99" step="0.01" required value="${Number(item.base_price||0).toFixed(2)}" ${isPizza?'title="Para pizzas, o valor cobrado é definido pelo tamanho"':''}></div><div class="product-edit-field"><label for="edit-product-addition">Acréscimo (R$)</label><input id="edit-product-addition" type="number" min="0" max="999999.99" step="0.01" required value="${Number(item.price_addition||0).toFixed(2)}"></div><div class="product-edit-field full"><label for="edit-product-image">Foto (URL)</label><input id="edit-product-image" type="url" inputmode="url" placeholder="https://..." value="${escapeMenuText(item.image_url||'')}"></div></div><label class="product-active-row" for="edit-product-active"><span><strong>Produto disponível</strong><small>Desative para esconder do cardápio do cliente.</small></span><input id="edit-product-active" type="checkbox" ${item.active!==false?'checked':''}></label><div class="modal-actions"><button class="button" type="submit"><i data-lucide="save"></i>Salvar alterações</button><button class="button secondary" type="button" data-close-product-editor>Cancelar</button></div></form>`;
    const modal=document.querySelector('#product-edit-modal');modal.classList.add('show');lucide.createIcons();
    const imageInput=document.querySelector('#edit-product-image'),preview=document.querySelector('#product-image-preview');
    imageInput?.addEventListener('input',()=>{preview.src=safeProductImage(imageInput.value)||'https://placehold.co/160x120?text=Sem+foto'});
    document.querySelector('#product-edit-form').onsubmit=event=>saveProductEdit(event,item.id);
  }
  async function saveProductEdit(event,id){
    event.preventDefault();
    const form=event.currentTarget,button=form.querySelector('button[type="submit"]');
    const name=document.querySelector('#edit-product-name').value.trim();
    const description=document.querySelector('#edit-product-description').value.trim();
    const basePrice=Number(document.querySelector('#edit-product-price').value);
    const priceAddition=Number(document.querySelector('#edit-product-addition').value);
    const rawImage=document.querySelector('#edit-product-image').value.trim();
    const imageUrl=rawImage?safeProductImage(rawImage):'';
    const active=document.querySelector('#edit-product-active').checked;
    if(!name){showToast('Informe o nome do produto');return}
    if(!Number.isFinite(basePrice)||basePrice<0||!Number.isFinite(priceAddition)||priceAddition<0){showToast('Confira os valores do produto');return}
    if(rawImage&&!imageUrl){showToast('Use um link de foto válido começando com http ou https');return}
    button.disabled=true;button.textContent='Salvando...';
    const{data,error}=await db.from('products').update({name,description:description||null,base_price:basePrice,price_addition:priceAddition,image_url:imageUrl||null,active}).eq('id',id).select('id');
    if(error||!data?.length){console.error('Erro ao salvar produto:',error);showToast(error?.message||'Não foi possível salvar o produto');button.disabled=false;button.textContent='Salvar alterações';return}
    document.querySelector('#product-edit-modal').classList.remove('show');
    await loadRealMenu();
    await loadRealOrders({notify:false});
    showToast('Produto atualizado no cardápio');
  }
'''
text = text[:fn_start] + new_functions + text[fn_end:]

# 5) Refresh/open/close editor actions, isolated from the existing order event handler.
insert_marker = '  let expenses=[];'
menu_events = r'''  document.addEventListener('click',event=>{
    const editProduct=event.target.closest('[data-edit-product]');if(editProduct){openProductEditor(editProduct.dataset.editProduct);return}
    if(event.target.closest('[data-refresh-menu]')){loadRealMenu();return}
    if(event.target.closest('[data-close-product-editor]')||event.target.id==='product-edit-modal')document.querySelector('#product-edit-modal').classList.remove('show');
  });
'''
text = text.replace(insert_marker, menu_events + insert_marker, 1)

# 6) Reload product data whenever the menu tab is opened.
old_switch = "  function switchView(view){document.querySelectorAll('.nav-item').forEach(item=>item.classList.toggle('active',item.dataset.view===view));document.querySelectorAll('.view').forEach(item=>item.classList.toggle('active',item.id===`view-${view}`));if(view==='orders')renderBoard('orders-board');window.scrollTo({top:0,behavior:'smooth'})}"
new_switch = "  function switchView(view){document.querySelectorAll('.nav-item').forEach(item=>item.classList.toggle('active',item.dataset.view===view));document.querySelectorAll('.view').forEach(item=>item.classList.toggle('active',item.id===`view-${view}`));if(view==='orders')renderBoard('orders-board');if(view==='menu')loadRealMenu();window.scrollTo({top:0,behavior:'smooth'})}"
if old_switch not in text:
    raise SystemExit('switchView marker not found')
text = text.replace(old_switch,new_switch,1)

path.write_text(text,encoding='utf-8')
