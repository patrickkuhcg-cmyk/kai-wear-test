from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

css=r'''
<style id="kai-clean-stock-style">
#kai-stock-search-wrap{position:relative;min-width:240px;flex:1 1 320px}
#kai-stock-search-dropdown{position:absolute;left:0;right:0;top:calc(100% + 5px);z-index:1200;background:#fff;border:1px solid #d7e6ea;border-radius:10px;box-shadow:0 10px 28px rgba(19,57,68,.14);max-height:280px;overflow:auto;display:none}
#kai-stock-search-dropdown.open{display:block}
.kai-stock-option{display:block;width:100%;padding:9px 11px;text-align:left;border:0;border-bottom:1px solid #edf3f5;background:#fff;color:inherit;cursor:pointer}
.kai-stock-option:last-child{border-bottom:0}.kai-stock-option:hover,.kai-stock-option:focus{background:#f5fbfc;outline:none}.kai-stock-option b{display:block;font-size:12px}.kai-stock-option small{display:block;color:var(--muted);font-size:10px;margin-top:2px}
.kai-stock-compact-bar{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin:10px 0 12px;padding:10px 12px;border:1px solid #dce9ed;border-radius:11px;background:#f9fcfd}
.kai-stock-compact-metrics{display:flex;gap:14px;flex-wrap:wrap}.kai-stock-compact-metrics span{font-size:11px;color:var(--muted)}.kai-stock-compact-metrics b{font-size:14px;color:#173f4a;margin-right:4px}
.kai-stock-actions{display:flex;gap:7px;flex-wrap:wrap;align-items:center}
.kai-stock-toggle{border:1px solid #cfe0e4;background:#fff;border-radius:8px;padding:7px 10px;font-weight:700;font-size:11px;cursor:pointer}
.kai-stock-toggle:hover{background:#f4fafb}.kai-stock-toggle.primary{background:#173f4a;color:#fff;border-color:#173f4a}.kai-stock-toggle.primary:hover{background:#214f5c}
#stock-table.kai-stock-collapsed .table-wrap,#stock-table.kai-stock-collapsed>.empty{display:none!important}
#stock-table.kai-stock-collapsed .excel-stock-summary{display:none!important}
#kai-category-summary.kai-category-collapsed .kai-category-grid{display:none!important}
#kai-category-summary.kai-category-collapsed .kai-category-summary-head{border-bottom:0}
#kai-category-summary .kai-category-summary-head{cursor:default}
#kai-category-summary .kai-category-summary-head>strong{display:none}
@media(max-width:700px){#kai-stock-search-wrap{min-width:100%;width:100%}.kai-stock-compact-bar{align-items:flex-start}.kai-stock-compact-metrics{gap:8px 12px}.kai-stock-actions{width:100%}.kai-stock-actions .kai-stock-toggle{flex:1 1 auto}}
</style>
'''

