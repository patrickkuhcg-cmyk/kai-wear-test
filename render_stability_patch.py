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
  let lastWindowY=window.scrollY;

  function activeControl(){
    const el=document.activeElement;
    if(!el||el===document.body)return false;
    return !!el.closest('input,textarea,select,[role="combobox"],[contenteditable="true"],dialog');
  }
  function snapshotScroll(){
    const snap={windowY:window.scrollY,els:[]};
    document.querySelectorAll('*').forEach((el,i)=>{
      if(el.scrollHeight>el.clientHeight+4||el.scrollWidth>el.clientWidth+4){
        if(el.scrollTop||el.scrollLeft) snap.els.push([el,i,el.scrollTop,el.scrollLeft]);
      }
    });
    return snap;
  }
  function restoreScroll(snap){
    requestAnimationFrame(()=>{
      window.scrollTo(0,snap.windowY);
      for(const [oldEl,,top,left] of snap.els){
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
    idleTimer=setTimeout(flushRender,ms+120);
  }

  render=function(...args){
    if(pointerActive||touchActive||activeControl()||Date.now()<interactionUntil){
      renderPending=true;
      return;
    }
    const snap=snapshotScroll();
    const out=coreRender(...args);
    restoreScroll(snap);
    return out;
  };

  window.addEventListener('scroll',()=>{lastWindowY=window.scrollY;markInteraction(3500)},{passive:true,capture:true});
  document.addEventListener('wheel',()=>markInteraction(3500),{passive:true,capture:true});
  document.addEventListener('touchstart',()=>{touchActive=true;markInteraction(4500)},{passive:true,capture:true});
  document.addEventListener('touchmove',()=>markInteraction(4500),{passive:true,capture:true});
  document.addEventListener('touchend',()=>{touchActive=false;markInteraction(1800)},{passive:true,capture:true});
  document.addEventListener('pointerdown',()=>{pointerActive=true;markInteraction(3000)},true);
  document.addEventListener('pointerup',()=>{pointerActive=false;markInteraction(1200)},true);
  document.addEventListener('input',()=>markInteraction(3000),true);
  document.addEventListener('keydown',()=>markInteraction(2500),true);
  document.addEventListener('focusin',()=>markInteraction(2200),true);
  document.addEventListener('focusout',()=>setTimeout(flushRender,500),true);
  document.addEventListener('change',()=>setTimeout(flushRender,700),true);

  // Fallback: if a render is pending but interaction events stop firing,
  // flush once the user has been idle long enough.
  setInterval(flushRender,1500);
})();
</script>
'''

body_end = html.rfind('</body>')
if body_end < 0:
    raise RuntimeError('Final body tag not found')
html = html[:body_end] + js + '\n' + html[body_end:]
index.write_text(html)
print('Kai Wear render stability guard enabled: page re-rendering deferred during scrolling and active controls.')
