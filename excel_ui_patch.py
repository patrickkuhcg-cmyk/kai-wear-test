from pathlib import Path

root = Path(__file__).parent
index = root / 'static' / 'index.html'
html = index.read_text()

css = r'''
<style id="kai-excel-inventory-style">
.excel-stock-summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:0 0 12px}
.excel-stock-kpi{border:1px solid #dce9ed;border-radius:10px;background:#f9fcfd;padding:11px}.excel-stock-kpi b{display:block;font-size:20px;color:#173f4a}.excel-stock-kpi span{font-size:11px;color:var(--muted)}
.excel-stock-tag{font-size:10px;padding:3px 7px;border-radius:999px;background:#eef6f8;color:#315763;white-space:nowrap}.excel-stock-tag.low{background:#fff3dc;color:#8a5700}.excel-stock-tag.out{background:#fde8e8;color:#9f2929}
.excel-form-section{grid-column:1/-1;font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:#4e7079;padding-top:4px;border-top:1px solid #e7eef0}
.excel-stock-sub{display:block;margin-top:2px;color:var(--muted);font-size:10px}
@media(max-width:760px){.excel-stock-summary{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>
'''

js = r'''
<script id="kai-excel-inventory-script">
(()=>{
 const CATEGORIES=['Original Jerseys','Fan/Net Version Jerseys','Copy Jerseys','Vintage Jerseys',"Children's Jersey Sets",'Shorts','2-Piece Play Sets','Body Armour','Baseball Jerseys','Lakers/Basketball Vests','Plain Jumpers','Other Sportswear'];
 const VERSIONS=['Original','Fan/Net Version','Copy','Vintage','N/A'];
 const SIZES=['XS','S','M','L','XL','XXL','XXXL','Kids S','Kids M','Kids L'];
 const KITS=['Home','Away','Third','N/A'];
 const STOCK_PAY=['Paid','Partially Paid','Unpaid'];
 let excelStockCategory='';
 function totalUnits(p){return Object.values(p?.alloc||{}).reduce((a,v)=>a+Number(v||0),0)}
 function pName(p){return String(p.name||p.club||p.id||'Product')}
 function pCategory(p){if(p.category)return p.category;const g=String(p.grade||'');if(g==='Original')return 'Original Jerseys';if(g==='Fan/Net Version')return 'Fan/Net Version Jerseys';if(g==='Copy')return 'Copy Jerseys';if(g==='Vintage')return 'Vintage Jerseys';if(String(p.size||'').toLowerCase().includes('kid'))return "Children's Jersey Sets";return 'Other Sportswear'}
 function minLevel(p){const x=Number(p.minStock);return Number.isFinite(x)&&x>=0?x:5}
 function stockStatus(p){const q=totalUnits(p),m=minLevel(p);return q===0?'OUT':q<=m?'RESTOCK':'OK'}
 function optionList(items,selected=''){return items.map(x=>`<option value="${esc(x)}" ${x===selected?'selected':''}>${esc(x)}</option>`).join('')}
 function searchText(p){return [p.id,p.name,p.category,p.club,p.grade,p.kit,p.season,p.size,p.color].filter(Boolean).join(' ').toLowerCase()}

 if(typeof saleSearchText==='function')saleSearchText=p=>searchText(p);

 stockTable=function(){
   const q=String(search||'').trim().toLowerCase();
   const pp=(state.products||[]).filter(p=>(!q||searchText(p).includes(q))&&(!excelStockCategory||pCategory(p)===excelStockCategory)&&(!stockGrade||p.grade===stockGrade)&&(!stockSize||p.size===stockSize));
   const total=pp.reduce((a,p)=>a+totalUnits(p),0), low=pp.filter(p=>stockStatus(p)==='RESTOCK').length, out=pp.filter(p=>stockStatus(p)==='OUT').length;
   $('#stock-table').innerHTML=`
     <div class="excel-stock-summary"><div class="excel-stock-kpi"><b>${total}</b><span>Units in current view</span></div><div class="excel-stock-kpi"><b>${pp.length}</b><span>Product variants</span></div><div class="excel-stock-kpi"><b>${low}</b><span>Need restocking</span></div><div class="excel-stock-kpi"><b>${out}</b><span>Out of stock</span></div></div>
     <div class="table-wrap"><table><thead><tr><th>Product</th><th>Category</th><th>Club / Country</th><th>Version</th><th>Kit</th><th>Season</th><th>Size</th><th class="end">Shop 1</th><th class="end">Shop 2</th><th class="end">Total</th><th>Status</th></tr></thead><tbody>
     ${pp.map(p=>{const st=stockStatus(p);return `<tr><td><b>${esc(pName(p))}</b><small>${esc(p.id||'')}</small></td><td>${esc(pCategory(p))}</td><td>${esc(p.club||'—')}</td><td>${esc(p.grade||'—')}</td><td>${esc(p.kit||'—')}</td><td>${esc(p.season||'—')}</td><td><span class="badge">${esc(p.size||'—')}</span></td><td class="end">${qty(p,'Shop 1')}</td><td class="end">${qty(p,'Shop 2')}</td><td class="end"><b>${totalUnits(p)}</b></td><td><span class="excel-stock-tag ${st==='RESTOCK'?'low':st==='OUT'?'out':''}">${st}</span><span class="excel-stock-sub">Min ${minLevel(p)}</span></td></tr>`}).join('')}
     </tbody></table></div>${!pp.length?'<div class="empty">No products match those filters.</div>':''}`;
 };

 restock=function(){
   const products=state.products||[];
   const list=products.map(p=>`<option value="${esc(p.id)}">${esc([pName(p),p.category||pCategory(p),p.club,p.grade,p.kit,p.season,p.size].filter(Boolean).join(' · '))}</option>`).join('');
   showForm('Receive / add stock',`
    <div class="full note"><b>Excel-style inventory receiving.</b><br>Choose an existing product or create a new product variant. Buying cost belongs to this delivery only; selling price is entered at sale time.</div>
    <label class="full">Stock type<select name="kind"><option value="existing" ${products.length?'selected':''}>Existing product / variant</option><option value="new" ${products.length?'':'selected'}>New product / variant</option></select></label>
    <label class="full" data-excel-existing>Find existing product<input name="existingSearch" list="excel-products" autocomplete="off" placeholder="Search name, category, club, code, size, version…"><datalist id="excel-products">${list}</datalist></label>
    <div class="excel-form-section" data-excel-new>Product master</div>
    <label data-excel-new>Product code<input name="newId" placeholder="Leave blank to auto-create"></label>
    <label data-excel-new>Product name<input name="name" placeholder="e.g. Manchester United Home Jersey 2026/27"></label>
    <label data-excel-new>Category<select name="category"><option value="">Choose category</option>${optionList(CATEGORIES)}<option value="__custom__">Other / custom…</option></select></label>
    <label data-excel-new data-custom-category hidden>Custom category<input name="categoryCustom"></label>
    <label data-excel-new>Club / Country<input name="club" placeholder="e.g. Manchester United, Uganda Cranes"></label>
    <label data-excel-new>Version / Grade<select name="grade"><option value="">Choose version</option>${optionList(VERSIONS)}<option value="__custom__">Other / custom…</option></select></label>
    <label data-excel-new data-custom-grade hidden>Custom version / grade<input name="gradeCustom"></label>
    <label data-excel-new>Home / Away / Third<select name="kit"><option value="">Choose</option>${optionList(KITS)}<option value="__custom__">Other / custom…</option></select></label>
    <label data-excel-new data-custom-kit hidden>Custom kit / style<input name="kitCustom"></label>
    <label data-excel-new>Season<input name="season" placeholder="e.g. 2026/2027 or N/A"></label>
    <label data-excel-new>Colour<input name="color" placeholder="e.g. Red"></label>
    <label data-excel-new>Size<select name="size"><option value="">Choose size</option>${optionList(SIZES)}<option value="__custom__">Other / custom…</option></select></label>
    <label data-excel-new data-custom-size hidden>Custom size<input name="sizeCustom" placeholder="Any supplier size"></label>
    <label data-excel-new>Minimum stock level<input name="minStock" type="number" min="0" step="1" value="5"></label>
    <div class="excel-form-section">Delivery / stock-in</div>
    <label>Destination counter<select name="device">${allowedDevices().map(d=>`<option value="${d}">${counterName(d)}</option>`).join('')}</select></label>
    <label>Quantity received<input name="qty" type="number" min="1" step="1" value="1" required></label>
    <label>Actual unit buying cost (UGX)<input name="cost" type="number" min="0" step="1" required placeholder="Cost for this delivery"></label>
    <label>Supplier<input name="supplier" placeholder="Supplier name"></label>
    <label>Payment status<select name="paymentStatus">${optionList(STOCK_PAY)}</select></label>
    <label class="full">Remarks<input name="note" placeholder="Optional note"></label>
   `,async f=>{
      const form=f instanceof HTMLFormElement?f:document.querySelector('#dialog-form'),v=Object.fromEntries(f);
      const custom=(n)=>String(v[n]==='__custom__'?v[n+'Custom']||'':v[n]||'').trim();
      const qtyN=Number(v.qty),cost=Number(v.cost);if(!Number.isInteger(qtyN)||qtyN<1)throw new Error('Enter quantity received');if(!Number.isFinite(cost)||cost<0)throw new Error('Enter actual buying cost');
      let id;
      if(v.kind==='new'){
        const name=String(v.name||'').trim(),club=String(v.club||'').trim(),size=custom('size'),grade=custom('grade'),kit=custom('kit'),category=custom('category');
        if(!name)throw new Error('Enter the product name');if(!category)throw new Error('Choose or enter a category');if(!size)throw new Error('Choose or enter a size');
        id=String(v.newId||'').trim()||newStockCode(name,size);
        await onlineEvent('product',{id,name,category,club,grade,kit,season:String(v.season||'').trim(),color:String(v.color||'').trim(),size,minStock:Number(v.minStock||5),cost,retail:0,wholesale:0});
      }else{
        const raw=String(v.existingSearch||'').trim().toLowerCase();const p=(state.products||[]).find(x=>String(x.id).toLowerCase()===raw)||(state.products||[]).find(x=>searchText(x)===raw)||(state.products||[]).filter(x=>searchText(x).includes(raw))[0];if(!p)throw new Error('Choose an existing product or switch to New product / variant');id=p.id;
      }
      await onlineEvent('restock',{id,device:v.device,qty:qtyN,cost,date:now(),supplier:String(v.supplier||'').trim(),paymentStatus:String(v.paymentStatus||'').trim(),note:String(v.note||'Stock received').trim()||'Stock received'});
      toast(v.kind==='new'?'New product and stock added.':'Stock received successfully.');
   });
   setTimeout(()=>{
     const form=document.querySelector('#dialog-form');if(!form)return;const kind=form.querySelector('[name="kind"]');
     const toggle=()=>{const isNew=kind.value==='new';form.querySelectorAll('[data-excel-new]').forEach(x=>x.hidden=!isNew);form.querySelectorAll('[data-excel-existing]').forEach(x=>x.hidden=isNew)};kind.onchange=toggle;toggle();
     for(const n of ['category','grade','kit','size']){const sel=form.querySelector(`[name="${n}"]`),lab=form.querySelector(`[data-custom-${n}]`);if(sel&&lab){const t=()=>lab.hidden=sel.value!=='__custom__';sel.onchange=t;t();}}
   },0);
 };
 addProduct=function(){restock()};

 function enhanceStockPage(){
   if(typeof page==='undefined'||page!=='Stock')return;
   const searchBox=document.querySelector('#search');if(searchBox)searchBox.placeholder='Search name, category, club/country, version, kit, season, size or code…';
   const filters=document.querySelector('.filters');
   const grade=document.querySelector('#grade'),size=document.querySelector('#size');
   if(filters&&!document.querySelector('#excel-category')){
     const cat=document.createElement('select');cat.id='excel-category';cat.setAttribute('aria-label','Category');
     cat.innerHTML='<option value="">All categories</option>'+optionList(CATEGORIES,excelStockCategory);
     cat.value=excelStockCategory;cat.onchange=e=>{excelStockCategory=e.target.value;stockTable()};
     if(grade)filters.insertBefore(cat,grade);else filters.appendChild(cat);
   }
   if(grade){
     const extras=[...new Set((state.products||[]).map(p=>String(p.grade||'').trim()).filter(x=>x&&!VERSIONS.includes(x)))];
     grade.innerHTML='<option value="">All versions / grades</option>'+optionList(VERSIONS,stockGrade)+extras.map(x=>`<option value="${esc(x)}" ${stockGrade===x?'selected':''}>${esc(x)} (custom)</option>`).join('');
     grade.value=stockGrade;
   }
   if(size){
     const extras=[...new Set((state.products||[]).map(p=>String(p.size||'').trim()).filter(x=>x&&!SIZES.includes(x)))];
     size.innerHTML='<option value="">All sizes</option>'+optionList(SIZES,stockSize)+extras.map(x=>`<option value="${esc(x)}" ${stockSize===x?'selected':''}>${esc(x)} (custom)</option>`).join('');
     size.value=stockSize;
   }
   const note=[...document.querySelectorAll('.note')].find(n=>n.textContent.includes('Stock is allocated'));if(note)note.innerHTML='<b>Excel inventory standards:</b> Category, Jersey Version and Size follow the workbook lists. Buying cost is captured per stock delivery; selling price is entered per sale. Custom values remain available when a supplier item falls outside the standard lists.';
   const h=[...document.querySelectorAll('h1,h2')].find(x=>x.textContent.trim()==='Jersey stock');if(h)h.textContent='Products & stock';
 }
 function excelDashboard(){
   if(typeof page==='undefined'||page!=='Dashboard'||!state)return;let box=document.getElementById('excel-dashboard-stock');if(!box){box=document.createElement('section');box.id='excel-dashboard-stock';box.className='kai-intel';(document.querySelector('main')||document.querySelector('.content'))?.appendChild(box)}if(!box)return;
   const ps=state.products||[], total=ps.reduce((a,p)=>a+totalUnits(p),0),low=ps.filter(p=>stockStatus(p)==='RESTOCK').length,out=ps.filter(p=>stockStatus(p)==='OUT').length,cats=new Map();ps.forEach(p=>cats.set(pCategory(p),(cats.get(pCategory(p))||0)+totalUnits(p)));
   box.innerHTML=`<div class="kai-intel-head"><div><h3>Stock control</h3><small>Excel inventory model: category, variant and minimum-stock monitoring.</small></div></div><div class="kai-intel-grid"><div class="kai-intel-card"><b>${total}</b><span>Total units available</span></div><div class="kai-intel-card"><b>${ps.length}</b><span>Product variants</span></div><div class="kai-intel-card"><b>${low}</b><span>RESTOCK variants</span></div><div class="kai-intel-card"><b>${out}</b><span>Out-of-stock variants</span></div></div><div class="kai-intel-list" style="margin-top:12px"><h4>Units by category</h4>${[...cats.entries()].sort((a,b)=>b[1]-a[1]).slice(0,8).map(([k,v])=>`<div class="kai-intel-row"><span>${esc(k)}</span><strong>${v} units</strong></div>`).join('')||'<div class="tiny">No inventory yet.</div>'}</div>`;
 }
 function enhance(){try{enhanceStockPage();excelDashboard()}catch(_){} }
 if(typeof render==='function'){const r=render;render=function(...a){const x=r.apply(this,a);setTimeout(enhance,0);return x}}
 setTimeout(enhance,0);
})();
</script>
'''

body_end=html.rfind('</body>')
if body_end<0:raise RuntimeError('Final body tag not found')
html=html[:body_end]+css+'\n'+js+'\n'+html[body_end:]
index.write_text(html)
print('Kai Wear Excel inventory UI enabled.')
