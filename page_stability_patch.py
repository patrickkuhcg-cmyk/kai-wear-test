from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

js=r'''
<script id="kai-render-architecture-v15-2">
(()=>{
  if(typeof render!=='function'||typeof sync!=='function')return;

  // render is taken from the fully composed UI so deliberate user actions keep
  // every feature enhancement. sync comes from the untouched base runtime,
  // captured before feature patches, so legacy wrappers cannot move the page.
  const composedRender=render;
  const baseSync=globalThis.__kaiBaseSync||sync;
  let inManagedSync=false;
  let syncRunning=false;
  let syncQueued=false;
  let manualSyncUntil=0;
  let renderedPage=String(typeof page==='undefined'?'':page);

  const pageName=()=>String(typeof page==='undefined'?'':page);
  const emitRendered=()=>{
    try{document.dispatchEvent(new CustomEvent('kai:rendered',{detail:{page:pageName()}}))}catch(_){ }
  };

  render=function(...args){
    const current=pageName();

    // Automatic synchronization is state-only. It is never allowed to rebuild
    // visible markup, which means it cannot alter document height or scroll.
    if(inManagedSync&&Date.now()>manualSyncUntil)return;

    const out=composedRender.apply(this,args);
    renderedPage=current;
    // One synchronous post-render signal replaces ad-hoc delayed observers in
    // patches that opt into the new architecture.
    emitRendered();
    return out;
  };

  sync=async function(...args){
    if(syncRunning){syncQueued=true;return;}
    syncRunning=true;
    const manual=Date.now()<=manualSyncUntil;
    inManagedSync=!manual;
    try{
      return await baseSync.apply(this,args);
    }finally{
      inManagedSync=false;
      syncRunning=false;
      if(syncQueued){
        syncQueued=false;
        setTimeout(()=>sync().catch(()=>{}),180);
      }
    }
  };

  // A user-requested Sync is allowed to repaint once. All automatic polling is
  // silent and data-only across every panel.
  document.addEventListener('click',e=>{
    const el=e.target.closest?.('button,a');if(!el)return;
    const t=(el.textContent||'').trim().toLowerCase();
    if(t==='sync'||t.includes('sync now'))manualSyncUntil=Date.now()+3000;
  },true);

  // This architecture layer never calls window.scrollTo(), scrollIntoView(),
  // or restores a saved page position. Native browser scrolling is authoritative.
  const markBuild=()=>{
    const b=document.getElementById('kai-build-marker');
    if(b)b.textContent='Excel Inventory Model v15.2 · Stable Stock Controls · 05 Oct 2026';
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',markBuild,{once:true});else markBuild();
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear v15.2 single-runtime stability enabled with stable Stock controls restored.')
