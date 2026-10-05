from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

js=r'''
<script id="kai-stock-scope-cleanup-script">
(()=>{
  function keepStockControlsScoped(){
    try{
      if(typeof page==='undefined'||page!=='Stock'){
        document.getElementById('kai-inventory-intelligence')?.remove();
        document.getElementById('excel-dashboard-stock')?.remove();
      }
    }catch(_){ }
  }

  if(typeof render==='function'){
    const baseRender=render;
    render=function(...args){
      const out=baseRender.apply(this,args);
      setTimeout(keepStockControlsScoped,0);
      return out;
    };
  }

  const observer=new MutationObserver(()=>keepStockControlsScoped());
  observer.observe(document.documentElement,{childList:true,subtree:true});
  setTimeout(keepStockControlsScoped,0);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear inventory intelligence and unit controls scoped to Stock page only.')
