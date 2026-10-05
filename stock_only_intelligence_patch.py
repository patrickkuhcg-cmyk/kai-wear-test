from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

css=r'''
<style id="kai-stock-only-intel-style">
#kai-stock-only-intel{margin:10px 0 12px;border:1px solid #dce9ed;border-radius:12px;background:#fff;overflow:hidden}
#kai-stock-only-intel .kai-stock-intel-head{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 12px;background:#f8fcfd}
#kai-stock-only-intel .kai-stock-intel-head h3{margin:0;font-size:14px;color:#173f4a}
#kai-stock-only-intel .kai-stock-intel-head small{display:block;margin-top:2px;color:var(--muted);font-size:10px}
#kai-stock-only-intel .kai-stock-intel-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;padding:10px}
#kai-stock-only-intel .kai-stock-intel-card{border:1px solid #e5eef0;border-radius:9px;padding:9px;background:#fff}
#kai-stock-only-intel .kai-stock-intel-card b{display:block;font-size:18px;color:#173f4a}
#kai-stock-only-intel .kai-stock-intel-card span{font-size:10px;color:var(--muted)}
#kai-stock-only-intel .kai-stock-intel-more{display:none;padding:0 10px 10px;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
#kai-stock-only-intel.open .kai-stock-intel-more{display:grid}
#kai-stock-only-intel .kai-stock-intel-list{border:1px solid #e5eef0;border-radius:9px;padding:9px}
#kai-stock-only-intel .kai-stock-intel-list h4{margin:0 0 6px;font-size:11px;color:#315763}
#kai-stock-only-intel .kai-stock-intel-row{display:flex;justify-content:space-between;gap:8px;padding:4px 0;border-bottom:1px solid #eef3f4;font-size:11px}
#kai-stock-only-intel .kai-stock-intel-row:last-child{border-bottom:0}
@media(max-width:720px){#kai-stock-only-intel .kai-stock-intel-grid{grid-template-columns:repeat(2,minmax(0,1fr))}#kai-stock-only-intel .kai-stock-intel-more{grid-template-columns:1fr}}
</style>
'''

js=r'''
<script id="kai-stock-only-intel-script">
(()=>{
 let open=false;
 function units(p){return Object.values(p?.alloc||{}).reduce((a,v)=>a+Number(v||0),0)}
 function minLevel(p){const x=Number(p?.minStock);return Number.isFinite(x)&&x>=0?x:5}
 function status(p){const q=units(p),m=minLevel(p);return q===0?'OUT':q<=m?'RESTOCK':'OK'}
 function tally(field){
   const m=new Map();
   (state?.products||[]).forEach(p=>{const k=String(p?.[field]||'').trim();if(k)m.set(k,(m.get(k)||0)+units(p))});
   return [...m.entries()].sort((a,b)=>b[1]-a[1]);
 }
 function rows(items){return items.slice(0,8).map(([k,v])=>`<div class="kai-stock-intel-row"><span>${esc(k)}</span><strong>${v} units</strong></div>`).join('')||'<div class="tiny">No stock data yet.</div>'}
 function removeElsewhere(){
   if(typeof page==='undefined'||page==='Stock')return;
   document.getElementById('kai-stock-only-intel')?.remove();
   document.getElementById('kai-inventory-intelligence')?.remove();
   document.getElementById('excel-dashboard-stock')?.remove();
 }
 function renderStockIntel(){
   if(typeof page==='undefined'||page!=='Stock'||typeof state==='undefined'||!state){removeElsewhere();return}
   document.getElementById('kai-inventory-intelligence')?.remove();
   document.getElementById('excel-dashboard-stock')?.remove();
   const host=document.querySelector('#kai-stock-compact-bar')||document.querySelector('#stock-table');if(!host)return;
   let box=document.getElementById('kai-stock-only-intel');
   if(!box){box=document.createElement('section');box.id='kai-stock-only-intel';host.parentNode.insertBefore(box,host.nextSibling)}
   const ps=state.products||[];
   const total=ps.reduce((a,p)=>a+units(p),0),low=ps.filter(p=>status(p)==='RESTOCK').length,out=ps.filter(p=>status(p)==='OUT').length,active=ps.filter(p=>units(p)>0).length;
   box.classList.toggle('open',open);
   box.innerHTML=`<div class="kai-stock-intel-head"><div><h3>Stock intelligence</h3><small>Inventory summary is kept here in Stock only.</small></div><button type="button" id="kai-stock-intel-toggle" class="kai-stock-toggle">${open?'Hide breakdown':'Show breakdown'}</button></div><div class="kai-stock-intel-grid"><div class="kai-stock-intel-card"><b>${total}</b><span>Total units</span></div><div class="kai-stock-intel-card"><b>${active}</b><span>Active variants</span></div><div class="kai-stock-intel-card"><b>${low}</b><span>Need restocking</span></div><div class="kai-stock-intel-card"><b>${out}</b><span>Out of stock</span></div></div><div class="kai-stock-intel-more"><div class="kai-stock-intel-list"><h4>Units by size</h4>${rows(tally('size'))}</div><div class="kai-stock-intel-list"><h4>Units by version / grade</h4>${rows(tally('grade'))}</div></div>`;
   box.querySelector('#kai-stock-intel-toggle').onclick=()=>{open=!open;renderStockIntel()};
 }
 function enhance(){try{if(page==='Stock')renderStockIntel();else removeElsewhere()}catch(_){}}
 if(typeof stockTable==='function'){
   const base=stockTable;
   stockTable=function(...args){const out=base.apply(this,args);setTimeout(enhance,0);return out}
 }
 if(typeof render==='function'){
   const base=render;
   render=function(...args){const out=base.apply(this,args);setTimeout(enhance,0);return out}
 }
 const obs=new MutationObserver(()=>{if(typeof page!=='undefined'&&page!=='Stock')removeElsewhere()});
 obs.observe(document.documentElement,{childList:true,subtree:true});
 setTimeout(enhance,0);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear stock intelligence restored on Stock page only.')
