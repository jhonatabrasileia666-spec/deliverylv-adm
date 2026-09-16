from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'{label} not found')
    s = s.replace(old, new, 1)

size_helper = "const sizeCode=name=>{const normalized=String(name||'').trim().toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');if(['p','pequena','pequeno'].includes(normalized))return'P';if(['m','media','medio'].includes(normalized))return'M';if(['g','grande'].includes(normalized))return'G';return String(name||'').trim().toUpperCase()};"
if 'const slugifyCategory=' not in s:
    replace_once(size_helper, size_helper + "\n  const slugifyCategory=value=>String(value||'').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().trim().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'');", 'sizeCode helper')

old = '''const categoryOptions=menuCategories.map(entry=>`<option value="${entry.id}" ${entry.id===item?.category_id?'selected':''}>${escapeMenuText(entry.name||entry.slug)}</option>`).join('');'''
new = '''const categoryOptions=menuCategories.map(entry=>`<option value="${entry.id}" ${entry.id===item?.category_id?'selected':''}>${escapeMenuText(entry.name||entry.slug)}</option>`).join('')+`<option value="__new__">+ Nova categoria</option>`;'''
if '+ Nova categoria' not in s:
    replace_once(old, new, 'categoryOptions')

marker = '''</select></div><div class="product-edit-field full"><label for="edit-product-name">Nome</label>'''
replacement = '''</select></div><div class="product-edit-field full" id="new-category-field" hidden><label for="edit-new-category">Nome da nova categoria</label><input id="edit-new-category" maxlength="80" placeholder="Ex.: Crepes"></div><div class="product-edit-field full"><label for="edit-product-name">Nome</label>'''
if 'id="new-category-field"' not in s:
    replace_once(marker, replacement, 'new category field marker')

old = "pricing.addEventListener('change',syncPricing);syncPricing();"
new = "pricing.addEventListener('change',syncPricing);syncPricing();\n    const categorySelect=document.querySelector('#edit-product-category'),newCategoryField=document.querySelector('#new-category-field'),newCategoryInput=document.querySelector('#edit-new-category');\n    const syncCategory=()=>{const creating=categorySelect.value==='__new__';newCategoryField.hidden=!creating;if(newCategoryInput)newCategoryInput.required=creating};\n    categorySelect.addEventListener('change',syncCategory);syncCategory();"
if 'const syncCategory=' not in s:
    replace_once(old, new, 'bindProductForm pricing hook')

old = "const categoryId=Number(document.querySelector('#edit-product-category').value);\n    const name=document.querySelector('#edit-product-name').value.trim();"
new = "const categoryChoice=document.querySelector('#edit-product-category').value;\n    let categoryId=categoryChoice;\n    const newCategoryName=document.querySelector('#edit-new-category')?.value.trim()||'';\n    const name=document.querySelector('#edit-product-name').value.trim();"
if 'const categoryChoice=' not in s:
    replace_once(old, new, 'category UUID parsing')

old = "if(!categoryId||!name){showToast('Informe categoria e nome do produto');return}"
new = "if(!categoryChoice||!name){showToast('Informe categoria e nome do produto');return}\n    if(categoryChoice==='__new__'&&!newCategoryName){showToast('Informe o nome da nova categoria');return}"
if "categoryChoice==='__new__'&&!newCategoryName" not in s:
    replace_once(old, new, 'category validation')

old = "try{\n      let imageUrl=rawImage?safeProductImage(rawImage):'';"
new = "try{\n      if(categoryChoice==='__new__'){\n        const slug=slugifyCategory(newCategoryName);\n        if(!slug)throw new Error('Nome de categoria inválido');\n        const existing=menuCategories.find(entry=>entry.slug===slug);\n        if(existing){categoryId=existing.id}else{\n          const{data:newCategory,error:categoryError}=await db.from('categories').insert({name:newCategoryName,slug,active:true}).select('id,slug,name').single();\n          if(categoryError)throw categoryError;\n          categoryId=newCategory.id;\n          menuCategories.push(newCategory);\n        }\n      }\n      let imageUrl=rawImage?safeProductImage(rawImage):'';"
if "if(categoryChoice==='__new__'){" not in s:
    replace_once(old, new, 'new category insert block')

path.write_text(s, encoding='utf-8')
print('ADM product creator patch applied')
