from pathlib import Path

root = Path(__file__).parent
index = root / 'static' / 'index.html'
html = index.read_text()

css = r'''
<style id="kai-business-model-style">
.kai-intel{margin-top:16px;border:1px solid var(--line);border-radius:14px;background:#fff;padding:16px;box-shadow:0 4px 14px rgba(16,42,56,.05)}
.kai-intel-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:12px}
.kai-intel-head h3{margin:0;font-size:18px;color:#173f4a}.kai-intel-head small{color:var(--muted)}
.kai-intel-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.kai-intel-card{border:1px solid #dfeaec;border-radius:10px;padding:11px;background:#f9fcfd}
.kai-intel-card b{display:block;font-size:21px;color:#173f4a}.kai-intel-card span{font-size:11px;color:var(--muted)}
.kai-intel-lists{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:12px}
.kai-intel-list{border:1px solid #e4ecee;border-radius:10px;padding:11px}.kai-intel-list h4{margin:0 0 8px;font-size:13px;color:#254d58}
.kai-intel-row{display:flex;justify-content:space-between;gap:10px;padding:5px 0;border-bottom:1px solid #eef3f4;font-size:12px}.kai-intel-row:last-child{border-bottom:0}.kai-intel-row strong{white-space:nowrap}
.kai-low{color:#9c5c00}.kai-out{color:#a12b2b}
@media(max-width:850px){.kai-intel-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.kai-intel-lists{grid-template-columns:1fr}}
</style>
'''

js = r'''
<script id="kai-business-model-script">
(()=>{
  function units(p){return Object.values(p?.alloc||{}).reduce((a,v)=>a+Number(v||0),0)}
  function tally(values){
    const m=new Map();
    values.filter(Boolean).forEach(v=>m.set(v,(m.get(v)||0)+1));
    return [...m.entries()].sort((a,b)=>b[1]-a[1]);
  }
  function unitTally(field){
    const m=new Map();
    (state?.products||[]).forEach(p=>{
      const key=String(p?.[field]||'').trim();if(!key)return;
      m.set(key,(m.get(key)||0)+units(p));
    });
    return [...m.entries()].sort((a,b)=>b[1]-a[1]);
  }
  function topSales(){
    const m=new Map();
    (state?.sales||[]).forEach(s=>(s.items||[]).forEach(i=>m.set(i.id,(m.get(i.id)||0)+Number(i.qty||0))));
    return [...m.entries()].sort((a,b)=>b[1]-a[1]).slice(0,5).map(([id,q])=>{
      const p=(state.products||[]).find(x=>x.id===id);
      return [p?.club||id,q];
    });
  }
  function rows(items,suffix=''){
    return items.slice(0,5).map(([k,v])=>`<div class="kai-intel-row"><span>${esc(k)}</span><strong>${v}${suffix}</strong></div>`).join('')||'<div class="tiny">No data yet.</div>';
  }
  function dashboardHost(){
    return document.querySelector('#dashboard')||document.querySelector('.dashboard')||document.querySelector('main')||document.querySelector('#main')||document.querySelector('.content');
  }
  function enhanceDashboard(){
    if(typeof page==='undefined'||page!=='Dashboard'||typeof state==='undefined'||!state)return;
    const host=dashboardHost();if(!host)return;
    let box=document.getElementById('kai-inventory-intelligence');
    if(!box){box=document.createElement('section');box.id='kai-inventory-intelligence';box.className='kai-intel';host.appendChild(box)}
    const products=state.products||[];
    const total=products.reduce((a,p)=>a+units(p),0);
    const low=products.filter(p=>units(p)>0&&units(p)<=3).length;
    const out=products.filter(p=>units(p)===0).length;
    const active=products.filter(p=>units(p)>0).length;
    const sizes=unitTally('size');
    const grades=unitTally('grade');
    const sellers=topSales();
    const estimate=products.reduce((a,p)=>a+(units(p)*Number(p.cost||0)),0);
    box.innerHTML=`
      <div class="kai-intel-head"><div><h3>Inventory intelligence</h3><small>Live view of product variants. Buying cost stays internal for accounting; selling price remains transaction-based.</small></div></div>
      <div class="kai-intel-grid">
        <div class="kai-intel-card"><b>${total}</b><span>Total units in stock</span></div>
        <div class="kai-intel-card"><b>${active}</b><span>Active product variants</span></div>
        <div class="kai-intel-card"><b class="kai-low">${low}</b><span>Low-stock variants (1–3 units)</span></div>
        <div class="kai-intel-card"><b class="kai-out">${out}</b><span>Out-of-stock variants</span></div>
      </div>
      <div class="kai-intel-lists">
        <div class="kai-intel-list"><h4>Stock by size</h4>${rows(sizes,' units')}</div>
        <div class="kai-intel-list"><h4>Stock by grade / type</h4>${rows(grades,' units')}</div>
        <div class="kai-intel-list"><h4>Top-selling products</h4>${rows(sellers,' sold')}</div>
      </div>
      ${typeof owner==='function'&&owner()?`<div class="stock-help" style="margin-top:10px">Estimated inventory cost at current weighted-average buying cost: <b>${money(estimate)}</b>. This is an accounting estimate, not a fixed product price.</div>`:''}
    `;
  }
  function updateLanguage(){
    const s=document.getElementById('search');
    if(s&&typeof page!=='undefined'&&page==='New sale')s.placeholder='Search product: team, code, size, colour, grade, style…';
  }
  function enhance(){try{enhanceDashboard();updateLanguage()}catch(_){}}

  if(typeof render==='function'){
    const coreRender=render;
    render=function(...args){const result=coreRender.apply(this,args);setTimeout(enhance,0);return result};
  }
  setTimeout(enhance,0);
})();
</script>
'''

body_end = html.rfind('</body>')
if body_end < 0:
    raise RuntimeError('Final body tag not found')
html = html[:body_end] + css + '\n' + js + '\n' + html[body_end:]
index.write_text(html)
print('Kai Wear protected inventory intelligence layer enabled.')
