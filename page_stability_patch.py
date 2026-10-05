from pathlib import Path
import runpy

root=Path(__file__).parent
index=root/'static'/'index.html'

# Final Stock correction is applied immediately before the stability controller,
# giving it final authority over Expand and legacy Stock summary cleanup.
stock_fix=root/'stock_expand_fix_v16_2_patch.py'
if stock_fix.exists():
    runpy.run_path(str(stock_fix),run_name='__kai_stock_expand_fix_v16_2__')

html=index.read_text()

css=r'''
<style id="kai-v16-2-legacy-stock-cleanup">
#excel-dashboard-stock,#kai-inventory-intelligence{display:none!important}
/* Remove ONLY the two obsolete blocks immediately below Stock search.
   Do not hide the v16.2 toolbar/intelligence or the working Expand control. */
#kai-stock-compact-bar,#kai-category-summary{display:none!important}
</style>
'''

js=r'''
<script id="kai-render-architecture-v16-2">
(()=>{
  if(typeof render!=='function'||typeof sync!=='function')return;

  const composedRender=render;
  const baseSync=globalThis.__kaiBaseSync||sync;
  let inManagedSync=false;
  let syncRunning=false;
  let syncQueued=false;
  let manualSyncUntil=0;

  const pageName=()=>String(typeof page==='undefined'?'':page);
  const removeLegacyStockSummary=()=>{
    document.getElementById('excel-dashboard-stock')?.remove();
    document.getElementById('kai-inventory-intelligence')?.remove();
    if(pageName()==='Stock'){
      document.querySelectorAll('.excel-stock-summary').forEach(el=>el.remove());
      document.getElementById('kai-stock-compact-bar')?.remove();
      document.getElementById('kai-category-summary')?.remove();
    }
  };
  const emitRendered=()=>{
    removeLegacyStockSummary();
    try{document.dispatchEvent(new CustomEvent('kai:rendered',{detail:{page:pageName()}}))}catch(_){ }
  };

  render=function(...args){
    if(inManagedSync&&Date.now()>manualSyncUntil)return;
    const out=composedRender.apply(this,args);
    emitRendered();
    return out;
  };

  sync=async function(...args){
    if(syncRunning){syncQueued=true;return;}
    syncRunning=true;
    const manual=Date.now()<=manualSyncUntil;
    inManagedSync=!manual;
    try{return await baseSync.apply(this,args)}
    finally{
      inManagedSync=false;
      syncRunning=false;
      if(syncQueued){syncQueued=false;setTimeout(()=>sync().catch(()=>{}),180)}
    }
  };

  document.addEventListener('click',e=>{
    const el=e.target.closest?.('button,a');if(!el)return;
    const t=(el.textContent||'').trim().toLowerCase();
    if(t==='sync'||t.includes('sync now'))manualSyncUntil=Date.now()+3000;
  },true);

  const markBuild=()=>{
    removeLegacyStockSummary();
    const b=document.getElementById('kai-build-marker');
    if(b)b.textContent='Excel Inventory Model v16.2.2 · Exact Stock Duplicate Cleanup · 05 Oct 2026';
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',markBuild,{once:true});else markBuild();
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear v16.2.2 enabled: exact obsolete Stock compact bar and category summary removed; working v16.2 controls remain intact.')
