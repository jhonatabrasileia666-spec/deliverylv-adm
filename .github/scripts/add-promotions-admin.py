from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'anchor not found: {label}')
    s=s.replace(old,new,1)

promo_style='''<style id="promotion-admin-styles">
  .promotion-admin-panel{margin:0 0 26px;padding:18px;background:linear-gradient(145deg,#211813,#191715 58%);border:1px solid #ff5a1648;border-radius:14px;box-shadow:0 14px 34px #0004}
  .promotion-admin-head{display:flex;align-items:center;justify-content:space-between;gap:18px;margin-bottom:14px}.promotion-admin-head h2{margin:4px 0 0;font:800 29px/1 "Barlow Condensed";text-transform:uppercase}.promotion-admin-head p{margin:6px 0 0;color:var(--muted);font-size:10px;line-height:1.45}.promotion-admin-actions{display:flex;align-items:center;gap:10px}.promotion-status{color:var(--muted);font-size:10px;text-align:right}
  .promotion-manager{display:grid;gap:8px;max-height:430px;overflow:auto;padding-right:3px}.promotion-row{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(110px,.7fr) 112px minmax(135px,.8fr);align-items:center;gap:12px;padding:11px 12px;background:#171412;border:1px solid var(--line);border-radius:11px;transition:.2s}.promotion-row.active{border-color:#d9f15c55;background:#1b2116}.promotion-product{display:flex;align-items:center;gap:10px;min-width:0}.promotion-thumb{width:48px;height:48px;flex:none;object-fit:cover;border-radius:9px;background:var(--panel-3)}.promotion-product-copy{min-width:0}.promotion-product-copy strong{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:12px}.promotion-product-copy small{display:block;margin-top:3px;color:var(--muted);font-size:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.promotion-check{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:10px;font-weight:800}.promotion-check input{width:18px;height:18px;accent-color:var(--orange)}.promotion-discount{display:flex;align-items:center;gap:5px}.promotion-discount input{width:72px;height:38px;padding:0 9px;border:1px solid var(--line);border-radius:8px;background:var(--panel-2);color:var(--text);font:inherit;font-weight:800}.promotion-discount input:focus{border-color:var(--orange);outline:none}.promotion-discount input:disabled{opacity:.45}.promotion-discount span{color:var(--orange-soft);font-weight:900}.promotion-preview{color:var(--muted);font-size:9px;line-height:1.35}.promotion-preview strong{display:block;margin-top:3px;color:var(--lime);font-size:12px}.promotion-empty{padding:25px;text-align:center;color:var(--muted);font-size:11px}
  @media(max-width:700px){.promotion-admin-panel{padding:14px;margin-bottom:20px}.promotion-admin-head{align-items:flex-start;flex-direction:column}.promotion-admin-actions{width:100%;justify-content:space-between}.promotion-status{text-align:left}.promotion-manager{max-height:470px}.promotion-row{grid-template-columns:minmax(0,1fr) 92px;gap:9px}.promotion-product{grid-column:1/-1}.promotion-preview{grid-column:1/-1;padding-top:7px;border-top:1px solid #ffffff0d}.promotion-discount{justify-self:end}}
</style>

'''
replace_once('<style id="internet-image-picker-styles">',promo_style+'<style id="internet-image-picker-styles">','promo styles')

promo_panel='''<section class="promotion-admin-panel"><div class="promotion-admin-head"><div><span class="eyebrow">Destaques do cardápio</span><h2>Promoções</h2><p>Marque os produtos que entram em oferta e informe o desconto. Eles aparecem antes do cardápio do cliente.</p></div><div class="promotion-admin-actions"><span class="promotion-status" id="promotion-status">Carregando...</span><button class="button small" id="save-promotions" type="button"><i data-lucide="badge-percent"></i>Salvar promoções</button></div></div><div class="promotion-manager" id="promotion-manager"><div class="promotion-empty">Carregando produtos...</div></div></section>'''
replace_once('<div class="menu-toolbar"><div><span class="eyebrow">Produtos cadastrados</span>',promo_panel+'<div class="menu-toolbar"><div><span class="eyebrow">Produtos cadastrados</span>','promo panel')

replace_once("db.from('products').select('id,name,description,base_price,price_addition,image_url,category_id,active,pricing_mode,allow_edges,sort_order').order('name')", "db.from('products').select('id,name,description,base_price,price_addition,image_url,category_id,active,pricing_mode,allow_edges,sort_order,promotion_active,promotion_discount,promotion_sort_order').order('name')", 'load promotion columns')

old_assign="    menuProducts=products||[];menuCategories=categories||[];menuProductSizes=sizeRows||[];menuPizzaSizes=pizzaSizeRows||[];\n    const categoryMap=new Map(menuCategories.map(category=>[category.id,category.name||category.slug]));"
new_assign="    menuProducts=products||[];menuCategories=categories||[];menuProductSizes=sizeRows||[];menuPizzaSizes=pizzaSizeRows||[];\n    renderPromotionManager();\n    const categoryMap=new Map(menuCategories.map(category=>[category.id,category.name||category.slug]));"
replace_once(old_assign,new_assign,'render promotion manager call')

