from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

css=r'''
<style id="kai-stock-controls-v15-3-style">
#kai-stock-v153-controls{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin:10px 0 12px;padding:10px 12px;border:1px solid #dce9ed;border-radius:11px;background:#f9fcfd}
#kai-stock-v153-metrics{display:flex;gap:14px;flex-wrap:wrap}#kai-stock-v153-metrics span{font-size:11px;color:var(--muted)}#kai-stock-v153-metrics b{font-size:14px;color:#173f4a;margin-right:4px}
#kai-stock-v153-actions{display:flex;gap:8px;flex-wrap:wrap}.kai-stock-v153-btn{border:1px solid #cfe0e4;background:#fff;color:#173f4a;border-radius:8px;padding:7px 10px;font-weight:750;font-size:11px;cursor:pointer}.kai-stock-v153-btn.primary{background:#173f4a;color:#fff;border-color:#173f4a}
#kai-stock-v153-intel{margin:0 0 12px;border:1px solid #dce9ed;border-radius:11px;background:#fff;overflow:hidden}#kai-stock-v153-intel-head{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 12px;background:#f8fcfd}#kai-stock-v153-intel-head h3{margin:0;font-size:14px;color:#173f4a}#kai-stock-v153-intel-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;padding:10px}#kai-stock-v153-intel-grid div{border:1px solid #e5eef0;border-radius:9px;padding:9px}#kai-stock-v153-intel-grid b{display:block;font-size:18px;color:#173f4a}#kai-stock-v153-intel-grid span{font-size:10px;color:var(--muted)}
#kai-stock-v153-search-wrap{position:relative;flex:1 1 280px;min-width:230px}#kai-stock-v153-dropdown{position:absolute;left:0;right:0;top:calc(100% + 5px);z-index:4000;background:#fff;border:1px solid #d7e6ea;border-radius:10px;box-shadow:0 10px 28px rgba(19,57,68,.16);max-height:300px;overflow-y:auto;overscroll-behavior:contain;display:none}#kai-stock-v153-dropdown.open{display:block}.kai-stock-v153-option{display:block;width:100%;border:0;border-bottom:1px solid #edf3f5;background:#fff;text-align:left;padding:9px 11px;cursor:pointer}.kai-stock-v153-option:hover{background:#f5fbfc}.kai-stock-v153-option b{display:block;font-size:12px}.kai-stock-v153-option small{display:block;font-size:10px;color:var(--muted);margin-top:2px}
#stock-table.kai-v153-collapsed .table-wrap,#stock-table.kai-v153-collapsed>.empty,#stock-table.kai-v153-collapsed .excel-stock-summary{display:none!important}
@media(max-width:700px){#kai-stock-v153-actions{width:100%}.kai-stock-v153-btn{flex:1 1 auto}#kai-stock-v153-intel-grid{grid-template-columns:repeat(2,minmax(0,1fr))}#kai-stock-v153-search-wrap{min-width:100%}}
</style>
'''

