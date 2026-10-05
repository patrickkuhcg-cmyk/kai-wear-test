from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

css=r'''
<style id="kai-stock-stable-controls-style">
#kai-stock-stable-search-wrap{position:relative;flex:1 1 320px;min-width:240px}
#kai-stock-stable-dropdown{position:absolute;left:0;right:0;top:calc(100% + 5px);z-index:1800;background:#fff;border:1px solid #d7e6ea;border-radius:10px;box-shadow:0 10px 28px rgba(19,57,68,.16);max-height:300px;overflow-y:auto;overscroll-behavior:contain;scrollbar-gutter:stable;display:none}
#kai-stock-stable-dropdown.open{display:block}
.kai-stock-stable-option{display:block;width:100%;padding:9px 11px;text-align:left;border:0;border-bottom:1px solid #edf3f5;background:#fff;color:inherit;cursor:pointer}
.kai-stock-stable-option:hover,.kai-stock-stable-option:focus{background:#f5fbfc;outline:none}
.kai-stock-stable-option b{display:block;font-size:12px}.kai-stock-stable-option small{display:block;color:var(--muted);font-size:10px;margin-top:2px}
#kai-stock-stable-bar{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin:10px 0 12px;padding:10px 12px;border:1px solid #dce9ed;border-radius:11px;background:#f9fcfd}
.kai-stock-stable-metrics{display:flex;gap:14px;flex-wrap:wrap}.kai-stock-stable-metrics span{font-size:11px;color:var(--muted)}.kai-stock-stable-metrics b{font-size:14px;color:#173f4a;margin-right:4px}
.kai-stock-stable-actions{display:flex;gap:7px;flex-wrap:wrap}.kai-stock-stable-btn{border:1px solid #cfe0e4;background:#fff;border-radius:8px;padding:7px 10px;font-weight:700;font-size:11px;cursor:pointer}.kai-stock-stable-btn.primary{background:#173f4a;color:#fff;border-color:#173f4a}
#kai-stock-stable-intel{margin:10px 0 12px;border:1px solid #dce9ed;border-radius:12px;background:#fff;overflow:hidden}
#kai-stock-stable-intel .head{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 12px;background:#f8fcfd}
#kai-stock-stable-intel .head h3{margin:0;font-size:14px;color:#173f4a}#kai-stock-stable-intel .head small{display:block;margin-top:2px;color:var(--muted);font-size:10px}
#kai-stock-stable-intel .grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;padding:10px}.kai-stock-stable-card{border:1px solid #e5eef0;border-radius:9px;padding:9px}.kai-stock-stable-card b{display:block;font-size:18px;color:#173f4a}.kai-stock-stable-card span{font-size:10px;color:var(--muted)}
#kai-stock-stable-category{margin:12px 0 16px;border:1px solid #dce9ed;border-radius:12px;background:#fff;overflow:hidden}#kai-stock-stable-category .head{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 12px;background:#f8fcfd}#kai-stock-stable-category .grid{display:none;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;padding:10px}#kai-stock-stable-category.open .grid{display:grid}.kai-stock-stable-cat{border:1px solid #e5eef0;border-radius:9px;padding:9px;background:#fff;text-align:left}.kai-stock-stable-cat b{display:block;font-size:17px;color:#173f4a}.kai-stock-stable-cat span{font-size:10px;color:#315763}
#stock-table.kai-stock-force-open .table-wrap,#stock-table.kai-stock-force-open>.empty,#stock-table.kai-stock-force-open .excel-stock-summary{display:block!important}
@media(max-width:720px){#kai-stock-stable-search-wrap{min-width:100%;width:100%}.kai-stock-stable-actions{width:100%}.kai-stock-stable-actions button{flex:1}.kai-stock-stable-intel .grid{grid-template-columns:repeat(2,minmax(0,1fr))}#kai-stock-stable-category .grid{grid-template-columns:1fr}}
</style>
'''

