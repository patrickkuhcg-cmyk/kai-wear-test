from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

css=r'''
<style id="kai-stock-legacy-summary-cleanup-style">
#excel-dashboard-stock,#kai-inventory-intelligence{display:none!important}
</style>
'''

js=r'''
<script id="kai-stock-legacy-summary-cleanup-script">
(()=>{
  function removeLegacy(){
    document.getElementById('excel-dashboard-stock')?.remove();
    document.getElementById('kai-inventory-intelligence')?.remove();
    if(typeof page!=='undefined'&&page==='Stock'){
      document.querySelectorAll('section,div').forEach(el=>{
        const t=(el.textContent||'').trim();
        if(t.startsWith('Stock control')&&t.includes('Excel inventory model: category, variant and minimum-stock monitoring.'))el.remove();
      });
    }
  }
  document.addEventListener('kai:rendered',removeLegacy);
  setTimeout(removeLegacy,0);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear legacy Stock control summary removed; v16 Stock intelligence retained.')
