from pathlib import Path
import re

path=Path('index.html')
s=path.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'anchor not found: {label}')
    s=s.replace(old,new,1)

rep("db.from('products').select('id,name,description,base_price,price_addition,image_url,category_id,active,pricing_mode,allow_edges,sort_order,promotion_active,promotion_discount,promotion_sort_order').order('name')",
"db.from('products').select('id,name,description,base_price,price_addition,image_url,category_id,active,pricing_mode,allow_edges,sort_order,promotion_active,promotion_discount,promotion_sort_order,promotion_size').order('name')",
'load promotion_size')

extra_css='''  .promotion-row{grid-template-columns:minmax(0,1.45fr) minmax(110px,.65fr) minmax(135px,.72fr) 112px minmax(135px,.8fr)}\n  .promotion-size{display:grid;gap:4px;color:var(--muted);font-size:9px;font-weight:800}.promotion-size select{width:100%;height:38px;padding:0 9px;border:1px solid var(--line);border-radius:8px;background:var(--panel-2);color:var(--text);font:inherit;font-size:10px;font-weight:800}.promotion-size select:focus{border-color:var(--orange);outline:none}.promotion-size select:disabled{opacity:.45}.promotion-size strong{display:flex;align-items:center;min-height:38px;color:var(--muted);font-size:10px}\n  @media(max-width:700px){.promotion-row{grid-template-columns:minmax(0,1fr) 92px}.promotion-size{grid-column:1/-1}.promotion-size select{min-height:40px}}\n'''
rep('</style>\n\n<style id="internet-image-picker-styles">',extra_css+'</style>\n\n<style id="internet-image-picker-styles">','promotion size css')

