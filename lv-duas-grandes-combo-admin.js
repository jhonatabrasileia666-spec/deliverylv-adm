(function installLvDuasGrandesAdmin(){
  const KIND='duas_grandes_calabresa_frango';
  const originalLoadRealMenu=loadRealMenu;
  function renderDuasGrandesAdmin(){
    const host=document.querySelector('#menu-subview-promotions');
    if(!host)return;
    let panel=document.querySelector('#lv-duas-grandes-admin');
    if(!panel){
      panel=document.createElement('section');
      panel.id='lv-duas-grandes-admin';
      panel.className='promotion-admin-panel';
      panel.style.marginBottom='24px';
      const oldPanel=document.querySelector('#lv-pizza-combo-admin');
      if(oldPanel)oldPanel.insertAdjacentElement('afterend',panel);
      else host.prepend(panel);
    }
    const combo=menuProducts.find(product=>product.combo_kind===KIND);
    if(!combo){
      panel.innerHTML='<h2>Combo 2 Pizzas Grandes</h2><p>Produto não encontrado no catálogo.</p>';return;
    }
    panel.innerHTML='<div class="promotion-admin-head"><div><span class="eyebrow">Promoção de pizzas</span>'+
      '<h2>2 pizzas Grandes · Calabresa ou Frango</h2>'+
      '<p>Permite escolher o sabor de cada pizza, uma borda por pizza e refrigerante opcional. Os adicionais seguem os preços cadastrados no cardápio.</p>'+
      '</div></div><div style="display:flex;flex-wrap:wrap;align-items:end;gap:14px">'+
      '<label style="display:grid;gap:6px;min-width:175px;flex:1"><strong>Preço das 2 pizzas (R$)</strong>'+
      '<input type="number" id="lv-duas-price" min="0.01" step="0.01" value="'+Number(combo.base_price||0).toFixed(2)+
      '" style="height:42px;padding:10px;background:var(--panel-2);border:1px solid var(--line);border-radius:8px;color:var(--text)"></label>'+
      '<label style="display:flex;align-items:center;gap:10px;min-height:42px">'+
      '<input type="checkbox" id="lv-duas-active" '+(combo.active?'checked':'')+'> <strong>Mostrar no cardápio</strong></label>'+
      '<button class="button" id="lv-duas-save" type="button">Salvar promoção</button></div>'+
      '<p class="menu-help" style="margin-top:12px">As duas pizzas custam o valor informado. Bordas e bebida são cobradas separadamente, conforme a escolha do cliente. Esta promoção não altera os preços das pizzas avulsas.</p>';
    panel.querySelector('#lv-duas-save').onclick=async()=>{
      const price=Number(panel.querySelector('#lv-duas-price').value);
      const active=panel.querySelector('#lv-duas-active').checked;
      if(!Number.isFinite(price)||price<=0||price>999999.99){
        showToast('Informe um valor válido para a promoção');return;
      }
      const button=panel.querySelector('#lv-duas-save');
      button.disabled=true;button.textContent='Salvando...';
      try{
        const {data,error}=await db.from('products')
          .update({base_price:Math.round(price*100)/100,active,promotion_active:false,promotion_discount:0})
          .eq('id',combo.id).select('id');
        if(error||!data?.length)throw error||new Error('Não foi possível salvar a promoção');
        await loadRealMenu();
        showToast(active?'Promoção disponível no cardápio':'Promoção desativada');
      }catch(error){
        console.error('Erro ao salvar promoção de duas pizzas:',error);
        button.disabled=false;button.textContent='Salvar promoção';
        showToast(error?.message||'Não foi possível salvar');
      }
    };
  }
  loadRealMenu=async function(){
    const result=await originalLoadRealMenu();
    renderDuasGrandesAdmin();
    return result;
  };
})();