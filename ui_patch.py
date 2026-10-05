from pathlib import Path

root = Path(__file__).parent
index = root / 'static' / 'index.html'
html = index.read_text()

css = r'''
<style id="kai-sale-picker-style">
.sale-search-wrap{position:relative;width:100%;z-index:60}
.sale-search-wrap #search{width:100%;margin:0}
.sale-search-dropdown{position:absolute;left:0;right:0;top:calc(100% + 5px);z-index:200;background:#fff;border:1px solid var(--line);border-radius:10px;box-shadow:0 12px 30px rgba(16,42,56,.18);max-height:270px;overflow-y:auto;overscroll-behavior:contain;scrollbar-gutter:stable;padding:6px;display:none}
.sale-search-dropdown.open{display:block}
.sale-search-item{width:100%;border:0;border-bottom:1px solid #edf2f4;background:#fff;color:inherit;text-align:left;padding:10px 11px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;border-radius:7px;cursor:pointer}
.sale-search-item:last-child{border-bottom:0}
.sale-search-item:hover,.sale-search-item.active{background:#eefafd;outline:1px solid rgba(0,189,221,.28)}
.sale-search-main{font-weight:700;line-height:1.25}
.sale-search-meta{font-size:11px;color:var(--muted);margin-top:3px;white-space:normal}
.sale-search-stock{font-size:11px;font-weight:700;white-space:nowrap;padding:4px 7px;border-radius:999px;background:#eef7f8;color:#315763}
.sale-search-empty{padding:10px 11px;color:var(--muted);font-size:12px}
.sale-manual-row{padding:7px 6px 3px;border-top:1px solid #e9f0f2;margin-top:4px}
.sale-manual-btn{width:100%;text-align:left;border:1px dashed var(--accent);background:#f8fdfe;color:#184f5d;border-radius:8px;padding:9px 10px;font-weight:700;cursor:pointer}
.sale-manual-btn:hover{background:#eefafd}
#catalog.sale-catalog-anchor{margin:0;padding:0;border:0;background:transparent}
.sale-manual-link{margin-top:8px;font-size:12px}
@media(max-width:700px){.sale-search-dropdown{max-height:230px}.sale-search-item{grid-template-columns:1fr}.sale-search-stock{justify-self:start}}
</style>
'''

