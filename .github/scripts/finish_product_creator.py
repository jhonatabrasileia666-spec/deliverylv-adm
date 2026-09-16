from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

old = "const sizeCode=name=>{const normalized=String(name||'').trim().toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');if(['p','pequena','pequeno'].includes(normalized))return'P';if(['m','media','medio'].includes(normalized))return'M';if(['g','grande'].includes(normalized))return'G';return String(name||'').trim().toUpperCase()};"
new = old + "\n  const slugifyCategory=value=>String(value||'').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().trim().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'');"
assert old in s, 'sizeCode helper not found'
s = s.replace(old, new, 1)

old = "const categoryOptions=menuCategories.map(entry=>`<option value=\\\"${entry.id}\\\" ${entry.id===item?.category_id?'selected':''}>${escapeMenuText(entry.name||entry.slug)}</option>`).join('');"
new = "const categoryOptions=menuCategories.map(entry=>`<option value=\\\"${entry.id}\\\" ${entry.id===item?.category_id?'selected':''}>${escapeMenuText(entry.name||entry.slug)}</option>`).join('')+`<option value=\\\"__new__\\\">+ Nova categoria</option>`;"
assert old in s, 'categoryOptions not found'
s = s.replace(old, new, 1)

old = '<div class=\\"product-edit-field\\"><label for=\\"edit-product-category\\">Categoria</label><select id=\\"edit-product-category\\" required>${categoryOptions}</select></div><div class=\\"product-edit-field\\"><label for=\\"edit-product-pricing\\">Como é o preço?</label>'
new = '<div class=\\"product-edit-field\\"><label for=\\"edit-product-category\\">Categoria</label><select id=\\"edit-product-category\\" required>${categoryOptions}</select></div><div class=\\"product-edit-field\\"><label for=\\"edit-product-pricing\\">Como é o preço?</label>'
# Product form is inside a template literal; insert the new-category field just after pricing selector block by replacing a stable following fragment.
marker = '</select></div><div class=\\"product-edit-field full\\"><label for=\\"edit-product-name\\">Nome</label>'
replacement = '</select></div><div class=\\"product-edit-field full\\" id=\\"new-category-field\\" hidden><label for=\\"edit-new-category\\">Nome da nova categoria</label><input id=\\"edit-new-category\\" maxlength=\\"80\\" placeholder=\\"Ex.: Crepes\\"></div><div class=\\"product-edit-field full\\"><label for=\\"edit-product-name\\">Nome</label>'
assert marker in s, 'product name marker not found'
s = s.replace(marker, replacement, 1)

old = "pricing.addEventListener('change',syncPricing);syncPricing();"
new = "pricing.addEventListener('change',syncPricing);syncPricing();\n    const categorySelect=document.querySelector('#edit-product-category'),newCategoryField=document.querySelector('#new-category-field'),newCategoryInput=document.querySelector('#edit-new-category');\n    const syncCategory=()=>{const creating=categorySelect.value==='__new__';newCategoryField.hidden=!creating;if(newCategoryInput)newCategoryInput.required=creating};\n    categorySelect.addEventListener('change',syncCategory);syncCategory();"
assert old in s, 'bindProductForm pricing hook not found'
s = s.replace(old, new, 1)

old = "const categoryId=Number(document.querySelector('#edit-product-category').value);\n    const name=document.querySelector('#edit-product-name').value.trim();"
new = "const categoryChoice=document.querySelector('#edit-product-category').value;\n    let categoryId=categoryChoice;\n    const newCategoryName=document.querySelector('#edit-new-category')?.value.trim()||'';\n    const name=document.querySelector('#edit-product-name').value.trim();"
assert old in s, 'categoryId parsing not found'
s = s.replace(old, new, 1)

old = "if(!categoryId||!name){showToast('Informe categoria e nome do produto');return}"
new = "if(!categoryChoice||!name){showToast('Informe categoria e nome do produto');return}\n    if(categoryChoice==='__new__'&&!newCategoryName){showToast('Informe o nome da nova categoria');return}"
assert old in s, 'category validation not found'
s = s.replace(old, new, 1)

old = "try{\n      let imageUrl=rawImage?safeProductImage(rawImage):'';"
new = "try{\n      if(categoryChoice==='__new__'){\n        const slug=slugifyCategory(newCategoryName);\n        if(!slug)throw new Error('Nome de categoria inválido');\n        const existing=menuCategories.find(entry=>entry.slug===slug);\n        if(existing){categoryId=existing.id}else{\n          const{data:newCategory,error:categoryError}=await db.from('categories').insert({name:newCategoryName,slug,active:true}).select('id,slug,name').single();\n          if(categoryError)throw categoryError;\n          categoryId=newCategory.id;\n          menuCategories.push(newCategory);\n        }\n      }\n      let imageUrl=rawImage?safeProductImage(rawImage):'';"
assert old in s, 'saveProductForm try block not found'
s = s.replace(old, new, 1)

path.write_text(s, encoding='utf-8')
print('ADM product creator patch applied')
