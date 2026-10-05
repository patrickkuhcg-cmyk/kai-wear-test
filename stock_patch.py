from pathlib import Path

root = Path(__file__).parent
index = root / 'static' / 'index.html'
html = index.read_text()

css = r'''
<style id="kai-smart-stock-style">
.stock-smart-note{padding:11px 12px;border:1px solid #dce9ed;border-radius:10px;background:#f8fcfd;color:#315763;line-height:1.45}
.stock-smart-note b{color:#173f4a}
.stock-preview{padding:9px 11px;border-radius:8px;background:#eef8fa;border:1px solid #d8ebef;font-size:12px;line-height:1.45}
.stock-preview strong{color:#163f4a}
.stock-new-fields{display:contents}
.stock-hidden{display:none!important}
.stock-help{font-size:11px;color:var(--muted);margin-top:4px;line-height:1.35}
</style>
'''

js = r'''
<script id="kai-smart-stock-script">
(()=>{
  function stockSearchText(p){
    return `${p.id||''} ${p.club||''} ${p.season||''} ${p.kit||''} ${p.color||''} ${p.size||''} ${p.grade||''}`.toLowerCase();
  }
  function totalStock(p){
    return Object.values(p?.alloc||{}).reduce((a,v)=>a+Number(v||0),0);
  }
  function resolveExisting(value){
    const q=String(value||'').trim().toLowerCase();
    if(!q)return null;
    const exact=(state.products||[]).find(p=>String(p.id).toLowerCase()===q);
    if(exact)return exact;
    const matches=(state.products||[]).filter(p=>stockSearchText(p).includes(q));
    return matches.length===1?matches[0]:null;
  }
  function referenceNote(base,ref){
    const clean=String(base||'Stock received').trim()||'Stock received';
    return ref>0?`${clean} · Reference sale price UGX ${Math.round(ref).toLocaleString()} (not fixed)`:clean;
  }
  function setupSmartStockForm(){
    const form=document.querySelector('#dialog-form');
    if(!form)return;
    const kind=form.querySelector('[name="kind"]');
    const existing=form.querySelector('[name="existingSearch"]');
    const newFields=[...form.querySelectorAll('[data-stock-new]')];
    const preview=form.querySelector('#stock-existing-preview');
    if(!kind)return;
    const redraw=()=>{
      const isNew=kind.value==='new';
      newFields.forEach(el=>el.classList.toggle('stock-hidden',!isNew));
      if(existing)existing.closest('label')?.classList.toggle('stock-hidden',isNew);
      if(preview)preview.classList.toggle('stock-hidden',isNew);
      if(!isNew&&existing)showPreview();
    };
    const showPreview=()=>{
      if(!preview||!existing)return;
      const p=resolveExisting(existing.value);
      if(!p){preview.innerHTML='<span class="stock-help">Search by club, code, size, colour, grade, kit or season, then choose the matching product.</span>';return;}
      preview.innerHTML=`<strong>${esc(p.club||p.id)}</strong><br>${esc([p.id,p.size,p.grade,p.color,p.kit,p.season].filter(Boolean).join(' · '))}<br><b>${totalStock(p)}</b> units currently in stock · Average buying cost: <b>${money(p.cost||0)}</b>`;
    };
    kind.onchange=redraw;
    if(existing){existing.oninput=showPreview;existing.onchange=showPreview;}
    redraw();
  }

  restock=function(){
    const products=state.products||[];
    const hasProducts=products.length>0;
    const options=products.map(p=>`<option value="${esc(p.id)}">${esc([p.club,p.size,p.grade,p.color,p.kit,p.season].filter(Boolean).join(' · '))}</option>`).join('');
    showForm('Receive / add stock',`
      <div class="full stock-smart-note"><b>Flexible stock receiving.</b><br>Buying cost is entered for this delivery only. Selling price is not fixed in Stock — the cashier enters the actual selling price when making a sale.</div>
      <label class="full">What are you receiving?
        <select name="kind">
          <option value="existing" ${hasProducts?'selected':''}>Add to an existing product</option>
          <option value="new" ${!hasProducts?'selected':''}>New product / variant</option>
        </select>
      </label>
      <label class="full">Find existing product
        <input name="existingSearch" list="kai-stock-products" type="text" placeholder="Search club, code, size, colour, grade…" autocomplete="off">
        <datalist id="kai-stock-products">${options}</datalist>
        <div class="stock-help">Start typing, then choose the matching item.</div>
      </label>
      <div id="stock-existing-preview" class="full stock-preview"><span class="stock-help">Choose a product to see current stock and average buying cost.</span></div>

      <label data-stock-new>Product code <input name="newId" type="text" placeholder="Leave blank to auto-create"></label>
      <label data-stock-new>Product / club / team <input name="club" type="text" placeholder="e.g. Arsenal jersey"></label>
      <label data-stock-new>Season <input name="season" type="text" placeholder="e.g. 2026/27"></label>
      <label data-stock-new>Kit / style <input name="kit" type="text" placeholder="Home / Away / Third"></label>
      <label data-stock-new>Colour <input name="color" type="text" placeholder="e.g. Red"></label>
      <label data-stock-new>Size <input name="size" type="text" placeholder="S / M / L / XL"></label>
      <label data-stock-new>Grade / type <input name="grade" type="text" placeholder="Replica / Original / other"></label>

      <label>Destination counter
        <select name="device">${allowedDevices().map(d=>`<option value="${d}">${counterName(d)}</option>`).join('')}</select>
      </label>
      <label>Quantity received <input name="qty" type="number" min="1" step="1" value="1" required></label>
      <label>Actual buying cost per item (UGX)
        <input name="cost" type="number" min="0" step="1" placeholder="Cost for this batch" required>
      </label>
      <label>Reference selling price (optional)
        <input name="referencePrice" type="number" min="0" step="1" placeholder="Guide only — not fixed">
        <div class="stock-help">This is only a note/reference. Sales can use any actual selling price.</div>
      </label>
      <label class="full">Supplier / note <input name="note" type="text" placeholder="Optional supplier or stock note"></label>
    `,async f=>{
      const v=Object.fromEntries(f);
      const qty=Number(v.qty),cost=Number(v.cost),ref=Number(v.referencePrice||0);
      if(!Number.isInteger(qty)||qty<1)throw new Error('Enter the quantity received');
      if(!Number.isFinite(cost)||cost<0)throw new Error('Enter the actual buying cost for this batch');
      if(!Number.isFinite(ref)||ref<0)throw new Error('Reference selling price must be zero/blank or a positive amount');
      let id='';
      if(v.kind==='new'){
        for(const k of ['club','size'])if(!String(v[k]||'').trim())throw new Error('Enter at least the product name/team and size');
        id=String(v.newId||'').trim()||newStockCode(v.club,v.size);
        await onlineEvent('product',{
          id,
          club:String(v.club||'').trim(),
          season:String(v.season||'').trim(),
          kit:String(v.kit||'').trim(),
          color:String(v.color||'').trim(),
          size:String(v.size||'').trim(),
          grade:String(v.grade||'').trim()||'Standard',
          cost,
          retail:0,
          wholesale:0
        });
      }else{
        const p=resolveExisting(v.existingSearch);
        if(!p)throw new Error('Choose one existing product from the search list, or switch to New product / variant');
        id=p.id;
      }
      await onlineEvent('restock',{
        id,
        device:v.device,
        qty,
        cost,
        date:now(),
        note:referenceNote(v.note,ref)
      });
      toast(v.kind==='new'?'New product and stock added.':'Stock received and average buying cost updated.');
    });
    setTimeout(setupSmartStockForm,0);
  };

  // Keep the existing Add product action consistent with the smarter stock workflow.
  addProduct=function(){restock()};
})();
</script>
'''

body_end = html.rfind('</body>')
if body_end < 0:
    raise RuntimeError('Final body tag not found')
html = html[:body_end] + css + '\n' + js + '\n' + html[body_end:]
index.write_text(html)
print('Kai Wear smart flexible stock workflow enabled.')