js=r'''
<script id="kai-stock-stable-controls-script">
(()=>{
 const CATS=['Original Jerseys','Fan/Net Version Jerseys','Copy Jerseys','Vintage Jerseys',"Children's Jersey Sets",'Shorts','2-Piece Play Sets','Body Armour','Baseball Jerseys','Lakers/Basketball Vests','Plain Jumpers','Other Sportswear'];
 let fullOpen=false,catOpen=false;
 const isStock=()=>typeof page!=='undefined'&&page==='Stock';
 const units=p=>Object.values(p?.alloc||{}).reduce((a,v)=>a+Number(v||0),0);
 const min=p=>Number.isFinite(Number(p?.minStock))?Number(p.minStock):5;
 const text=p=>[p?.id,p?.name,p?.category,p?.club,p?.grade,p?.kit,p?.season,p?.size,p?.color].filter(Boolean).join(' ').toLowerCase();
 const label=p=>p?.name||p?.club||p?.id||'Product';
 function ensureSearch(){
   if(!isStock())return;
   const input=document.querySelector('#search');if(!input)return;
   let wrap=input.closest('#kai-stock-stable-search-wrap');
   if(!wrap){wrap=document.createElement('div');wrap.id='kai-stock-stable-search-wrap';input.parentNode.insertBefore(wrap,input);wrap.appendChild(input)}
   let drop=wrap.querySelector('#kai-stock-stable-dropdown');if(!drop){drop=document.createElement('div');drop.id='kai-stock-stable-dropdown';wrap.appendChild(drop)}
   if(input.dataset.kaiStableStock==='1')return;
   input.dataset.kaiStableStock='1';input.autocomplete='off';
   const draw=()=>{
     const q=(input.value||'').trim().toLowerCase();
     const rows=(state?.products||[]).filter(p=>!q||text(p).includes(q)).slice(0,30);
     drop.innerHTML=rows.length?rows.map((p,i)=>`<button type="button" class="kai-stock-stable-option" data-i="${i}"><b>${esc(label(p))}</b><small>${esc([p.id,p.category,p.grade,p.kit,p.season,p.size,`${units(p)} units`].filter(Boolean).join(' · '))}</small></button>`).join(''):'<div class="empty" style="padding:10px">No matching product.</div>';
     drop.classList.add('open');
     drop.querySelectorAll('[data-i]').forEach((b,i)=>b.onclick=()=>{const p=rows[i];if(!p)return;input.value=label(p);search=input.value;drop.classList.remove('open');if(typeof stockTable==='function')stockTable()});
   };
   input.addEventListener('focus',draw);input.addEventListener('input',()=>{search=input.value;draw();if(typeof stockTable==='function')stockTable()});
   drop.addEventListener('wheel',e=>{e.stopPropagation()},{passive:true});
   drop.addEventListener('touchmove',e=>{e.stopPropagation()},{passive:true});
   drop.addEventListener('pointerdown',e=>e.stopPropagation());
   document.addEventListener('pointerdown',e=>{if(isStock()&&!wrap.contains(e.target))drop.classList.remove('open')},false);
 }
 function metrics(){
   const ps=state?.products||[];return {ps,total:ps.reduce((a,p)=>a+units(p),0),low:ps.filter(p=>units(p)>0&&units(p)<=min(p)).length,out:ps.filter(p=>units(p)===0).length,active:ps.filter(p=>units(p)>0).length};
 }
 function ensureBar(){
   if(!isStock())return;const host=document.querySelector('#stock-table');if(!host)return;let bar=document.getElementById('kai-stock-stable-bar');if(!bar){bar=document.createElement('div');bar.id='kai-stock-stable-bar';host.parentNode.insertBefore(bar,host)}
   const m=metrics();bar.innerHTML=`<div class="kai-stock-stable-metrics"><span><b>${m.total}</b>units</span><span><b>${m.ps.length}</b>variants</span><span><b>${m.low}</b>restock</span><span><b>${m.out}</b>out</span></div><div class="kai-stock-stable-actions"><button type="button" class="kai-stock-stable-btn primary" id="kai-stock-stable-expand">${fullOpen?'Full stock open':'View all stock / Expand'}</button><button type="button" class="kai-stock-stable-btn" id="kai-stock-stable-collapse">${fullOpen?'Collapse full stock':'Show stock details'}</button></div>`;
   host.classList.toggle('kai-stock-force-open',fullOpen);
   bar.querySelector('#kai-stock-stable-expand').onclick=()=>{fullOpen=true;const input=document.querySelector('#search');if(input){input.value='';search=''};for(const id of ['excel-category','grade','size']){const el=document.getElementById(id);if(el&&el.value!==''){el.value='';el.dispatchEvent(new Event('change',{bubbles:true}))}};if(typeof stockTable==='function')stockTable();ensureBar()};
   bar.querySelector('#kai-stock-stable-collapse').onclick=()=>{fullOpen=!fullOpen;host.classList.toggle('kai-stock-force-open',fullOpen);ensureBar()};
 }
 function ensureIntel(){
   if(!isStock())return;const bar=document.getElementById('kai-stock-stable-bar')||document.querySelector('#stock-table');if(!bar)return;let box=document.getElementById('kai-stock-stable-intel');if(!box){box=document.createElement('section');box.id='kai-stock-stable-intel';bar.parentNode.insertBefore(box,bar.nextSibling)}const m=metrics();box.innerHTML=`<div class="head"><div><h3>Stock intelligence</h3><small>Current inventory position</small></div></div><div class="grid"><div class="kai-stock-stable-card"><b>${m.total}</b><span>Total units</span></div><div class="kai-stock-stable-card"><b>${m.active}</b><span>Active variants</span></div><div class="kai-stock-stable-card"><b>${m.low}</b><span>Need restocking</span></div><div class="kai-stock-stable-card"><b>${m.out}</b><span>Out of stock</span></div></div>`;
 }
 function ensureCategories(){
   if(!isStock())return;const host=document.querySelector('#stock-table');if(!host)return;let box=document.getElementById('kai-stock-stable-category');if(!box){box=document.createElement('section');box.id='kai-stock-stable-category';host.parentNode.insertBefore(box,host)}const ps=state?.products||[];box.classList.toggle('open',catOpen);box.innerHTML=`<div class="head"><div><b>Category stock units</b><div class="tiny">All product categories</div></div><button type="button" class="kai-stock-stable-btn" id="kai-stock-stable-cat-toggle">${catOpen?'Hide category breakdown':'Show category breakdown'}</button></div><div class="grid">${CATS.map(c=>{const rows=ps.filter(p=>String(p.category||'Other Sportswear')===c),u=rows.reduce((a,p)=>a+units(p),0);return `<div class="kai-stock-stable-cat"><b>${u}</b><span>${esc(c)} · ${rows.length} variant${rows.length===1?'':'s'}</span></div>`}).join('')}</div>`;box.querySelector('#kai-stock-stable-cat-toggle').onclick=()=>{catOpen=!catOpen;ensureCategories()};
 }
 function enhance(){if(!isStock())return;ensureSearch();ensureBar();ensureIntel();ensureCategories()}
 document.addEventListener('kai:rendered',enhance);
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(enhance,0),{once:true});else setTimeout(enhance,0);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear stable Stock controls restored without render/sync wrappers.')
