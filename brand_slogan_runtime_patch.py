from pathlib import Path
import base64

root=Path(__file__).parent
static=root/'static'
index=static/'index.html'

# Preserve the user's original Kai artwork exactly. Only the bottom slogan line
# is changed to "WEAR YOUR PASSION". The same embedded asset is used everywhere
# so mobile and desktop cannot diverge because of browser image caching.
b64=(root/'kai-wear-logo-original-kai.b64').read_text().strip()
png=base64.b64decode(b64)
logo_path=static/'kai-wear-logo.png'
logo_path.write_bytes(png)
data_uri='data:image/png;base64,'+b64

html=index.read_text()
style=r'''
<style id="kai-shared-logo-style">
.kai-shared-logo{display:block;max-width:100%;height:auto;object-fit:contain}
#kai-login-logo{width:min(360px,82%);margin:0 auto 14px}
#kai-sidebar-logo{width:176px;margin:0 auto 10px}
.kai-receipt-logo{display:block;width:220px;max-width:85%;height:auto;margin:0 auto 10px}
@media(max-width:700px){#kai-login-logo{width:min(300px,88%)}#kai-sidebar-logo{width:156px}}
@media print{.kai-receipt-logo{width:190px}}
</style>
'''
script=f'''
<script id="kai-shared-logo-runtime">
(()=>{{
  const DATA={data_uri!r};
  const OLD=/wear\\s*it\\.?\\s*live\\s*it\\.?\\s*love\\s*it\\.?/gi;
  function setLogo(img,id){{
    if(!img)return null;
    img.src=DATA;
    img.removeAttribute('srcset');
    img.removeAttribute('sizes');
    img.id=id;
    img.alt='Kai Wear — Wear Your Passion';
    img.classList.add('kai-shared-logo');
    return img;
  }}
  function ensureLogin(){{
    const form=document.querySelector('#login-form');if(!form)return;
    const host=form.closest('.panel,.card,.login-card,.auth-card,.login-panel')||form.parentElement;if(!host)return;
    let img=host.querySelector('#kai-login-logo')||[...host.querySelectorAll('img')].find(x=>/kai|logo/i.test((x.alt||'')+' '+(x.src||'')+' '+(x.className||'')));
    if(img)setLogo(img,'kai-login-logo');
    else{{img=document.createElement('img');setLogo(img,'kai-login-logo');host.insertBefore(img,host.firstChild)}}
    [...host.querySelectorAll('img')].forEach(other=>{{if(other!==img&&/kai|logo/i.test((other.alt||'')+' '+(other.src||'')+' '+(other.className||'')))other.remove()}});
  }}
  function ensureSidebar(){{
    const area=document.querySelector('aside,.sidebar,#sidebar,.side-nav,nav');if(!area)return;
    let img=area.querySelector('#kai-sidebar-logo')||[...area.querySelectorAll('img')].find(x=>/kai|logo/i.test((x.alt||'')+' '+(x.src||'')+' '+(x.className||'')));
    if(img)setLogo(img,'kai-sidebar-logo');
    else{{img=document.createElement('img');setLogo(img,'kai-sidebar-logo');area.insertBefore(img,area.firstChild)}}
  }}
  function replaceOldText(){{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){{if(OLD.test(n.nodeValue||''))n.nodeValue=(n.nodeValue||'').replace(OLD,'Wear Your Passion');OLD.lastIndex=0}}}}
  function applyBrand(){{ensureLogin();ensureSidebar();replaceOldText()}}
  if(typeof receiptHTML==='function'&&!receiptHTML.__kaiSharedLogo){{const base=receiptHTML;const wrapped=function(...args){{let out=String(base.apply(this,args)).replace(OLD,'Wear Your Passion');OLD.lastIndex=0;const tag=`<img class="kai-receipt-logo" alt="Kai Wear — Wear Your Passion" src="${{DATA}}">`;if(/<img\\b[^>]*>/i.test(out))out=out.replace(/<img\\b[^>]*>/i,tag);else out=tag+out;return out}};wrapped.__kaiSharedLogo=true;receiptHTML=wrapped}}
  document.addEventListener('kai:rendered',applyBrand);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',applyBrand,{{once:true}});else applyBrand();
  setTimeout(applyBrand,200);setTimeout(applyBrand,800);setTimeout(applyBrand,1600);
}})();
</script>
'''
pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+style+'\n'+script+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear login, sidebar and receipts now use one identical embedded logo asset on mobile and desktop.')
