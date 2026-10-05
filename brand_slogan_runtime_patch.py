from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

style=r'''
<style id="kai-brand-slogan-runtime-style">
.kai-brand-slogan{font:700 12px/1.25 system-ui,-apple-system,Segoe UI,sans-serif;letter-spacing:.04em;color:#0f5b6a;text-align:center;margin:6px 0 10px}
#kai-login-slogan{font-size:14px;margin:8px 0 16px}
.kai-receipt-brand-slogan{font:700 11px/1.3 system-ui,-apple-system,Segoe UI,sans-serif;text-align:center;letter-spacing:.04em;margin:2px 0 10px;color:#111}
@media print{.kai-receipt-brand-slogan{display:block!important;color:#000!important}}
</style>
'''

script=r'''
<script id="kai-brand-slogan-runtime-script">
(()=>{
  const SLOGAN='Wear Your Passion';
  const OLD=/wear\s*it\.?\s*live\s*it\.?\s*love\s*it\.?/gi;

  function replaceText(root=document){
    try{
      const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
      const nodes=[];let n;
      while((n=walker.nextNode()))nodes.push(n);
      nodes.forEach(node=>{if(OLD.test(node.nodeValue||''))node.nodeValue=(node.nodeValue||'').replace(OLD,SLOGAN);OLD.lastIndex=0});
    }catch(_){ }
  }

  function addAfter(target,id,cls){
    if(!target||document.getElementById(id))return;
    const el=document.createElement('div');el.id=id;el.className='kai-brand-slogan '+(cls||'');el.textContent=SLOGAN;
    target.insertAdjacentElement('afterend',el);
  }

  function ensureLogin(){
    const form=document.querySelector('#login-form');if(!form)return;
    const host=form.closest('.panel,.card,.login-card,.auth-card,.login-panel')||form.parentElement;
    if(!host)return;
    if(host.querySelector('#kai-login-slogan'))return;
    const logo=[...host.querySelectorAll('img,svg')].find(el=>/kai|logo/i.test((el.getAttribute('alt')||'')+' '+(el.getAttribute('src')||'')+' '+(el.id||'')+' '+(el.className?.baseVal||el.className||'')));
    if(logo){addAfter(logo,'kai-login-slogan','')}
    else{
      const heading=host.querySelector('h1,h2,.brand,.logo');
      if(heading)addAfter(heading,'kai-login-slogan','');
      else{const el=document.createElement('div');el.id='kai-login-slogan';el.className='kai-brand-slogan';el.textContent=SLOGAN;host.insertBefore(el,form)}
    }
  }

  function ensureSidebar(){
    const areas=[...document.querySelectorAll('aside,.sidebar,#sidebar,.side-nav,nav')];
    for(const area of areas){
      if(area.querySelector('#kai-sidebar-slogan'))return;
      const logo=[...area.querySelectorAll('img,svg')].find(el=>/kai|logo/i.test((el.getAttribute('alt')||'')+' '+(el.getAttribute('src')||'')+' '+(el.id||'')+' '+(el.className?.baseVal||el.className||'')));
      if(logo){addAfter(logo,'kai-sidebar-slogan','');return;}
    }
  }

  function ensureRuntimeBranding(){replaceText(document);ensureLogin();ensureSidebar();}

  if(typeof receiptHTML==='function'&&!receiptHTML.__kaiSloganWrapped){
    const baseReceiptHTML=receiptHTML;
    const wrapped=function(...args){
      let out=String(baseReceiptHTML.apply(this,args));
      out=out.replace(OLD,SLOGAN);OLD.lastIndex=0;
      if(!/Wear Your Passion/i.test(out)){
        const slogan='<div class="kai-receipt-brand-slogan">Wear Your Passion</div>';
        const brand=/(<(?:h1|h2|div)[^>]*>[^<]*Kai\s*Wear[^<]*<\/(?:h1|h2|div)>)/i;
        out=brand.test(out)?out.replace(brand,'$1'+slogan):slogan+out;
      }
      return out;
    };
    wrapped.__kaiSloganWrapped=true;
    receiptHTML=wrapped;
  }

  document.addEventListener('kai:rendered',ensureRuntimeBranding);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ensureRuntimeBranding,{once:true});else ensureRuntimeBranding();
  setTimeout(ensureRuntimeBranding,250);
  setTimeout(ensureRuntimeBranding,1200);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+style+'\n'+script+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear explicit Wear Your Passion branding enabled for login, sidebar and receipts.')
