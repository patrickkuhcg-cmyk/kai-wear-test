from pathlib import Path

root = Path(__file__).parent
index = root / 'static' / 'index.html'
html = index.read_text()

js = r'''
<script id="kai-render-stability-script">
(()=>{
  if(typeof render!=='function')return;
  const coreRender=render;
  let renderPending=false;
  let interactionUntil=0;
  let idleTimer=null;
  let pointerActive=false;
  let touchActive=false;
  let forceNavigationRender=false;

  function activeControl(){
    const el=document.activeElement;
    if(!el||el===document.body)return false;
    return !!el.closest('input,textarea,select,[role="combobox"],[contenteditable="true"],dialog');
  }
  function isNavigationTarget(target){
    const el=target?.closest?.('button,a,[data-page],[data-nav]');
    if(!el)return false;
    if(el.closest('nav,aside,.sidebar,.nav,.menu'))return true;
    const t=(el.textContent||'').trim().toLowerCase();
    return /^(dashboard|new sale|sales|stock|inventory|purchases|expenses|credit|reports|admin|users|settings|suppliers|cash|receipts)$/.test(t);
  }
  function snapshotScroll(){
    const snap={windowY:window.scrollY,els:[]};
    document.querySelectorAll('.sale-search-dropdown,.table-wrap,.table-scroll,.scrollable,[data-kai-scroll],dialog').forEach(el=>{
      if(el.scrollTop||el.scrollLeft)snap.els.push([el,el.scrollTop,el.scrollLeft]);
    });
    return snap;
  }
  function restoreScroll(snap){
    requestAnimationFrame(()=>{
      window.scrollTo(0,snap.windowY);
      for(const [oldEl,top,left] of snap.els){
        if(document.contains(oldEl)){oldEl.scrollTop=top;oldEl.scrollLeft=left;}
      }
    });
  }
  function flushRender(){
    if(!renderPending)return;
    if(pointerActive||touchActive||activeControl()||Date.now()<interactionUntil)return;
    renderPending=false;
    const snap=snapshotScroll();
    coreRender();
    restoreScroll(snap);
  }
  function markInteraction(ms=3000){
    interactionUntil=Math.max(interactionUntil,Date.now()+ms);
    if(idleTimer)clearTimeout(idleTimer);
    idleTimer=setTimeout(flushRender,ms+100);
  }

  render=function(...args){
    if(forceNavigationRender){
      forceNavigationRender=false;
      renderPending=false;
      interactionUntil=0;
      const out=coreRender(...args);
      requestAnimationFrame(()=>window.scrollTo(0,0));
      return out;
    }
    if(pointerActive||touchActive||activeControl()||Date.now()<interactionUntil){
      renderPending=true;
      return;
    }
    const snap=snapshotScroll();
    const out=coreRender(...args);
    restoreScroll(snap);
    return out;
  };

  // Intentional feature/menu navigation must be immediate. Mark it in the
  // capture phase so the app's existing click handler can call render() right away.
  document.addEventListener('click',e=>{
    if(isNavigationTarget(e.target)){
      forceNavigationRender=true;
      pointerActive=false;
      touchActive=false;
      interactionUntil=0;
    }
  },true);

  window.addEventListener('scroll',()=>markInteraction(1200),{passive:true,capture:true});
  document.addEventListener('wheel',()=>markInteraction(1200),{passive:true,capture:true});
  document.addEventListener('touchstart',()=>{touchActive=true;markInteraction(1600)},{passive:true,capture:true});
  document.addEventListener('touchmove',()=>markInteraction(1600),{passive:true,capture:true});
  document.addEventListener('touchend',()=>{touchActive=false;markInteraction(500)},{passive:true,capture:true});
  document.addEventListener('pointerdown',e=>{if(!isNavigationTarget(e.target)){pointerActive=true;markInteraction(900)}},true);
  document.addEventListener('pointerup',e=>{pointerActive=false;if(!isNavigationTarget(e.target))markInteraction(350)},true);
  document.addEventListener('input',()=>markInteraction(1200),true);
  document.addEventListener('keydown',()=>markInteraction(900),true);
  document.addEventListener('focusin',()=>markInteraction(700),true);
  document.addEventListener('focusout',()=>setTimeout(flushRender,180),true);
  document.addEventListener('change',()=>setTimeout(flushRender,220),true);

  setInterval(flushRender,800);
})();
</script>
'''

body_end = html.rfind('</body>')
if body_end < 0:
    raise RuntimeError('Final body tag not found')
html = html[:body_end] + js + '\n' + html[body_end:]
index.write_text(html)
print('Kai Wear render stability enabled with instant dashboard navigation.')