pattern=re.compile(r"  function promotionBasePrice\(item\)\{.*?\n  function formSizesFor\(item\)\{",re.S)
new=r'''  const promotionSizeKey=value=>String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  function promotionSizeRows(item){
    const own=productSizesFor(item.id);
    const category=menuCategories.find(entry=>String(entry.id)===String(item.category_id));
    const fallback=!own.length&&String(category?.slug||'').toLowerCase()==='pizzas'?menuPizzaSizes:[];
    return (own.length?own:fallback).filter(size=>size.active!==false).sort((a,b)=>Number(a.sort_order||0)-Number(b.sort_order||0));
  }
  function promotionBasePrice(item,sizeName=''){
    const rows=promotionSizeRows(item),addition=Number(item.price_addition||0);
    if(rows.length){const chosen=rows.find(size=>promotionSizeKey(size.name)===promotionSizeKey(sizeName))||rows[0];return Number(chosen?.price||0)+addition}
    return Number(item.base_price||0)+addition;
  }
  function promotionPreview(item,discount,sizeName=''){
    const regular=promotionBasePrice(item,sizeName),value=Math.round(regular*(1-Number(discount||0)/100)*100)/100;
    return `${sizeName?escapeMenuText(sizeName)+' · ':''}${money(regular)} → <strong>${money(value)}</strong>`;
  }
  function syncPromotionRow(row){
    const check=row.querySelector('[data-promotion-enabled]'),input=row.querySelector('[data-promotion-discount]'),sizeSelect=row.querySelector('[data-promotion-size]'),preview=row.querySelector('[data-promotion-preview]');
    const item=menuProducts.find(product=>String(product.id)===String(row.dataset.promotionProduct));
    if(!check||!input||!preview||!item)return;
    row.classList.toggle('active',check.checked);input.disabled=!check.checked;if(sizeSelect)sizeSelect.disabled=!check.checked;
    const discount=Number(input.value||0),sizeName=sizeSelect?.value||'';
    preview.innerHTML=check.checked&&discount>0&&discount<100?promotionPreview(item,discount,sizeName):(check.checked?'Informe o desconto para ativar a oferta':'Preço normal: '+money(promotionBasePrice(item,sizeName)));
  }
  function renderPromotionManager(){
    const host=document.querySelector('#promotion-manager'),status=document.querySelector('#promotion-status'),save=document.querySelector('#save-promotions');if(!host)return;
    const categoryMap=new Map(menuCategories.map(category=>[String(category.id),category.name||category.slug]));
    const products=menuProducts.filter(item=>item.active!==false).sort((a,b)=>Number(Boolean(b.promotion_active))-Number(Boolean(a.promotion_active))||Number(a.promotion_sort_order||0)-Number(b.promotion_sort_order||0)||String(a.name||'').localeCompare(String(b.name||''),'pt-BR'));
    if(!products.length){host.innerHTML='<div class="promotion-empty">Nenhum produto disponível para promoção.</div>';if(status)status.textContent='0 produtos';if(save)save.disabled=true;return}
    host.innerHTML=products.map(item=>{
      const image=safeProductImage(item.image_url)||'https://placehold.co/96x96?text=LV',active=Boolean(item.promotion_active)&&Number(item.promotion_discount||0)>0,discount=Number(item.promotion_discount||0),sizeRows=promotionSizeRows(item);
      const selectedSize=sizeRows.find(size=>promotionSizeKey(size.name)===promotionSizeKey(item.promotion_size))?.name||sizeRows[0]?.name||'';
      const sizeControl=sizeRows.length?`<label class="promotion-size"><span>Tamanho da promoção</span><select data-promotion-size ${active?'':'disabled'}>${sizeRows.map(size=>`<option value="${escapeMenuText(size.name)}" ${promotionSizeKey(size.name)===promotionSizeKey(selectedSize)?'selected':''}>${escapeMenuText(size.name)}</option>`).join('')}</select></label>`:`<div class="promotion-size"><span>Tamanho</span><strong>Tamanho único</strong></div>`;
      return `<div class="promotion-row ${active?'active':''}" data-promotion-product="${item.id}"><div class="promotion-product"><img class="promotion-thumb" src="${escapeMenuText(image)}" alt=""><div class="promotion-product-copy"><strong>${escapeMenuText(item.name||'')}</strong><small>${escapeMenuText(categoryMap.get(String(item.category_id))||'Produto')}</small></div></div><label class="promotion-check"><input type="checkbox" data-promotion-enabled ${active?'checked':''}> Em promoção</label>${sizeControl}<label class="promotion-discount"><input type="number" min="0.01" max="99.99" step="0.01" data-promotion-discount value="${discount>0?discount:''}" placeholder="10" ${active?'':'disabled'}><span>%</span></label><div class="promotion-preview" data-promotion-preview></div></div>`
    }).join('');
    host.querySelectorAll('.promotion-row').forEach(row=>{const check=row.querySelector('[data-promotion-enabled]'),input=row.querySelector('[data-promotion-discount]'),size=row.querySelector('[data-promotion-size]');check?.addEventListener('change',()=>{syncPromotionRow(row);if(check.checked&&!input.value)input.focus()});input?.addEventListener('input',()=>syncPromotionRow(row));size?.addEventListener('change',()=>syncPromotionRow(row));syncPromotionRow(row)});
    const activeCount=products.filter(item=>Boolean(item.promotion_active)&&Number(item.promotion_discount||0)>0).length;if(status)status.textContent=`${activeCount} ${activeCount===1?'produto em promoção':'produtos em promoção'}`;if(save){save.disabled=false;save.onclick=savePromotions}lucide.createIcons();
  }
  async function savePromotions(){
    const button=document.querySelector('#save-promotions'),status=document.querySelector('#promotion-status'),rows=[...document.querySelectorAll('[data-promotion-product]')];if(!button||!rows.length)return;
    let order=0;const updates=[];
    for(const row of rows){
      const id=row.dataset.promotionProduct,enabled=Boolean(row.querySelector('[data-promotion-enabled]')?.checked),discount=Number(row.querySelector('[data-promotion-discount]')?.value||0),sizeSelect=row.querySelector('[data-promotion-size]'),sizeName=enabled&&sizeSelect?sizeSelect.value:null,item=menuProducts.find(product=>String(product.id)===String(id));
      if(enabled&&(!Number.isFinite(discount)||discount<=0||discount>=100)){showToast(`Confira o desconto de ${item?.name||'um produto'}`);row.querySelector('[data-promotion-discount]')?.focus();return}
      if(enabled&&sizeSelect&&!sizeName){showToast(`Escolha o tamanho da promoção de ${item?.name||'um produto'}`);sizeSelect.focus();return}
      const sortOrder=enabled?++order:0;
      if(!item||Boolean(item.promotion_active)!==enabled||Math.abs(Number(item.promotion_discount||0)-(enabled?discount:0))>.001||Number(item.promotion_sort_order||0)!==sortOrder||String(item.promotion_size||'')!==String(sizeName||''))updates.push({id,enabled,discount:enabled?discount:0,sortOrder,sizeName:sizeName||null});
    }
    button.disabled=true;status.textContent='Salvando promoções...';
    try{
      await Promise.all(updates.map(async item=>{const{error}=await db.from('products').update({promotion_active:item.enabled,promotion_discount:item.discount,promotion_sort_order:item.sortOrder,promotion_size:item.sizeName}).eq('id',item.id);if(error)throw error}));
      await loadRealMenu();showToast(updates.length?'Promoções atualizadas':'Promoções já estavam salvas');
    }catch(error){console.error('Erro ao salvar promoções:',error);status.textContent='Não foi possível salvar';showToast(error?.message||'Erro ao salvar promoções');button.disabled=false}
  }
  function formSizesFor(item){'''
s,count=pattern.subn(lambda _: new,s,count=1)
if count!=1: raise SystemExit('promotion manager block not found')

path.write_text(s,encoding='utf-8')
print('promotion size admin patch applied')
