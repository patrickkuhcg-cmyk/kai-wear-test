from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

js=r'''
<script id="kai-page-stability-v13">
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
  function snapshot(name=pageName()){
    const snap={y:window.scrollY,focus:null,scrolls:[]};
    const a=document.activeElement;
    if(a&&a!==document.body){
      if(a.id)snap.focus='#'+CSS.escape(a.id);
      else if(a.name)snap.focus='[name="'+CSS.escape(a.name)+'"]';
    }
    document.querySelectorAll('.table-wrap,.table-scroll,.scrollable,.sale-search-dropdown,#kai-stock-search-dropdown,dialog,[data-kai-scroll]').forEach(el=>{
      if(!el.scrollTop&&!el.scrollLeft)return;
      const key=keyFor(el);if(key)snap.scrolls.push([key,el.scrollTop,el.scrollLeft]);
    });
    pageMemory.set(name,snap);
    return snap;
  }
  function restore(name=pageName(),fallback=null){
    const snap=pageMemory.get(name)||fallback;if(!snap)return;
    requestAnimationFrame(()=>{
      window.scrollTo(0,snap.y||0);
      for(const [key,top,left] of snap.scrolls||[]){const el=document.querySelector(key);if(el){el.scrollTop=top;el.scrollLeft=left}}
      if(snap.focus){const el=document.querySelector(snap.focus);if(el&&document.activeElement!==el)try{el.focus({preventScroll:true})}catch(_){}}
    });
  }

  render=function(...args){
    const current=pageName();
    if(current!==renderedPage){
      if(renderedPage)snapshot(renderedPage);
      const out=coreRender(...args);
      renderedPage=current;
      const remembered=pageMemory.get(current);
      if(remembered)restore(current,remembered);else requestAnimationFrame(()=>window.scrollTo(0,0));
      return out;
    }

    // Background sync is data-only on stable workspace pages. It may refresh
    // in-memory state, but it must never reconstruct the active DOM.
    if(inBackgroundSync&&stableWorkspace()&&Date.now()>manualSyncUntil)return;

    const snap=snapshot(current);
    const out=coreRender(...args);
    restore(current,snap);
    return out;
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

  // Explicit Sync is the only sync-driven redraw allowed on Stock and
  // Accounts & Access. Automatic polling stays silent there.
  document.addEventListener('click',e=>{
    const el=e.target.closest?.('button,a');if(!el)return;
    const t=(el.textContent||'').trim().toLowerCase();
    if(t==='sync'||t.includes('sync now'))manualSyncUntil=Date.now()+3000;
  },true);

  let rememberTimer=null;
  const remember=()=>{if(rememberTimer)clearTimeout(rememberTimer);rememberTimer=setTimeout(()=>snapshot(pageName()),80)};
  window.addEventListener('scroll',remember,{passive:true});
  document.addEventListener('scroll',remember,{capture:true,passive:true});
  document.addEventListener('input',remember,true);
  document.addEventListener('change',remember,true);

  const markV13=()=>{const b=document.getElementById('kai-build-marker');if(b)b.textContent='Excel Inventory Model v13 · Stable Workspace Architecture · 05 Oct 2026'};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',markV13,{once:true});else markV13();
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear v13 stable workspace architecture enabled: no deferred sync redraws on Stock or Accounts & Access.')
