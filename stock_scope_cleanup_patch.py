from pathlib import Path
import runpy

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
        document.getElementById('kai-stock-only-intel')?.remove();
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

# Apply the dedicated Stock-only intelligence layer after the cleanup scope.
stock_only = root/'stock_only_intelligence_patch.py'
if stock_only.exists():
    runpy.run_path(str(stock_only), run_name='__kai_stock_only_intelligence_patch__')

print('Kai Wear inventory intelligence removed from non-Stock pages and restored on Stock only.')
