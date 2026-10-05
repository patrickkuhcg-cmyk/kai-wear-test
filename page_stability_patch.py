from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

js=r'''
<script id="kai-render-architecture-v14">
(()=>{
  if(typeof render!=='function'||typeof sync!=='function')return;
  const coreRender=render;
  const coreSync=sync;
  let renderedPage=String(typeof page==='undefined'?'':page);
  let inBackgroundSync=false;
  let syncRunning=false;
  let syncQueued=false;
  let manualSyncUntil=0;

  const pageName=()=>String(typeof page==='undefined'?'':page);

  render=function(...args){
    const current=pageName();

    // Deliberate feature navigation still renders immediately. The browser
    // determines scroll position naturally; Kai Wear never restores or forces it.
    if(current!==renderedPage){
      const out=coreRender(...args);
      renderedPage=current;
      return out;
    }

    // Core v14 rule: automatic sync is data-only everywhere in the app.
    // It can refresh state, but it is never allowed to rebuild the visible DOM.
    // This removes the root cause of page/scroll jumping across all panels.
    if(inBackgroundSync&&Date.now()>manualSyncUntil)return;

    // User-driven same-page actions render normally with no programmatic scroll.
    return coreRender(...args);
  };

  sync=async function(...args){
    if(syncRunning){syncQueued=true;return;}
    syncRunning=true;
    const manual=Date.now()<=manualSyncUntil;
    inBackgroundSync=!manual;
    try{return await coreSync(...args)}
    finally{
      inBackgroundSync=false;
      syncRunning=false;
      if(syncQueued){syncQueued=false;setTimeout(()=>sync().catch(()=>{}),180)}
    }
  };

  // Only an explicit user Sync may allow sync to redraw the current screen.
  document.addEventListener('click',e=>{
    const el=e.target.closest?.('button,a');if(!el)return;
    const t=(el.textContent||'').trim().toLowerCase();
    if(t==='sync'||t.includes('sync now'))manualSyncUntil=Date.now()+3000;
  },true);

  const markBuild=()=>{
    const b=document.getElementById('kai-build-marker');
    if(b)b.textContent='Excel Inventory Model v14 · Core Render Stability · 05 Oct 2026';
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',markBuild,{once:true});else markBuild();
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear v14 core render architecture enabled: automatic sync is data-only across the entire app; no scroll restoration or forced movement.')