js=r'''
<script id="kai-stock-controls-v15-3-script">
(()=>{
 let expanded=false;
 const units=p=>Object.values(p?.alloc||{}).reduce((a,v)=>a+Number(v||0),0);
 const min=p=>Number.isFinite(Number(p?.minStock))?Number(p.minStock):5;
 const text=p=>[p.id,p.name,p.category,p.club,p.grade,p.kit,p.season,p.size,p.color].filter(Boolean).join(' ').toLowerCase();
 function isStock(){return typeof page!=='undefined'&&page==='Stock'}
 function rename(){if(!isStock())return;document.querySelectorAll('h1,h2').forEach(h=>{if(['Jersey stock','Products & stock','Stock'].includes(h.textContent.trim()))h.textContent='Stock products'})}
 function filtered(){const q=String(typeof search==='undefined'?'':search||'').trim().toLowerCase();return (state?.products||[]).filter(p=>!q||text(p).includes(q))}
 function renderDropdown(){if(!isStock())return;const input=document.querySelector('#search'),d=document.querySelector('#kai-stock-v153-dropdown');if(!input||!d)return;const q=input.value.trim().toLowerCase();const rows=(state?.products||[]).filter(p=>!q||text(p).includes(q)).slice(0,30);d.innerHTML=rows.length?rows.map((p,i)=>`<button type="button" class="kai-stock-v153-option" data-i="${i}"><b>${esc(p.name||p.club||p.id)}</b><small>${esc([p.id,p.category,p.grade,p.size,`${units(p)} units`].filter(Boolean).join(' · '))}</small></button>`).join(''):'<div class="empty" style="padding:10px">No matching product.</div>';d.classList.add('open');d.querySelectorAll('[data-i]').forEach((b,i)=>b.onclick=()=>{const p=rows[i];if(!p)return;input.value=p.name||p.club||p.id;search=input.value;d.classList.remove('open');stockTable?.()})}
 function mountSearch(){const input=document.querySelector('#search');if(!isStock()||!input||input.dataset.kaiV153==='1')return;input.dataset.kaiV153='1';let wrap=input.parentElement;if(!wrap||wrap.id!=='kai-stock-v153-search-wrap'){const w=document.createElement('div');w.id='kai-stock-v153-search-wrap';input.parentNode.insertBefore(w,input);w.appendChild(input);wrap=w}let d=document.querySelector('#kai-stock-v153-dropdown');if(!d){d=document.createElement('div');d.id='kai-stock-v153-dropdown';wrap.appendChild(d)}input.autocomplete='off';input.addEventListener('focus',renderDropdown);input.addEventListener('input',()=>{search=input.value;renderDropdown();stockTable?.()});d.addEventListener('wheel',e=>e.stopPropagation(),{passive:true});d.addEventListener('pointerdown',e=>e.stopPropagation());document.addEventListener('pointerdown',e=>{if(isStock()&&!wrap.contains(e.target))d.classList.remove('open')},true)}
 function mount(){if(!isStock())return;rename();mountSearch();const host=document.querySelector('#stock-table');if(!host)return;let controls=document.querySelector('#kai-stock-v153-controls');if(!controls){controls=document.createElement('div');controls.id='kai-stock-v153-controls';host.parentNode.insertBefore(controls,host)}const ps=filtered(),total=ps.reduce((a,p)=>a+units(p),0),low=ps.filter(p=>units(p)>0&&units(p)<=min(p)).length,out=ps.filter(p=>units(p)===0).length;controls.innerHTML=`<div id="kai-stock-v153-metrics"><span><b>${total}</b>units</span><span><b>${ps.length}</b>variants</span><span><b>${low}</b>restock</span><span><b>${out}</b>out</span></div><div id="kai-stock-v153-actions"><button type="button" class="kai-stock-v153-btn primary" id="kai-stock-v153-expand">${expanded?'Full stock open':'View all stock / Expand'}</button><button type="button" class="kai-stock-v153-btn" id="kai-stock-v153-collapse" ${expanded?'':'hidden'}>Collapse</button></div>`;host.classList.toggle('kai-v153-collapsed',!expanded);controls.querySelector('#kai-stock-v153-expand').onclick=()=>{expanded=true;if(typeof search!=='undefined')search='';const s=document.querySelector('#search');if(s)s.value='';host.classList.remove('kai-v153-collapsed');stockTable?.();mount()};controls.querySelector('#kai-stock-v153-collapse').onclick=()=>{expanded=false;host.classList.add('kai-v153-collapsed');mount()};let intel=document.querySelector('#kai-stock-v153-intel');if(!intel){intel=document.createElement('section');intel.id='kai-stock-v153-intel';controls.insertAdjacentElement('afterend',intel)}const all=state?.products||[],allTotal=all.reduce((a,p)=>a+units(p),0),active=all.filter(p=>units(p)>0).length,allLow=all.filter(p=>units(p)>0&&units(p)<=min(p)).length,allOut=all.filter(p=>units(p)===0).length;intel.innerHTML=`<div id="kai-stock-v153-intel-head"><h3>Stock intelligence</h3><span class="tiny">Stock products overview</span></div><div id="kai-stock-v153-intel-grid"><div><b>${allTotal}</b><span>Total units</span></div><div><b>${active}</b><span>Active variants</span></div><div><b>${allLow}</b><span>Need restocking</span></div><div><b>${allOut}</b><span>Out of stock</span></div></div>`}
 document.addEventListener('kai:rendered',mount);
 if(typeof stockTable==='function'){const base=stockTable;stockTable=function(...a){const out=base.apply(this,a);mount();return out}}
 setTimeout(mount,0);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear v15.3 Stock products controls restored without global render or sync wrappers.')