promo_js=r'''  function promotionBasePrice(item){
    const ownSizes=productSizesFor(item.id);
    const category=menuCategories.find(entry=>String(entry.id)===String(item.category_id));
    const fallbackSizes=!ownSizes.length&&String(category?.slug||'').toLowerCase()==='pizzas'?menuPizzaSizes:[];
    const pricedSizes=ownSizes.length?ownSizes:fallbackSizes;
    const base=item.pricing_mode==='sizes'&&pricedSizes.length?Math.min(...pricedSizes.map(size=>Number(size.price||0))):Number(item.base_price||0);
    return base+Number(item.price_addition||0);
  }
  function promotionPreview(item,discount){
    const regular=promotionBasePrice(item),value=Math.round(regular*(1-Number(discount||0)/100)*100)/100;
    const sized=item.pricing_mode==='sizes'||productSizesFor(item.id).length>0;
    return `${sized?'A partir de ':''}${money(regular)} → <strong>${money(value)}</strong>`;
  }
  function syncPromotionRow(row){
    const check=row.querySelector('[data-promotion-enabled]'),input=row.querySelector('[data-promotion-discount]'),preview=row.querySelector('[data-promotion-preview]');
    const item=menuProducts.find(product=>String(product.id)===String(row.dataset.promotionProduct));
    if(!check||!input||!preview||!item)return;
    row.classList.toggle('active',check.checked);input.disabled=!check.checked;
    const discount=Number(input.value||0);
    preview.innerHTML=check.checked&&discount>0&&discount<100?promotionPreview(item,discount):(check.checked?'Informe o desconto para ativar a oferta':'Preço normal: '+money(promotionBasePrice(item)));
  }
  function renderPromotionManager(){
    const host=document.querySelector('#promotion-manager'),status=document.querySelector('#promotion-status'),save=document.querySelector('#save-promotions');if(!host)return;
    const categoryMap=new Map(menuCategories.map(category=>[String(category.id),category.name||category.slug]));
    const products=menuProducts.filter(item=>item.active!==false).sort((a,b)=>Number(Boolean(b.promotion_active))-Number(Boolean(a.promotion_active))||Number(a.promotion_sort_order||0)-Number(b.promotion_sort_order||0)||String(a.name||'').localeCompare(String(b.name||''),'pt-BR'));
    if(!products.length){host.innerHTML='<div class="promotion-empty">Nenhum produto disponível para promoção.</div>';if(status)status.textContent='0 produtos';if(save)save.disabled=true;return}
    host.innerHTML=products.map(item=>{const image=safeProductImage(item.image_url)||'https://placehold.co/96x96?text=LV';const active=Boolean(item.promotion_active)&&Number(item.promotion_discount||0)>0;const discount=Number(item.promotion_discount||0);return `<div class="promotion-row ${active?'active':''}" data-promotion-product="${item.id}"><div class="promotion-product"><img class="promotion-thumb" src="${escapeMenuText(image)}" alt=""><div class="promotion-product-copy"><strong>${escapeMenuText(item.name||'')}</strong><small>${escapeMenuText(categoryMap.get(String(item.category_id))||'Produto')}</small></div></div><label class="promotion-check"><input type="checkbox" data-promotion-enabled ${active?'checked':''}> Em promoção</label><label class="promotion-discount"><input type="number" min="0.01" max="99.99" step="0.01" data-promotion-discount value="${discount>0?discount:''}" placeholder="10" ${active?'':'disabled'}><span>%</span></label><div class="promotion-preview" data-promotion-preview></div></div>`}).join('');
    host.querySelectorAll('.promotion-row').forEach(row=>{const check=row.querySelector('[data-promotion-enabled]'),input=row.querySelector('[data-promotion-discount]');check?.addEventListener('change',()=>{syncPromotionRow(row);if(check.checked&&!input.value)input.focus()});input?.addEventListener('input',()=>syncPromotionRow(row));syncPromotionRow(row)});
    const activeCount=products.filter(item=>Boolean(item.promotion_active)&&Number(item.promotion_discount||0)>0).length;if(status)status.textContent=`${activeCount} ${activeCount===1?'produto em promoção':'produtos em promoção'}`;if(save){save.disabled=false;save.onclick=savePromotions}lucide.createIcons();
  }
  async function savePromotions(){
    const button=document.querySelector('#save-promotions'),status=document.querySelector('#promotion-status'),rows=[...document.querySelectorAll('[data-promotion-product]')];if(!button||!rows.length)return;
    let order=0;const updates=[];
    for(const row of rows){
      const id=row.dataset.promotionProduct,enabled=Boolean(row.querySelector('[data-promotion-enabled]')?.checked),discount=Number(row.querySelector('[data-promotion-discount]')?.value||0),item=menuProducts.find(product=>String(product.id)===String(id));
      if(enabled&&(!Number.isFinite(discount)||discount<=0||discount>=100)){showToast(`Confira o desconto de ${item?.name||'um produto'}`);row.querySelector('[data-promotion-discount]')?.focus();return}
      const sortOrder=enabled?++order:0;
      if(!item||Boolean(item.promotion_active)!==enabled||Math.abs(Number(item.promotion_discount||0)-(enabled?discount:0))>.001||Number(item.promotion_sort_order||0)!==sortOrder)updates.push({id,enabled,discount:enabled?discount:0,sortOrder});
    }
    button.disabled=true;status.textContent='Salvando promoções...';
    try{
      await Promise.all(updates.map(async item=>{const{error}=await db.from('products').update({promotion_active:item.enabled,promotion_discount:item.discount,promotion_sort_order:item.sortOrder}).eq('id',item.id);if(error)throw error}));
      await loadRealMenu();showToast(updates.length?'Promoções atualizadas':'Promoções já estavam salvas');
    }catch(error){console.error('Erro ao salvar promoções:',error);status.textContent='Não foi possível salvar';showToast(error?.message||'Erro ao salvar promoções');button.disabled=false}
  }
'''
replace_once('  function formSizesFor(item){',promo_js+'  function formSizesFor(item){','promo functions')

path.write_text(s,encoding='utf-8')
print('admin promotion patch applied')
