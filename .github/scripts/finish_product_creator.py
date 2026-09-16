from pathlib import Path
import re

path=Path('index.html')
s=path.read_text(encoding='utf-8')

def sub_once(pattern,repl,label,flags=0):
    global s
    s2,n=re.subn(pattern,repl,s,count=1,flags=flags)
    if n!=1:
        raise SystemExit(f'{label} not found')
    s=s2

if 'const slugifyCategory=' not in s:
    sub_once(r"(const sizeCode=name=>\{.*?\};)", r"\1\n  const slugifyCategory=value=>String(value||'').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().trim().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'');", 'size helper', re.S)

if '+ Nova categoria' not in s:
    sub_once(r"const categoryOptions=(.*?\.join\(''\));", r"const categoryOptions=\1+`<option value=\"__new__\">+ Nova categoria</option>`;", 'category options')

if 'id="new-category-field"' not in s:
    sub_once(r"(id=\"edit-product-pricing\".*?</select></div>)(<div class=\"product-edit-field full\"><label for=\"edit-product-name\">)", r"\1<div class=\"product-edit-field full\" id=\"new-category-field\" hidden><label for=\"edit-new-category\">Nome da nova categoria</label><input id=\"edit-new-category\" maxlength=\"80\" placeholder=\"Ex.: Crepes\"></div>\2", 'new category input', re.S)

if 'const syncCategory=' not in s:
    sub_once(r"pricing\.addEventListener\('change',syncPricing\);syncPricing\(\);", "pricing.addEventListener('change',syncPricing);syncPricing();\n    const categorySelect=document.querySelector('#edit-product-category'),newCategoryField=document.querySelector('#new-category-field'),newCategoryInput=document.querySelector('#edit-new-category');\n    const syncCategory=()=>{const creating=categorySelect.value==='__new__';newCategoryField.hidden=!creating;if(newCategoryInput)newCategoryInput.required=creating};\n    categorySelect.addEventListener('change',syncCategory);syncCategory();", 'category field binding')

if 'const categoryChoice=' not in s:
    sub_once(r"const categoryId=Number\(document\.querySelector\('#edit-product-category'\)\.value\);", "const categoryChoice=document.querySelector('#edit-product-category').value;\n    let categoryId=categoryChoice;\n    const newCategoryName=document.querySelector('#edit-new-category')?.value.trim()||'';", 'category uuid parsing')

if "categoryChoice==='__new__'&&!newCategoryName" not in s:
    sub_once(r"if\(!categoryId\|\|!name\)\{showToast\('Informe categoria e nome do produto'\);return\}", "if(!categoryChoice||!name){showToast('Informe categoria e nome do produto');return}\n    if(categoryChoice==='__new__'&&!newCategoryName){showToast('Informe o nome da nova categoria');return}", 'category validation')

if "if(categoryChoice==='__new__'){" not in s:
    sub_once(r"try\{\s*let imageUrl=rawImage\?safeProductImage\(rawImage\):'';", "try{\n      if(categoryChoice==='__new__'){\n        const slug=slugifyCategory(newCategoryName);\n        if(!slug)throw new Error('Nome de categoria inválido');\n        const existing=menuCategories.find(entry=>entry.slug===slug);\n        if(existing){categoryId=existing.id}else{\n          const{data:newCategory,error:categoryError}=await db.from('categories').insert({name:newCategoryName,slug,active:true}).select('id,slug,name').single();\n          if(categoryError)throw categoryError;\n          categoryId=newCategory.id;\n          menuCategories.push(newCategory);\n        }\n      }\n      let imageUrl=rawImage?safeProductImage(rawImage):'';", 'new category insert', re.S)

path.write_text(s,encoding='utf-8')
print('ADM flexible creator patch applied')
