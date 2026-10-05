from pathlib import Path
import runpy

root=Path(__file__).parent
index=root/'static'/'index.html'

# Keep the working v16.2 Stock runtime/fix intact.
stock_fix=root/'stock_expand_fix_v16_2_patch.py'
if stock_fix.exists():
    runpy.run_path(str(stock_fix),run_name='__kai_stock_expand_fix_v16_2__')

# Preserve all existing product/variant catalogue entries after the clean reset.
catalogue_patch=root/'catalogue_zero_stock_patch.py'
if catalogue_patch.exists():
    runpy.run_path(str(catalogue_patch),run_name='__kai_catalogue_zero_stock__')

# New Sale should show the complete preserved catalogue in its search dropdown.
sale_catalogue_patch=root/'sale_catalogue_dropdown_patch.py'
if sale_catalogue_patch.exists():
    runpy.run_path(str(sale_catalogue_patch),run_name='__kai_sale_catalogue_dropdown__')

html=index.read_text()
css=r'''
<style id="kai-v16-2-legacy-stock-cleanup">
#excel-dashboard-stock,#kai-inventory-intelligence{display:none!important}
#kai-stock-compact-bar,#kai-category-summary{display:none!important}
</style>
'''
js=r'''
<script id="kai-render-architecture-v16-2">
(()=>{
  if(typeof render!=='function'||typeof sync!=='function')return;
  const composedRender=render;
  const baseSync=globalThis.__kaiBaseSync||sync;
  let inManagedSync=false,syncRunning=false,syncQueued=false,manualSyncUntil=0;
  const pageName=()=>String(typeof page==='undefined'?'':page);
  const removeOnlyLegacyTopStockBlocks=()=>{
    document.getElementById('excel-dashboard-stock')?.remove();
    document.getElementById('kai-inventory-intelligence')?.remove();
    if(pageName()!=='Stock')return;
    document.querySelectorAll('.excel-stock-summary').forEach(el=>el.remove());
    document.getElementById('kai-stock-compact-bar')?.remove();
    document.getElementById('kai-category-summary')?.remove();
  };
  const emitRendered=()=>{removeOnlyLegacyTopStockBlocks();try{document.dispatchEvent(new CustomEvent('kai:rendered',{detail:{page:pageName()}}))}catch(_){}};
  render=function(...args){if(inManagedSync&&Date.now()>manualSyncUntil)return;const out=composedRender.apply(this,args);emitRendered();return out};
  sync=async function(...args){if(syncRunning){syncQueued=true;return;}syncRunning=true;const manual=Date.now()<=manualSyncUntil;inManagedSync=!manual;try{return await baseSync.apply(this,args)}finally{inManagedSync=false;syncRunning=false;if(syncQueued){syncQueued=false;setTimeout(()=>sync().catch(()=>{}),180)}}};
  document.addEventListener('click',e=>{const el=e.target.closest?.('button,a');if(!el)return;const t=(el.textContent||'').trim().toLowerCase();if(t==='sync'||t.includes('sync now'))manualSyncUntil=Date.now()+3000},true);
  const markBuild=()=>{removeOnlyLegacyTopStockBlocks();const b=document.getElementById('kai-build-marker');if(b)b.textContent='Kai Wear Management System v16.2.10 · Original Logo Preserved · 05 Oct 2026'};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',markBuild,{once:true});else markBuild();
})();
</script>
'''
pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+js+'\n'+html[pos:]
index.write_text(html)

wording_patch=root/'product_wording_patch.py'
if wording_patch.exists():runpy.run_path(str(wording_patch),run_name='__kai_product_wording__')
logo_slogan_patch=root/'logo_slogan_patch.py'
if logo_slogan_patch.exists():runpy.run_path(str(logo_slogan_patch),run_name='__kai_logo_slogan__')
brand_runtime_patch=root/'brand_slogan_runtime_patch.py'
if brand_runtime_patch.exists():runpy.run_path(str(brand_runtime_patch),run_name='__kai_brand_slogan_runtime__')

print('Kai Wear Management System v16.2.10 enabled: original Kai logo preserved exactly with Wear Your Passion; business logic unchanged.')
