(function installLvPizzaComboAdmin(){
  const kind='grande_pequena_choco_morango';
  const originalLoadRealMenu=loadRealMenu;
  function renderPizzaComboAdmin(){
    const host=document.querySelector('#menu-subview-promotions');
    if(!host)return;
    let panel=document.querySelector('#lv-pizza-combo-admin');
    if(!panel){
      panel=document.createElement('section');
      panel.id='lv-pizza-combo-admin';
      panel.className='promotion-admin-panel';
      panel.style.marginBottom='24px';
      host.prepend(panel);
    }
    const combo=menuProducts.find(product=>product.combo_kind===kind);
    if(!combo){panel.innerHTML='<h2>Combo de Pizzas</h2><p>Produto do combo não foi encontrado no catálogo.</p>';return}
    panel.innerHTML=`<div class="promotion-admin-head"><div><span class="eyebrow">Promoção pronta para personalizar</span><h2>Combo de 2 Pizzas</h2><p>1 pizza Grande (até 2 sabores) + 1 pizza Pequena de Chocolate com Morango.</p></div></div><div style="display:flex;flex-wrap:wrap;align-items:end;gap:14px"><label style="display:grid;gap:6px;min-width:175px;flex:1"><strong>Preço base (R$)</strong><input type="number" id="lv-combo-price" min="0.01" step="0.01" value="${Number(combo.base_price||0).toFixed(2)}" style="height:42px;padding:10px;background:var(--panel-2);border:1px solid var(--line);border-radius:8px;color:var(--text)"></label><label style="display:flex;align-items:center;gap:10px;min-height:42px"><input type="checkbox" id="lv-combo-active" ${combo.active?'checked':''}> <strong>Mostrar no cardápio</strong></label><button class="button" id="lv-combo-save" type="button">Salvar combo</button></div><p class="menu-help" style="margin-top:12px">Os adicionais de Pizzaiolo, Quatro Queijos, Carne Seca e demais sabores são lidos automaticamente dos produtos existentes. Dois sabores especiais somam dois adicionais. Esta oferta não altera as pizzas avulsas.</p>`;
    panel.querySelector('#lv-combo-save').addEventListener('click',async()=>{
      const price=Number(panel.querySelector('#lv-combo-price').value);
      const active=panel.querySelector('#lv-combo-active').checked;
      if(!Number.isFinite(price)||price<=0||price>999999.99){showToast('Informe um preço válido para o combo');return}
      const button=panel.querySelector('#lv-combo-save');
      button.disabled=true;button.textContent='Salvando...';
      try{
        const {data,error}=await db.from('products')
          .update({base_price:Math.round(price*100)/100,active,promotion_active:false,promotion_discount:0})
          .eq('id',combo.id).select('id');
        if(error||!data?.length)throw error||new Error('Sem permissão para salvar o combo');
        await loadRealMenu();
        showToast(active?'Combo disponível no cardápio':'Combo desativado no cardápio');
      }catch(error){
        button.disabled=false;button.textContent='Salvar combo';
        console.error('Erro ao salvar combo',error);
        showToast(error?.message||'Não foi possível salvar a promoção');
      }
    });
  }
  loadRealMenu=async function(){
    const result=await originalLoadRealMenu();
    renderPizzaComboAdmin();
    return result;
  };
})();
