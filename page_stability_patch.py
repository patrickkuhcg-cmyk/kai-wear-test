from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

js=r'''
<script id="kai-page-stability-v13-1">
(()=>{
  if(typeof render!=='function'||typeof sync!=='function')return;
  const coreRender=render;
  const coreSync=sync;
  let renderedPage=String(typeof page==='undefined'?'':page);
  let inBackgroundSync=false;
  let syncRunning=false;
  let syncQueued=false;
  let manualSyncUntil=0;
  const pageMemory=new Map();

  const pageName=()=>String(typeof page==='undefined'?'':page);
  const stableWorkspace=()=>{
    const p=pageName().trim().toLowerCase();
    return p==='stock'||p.includes('account')||p.includes('access');
  };

  function keyFor(el){
    if(el.id)return '#'+CSS.escape(el.id);
    const k=el.getAttribute?.('data-kai-scroll-key');
    return k?'[data-kai-scroll-key="'+CSS.escape(k)+'"]':null;
  }

  // Page position is remembered only when leaving a feature. We deliberately
  // do not continuously capture/restore while the user is scrolling.
  function snapshotPage(name=pageName()){
    const snap={y:window.scrollY,scrolls:[]};
    document.querySelectorAll('.table-wrap,.table-scroll,.scrollable,#kai-stock-search-dropdown,[data-kai-scroll]').forEach(el=>{
      if(!el.scrollTop&&!el.scrollLeft)return;
      const key=keyFor(el);if(key)snap.scrolls.push([key,el.scrollTop,el.scrollLeft]);
    });
    pageMemory.set(name,snap);
    return snap;
  }

  function restorePage(name){
    const snap=pageMemory.get(name);if(!snap)return false;
    requestAnimationFrame(()=>{
      // Navigation is the only place where Kai Wear is allowed to move the
      // window programmatically. Ordinary same-page use remains native.
      window.scrollTo({left:0,top:snap.y||0,behavior:'auto'});
      for(const [key,top,left] of snap.scrolls||[]){
        const el=document.querySelector(key);if(el){el.scrollTop=top;el.scrollLeft=left}
      }
    });
    return true;
  }

  render=function(...args){
    const current=pageName();

    // Feature navigation: remember the feature being left and restore the
    // destination once. This is intentionally separate from same-page renders.
    if(current!==renderedPage){
      if(renderedPage)snapshotPage(renderedPage);
      const out=coreRender(...args);
      renderedPage=current;
      if(!restorePage(current))requestAnimationFrame(()=>window.scrollTo({left:0,top:0,behavior:'auto'}));
      return out;
    }

    // Automatic sync is data-only on control-heavy workspace pages.
    if(inBackgroundSync&&stableWorkspace()&&Date.now()>manualSyncUntil)return;

    // Critical v13.1 rule: ordinary same-page renders NEVER call scrollTo and
    // never restore an old scroll snapshot. The browser owns scrolling fully.
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

  // Explicit Sync may refresh the current workspace once. Automatic polling
  // remains data-only on Stock and Accounts & Access.
  document.addEventListener('click',e=>{
    const el=e.target.closest?.('button,a');if(!el)return;
    const t=(el.textContent||'').trim().toLowerCase();
    if(t==='sync'||t.includes('sync now'))manualSyncUntil=Date.now()+3000;
  },true);

  const markBuild=()=>{
    const b=document.getElementById('kai-build-marker');
    if(b)b.textContent='Excel Inventory Model v13.1 · Native Scroll Stability · 05 Oct 2026';
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',markBuild,{once:true});else markBuild();
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear v13.1 native scroll stability enabled: no same-page scroll restoration or deferred movement.')