js=r'''
<script id="kai-clean-stock-script">
(()=>{
 let stockDetailsOpen=false;
 let categoryOpen=false;
 let stockSearchFocus=-1;

 function stockText(p){return [p.id,p.name,p.category,p.club,p.grade,p.kit,p.season,p.size,p.color].filter(Boolean).join(' ').toLowerCase()}
 function totalUnitsOf(p){return Object.values(p?.alloc||{}).reduce((a,v)=>a+Number(v||0),0)}
 function getMatches(q){
   q=String(q||'').trim().toLowerCase();
   const ps=(state?.products||[]).filter(p=>!q||stockText(p).includes(q));
   return ps.slice(0,14);
 }
 function closeStockDrop(){const d=document.querySelector('#kai-stock-search-dropdown');if(d)d.classList.remove('open');stockSearchFocus=-1}
 function renderStockDrop(){
   if(typeof page==='undefined'||page!=='Stock')return;
   const input=document.querySelector('#search');const d=document.querySelector('#kai-stock-search-dropdown');if(!input||!d)return;
   const matches=getMatches(input.value);
   d.innerHTML=matches.length?matches.map((p,i)=>`<button type="button" class="kai-stock-option" data-stock-i="${i}"><b>${esc(p.name||p.club||p.id)}</b><small>${esc([p.id,p.category,p.grade,p.kit,p.season,p.size,`${totalUnitsOf(p)} units`].filter(Boolean).join(' · '))}</small></button>`).join(''):'<div class="empty" style="padding:10px">No matching product.</div>';
   d.classList.add('open');
   d.querySelectorAll('[data-stock-i]').forEach((b,i)=>b.onclick=()=>{
      const p=matches[i];if(!p)return;
      input.value=p.name||p.club||p.id;search=input.value;closeStockDrop();stockTable();
   });
 }
 function installSearchDropdown(){
   const input=document.querySelector('#search');if(!input||input.dataset.kaiStockClean==='1')return;
   input.dataset.kaiStockClean='1';
   let wrap=input.parentElement;
   if(!wrap||wrap.id!=='kai-stock-search-wrap'){
      const w=document.createElement('div');w.id='kai-stock-search-wrap';input.parentNode.insertBefore(w,input);w.appendChild(input);wrap=w;
   }
   let d=document.querySelector('#kai-stock-search-dropdown');if(!d){d=document.createElement('div');d.id='kai-stock-search-dropdown';wrap.appendChild(d)}
   input.setAttribute('autocomplete','off');
   input.placeholder='Search products…';
   input.addEventListener('focus',renderStockDrop);
   input.addEventListener('input',()=>{search=input.value;renderStockDrop();stockTable()});
   input.addEventListener('keydown',e=>{
      const opts=[...d.querySelectorAll('.kai-stock-option')];
      if(e.key==='ArrowDown'){e.preventDefault();stockSearchFocus=Math.min(stockSearchFocus+1,opts.length-1);opts[stockSearchFocus]?.focus()}
      else if(e.key==='Escape')closeStockDrop();
   });
   document.addEventListener('pointerdown',e=>{if(page==='Stock'&&!wrap.contains(e.target))closeStockDrop()},true);
 }
 function clearAllStockFilters(){
   search='';excelStockCategory='';stockGrade='';stockSize='';
   const input=document.querySelector('#search');if(input)input.value='';
   const cat=document.querySelector('#excel-category');if(cat)cat.value='';
   const grade=document.querySelector('#grade');if(grade)grade.value='';
   const size=document.querySelector('#size');if(size)size.value='';
   closeStockDrop();
 }
 function openFullStock(){
   clearAllStockFilters();
   stockDetailsOpen=true;
   stockTable();
   setTimeout(()=>document.querySelector('#stock-table')?.scrollIntoView({behavior:'smooth',block:'start'}),80);
 }
 function compactStock(){
   if(typeof page==='undefined'||page!=='Stock')return;
   const host=document.querySelector('#stock-table');if(!host)return;
   host.classList.toggle('kai-stock-collapsed',!stockDetailsOpen);
   let bar=document.querySelector('#kai-stock-compact-bar');
   const products=(state?.products||[]).filter(p=>{
      const q=String(search||'').trim().toLowerCase();
      return (!q||stockText(p).includes(q))&&(!excelStockCategory||String(p.category||'Other Sportswear')===excelStockCategory)&&(!stockGrade||p.grade===stockGrade)&&(!stockSize||p.size===stockSize);
   });
   const units=products.reduce((a,p)=>a+totalUnitsOf(p),0);
   const low=products.filter(p=>{const q=totalUnitsOf(p),m=Number(p.minStock||5);return q>0&&q<=m}).length;
   const out=products.filter(p=>totalUnitsOf(p)===0).length;
   if(!bar){bar=document.createElement('div');bar.id='kai-stock-compact-bar';bar.className='kai-stock-compact-bar';host.parentNode.insertBefore(bar,host)}
   bar.innerHTML=`<div class="kai-stock-compact-metrics"><span><b>${units}</b>units</span><span><b>${products.length}</b>variants</span><span><b>${low}</b>restock</span><span><b>${out}</b>out</span></div><div class="kai-stock-actions"><button type="button" id="kai-view-all-stock" class="kai-stock-toggle primary">View all stock</button><button type="button" id="kai-stock-detail-toggle" class="kai-stock-toggle">${stockDetailsOpen?'Collapse stock list':'Show stock details'}</button></div>`;
   bar.querySelector('#kai-view-all-stock').onclick=openFullStock;
   bar.querySelector('#kai-stock-detail-toggle').onclick=()=>{stockDetailsOpen=!stockDetailsOpen;compactStock()};
 }
 function compactCategories(){
   if(typeof page==='undefined'||page!=='Stock')return;
   const box=document.querySelector('#kai-category-summary');if(!box)return;
   box.classList.toggle('kai-category-collapsed',!categoryOpen);
   let btn=box.querySelector('#kai-category-toggle');
   const head=box.querySelector('.kai-category-summary-head');if(!head)return;
   if(!btn){btn=document.createElement('button');btn.type='button';btn.id='kai-category-toggle';btn.className='kai-stock-toggle';head.appendChild(btn)}
   btn.textContent=categoryOpen?'Hide category breakdown':'Show category breakdown';
   btn.onclick=()=>{categoryOpen=!categoryOpen;compactCategories()};
 }
 function enhanceCleanStock(){
   if(typeof page==='undefined'||page!=='Stock')return;
   installSearchDropdown();compactStock();setTimeout(compactCategories,0);
 }
 if(typeof stockTable==='function'){
   const baseStockTable=stockTable;
   stockTable=function(...args){const out=baseStockTable.apply(this,args);setTimeout(enhanceCleanStock,0);return out}
 }
 if(typeof render==='function'){
   const baseRender=render;
   render=function(...args){const out=baseRender.apply(this,args);setTimeout(enhanceCleanStock,0);return out}
 }
 setTimeout(enhanceCleanStock,0);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0: raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear clean stock page enabled: anchored search dropdown, View all stock, and collapsible displays.')