js = r'''
<script id="kai-sale-picker-script">
(()=>{
  let pickerOpen=false;
  let pickerIndex=-1;
  let pickerScroll=0;
  let pendingSync=false;
  let pickerPointer=false;
  let interactionUntil=0;
  let idleTimer=null;
  const coreSync=typeof sync==='function'?sync:null;
  const coreAdd=typeof addSaleProduct==='function'?addSaleProduct:null;

  function touchInteraction(ms=2500){
    interactionUntil=Date.now()+ms;
    if(idleTimer)clearTimeout(idleTimer);
    idleTimer=setTimeout(()=>{
      if(pendingSync&&coreSync&&Date.now()>=interactionUntil){
        pendingSync=false;
        const y=window.scrollY;
        coreSync().catch(()=>{}).finally(()=>requestAnimationFrame(()=>window.scrollTo(0,y)));
      }
    },ms+80);
  }
  function availableProducts(){
    return (state?.products||[]).filter(p=>((p.alloc?.[device]||0)-(cart.find(l=>l.id===p.id)?.qty||0))>0);
  }
  function searchable(p){
    return `${p.id||''} ${p.club||''} ${p.season||''} ${p.kit||''} ${p.color||''} ${p.size||''} ${p.grade||''}`.toLowerCase();
  }
  function ensurePicker(){
    const input=document.getElementById('search');
    const catalog=document.getElementById('catalog');
    if(!input||!catalog)return null;
    let wrap=input.closest('.sale-search-wrap');
    if(!wrap){
      wrap=document.createElement('div');
      wrap.className='sale-search-wrap';
      input.parentNode.insertBefore(wrap,input);
      wrap.appendChild(input);
      wrap.appendChild(catalog);
    }else if(catalog.parentNode!==wrap){wrap.appendChild(catalog)}
    catalog.classList.add('sale-catalog-anchor','sale-search-dropdown');
    let manual=document.getElementById('kai-manual-product-link');
    if(!manual&&wrap.parentNode){
      manual=document.createElement('div');
      manual.id='kai-manual-product-link';
      manual.className='sale-manual-link';
      manual.innerHTML='<button type="button" class="sale-manual-btn">+ Product not in the system — type it manually</button>';
      wrap.parentNode.insertBefore(manual,wrap.nextSibling);
      manual.querySelector('button').onclick=()=>openManualProduct(input.value||'');
    }
    return {input,catalog,wrap};
  }
  function closePicker(runSync=true){
    const ui=ensurePicker();
    pickerOpen=false;pickerIndex=-1;
    if(ui)ui.catalog.classList.remove('open');
    if(runSync&&pendingSync&&coreSync&&Date.now()>=interactionUntil){
      pendingSync=false;
      const y=window.scrollY;
      setTimeout(()=>coreSync().catch(()=>{}).finally(()=>requestAnimationFrame(()=>window.scrollTo(0,y))),0);
    }
  }
  function chooseProduct(p){
    if(!p||!coreAdd)return;
    touchInteraction();
    closePicker(false);
    coreAdd(p);
    const ui=ensurePicker();
    if(ui){ui.input.value='';search='';ui.catalog.classList.remove('open')}
  }
  function drawPicker(){
    const ui=ensurePicker();if(!ui)return;
    const q=(ui.input.value||'').trim().toLowerCase();
    search=ui.input.value||'';
    const all=availableProducts();
    const results=(q?all.filter(p=>searchable(p).includes(q)):all).slice(0,10);
    const prevScroll=ui.catalog.scrollTop||pickerScroll;
    const rows=results.map((p,i)=>{
      const left=(p.alloc?.[device]||0)-(cart.find(l=>l.id===p.id)?.qty||0);
      return `<button type="button" class="sale-search-item${i===pickerIndex?' active':''}" data-kai-sale-id="${esc(p.id)}"><span><div class="sale-search-main">${esc(p.club||p.id)}</div><div class="sale-search-meta">${esc([p.id,p.size,p.grade,p.color,p.kit,p.season].filter(Boolean).join(' · '))}</div></span><span class="sale-search-stock">${left} in stock</span></button>`;
    }).join('');
    const manualLabel=q?`Use “${esc(ui.input.value.trim())}” as a new product`:'Type a product name manually';
    ui.catalog.innerHTML=(rows||'<div class="sale-search-empty">No matching product in current inventory.</div>')+`<div class="sale-manual-row"><button type="button" class="sale-manual-btn" id="kai-manual-from-search">+ ${manualLabel}</button></div>`;
    ui.catalog.classList.toggle('open',pickerOpen);
    requestAnimationFrame(()=>{ui.catalog.scrollTop=prevScroll;pickerScroll=prevScroll});
    ui.catalog.onpointerdown=()=>{pickerPointer=true;touchInteraction(3000)};
    ui.catalog.onpointerup=()=>{pickerPointer=false;touchInteraction(1600)};
    ui.catalog.onscroll=()=>{pickerScroll=ui.catalog.scrollTop;touchInteraction(1800)};
    ui.catalog.querySelectorAll('[data-kai-sale-id]').forEach(btn=>{
      btn.onmousedown=e=>e.preventDefault();
      btn.onclick=()=>chooseProduct(all.find(p=>p.id===btn.dataset.kaiSaleId));
    });
    const manual=ui.catalog.querySelector('#kai-manual-from-search');
    if(manual){manual.onmousedown=e=>e.preventDefault();manual.onclick=()=>openManualProduct(ui.input.value||'')}
  }

  async function openManualProduct(prefill=''){
    touchInteraction(4000);
    closePicker(false);
    if(typeof showForm!=='function'||typeof onlineEvent!=='function'){
      toast('Manual product entry is unavailable on this screen.');return;
    }
    showForm('Add product for this sale',`
      <div class="full note"><b>Product not yet in the system.</b><br>Enter it here. The system will create it, receive the quantity into this counter, then add it to this sale.</div>
      <label class="full">Product / club / description<input name="club" type="text" value="${esc(prefill)}" placeholder="e.g. Uganda Cranes jersey" required></label>
      <label>Size<input name="size" type="text" placeholder="e.g. M"></label>
      <label>Colour<input name="color" type="text" placeholder="e.g. Red"></label>
      <label>Grade / type<input name="grade" type="text" placeholder="e.g. Replica"></label>
      <label>Quantity<input name="qty" type="number" min="1" step="1" value="1" required></label>
      <label>Buying cost per item (UGX)<input name="cost" type="number" min="0" step="1" required></label>
      <label class="full">Selling price per item (UGX)<input name="price" type="number" min="1" step="1" required></label>
    `,async f=>{
      const v=Object.fromEntries(f),qty=Number(v.qty),cost=Number(v.cost),price=Number(v.price);
      if(!String(v.club||'').trim())throw new Error('Enter the product name');
      if(!Number.isInteger(qty)||qty<1)throw new Error('Enter a valid quantity');
      if(!Number.isFinite(cost)||cost<0)throw new Error('Enter the buying cost');
      if(!Number.isFinite(price)||price<=0)throw new Error('Enter the selling price');
      if(typeof newStockCode!=='function')throw new Error('Product code generator is unavailable');
      const id=newStockCode(v.club,v.size||'NA');
      await onlineEvent('product',{id,club:String(v.club).trim(),season:'',kit:'',color:String(v.color||'').trim(),size:String(v.size||'N/A').trim()||'N/A',grade:String(v.grade||'Manual').trim()||'Manual',cost,retail:0,wholesale:0});
      await onlineEvent('restock',{id,device,qty,cost,date:now(),note:'Quick product entry from New Sale'});
      if(coreSync)await coreSync().catch(()=>{});
      const p=(state.products||[]).find(x=>x.id===id);
      if(!p)throw new Error('The new product was saved but could not be loaded. Refresh and try again.');
      cart.push({id:p.id,qty,price,cost:p.cost});
      search='';
      renderCart();
      catalog();
      toast('Product added to this sale and inventory.');
    });
  }

  catalog=function(){
    const ui=ensurePicker();if(!ui)return;
    if(document.activeElement===ui.input)pickerOpen=true;
    drawPicker();
    ui.input.onfocus=()=>{touchInteraction(3000);pickerOpen=true;pickerIndex=-1;drawPicker()};
    ui.input.oninput=e=>{touchInteraction(3000);search=e.target.value;pickerOpen=true;pickerIndex=-1;pickerScroll=0;drawPicker()};
    ui.input.onkeydown=e=>{
      touchInteraction(2200);
      const items=[...ui.catalog.querySelectorAll('[data-kai-sale-id]')];
      if(e.key==='ArrowDown'&&items.length){e.preventDefault();pickerOpen=true;pickerIndex=Math.min(pickerIndex+1,items.length-1);drawPicker();ui.catalog.querySelector('.active')?.scrollIntoView({block:'nearest'})}
      else if(e.key==='ArrowUp'&&items.length){e.preventDefault();pickerIndex=Math.max(pickerIndex-1,0);drawPicker();ui.catalog.querySelector('.active')?.scrollIntoView({block:'nearest'})}
      else if(e.key==='Enter'){
        e.preventDefault();
        if(items.length){const idx=pickerIndex>=0?pickerIndex:0;const btn=items[idx];chooseProduct(availableProducts().find(p=>p.id===btn?.dataset.kaiSaleId))}
        else openManualProduct(ui.input.value||'');
      }
      else if(e.key==='Escape'){e.preventDefault();closePicker()}
    };
    ui.input.onblur=()=>setTimeout(()=>{if(!pickerPointer)closePicker()},180);
  };

  // Strong interaction lock: live sync is deferred while the user is typing,
  // scrolling or choosing a sale item. This prevents the New Sale DOM from
  // being rebuilt underneath the dropdown.
  if(coreSync){
    sync=async function(...args){
      const ui=ensurePicker();
      const activeSale=(typeof page!=='undefined'&&page==='New sale');
      const interacting=activeSale&&(pickerOpen||pickerPointer||document.activeElement===ui?.input||Date.now()<interactionUntil);
      if(interacting){pendingSync=true;return}
      const pageY=window.scrollY;
      const dropY=ui?.catalog.scrollTop||0;
      const result=await coreSync(...args);
      requestAnimationFrame(()=>{
        window.scrollTo(0,pageY);
        const next=ensurePicker();if(next)next.catalog.scrollTop=dropY;
      });
      return result;
    };
  }

  document.addEventListener('click',e=>{
    const wrap=document.querySelector('.sale-search-wrap');
    if(wrap&&!wrap.contains(e.target)&&!e.target.closest('#kai-manual-product-link'))closePicker();
  });

  setTimeout(()=>{try{catalog()}catch(_){ }},0);
})();
</script>
'''

body_end = html.rfind('</body>')
if body_end < 0:
    raise RuntimeError('Final body tag not found')
html = html[:body_end] + css + '\n' + js + '\n' + html[body_end:]
index.write_text(html)
print('Kai Wear sales picker stabilized and manual product entry enabled.')
