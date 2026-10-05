from pathlib import Path

root=Path(__file__).parent
static=root/'static'
index=static/'index.html'

# Rebuilt shared vector logo. This is written after assemble.py has recreated
# static/, so it survives the build and becomes the single branding asset.
svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 405" role="img" aria-label="Kai Wear Jersey and Sportswear - Wear Your Passion">
<rect width="700" height="405" rx="24" fill="#ffffff"/>
<g text-anchor="middle" font-family="Arial,Helvetica,sans-serif">
  <text x="350" y="212" font-size="168" font-weight="900" fill="#08b7d4" letter-spacing="-12">Kai</text>
  <text x="452" y="72" font-size="64" font-weight="900" fill="#08b7d4">✱</text>
  <rect x="217" y="222" width="266" height="55" rx="18" fill="#08b7d4"/>
  <text x="350" y="264" font-size="39" font-weight="900" fill="#ffffff" letter-spacing="4">WEAR</text>
  <text x="350" y="322" font-size="42" font-style="italic" font-weight="900" fill="#071d31">JERSEY &amp; SPORTSWEAR</text>
  <text x="350" y="368" font-size="29" font-weight="600" fill="#30479a" letter-spacing="6">WEAR YOUR PASSION</text>
</g>
</svg>'''
(static/'kai-wear-logo.svg').write_text(svg)

html=index.read_text()
style=r'''
<style id="kai-shared-logo-style">
.kai-shared-logo{display:block;max-width:100%;height:auto;object-fit:contain}
#kai-login-logo{width:min(360px,82%);margin:0 auto 14px}
#kai-sidebar-logo{width:176px;margin:0 auto 10px}
.kai-receipt-logo{display:block;width:220px;max-width:85%;margin:0 auto 10px}
@media(max-width:700px){#kai-login-logo{width:min(300px,88%)}#kai-sidebar-logo{width:156px}}
@media print{.kai-receipt-logo{width:190px}}
</style>
'''
script=r'''
<script id="kai-shared-logo-runtime">
(()=>{
  const LOGO='/kai-wear-logo.svg?v=16.2.9';
  const INLINE=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 405"><rect width="700" height="405" rx="24" fill="#fff"/><g text-anchor="middle" font-family="Arial,Helvetica,sans-serif"><text x="350" y="212" font-size="168" font-weight="900" fill="#08b7d4" letter-spacing="-12">Kai</text><text x="452" y="72" font-size="64" font-weight="900" fill="#08b7d4">✱</text><rect x="217" y="222" width="266" height="55" rx="18" fill="#08b7d4"/><text x="350" y="264" font-size="39" font-weight="900" fill="#fff" letter-spacing="4">WEAR</text><text x="350" y="322" font-size="42" font-style="italic" font-weight="900" fill="#071d31">JERSEY &amp; SPORTSWEAR</text><text x="350" y="368" font-size="29" font-weight="600" fill="#30479a" letter-spacing="6">WEAR YOUR PASSION</text></g></svg>`;
  const DATA='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(INLINE);
  const OLD=/wear\s*it\.?\s*live\s*it\.?\s*love\s*it\.?/gi;

  function setLogo(img,id){
    if(!img)return null;
    img.src=LOGO;img.id=id;img.alt='Kai Wear — Wear Your Passion';img.classList.add('kai-shared-logo');
    return img;
  }
  function ensureLogin(){
    const form=document.querySelector('#login-form');if(!form)return;
    const host=form.closest('.panel,.card,.login-card,.auth-card,.login-panel')||form.parentElement;
    if(!host)return;
    let img=host.querySelector('#kai-login-logo')||[...host.querySelectorAll('img')].find(x=>/kai|logo/i.test((x.alt||'')+' '+(x.src||'')+' '+(x.className||'')));
    if(img)setLogo(img,'kai-login-logo');
    else{img=document.createElement('img');setLogo(img,'kai-login-logo');host.insertBefore(img,host.firstChild)}
  }
  function ensureSidebar(){
    const area=document.querySelector('aside,.sidebar,#sidebar,.side-nav,nav');if(!area)return;
    let img=area.querySelector('#kai-sidebar-logo')||[...area.querySelectorAll('img')].find(x=>/kai|logo/i.test((x.alt||'')+' '+(x.src||'')+' '+(x.className||'')));
    if(img)setLogo(img,'kai-sidebar-logo');
    else{img=document.createElement('img');setLogo(img,'kai-sidebar-logo');area.insertBefore(img,area.firstChild)}
  }
  function replaceOldText(){
    const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
    while((n=w.nextNode())){if(OLD.test(n.nodeValue||''))n.nodeValue=(n.nodeValue||'').replace(OLD,'Wear Your Passion');OLD.lastIndex=0}
  }
  function applyBrand(){ensureLogin();ensureSidebar();replaceOldText()}

  if(typeof receiptHTML==='function'&&!receiptHTML.__kaiSharedLogo){
    const base=receiptHTML;
    const wrapped=function(...args){
      let out=String(base.apply(this,args)).replace(OLD,'Wear Your Passion');OLD.lastIndex=0;
      const tag=`<img class="kai-receipt-logo" alt="Kai Wear — Wear Your Passion" src="${DATA}">`;
      if(/<img\b[^>]*>/i.test(out))out=out.replace(/<img\b[^>]*>/i,tag);else out=tag+out;
      return out;
    };
    wrapped.__kaiSharedLogo=true;receiptHTML=wrapped;
  }

  document.addEventListener('kai:rendered',applyBrand);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',applyBrand,{once:true});else applyBrand();
  setTimeout(applyBrand,300);setTimeout(applyBrand,1200);
})();
</script>
'''
pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+style+'\n'+script+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear shared SVG logo rebuilt with Wear Your Passion and wired to login, sidebar and receipts.')
