from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global text
    if old not in text:
        raise SystemExit(f'{label} marker not found')
    text = text.replace(old, new, 1)

replace_once(
"const categoryOptions=menuCategories.map(entry=>`<option value=\"${entry.id}\" ${entry.id===item?.category_id?'selected':''}>${escapeMenuText(entry.name||entry.slug)}</option>`).join('');",
"const categoryOptions=menuCategories.map(entry=>`<option value=\"${entry.id}\" ${entry.id===item?.category_id?'selected':''}>${escapeMenuText(entry.name||entry.slug)}</option>`).join('')+(item?'':'<option value=\"__new__\">+ Criar nova categoria</option>');",
'category options'
)

replace_once(
'<div class="product-edit-field"><label for="edit-product-category">Categoria</label><select id="edit-product-category" required>${categoryOptions}</select></div><div class="product-edit-field"><label for="edit-product-pricing">Como é o preço?</label>',
'<div class="product-edit-field"><label for="edit-product-category">Categoria</label><select id="edit-product-category" required>${categoryOptions}</select></div><div class="product-edit-field full" id="new-category-field" style="display:none"><label for="edit-product-new-category">Nome da nova categoria</label><input id="edit-product-new-category" maxlength="80" placeholder="Ex.: Crepes"></div><div class="product-edit-field"><label for="edit-product-pricing">Como é o preço?</label>',
'new category field'
)

replace_once(
"const sizesSection=document.querySelector('#sizes-section');\n    const syncPricing=()=>{const usesSizes=pricing.value==='sizes';fixedField.style.display=usesSizes?'none':'grid';sizesSection.style.display=usesSizes?'grid':'none'};\n    pricing.addEventListener('change',syncPricing);syncPricing();",
"const sizesSection=document.querySelector('#sizes-section');\n    const categorySelect=document.querySelector('#edit-product-category');\n    const newCategoryField=document.querySelector('#new-category-field');\n    const newCategoryInput=document.querySelector('#edit-product-new-category');\n    const syncCategory=()=>{const creating=categorySelect?.value==='__new__';if(newCategoryField)newCategoryField.style.display=creating?'grid':'none';if(newCategoryInput)newCategoryInput.required=creating};\n    const syncPricing=()=>{const usesSizes=pricing.value==='sizes';fixedField.style.display=usesSizes?'none':'grid';sizesSection.style.display=usesSizes?'grid':'none'};\n    categorySelect?.addEventListener('change',syncCategory);syncCategory();\n    pricing.addEventListener('change',syncPricing);syncPricing();",
'bind category chooser'
)

replace_once(
"const categoryId=Number(document.querySelector('#edit-product-category').value);\n    const name=document.querySelector('#edit-product-name').value.trim();",
"const categoryValue=document.querySelector('#edit-product-category').value;\n    let categoryId=categoryValue==='__new__'?null:Number(categoryValue);\n    const newCategoryName=document.querySelector('#edit-product-new-category')?.value.trim()||'';\n    const name=document.querySelector('#edit-product-name').value.trim();",
'category value save'
)

replace_once(
"if(!categoryId||!name){showToast('Informe categoria e nome do produto');return}",
"if((categoryValue==='__new__'&&!newCategoryName)||(!categoryId&&categoryValue!=='__new__')||!name){showToast('Informe categoria e nome do produto');return}",
'category validation'
)

replace_once(
"try{\n      let imageUrl=rawImage?safeProductImage(rawImage):'';",
"try{\n      if(categoryValue==='__new__'){\n        const slug=newCategoryName.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().trim().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'');\n        if(!slug)throw new Error('Nome da categoria inválido');\n        const existing=menuCategories.find(entry=>String(entry.slug||'').toLowerCase()===slug||String(entry.name||'').toLowerCase()===newCategoryName.toLowerCase());\n        if(existing){categoryId=Number(existing.id)}else{\n          const{data:createdCategory,error:categoryError}=await db.from('categories').insert({name:newCategoryName,slug,active:true,sort_order:menuCategories.length+1}).select('id,slug,name').single();\n          if(categoryError||!createdCategory?.id)throw categoryError||new Error('Não foi possível criar a categoria');\n          categoryId=Number(createdCategory.id);\n        }\n      }\n      let imageUrl=rawImage?safeProductImage(rawImage):'';",
'create category before product'
)

path.write_text(text, encoding='utf-8')
print('custom category support applied')
