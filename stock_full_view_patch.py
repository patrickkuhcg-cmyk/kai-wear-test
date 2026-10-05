from pathlib import Path
import runpy

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

css=r'''
<style id="kai-stock-full-view-style">
#kai-stock-full-view-control{display:flex;justify-content:flex-end;gap:8px;align-items:center;margin:8px 0 10px}
#kai-stock-full-view-control button{border:1px solid #173f4a;border-radius:9px;padding:8px 12px;font-weight:750;font-size:11px;cursor:pointer;background:#173f4a;color:#fff}
#kai-stock-full-view-control button.secondary{background:#fff;color:#173f4a;border-color:#cfe0e4}
#stock-table.kai-force-full-stock .table-wrap,#stock-table.kai-force-full-stock>.empty,#stock-table.kai-force-full-stock .excel-stock-summary{display:block!important}
@media(max-width:700px){#kai-stock-full-view-control{justify-content:stretch}#kai-stock-full-view-control button{flex:1}}
</style>
'''

js=r'''
<script id="kai-stock-full-view-script">
(()=>{
 let fullOpen=false;
 function resetVisibleFilters(){
   const input=document.querySelector('#search');
   if(input){input.value='';input.dispatchEvent(new Event('input',{bubbles:true}))}
   for(const id of ['excel-category','grade','size']){
     const el=document.getElementById(id);
     if(el&&el.value!==''){el.value='';el.dispatchEvent(new Event('change',{bubbles:true}))}
   }
 }
 function applyFullView(){
   if(typeof page==='undefined'||page!=='Stock')return;
   const host=document.querySelector('#stock-table');if(!host)return;
   let controls=document.getElementById('kai-stock-full-view-control');
   if(!controls){
     controls=document.createElement('div');controls.id='kai-stock-full-view-control';
     host.parentNode.insertBefore(controls,host);
   }
   host.classList.toggle('kai-force-full-stock',fullOpen);
   controls.innerHTML=`<button type="button" id="kai-force-view-all">${fullOpen?'Full stock list open':'View all stock / Expand'}</button>${fullOpen?'<button type="button" class="secondary" id="kai-force-collapse">Collapse full stock</button>':''}`;
   controls.querySelector('#kai-force-view-all').onclick=()=>{
     fullOpen=true;resetVisibleFilters();
     setTimeout(()=>{const h=document.querySelector('#stock-table');h?.classList.add('kai-force-full-stock');applyFullView();h?.scrollIntoView({behavior:'smooth',block:'start'})},80);
   };
   controls.querySelector('#kai-force-collapse')?.addEventListener('click',()=>{fullOpen=false;host.classList.remove('kai-force-full-stock');applyFullView()});
 }
 if(typeof render==='function'){
   const base=render;
   render=function(...args){const out=base.apply(this,args);setTimeout(applyFullView,0);return out};
 }
 if(typeof stockTable==='function'){
   const baseStock=stockTable;
   stockTable=function(...args){const out=baseStock.apply(this,args);setTimeout(applyFullView,0);return out};
 }
 setTimeout(applyFullView,0);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+js+'\n'+html[pos:]
index.write_text(html)

# Consolidated page stability is applied last so it governs all earlier UI wrappers.
stability=root/'page_stability_patch.py'
if stability.exists():
    runpy.run_path(str(stability),run_name='__kai_page_stability_patch__')

print('Kai Wear always-visible View all stock / Expand control enabled with consolidated page stability.')
