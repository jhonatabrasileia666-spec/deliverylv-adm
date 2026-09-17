from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')

old_css=".promotion-check input{width:18px;height:18px;accent-color:var(--orange)}.promotion-discount"
new_css=".promotion-check input{width:18px;height:18px;accent-color:var(--orange)}.promotion-toggle-area{display:grid;gap:7px;align-content:center}.promotion-disable{width:max-content;padding:6px 9px;border:1px solid #ff8f7955;border-radius:7px;background:#3a211c;color:#ffb2a3;font-size:9px;font-weight:900}.promotion-disable:hover{border-color:#ff8f79;background:#49251e}.promotion-disable:disabled{opacity:.5;cursor:wait}.promotion-discount"
if old_css not in s: raise SystemExit('css anchor not found')
s=s.replace(old_css,new_css,1)

old_markup='''<label class="promotion-check"><input type="checkbox" data-promotion-enabled ${active?'checked':''}> Em promoção</label>${sizeControl}<label class="promotion-discount">'''
new_markup='''<div class="promotion-toggle-area"><label class="promotion-check"><input type="checkbox" data-promotion-enabled ${active?'checked':''}> Em promoção</label>${active?`<button type="button" class="promotion-disable" data-disable-promotion="${item.id}">Desativar promoção</button>`:''}</div>${sizeControl}<label class="promotion-discount">'''
if old_markup not in s: raise SystemExit('markup anchor not found')
s=s.replace(old_markup,new_markup,1)

old_bind="host.querySelectorAll('.promotion-row').forEach(row=>{const check=row.querySelector('[data-promotion-enabled]'),input=row.querySelector('[data-promotion-discount]'),size=row.querySelector('[data-promotion-size]');check?.addEventListener('change',()=>{syncPromotionRow(row);if(check.checked&&!input.value)input.focus()});input?.addEventListener('input',()=>syncPromotionRow(row));size?.addEventListener('change',()=>syncPromotionRow(row));syncPromotionRow(row)});"
new_bind="host.querySelectorAll('.promotion-row').forEach(row=>{const check=row.querySelector('[data-promotion-enabled]'),input=row.querySelector('[data-promotion-discount]'),size=row.querySelector('[data-promotion-size]');check?.addEventListener('change',()=>{syncPromotionRow(row);if(check.checked&&!input.value)input.focus()});input?.addEventListener('input',()=>syncPromotionRow(row));size?.addEventListener('change',()=>syncPromotionRow(row));syncPromotionRow(row)});host.querySelectorAll('[data-disable-promotion]').forEach(button=>button.addEventListener('click',()=>disablePromotion(button.dataset.disablePromotion,button)));"
if old_bind not in s: raise SystemExit('bind anchor not found')
s=s.replace(old_bind,new_bind,1)

anchor='''  async function savePromotions(){'''
insert='''  async function disablePromotion(id,button){
    const item=menuProducts.find(product=>String(product.id)===String(id));
    if(!item)return;
    const original=button?.textContent||'Desativar promoção';
    if(button){button.disabled=true;button.textContent='Desativando...'}
    try{
      const{error}=await db.from('products').update({promotion_active:false,promotion_discount:0,promotion_sort_order:0,promotion_size:null}).eq('id',id);
      if(error)throw error;
      await loadRealMenu();
      showToast(`Promoção de ${item.name} desativada`);
    }catch(error){
      console.error('Erro ao desativar promoção:',error);
      showToast(error?.message||'Erro ao desativar promoção');
      if(button){button.disabled=false;button.textContent=original}
    }
  }
'''
if anchor not in s: raise SystemExit('function anchor not found')
s=s.replace(anchor,insert+anchor,1)

path.write_text(s,encoding='utf-8')
print('disable promotion button patch applied')
