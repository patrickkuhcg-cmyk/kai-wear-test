from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

js=r'''
<script id="kai-page-stability-v12">
(()=>{
  if(typeof render!=='function'||typeof sync!=='function')return;
  const coreRender=render;
  const coreSync=sync;
  let renderedPage=String(typeof page==='undefined'?'':page);
  let syncRunning=false;
  let syncQueued=false;
  let syncRenderPending=false;
  let inBackgroundSync=false;
  let activeUntil=0;
  let flushTimer=null;
  const pageMemory=new Map();

  const pageName=()=>String(typeof page==='undefined'?'':page);
  const activeControl=()=>{
    const el=document.activeElement;
    return !!(el&&el!==document.body&&el.closest?.('input,textarea,select,[role="combobox"],[contenteditable="true"],dialog'));
  };
  const userBusy=()=>Date.now()<activeUntil||activeControl()||!!document.querySelector('dialog[open]');

  function keyFor(el,i){
    if(el.id)return '#'+el.id;
    const k=el.getAttribute('data-kai-scroll-key');
    if(k)return '[data-kai-scroll-key="'+CSS.escape(k)+'"]';
    return null;
  }
  function snapshot(name=pageName()){
    const snap={y:window.scrollY,focus:null,scrolls:[]};
    const a=document.activeElement;
    if(a&&a!==document.body){
      if(a.id)snap.focus='#'+a.id;
      else if(a.name)snap.focus='[name="'+CSS.escape(a.name)+'"]';
    }
    document.querySelectorAll('.table-wrap,.table-scroll,.scrollable,.sale-search-dropdown,#kai-stock-search-dropdown,dialog,[data-kai-scroll]').forEach((el,i)=>{
      if(!el.scrollTop&&!el.scrollLeft)return;
      const key=keyFor(el,i);
      if(key)snap.scrolls.push([key,el.scrollTop,el.scrollLeft]);
    });
    pageMemory.set(name,snap);
    return snap;
  }
  function restore(name=pageName(),fallback=null){
    const snap=pageMemory.get(name)||fallback;
    if(!snap)return;
    requestAnimationFrame(()=>{
      window.scrollTo(0,snap.y||0);
      for(const [key,top,left] of snap.scrolls||[]){
        const el=document.querySelector(key);if(el){el.scrollTop=top;el.scrollLeft=left;}
      }
      if(snap.focus){
        const el=document.querySelector(snap.focus);
        if(el&&document.activeElement!==el)try{el.focus({preventScroll:true})}catch(_){ }
      }
    });
  }
  function scheduleFlush(delay=900){
    if(flushTimer)clearTimeout(flushTimer);
    flushTimer=setTimeout(flushPending,delay);
  }
  function markBusy(ms){activeUntil=Math.max(activeUntil,Date.now()+ms);if(syncRenderPending)scheduleFlush(ms+120)}
  function flushPending(){
    if(!syncRenderPending||inBackgroundSync||syncRunning)return;
    if(userBusy()){scheduleFlush(700);return;}
    syncRenderPending=false;
    const name=pageName();
    const snap=snapshot(name);
    coreRender();
    renderedPage=name;
    restore(name,snap);
  }

  render=function(...args){
    const current=pageName();
    // A real feature/page change is always immediate.
    if(current!==renderedPage){
      if(renderedPage)snapshot(renderedPage);
      const out=coreRender(...args);
      renderedPage=current;
      const remembered=pageMemory.get(current);
      if(remembered)restore(current,remembered);else requestAnimationFrame(()=>window.scrollTo(0,0));
      return out;
    }
    // Background sync may update state, but never rebuild the active page directly.
    if(inBackgroundSync){syncRenderPending=true;return;}
    const snap=snapshot(current);
    const out=coreRender(...args);
    restore(current,snap);
    return out;
  };

  sync=async function(...args){
    if(syncRunning){syncQueued=true;return;}
    syncRunning=true;
    inBackgroundSync=true;
    try{
      return await coreSync(...args);
    }finally{
      inBackgroundSync=false;
      syncRunning=false;
      if(syncRenderPending)scheduleFlush(userBusy()?900:350);
      if(syncQueued){syncQueued=false;setTimeout(()=>sync().catch(()=>{}),180);}
    }
  };

  // Stock and Accounts & Access are control-heavy. Keep their scroll and focus
  // stable for longer while the user is interacting with them.
  document.addEventListener('wheel',()=>markBusy(1100),{capture:true,passive:true});
  document.addEventListener('scroll',()=>markBusy(900),{capture:true,passive:true});
  document.addEventListener('touchstart',()=>markBusy(1400),{capture:true,passive:true});
  document.addEventListener('touchmove',()=>markBusy(1400),{capture:true,passive:true});
  document.addEventListener('touchend',()=>markBusy(650),{capture:true,passive:true});
  document.addEventListener('input',()=>markBusy(1600),true);
  document.addEventListener('keydown',()=>markBusy(1200),true);
  document.addEventListener('focusin',()=>markBusy(1400),true);
  document.addEventListener('change',()=>{markBusy(700);scheduleFlush(850)},true);
  document.addEventListener('focusout',()=>scheduleFlush(450),true);
  document.addEventListener('pointerdown',e=>{
    if(e.target.closest?.('input,textarea,select,[role="combobox"],.table-wrap,.filters,dialog,#kai-stock-search-dropdown'))markBusy(900);
  },true);
  window.addEventListener('focus',()=>{syncQueued=true;if(!syncRunning)setTimeout(()=>sync().catch(()=>{}),250)});
  document.addEventListener('visibilitychange',()=>{if(!document.hidden){syncQueued=true;if(!syncRunning)setTimeout(()=>sync().catch(()=>{}),250)}});
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear v12 consolidated page stability enabled for Stock, Accounts & Access, and all pages.')
