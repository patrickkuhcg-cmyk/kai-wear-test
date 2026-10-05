from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

js=r'''
<script id="kai-render-architecture-v15-3">
(()=>{
  if(typeof render!=='function'||typeof sync!=='function')return;

  const composedRender=render;
  const baseSync=globalThis.__kaiBaseSync||sync;
  let inManagedSync=false;
  let syncRunning=false;
  let syncQueued=false;
  let manualSyncUntil=0;

  const pageName=()=>String(typeof page==='undefined'?'':page);
  const emitRendered=()=>{
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
    const b=document.getElementById('kai-build-marker');
    if(b)b.textContent='Excel Inventory Model v15.3 · Stock Products Controls · 05 Oct 2026';
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',markBuild,{once:true});else markBuild();
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear v15.3 stable runtime enabled with Stock products controls.')
