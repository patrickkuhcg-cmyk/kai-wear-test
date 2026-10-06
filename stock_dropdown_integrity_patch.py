from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

js=r'''
<script id="kai-stock-dropdown-integrity">
(()=>{
  const isStock=()=>typeof page!=='undefined'&&page==='Stock';

  function addCustomCategories(){
    if(!isStock())return;
    const select=document.getElementById('excel-category');
    if(!select||typeof state==='undefined')return;
    const existing=new Set([...select.options].map(o=>String(o.value||'')));
    const extras=[...new Set((state?.products||[])
      .map(p=>String(p?.category||'').trim())
      .filter(v=>v&&!existing.has(v)))].sort((a,b)=>a.localeCompare(b));
    const current=select.value;
    for(const value of extras){
      const o=document.createElement('option');
      o.value=value;o.textContent=value+' (custom)';select.appendChild(o);
    }
    if(current)select.value=current;
  }

  // The v16 Stock picker displays variant metadata, but its original click
  // handler searches by product name after selection. If two variants share a
  // name (for example different sizes), refine the final filter to the exact
  // product code shown in the selected row. The original handler still owns
  // expansion and dropdown closing, so no existing Stock behavior is replaced.
  document.addEventListener('click',e=>{
    if(!isStock())return;
    const row=e.target.closest?.('.kai-stock-s16-option');
    if(!row)return;
    const meta=(row.querySelector('small')?.textContent||'').trim();
    const id=meta.split(' · ')[0]?.trim();
    if(!id||typeof state==='undefined')return;
    const product=(state?.products||[]).find(p=>String(p?.id||'')===id);
    if(!product)return;
    setTimeout(()=>{
      if(!isStock())return;
      try{
        if(typeof search!=='undefined')search=String(product.id);
        if(typeof stockTable==='function')stockTable();
      }catch(_){ }
    },0);
  });

  document.addEventListener('kai:rendered',()=>setTimeout(addCustomCategories,0));
  document.addEventListener('change',e=>{
    if(isStock()&&e.target?.id==='excel-category')setTimeout(addCustomCategories,0);
  },true);
  setTimeout(addCustomCategories,0);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear Stock dropdown integrity enabled: exact variant selection and custom category filtering preserved.')
