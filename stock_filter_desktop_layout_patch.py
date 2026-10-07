from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

css=r'''
<style id="kai-stock-filter-desktop-layout-fix">
@media(min-width:761px){
  body .filters{display:flex!important;align-items:stretch!important;gap:10px!important;flex-wrap:wrap!important;overflow:visible!important}
  body .filters>#kai-stock-s16-search-wrap{flex:1 1 360px!important;min-width:280px!important;width:auto!important;margin:0!important}
  body .filters>.kai-stock-filter-select{flex:0 1 180px!important;min-width:165px!important;max-width:220px!important;margin:0!important}
  body .filters>#kai-stock-s16-search-wrap #search{width:100%!important;min-width:0!important;box-sizing:border-box!important;margin:0!important}
  body .filters>.kai-stock-filter-select .kai-stock-filter-button{width:100%!important;box-sizing:border-box!important;margin:0!important}
}
</style>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear desktop Stock filter row spacing fixed: search and filters no longer overlap.')
