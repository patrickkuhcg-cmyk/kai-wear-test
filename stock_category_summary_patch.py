from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

css=r'''
<style id="kai-category-summary-style">
.kai-category-summary{margin:12px 0 16px;border:1px solid #dce9ed;border-radius:12px;background:#fff;overflow:hidden}
.kai-category-summary-head{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:11px 13px;background:#f8fcfd;border-bottom:1px solid #e5eef0}.kai-category-summary-head h3{margin:0;font-size:14px;color:#173f4a}.kai-category-summary-head small{color:var(--muted)}
.kai-category-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;padding:10px}
.kai-category-card{border:1px solid #e5eef0;border-radius:10px;padding:10px;background:#fff;cursor:pointer;text-align:left}.kai-category-card:hover{background:#f8fcfd}.kai-category-card.active{outline:2px solid #4fbfd8;background:#f4fbfd}.kai-category-card b{display:block;font-size:18px;color:#173f4a}.kai-category-card span{display:block;font-size:11px;color:#315763;margin-top:2px}.kai-category-card small{display:block;font-size:10px;color:var(--muted);margin-top:3px}
@media(max-width:900px){.kai-category-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.kai-category-grid{grid-template-columns:1fr}}
</style>
'''

js=r'''
<script id="kai-category-summary-script">
(()=>{
 const KAI_CATEGORIES=['Original Jerseys','Fan/Net Version Jerseys','Copy Jerseys','Vintage Jerseys',"Children's Jersey Sets",'Shorts','2-Piece Play Sets','Body Armour','Baseball Jerseys','Lakers/Basketball Vests','Plain Jumpers','Other Sportswear'];
 const catOf=p=>String(p?.category||'Other Sportswear');
 const unitsOf=p=>Object.values(p?.alloc||{}).reduce((a,v)=>a+Number(v||0),0);
 function renderCategorySummary(){
   if(typeof page==='undefined'||page!=='Stock'||typeof state==='undefined')return;
   const host=document.querySelector('#stock-table');if(!host)return;
   let box=document.getElementById('kai-category-summary');
   if(!box){box=document.createElement('section');box.id='kai-category-summary';box.className='kai-category-summary';host.parentNode.insertBefore(box,host)}
   const products=state.products||[];
   const rows=KAI_CATEGORIES.map(name=>{
      const ps=products.filter(p=>catOf(p)===name),units=ps.reduce((a,p)=>a+unitsOf(p),0);
      return {name,units,variants:ps.length};
   });
   const grand=rows.reduce((a,r)=>a+r.units,0);
   box.innerHTML=`<div class="kai-category-summary-head"><div><h3>Category stock units</h3><small>All Excel categories remain visible, including categories with zero stock.</small></div><strong>${grand} total units</strong></div><div class="kai-category-grid">${rows.map(r=>`<button type="button" class="kai-category-card ${typeof excelStockCategory!=='undefined'&&excelStockCategory===r.name?'active':''}" data-cat="${esc(r.name)}"><b>${r.units}</b><span>${esc(r.name)}</span><small>${r.variants} product variant${r.variants===1?'':'s'}</small></button>`).join('')}</div>`;
   box.querySelectorAll('[data-cat]').forEach(btn=>btn.onclick=()=>{
      const cat=btn.getAttribute('data-cat')||'';
      const sel=document.querySelector('#excel-category');
      if(sel){sel.value=(sel.value===cat?'':cat);sel.dispatchEvent(new Event('change',{bubbles:true}))}
   });
 }
 if(typeof stockTable==='function'){
   const base=stockTable;
   stockTable=function(...args){const out=base.apply(this,args);setTimeout(renderCategorySummary,0);return out}
 }
 if(typeof render==='function'){
   const baseRender=render;
   render=function(...args){const out=baseRender.apply(this,args);setTimeout(renderCategorySummary,0);return out}
 }
 setTimeout(renderCategorySummary,0);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear full category stock-unit summary enabled once, without nested stock-clean injection.')
