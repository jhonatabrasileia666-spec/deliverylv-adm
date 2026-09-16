from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="<input id=\"edit-product-price\" type=\"number\" min=\"0\" max=\"999999.99\" step=\"0.01\" required value=\"${Number(item.base_price||0).toFixed(2)}\" ${isPizza?'title=\"Para pizzas, o valor cobrado é definido pelo tamanho\"':''}>"
new="<input id=\"edit-product-price\" type=\"number\" min=\"0\" max=\"999999.99\" step=\"0.01\" required value=\"${Number(item.base_price||0).toFixed(2)}\" ${isPizza?'disabled title=\"Nas pizzas, o valor é definido pelos tamanhos Pequena, Média e Grande\"':''}>"
if old not in s: raise SystemExit('price input marker not found')
s=s.replace(old,new,1)
old2="const basePrice=Number(document.querySelector('#edit-product-price').value);"
new2="const currentProduct=menuProducts.find(product=>String(product.id)===String(id));\n    const currentCategory=menuCategories.find(category=>category.id===currentProduct?.category_id);\n    const isPizza=String(currentCategory?.slug||'').toLowerCase()==='pizzas';\n    const basePrice=isPizza?Number(currentProduct?.base_price||0):Number(document.querySelector('#edit-product-price').value);"
if old2 not in s: raise SystemExit('base price marker not found')
s=s.replace(old2,new2,1)
p.write_text(s,encoding='utf-8')
