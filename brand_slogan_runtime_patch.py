from pathlib import Path
import base64

root=Path(__file__).parent
static=root/'static'
index=static/'index.html'

# Use the user's approved Kai Wear artwork as the one source of truth.
b64=(root/'kai-wear-logo-original-kai.b64').read_text().strip()
logo_bytes=base64.b64decode(b64)
logo_path=static/'kai-wear-logo.webp'
logo_path.write_bytes(logo_bytes)
data_uri='data:image/webp;base64,'+b64

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
  let queued=false;

  function setLogo(img,id){{
    if(!img)return null;
    if(img.getAttribute('src')!==DATA)img.setAttribute('src',DATA);
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
    const imgs=[...host.querySelectorAll('img')];
    let img=host.querySelector('#kai-login-logo')||imgs.find(x=>/kai|logo/i.test((x.alt||'')+' '+(x.src||'')+' '+(x.className||'')))||imgs[0];
    if(img)setLogo(img,'kai-login-logo');
    else{{img=document.createElement('img');setLogo(img,'kai-login-logo');host.insertBefore(img,host.firstChild)}}
    [...host.querySelectorAll('img')].forEach(other=>{{if(other!==img)other.remove()}});
  }}

  function ensureSidebar(){{
    const area=document.querySelector('aside,.sidebar,#sidebar,.side-nav,nav');if(!area)return;
    const imgs=[...area.querySelectorAll('img')];
    let img=area.querySelector('#kai-sidebar-logo')||imgs.find(x=>/kai|logo/i.test((x.alt||'')+' '+(x.src||'')+' '+(x.className||'')));
    if(img)setLogo(img,'kai-sidebar-logo');
    else if(imgs.length)setLogo(imgs[0],'kai-sidebar-logo');
  }}

  function ensureBrand(){{ensureLogin();ensureSidebar()}}
  function queueBrand(){{if(queued)return;queued=true;requestAnimationFrame(()=>{{queued=false;ensureBrand()}})}}

  // Old slogan text replacement is intentionally a one-time/lightweight task.
  // It is not allowed to run on every DOM mutation or navigation render.
  function replaceOldTextOnce(){{
    if(!document.body)return;
    const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
    while((n=w.nextNode())){{const t=n.nodeValue||'';if(OLD.test(t))n.nodeValue=t.replace(OLD,'Wear Your Passion');OLD.lastIndex=0}}
  }}

  if(typeof receiptHTML==='function'&&!receiptHTML.__kaiSharedLogo){{
    const base=receiptHTML;
    const wrapped=function(...args){{
      let out=String(base.apply(this,args)).replace(OLD,'Wear Your Passion');OLD.lastIndex=0;
      const tag=`<img class="kai-receipt-logo" alt="Kai Wear — Wear Your Passion" src="${{DATA}}">`;
      if(/<img\\b[^>]*>/i.test(out))out=out.replace(/<img\\b[^>]*>/i,tag);else out=tag+out;
      return out
    }};
    wrapped.__kaiSharedLogo=true;receiptHTML=wrapped
  }}

  document.addEventListener('kai:rendered',queueBrand);
  const start=()=>{{ensureBrand();replaceOldTextOnce()}};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{{once:true}});else start();

  // Lightweight observer: react only when a login/logo node is added or an
  // existing logo image has its source replaced. It does no page-wide work.
  const observer=new MutationObserver(mutations=>{{
    for(const m of mutations){{
      if(m.type==='attributes'&&m.target?.tagName==='IMG'&&(/kai|logo/i.test((m.target.id||'')+' '+(m.target.alt||'')+' '+(m.target.className||'')))){{queueBrand();return}}
      if(m.type==='childList'){{
        for(const n of m.addedNodes){{
          if(n.nodeType!==1)continue;
          if(n.matches?.('#login-form,img,#kai-login-logo,#kai-sidebar-logo')||n.querySelector?.('#login-form,#kai-login-logo,#kai-sidebar-logo')){{queueBrand();return}}
        }}
      }}
    }}
  }});
  const startObserver=()=>observer.observe(document.documentElement,{{childList:true,subtree:true,attributes:true,attributeFilter:['src']}});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',startObserver,{{once:true}});else startObserver();

  setTimeout(queueBrand,300);setTimeout(queueBrand,1200);
}})();
</script>
'''
pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+style+'\n'+script+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear branding runtime optimized: approved logo preserved without whole-page mutation work during navigation.')
