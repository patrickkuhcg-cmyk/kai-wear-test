from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

js=r'''
<script id="kai-interaction-sync-guard">
(()=>{
  if(typeof sync!=='function')return;
  const baseSync=sync;
  let busyUntil=0;
  let queued=false;
  let timer=null;
  let running=false;
  const isFormControl=el=>!!(el&&el.matches&&el.matches('input,textarea,select,[role="combobox"],[contenteditable="true"]'));
  const dialogOpen=()=>!!document.querySelector('dialog[open]');
  const interacting=()=>Date.now()<busyUntil||isFormControl(document.activeElement)||dialogOpen();
  function mark(ms=1400){
    busyUntil=Math.max(busyUntil,Date.now()+ms);
    if(timer)clearTimeout(timer);
    timer=setTimeout(flush,ms+80);
  }
  async function flush(){
    if(!queued||running||interacting())return;
    queued=false;running=true;
    const y=window.scrollY;
    const active=document.activeElement;
    const id=active&&active.id;
    try{await baseSync()}catch(_){}finally{
      requestAnimationFrame(()=>{
        window.scrollTo(0,y);
        if(id){const el=document.getElementById(id);if(el&&document.activeElement!==el)try{el.focus({preventScroll:true})}catch(_){}}
      });
      running=false;
      if(queued)setTimeout(flush,120);
    }
  }
  sync=async function(...args){
    if(interacting()){
      queued=true;
      mark(900);
      return;
    }
    if(running){queued=true;return;}
    running=true;
    const y=window.scrollY;
    try{return await baseSync(...args)}finally{
      requestAnimationFrame(()=>window.scrollTo(0,y));
      running=false;
      if(queued)setTimeout(flush,120);
    }
  };

  document.addEventListener('input',()=>mark(1800),true);
  document.addEventListener('keydown',()=>mark(1200),true);
  document.addEventListener('focusin',e=>{if(isFormControl(e.target))mark(2200)},true);
  document.addEventListener('pointerdown',e=>{if(isFormControl(e.target)||e.target.closest?.('.filters,.table-wrap,.sale-search-dropdown,dialog'))mark(1500)},true);
  document.addEventListener('wheel',()=>mark(900),{capture:true,passive:true});
  document.addEventListener('touchstart',()=>mark(1400),{capture:true,passive:true});
  document.addEventListener('touchmove',()=>mark(900),{capture:true,passive:true});
  document.addEventListener('scroll',()=>mark(650),{capture:true,passive:true});
  document.addEventListener('change',()=>{mark(700);setTimeout(flush,760)},true);
  document.addEventListener('focusout',()=>setTimeout(flush,300),true);
  window.addEventListener('online',()=>{queued=true;setTimeout(flush,250)});
  window.addEventListener('focus',()=>{queued=true;setTimeout(flush,300)});
  document.addEventListener('visibilitychange',()=>{if(!document.hidden){queued=true;setTimeout(flush,300)}});
})();
</script>
'''

end=html.rfind('</body>')
if end<0: raise RuntimeError('Final body tag not found')
html=html[:end]+js+'\n'+html[end:]
index.write_text(html)
print('Kai Wear interaction-aware sync guard enabled.')
