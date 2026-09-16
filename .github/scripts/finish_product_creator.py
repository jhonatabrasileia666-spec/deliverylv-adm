from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

marker = '<script id="flexible-product-creator-fix">'
if marker in s:
    print('Flexible product creator override already present')
    raise SystemExit(0)

addon = r'''
<script id="flexible-product-creator-fix">
(()=>{
  const slugifyProductCategory=value=>String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'');
  const originalBindProductForm=bindProductForm;
  bindProductForm=function(item=null){
    originalBindProductForm(item);
    const categorySelect=document.querySelector('#edit-product-category');
    if(!categorySelect)return;
    if(!categorySelect.querySelector('option[value="__new__"]')){
      const option=document.createElement('option');
      option.value='__new__';option.textContent='+ Nova categoria';
      categorySelect.appendChild(option);
    }
    let field=document.querySelector('#new-category-field');
    if(!field){
      field=document.createElement('div');
      field.className='product-edit-field full';
      field.id='new-category-field';
      field.hidden=true;
      field.innerHTML='<label for="edit-new-category">Nome da nova categoria</label><input id="edit-new-category" maxlength="80" placeholder="Ex.: Crepes">';
      categorySelect.closest('.product-edit-field')?.insertAdjacentElement('afterend',field);
    }
    const input=document.querySelector('#edit-new-category');
    const sync=()=>{const creating=categorySelect.value==='__new__';field.hidden=!creating;if(input)input.required=creating};
    categorySelect.addEventListener('change',sync);sync();
  };

  saveProductForm=async function(event,id=null){
    event.preventDefault();
    const form=event.currentTarget,button=form.querySelector('button[type="submit"]');
    const categoryChoice=document.querySelector('#edit-product-category')?.value||'';
    let categoryId=categoryChoice;
    const newCategoryName=document.querySelector('#edit-new-category')?.value.trim()||'';
    const name=document.querySelector('#edit-product-name')?.value.trim()||'';
    const description=document.querySelector('#edit-product-description')?.value.trim()||'';
    const pricingMode=document.querySelector('#edit-product-pricing')?.value||'fixed';
    const sizes=collectProductSizes();
    const fixedPrice=Number(document.querySelector('#edit-product-price')?.value||0);
    const priceAddition=Number(document.querySelector('#edit-product-addition')?.value||0);
    const allowEdges=Boolean(document.querySelector('#edit-product-edges')?.checked);
    const active=Boolean(document.querySelector('#edit-product-active')?.checked);
    const file=document.querySelector('#edit-product-file')?.files?.[0]||null;
    const rawImage=document.querySelector('#edit-product-image')?.value.trim()||'';

    if(!categoryChoice||!name){showToast('Informe categoria e nome do produto');return}
    if(categoryChoice==='__new__'&&!newCategoryName){showToast('Informe o nome da nova categoria');return}
    if(pricingMode==='fixed'&&(!Number.isFinite(fixedPrice)||fixedPrice<0)){showToast('Confira o preço do produto');return}
    if(pricingMode==='sizes'&&(!sizes.length||sizes.some(size=>!Number.isFinite(size.price)||size.price<0))){showToast('Marque pelo menos um tamanho e informe seus preços');return}
    if(!Number.isFinite(priceAddition)||priceAddition<0){showToast('Confira o valor do acréscimo');return}
    if(rawImage&&!safeProductImage(rawImage)&&!file){showToast('Use um link de foto válido começando com http ou https');return}

    button.disabled=true;button.textContent='Salvando...';
    let createdId=id;
    try{
      if(categoryChoice==='__new__'){
        const slug=slugifyProductCategory(newCategoryName);
        if(!slug)throw new Error('Nome de categoria inválido');
        let category=menuCategories.find(entry=>String(entry.slug)===slug);
        if(!category){
          const{data:existing,error:lookupError}=await db.from('categories').select('id,slug,name,active').eq('slug',slug).maybeSingle();
          if(lookupError)throw lookupError;
          category=existing;
        }
        if(!category){
          const maxSort=menuCategories.reduce((max,entry)=>Math.max(max,Number(entry.sort_order||0)),0);
          const{data:newCategory,error:categoryError}=await db.from('categories').insert({name:newCategoryName,slug,active:true,sort_order:maxSort+1}).select('id,slug,name,active,sort_order').single();
          if(categoryError)throw categoryError;
          category=newCategory;
        }
        if(category.active===false)throw new Error('Essa categoria já existe, mas está desativada');
        categoryId=category.id;
      }

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

      document.querySelector('#product-edit-modal')?.classList.remove('show');
      await loadRealMenu();
      showToast(id?'Produto atualizado':'Produto adicionado ao cardápio');
    }catch(error){
      console.error('Erro ao salvar produto:',error);
      showToast(error?.message||'Não foi possível salvar o produto');
    }finally{
      button.disabled=false;
      button.innerHTML=id?'<i data-lucide="save"></i>Salvar alterações':'<i data-lucide="plus"></i>Adicionar produto';
      lucide.createIcons();
    }
  };
})();
</script>
'''

if '</body>' not in s:
    raise SystemExit('closing body not found')
s = s.replace('</body>', addon + '</body>', 1)
path.write_text(s, encoding='utf-8')
print('Runtime product creator override added')
