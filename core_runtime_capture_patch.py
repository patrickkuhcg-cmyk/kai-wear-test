from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

js=r'''
<script id="kai-core-runtime-capture">
(()=>{
  // Capture the untouched application runtime before feature patches wrap it.
  // The final architecture layer will use these references to avoid legacy
  // sync wrappers that restore scroll positions or defer page updates.
  if(typeof sync==='function'&&!globalThis.__kaiBaseSync)globalThis.__kaiBaseSync=sync;
  if(typeof render==='function'&&!globalThis.__kaiBaseRender)globalThis.__kaiBaseRender=render;
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear base runtime captured before feature wrappers.')
