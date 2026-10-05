from pathlib import Path

root = Path(__file__).parent
index = root / 'static' / 'index.html'
html = index.read_text()

# Replace the old fixed-price stock note with the flexible inventory rule.
html = html.replace(
    'Stock is allocated to counters for safe offline selling. Receiving stock adds new units to the chosen counter. Unit cost is fixed per variant in v1; historical sale costs are kept on receipts.',
    'Stock is allocated to counters for safe offline selling. Buying cost is entered when stock is received; selling price is entered when the item is sold. Prices are not fixed to a product.',
    1
)

css = r'''
<style id="kai-smart-stock-style">
.stock-smart-note{padding:11px 12px;border:1px solid #dce9ed;border-radius:10px;background:#f8fcfd;color:#315763;line-height:1.45}
.stock-smart-note b{color:#173f4a}
.stock-preview{padding:9px 11px;border-radius:8px;background:#eef8fa;border:1px solid #d8ebef;font-size:12px;line-height:1.45}
.stock-preview strong{color:#163f4a}
.stock-new-fields{display:contents}
.stock-hidden{display:none!important}
.stock-help{font-size:11px;color:var(--muted);margin-top:4px;line-height:1.35}
.stock-table-total{font-weight:800;color:#173f4a}
</style>
'''

js = r'''
<script id="kai-smart-stock-script">
(()=>{
  const ADULT_SIZES=['XS','S','M','L','XL','XXL','XXXL','4XL'];
  const CHILD_SIZES=['Kids XS','Kids S','Kids M','Kids L','Kids XL','2Y','3Y','4Y','5Y','6Y','7Y','8Y','9Y','10Y','11Y','12Y','13Y','14Y','15Y','16Y'];
  const GRADES=['Original','Fan/Net Version','Copy','Vintage','Player version','Replica','Training','Kids set','N/A'];

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
  function option(value,label=value){return `<option value="${esc(value)}">${esc(label)}</option>`}
  function sizeOptions(){
    return '<option value="">Choose size</option><optgroup label="Adult sizes">'+ADULT_SIZES.map(x=>option(x)).join('')+'</optgroup><optgroup label="Children sizes">'+CHILD_SIZES.map(x=>option(x)).join('')+'</optgroup><option value="__custom__">Other / custom size…</option>';
  }
  function gradeOptions(){
    return '<option value="">Choose grade / type</option>'+GRADES.map(x=>option(x)).join('')+'<option value="__custom__">Other / custom grade…</option>';
  }
  function chosenFlexible(form,name){
    const select=form.querySelector(`[name="${name}"]`);
    if(!select)return '';
    if(select.value==='__custom__')return String(form.querySelector(`[name="${name}Custom"]`)?.value||'').trim();
    return String(select.value||'').trim();
  }
  function setupSmartStockForm(){
    const form=document.querySelector('#dialog-form');
    if(!form)return;
    const kind=form.querySelector('[name="kind"]');
    const existing=form.querySelector('[name="existingSearch"]');
    const newFields=[...form.querySelectorAll('[data-stock-new]')];
    const preview=form.querySelector('#stock-existing-preview');
    if(!kind)return;

    const wireCustom=(name)=>{
      const select=form.querySelector(`[name="${name}"]`), custom=form.querySelector(`[name="${name}Custom"]`);
      if(!select||!custom)return;
      const refresh=()=>custom.closest('label')?.classList.toggle('stock-hidden',select.value!=='__custom__');
      select.addEventListener('change',refresh);refresh();
    };
    wireCustom('size');wireCustom('grade');

    const showPreview=()=>{
      if(!preview||!existing)return;
      const p=resolveExisting(existing.value);
      if(!p){preview.innerHTML='<span class="stock-help">Search by product, club, code, size, colour, grade/type, kit or season, then choose the matching item.</span>';return;}
      preview.innerHTML=`<strong>${esc(p.club||p.id)}</strong><br>${esc([p.id,p.size,p.grade,p.color,p.kit,p.season].filter(Boolean).join(' · '))}<br><b>${totalStock(p)}</b> units currently in stock`;
    };
    const redraw=()=>{
      const isNew=kind.value==='new';
      newFields.forEach(el=>el.classList.toggle('stock-hidden',!isNew));
      if(existing)existing.closest('label')?.classList.toggle('stock-hidden',isNew);
      if(preview)preview.classList.toggle('stock-hidden',isNew);
      if(!isNew&&existing)showPreview();
    };
    kind.onchange=redraw;
    if(existing){existing.oninput=showPreview;existing.onchange=showPreview;}
    redraw();
  }

  // Stock display: quantities and product attributes only. No fixed cost/retail/wholesale columns.
  stockTable=function(){
    const pp=state.products.filter(p=>matches(p)&&(!stockGrade||p.grade===stockGrade)&&(!stockSize||p.size===stockSize));
    $('#stock-table').innerHTML=`<div class="table-wrap"><table><thead><tr><th>Product / variant</th><th>Colour</th><th>Size</th><th>Grade / type</th><th class="end">Shop 1</th><th class="end">Shop 2</th><th class="end">Total units</th></tr></thead><tbody>${pp.map(p=>`<tr><td><span class="product-icon" aria-hidden="true">⚽</span>${esc(p.club)}<small>${esc([p.id,p.season,p.kit].filter(Boolean).join(' · '))}</small></td><td>${esc(p.color||'—')}</td><td><span class="badge">${esc(p.size||'—')}</span></td><td>${esc(p.grade||'—')}</td><td class="end">${qty(p,'Shop 1')}</td><td class="end">${qty(p,'Shop 2')}</td><td class="end stock-table-total">${totalStock(p)}</td></tr>`).join('')}</tbody></table></div>${!pp.length?'<div class="empty">No products match those filters.</div>':''}`;
  };

  restock=function(){
    const products=state.products||[];
    const hasProducts=products.length>0;
    const options=products.map(p=>`<option value="${esc(p.id)}">${esc([p.club,p.size,p.grade,p.color,p.kit,p.season].filter(Boolean).join(' · '))}</option>`).join('');
    showForm('Receive / add stock',`
      <div class="full stock-smart-note"><b>Flexible stock receiving.</b><br>Products can use adult sizes, children sizes, age sizes or any custom size/grade. Buying cost belongs to this delivery; selling price is entered later at the time of sale.</div>
      <label class="full">What are you receiving?
        <select name="kind">
          <option value="existing" ${hasProducts?'selected':''}>Add to an existing product</option>
          <option value="new" ${!hasProducts?'selected':''}>New product / variant</option>
        </select>
      </label>
      <label class="full">Find existing product
        <input name="existingSearch" list="kai-stock-products" type="text" placeholder="Search product, club, code, size, colour, grade…" autocomplete="off">
        <datalist id="kai-stock-products">${options}</datalist>
        <div class="stock-help">Start typing, then choose the matching item.</div>
      </label>
      <div id="stock-existing-preview" class="full stock-preview"><span class="stock-help">Choose a product to see its current quantity.</span></div>

      <label data-stock-new>Product code <input name="newId" type="text" placeholder="Leave blank to auto-create"></label>
      <label data-stock-new>Product / club / description <input name="club" type="text" placeholder="e.g. Arsenal home jersey, sports shorts, kids set"></label>
      <label data-stock-new>Season <input name="season" type="text" placeholder="e.g. 2026/27 or N/A"></label>
      <label data-stock-new>Kit / style <input name="kit" type="text" placeholder="Home / Away / Third / shorts / vest / other"></label>
      <label data-stock-new>Colour <input name="color" type="text" placeholder="e.g. Red"></label>
      <label data-stock-new>Size
        <select name="size">${sizeOptions()}</select>
        <div class="stock-help">Adult, kids and age sizes are included. Choose Other for anything else.</div>
      </label>
      <label data-stock-new class="stock-hidden">Custom size <input name="sizeCustom" type="text" placeholder="Type any size, e.g. 18-20, 5XL, 24"></label>
      <label data-stock-new>Grade / type
        <select name="grade">${gradeOptions()}</select>
      </label>
      <label data-stock-new class="stock-hidden">Custom grade / type <input name="gradeCustom" type="text" placeholder="Type any grade or product type"></label>

      <label>Destination counter
        <select name="device">${allowedDevices().map(d=>`<option value="${d}">${counterName(d)}</option>`).join('')}</select>
      </label>
      <label>Quantity received <input name="qty" type="number" min="1" step="1" value="1" required></label>
      <label>Actual buying cost per item (UGX)
        <input name="cost" type="number" min="0" step="1" placeholder="Cost for this delivery" required>
        <div class="stock-help">Used for profit accounting only. It is not a fixed product price.</div>
      </label>
      <label class="full">Supplier / note <input name="note" type="text" placeholder="Optional supplier, payment status or stock note"></label>
    `,async f=>{
      const form=f instanceof HTMLFormElement?f:document.querySelector('#dialog-form');
      const v=Object.fromEntries(f),qty=Number(v.qty),cost=Number(v.cost);
      if(!Number.isInteger(qty)||qty<1)throw new Error('Enter the quantity received');
      if(!Number.isFinite(cost)||cost<0)throw new Error('Enter the actual buying cost for this delivery');
      let id='';
      if(v.kind==='new'){
        const size=chosenFlexible(form,'size');
        const grade=chosenFlexible(form,'grade');
        if(!String(v.club||'').trim())throw new Error('Enter the product / club / description');
        if(!size)throw new Error('Choose or enter a size');
        if(!grade)throw new Error('Choose or enter a grade / type');
        id=String(v.newId||'').trim()||newStockCode(v.club,size);
        await onlineEvent('product',{
          id,
          club:String(v.club||'').trim(),
          season:String(v.season||'').trim(),
          kit:String(v.kit||'').trim(),
          color:String(v.color||'').trim(),
          size,
          grade,
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
        note:String(v.note||'Stock received').trim()||'Stock received'
      });
      toast(v.kind==='new'?'New product and stock added.':'Stock received successfully.');
    });
    setTimeout(setupSmartStockForm,0);
  };

  // Add product uses the same flexible receive-stock workflow.
  addProduct=function(){restock()};
})();
</script>
'''

body_end = html.rfind('</body>')
if body_end < 0:
    raise RuntimeError('Final body tag not found')
html = html[:body_end] + css + '\n' + js + '\n' + html[body_end:]
index.write_text(html)
print('Kai Wear broad sportswear variants and transaction-based stock pricing enabled.')
