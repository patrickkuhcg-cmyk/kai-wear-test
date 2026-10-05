from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

css=r'''
<style id="kai-stock-v162-fix-style">
#kai-s16-full-list{margin-top:10px}
#kai-s16-full-list[hidden]{display:none!important}
#kai-s16-full-list .table-wrap{display:block!important;overflow:auto;max-width:100%}
#kai-s16-full-list table{min-width:980px}
</style>
'''

js=r'''
<script id="kai-stock-v162-fix-script">
(()=>{
  const isStock=()=>typeof page!=='undefined'&&page==='Stock';
  const units=p=>Object.values(p?.alloc||{}).reduce((a,v)=>a+Number(v||0),0);
  const minLevel=p=>{const n=Number(p?.minStock);return Number.isFinite(n)&&n>=0?n:5};
  const pName=p=>String(p?.name||p?.club||p?.id||'Product');
  const pCategory=p=>String(p?.category||'Other Sportswear');
  const status=p=>{const q=units(p);return q===0?'OUT':q<=minLevel(p)?'RESTOCK':'OK'};

  function removeLegacy(){
    if(!isStock())return;
    for(const sel of ['#excel-dashboard-stock','#kai-inventory-intelligence','.excel-stock-summary']){
      document.querySelectorAll(sel).forEach(el=>el.remove());
    }
    const intel=[...document.querySelectorAll('section,.kai-intel,.card')].filter(el=>{
      if(el.closest('#stock-table'))return false;
      const h=el.querySelector('h1,h2,h3,h4');
      const t=(h?.textContent||'').trim().toLowerCase();
      return t==='stock intelligence'||t==='stock control';
    });
    intel.forEach(el=>el.remove());
  }

  function fullListHost(){
    const host=document.querySelector('#stock-table');
    if(!host)return null;
    let box=document.getElementById('kai-s16-full-list');
    if(!box){
      box=document.createElement('div');
      box.id='kai-s16-full-list';
      box.hidden=true;
      host.appendChild(box);
    }
    return box;
  }

  function renderAll(){
    if(!isStock())return;
    removeLegacy();
    const box=fullListHost();if(!box)return;
    const ps=state?.products||[];
    box.innerHTML=`<div class="table-wrap"><table><thead><tr><th>Product</th><th>Category</th><th>Club / Country</th><th>Version</th><th>Kit</th><th>Season</th><th>Size</th><th class="end">Shop 1</th><th class="end">Shop 2</th><th class="end">Total</th><th>Status</th></tr></thead><tbody>${ps.map(p=>{const st=status(p);const shop1=typeof qty==='function'?qty(p,'Shop 1'):Number(p.alloc?.['Shop 1']||0);const shop2=typeof qty==='function'?qty(p,'Shop 2'):Number(p.alloc?.['Shop 2']||0);return `<tr><td><b>${esc(pName(p))}</b><small>${esc(p.id||'')}</small></td><td>${esc(pCategory(p))}</td><td>${esc(p.club||'—')}</td><td>${esc(p.grade||'—')}</td><td>${esc(p.kit||'—')}</td><td>${esc(p.season||'—')}</td><td><span class="badge">${esc(p.size||'—')}</span></td><td class="end">${shop1}</td><td class="end">${shop2}</td><td class="end"><b>${units(p)}</b></td><td><span class="excel-stock-tag ${st==='RESTOCK'?'low':st==='OUT'?'out':''}">${st}</span><span class="excel-stock-sub">Min ${minLevel(p)}</span></td></tr>`}).join('')}</tbody></table></div>${ps.length?'':'<div class="empty">No stock products found.</div>'}`;
    box.hidden=false;
    const btn=document.getElementById('kai-s16-expand');if(btn)btn.textContent='Full stock open';
  }

  function collapse(){
    const box=document.getElementById('kai-s16-full-list');if(box)box.hidden=true;
    const btn=document.getElementById('kai-s16-expand');if(btn)btn.textContent='View all stock / Expand';
  }

  document.addEventListener('click',e=>{
    const expand=e.target.closest?.('#kai-s16-expand');
    if(expand&&isStock()){
      e.preventDefault();e.stopImmediatePropagation();
      const box=document.getElementById('kai-s16-full-list');
      if(box&&!box.hidden)collapse();else renderAll();
      return;
    }
    const collapseBtn=e.target.closest?.('#kai-s16-collapse');
    if(collapseBtn&&isStock()){
      e.preventDefault();e.stopImmediatePropagation();collapse();
    }
  },true);

  document.addEventListener('kai:rendered',()=>{removeLegacy();if(isStock()){const box=document.getElementById('kai-s16-full-list');if(box&&!box.hidden)renderAll();}});
  setTimeout(removeLegacy,0);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0: raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear v16.2 stock expand and duplicate intelligence fix enabled.')
