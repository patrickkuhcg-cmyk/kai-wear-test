from pathlib import Path

root = Path(__file__).parent
index = root / 'static' / 'index.html'
html = index.read_text()

css = r'''
<style id="kai-sale-picker-style">
.sale-search-wrap{position:relative;width:100%;z-index:40}
.sale-search-wrap #search{width:100%;margin:0}
.sale-search-dropdown{position:absolute;left:0;right:0;top:calc(100% + 5px);z-index:120;background:#fff;border:1px solid var(--line);border-radius:10px;box-shadow:0 12px 30px rgba(16,42,56,.16);max-height:300px;overflow-y:auto;overscroll-behavior:contain;padding:6px;display:none}
.sale-search-dropdown.open{display:block}
.sale-search-item{width:100%;border:0;border-bottom:1px solid #edf2f4;background:#fff;color:inherit;text-align:left;padding:10px 11px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;border-radius:7px;cursor:pointer}
.sale-search-item:last-child{border-bottom:0}
.sale-search-item:hover,.sale-search-item.active{background:#eefafd;outline:1px solid rgba(0,189,221,.28)}
.sale-search-main{font-weight:700;line-height:1.25}
.sale-search-meta{font-size:11px;color:var(--muted);margin-top:3px;white-space:normal}
.sale-search-stock{font-size:11px;font-weight:700;white-space:nowrap;padding:4px 7px;border-radius:999px;background:#eef7f8;color:#315763}
.sale-search-empty{padding:12px;color:var(--muted);font-size:12px}
#catalog.sale-catalog-anchor{margin:0;padding:0;border:0;background:transparent}
@media(max-width:700px){.sale-search-dropdown{max-height:250px}.sale-search-item{grid-template-columns:1fr}.sale-search-stock{justify-self:start}}
</style>
'''

js = r'''
<script id="kai-sale-picker-script">
(()=>{
  let pickerOpen=false;
  let pickerIndex=-1;
  let pickerScroll=0;
  let pendingSync=false;
  let pickerPointer=false;
  const coreSync=typeof sync==='function'?sync:null;
  const coreAdd=typeof addSaleProduct==='function'?addSaleProduct:null;

  function availableProducts(){
    return (state?.products||[]).filter(p=>((p.alloc?.[device]||0)-(cart.find(l=>l.id===p.id)?.qty||0))>0);
  }
  function searchable(p){
    return `${p.id||''} ${p.club||''} ${p.season||''} ${p.kit||''} ${p.color||''} ${p.size||''} ${p.grade||''}`.toLowerCase();
  }
  function ensurePicker(){
    const input=document.getElementById('search');
    const catalog=document.getElementById('catalog');
    if(!input||!catalog)return null;
    let wrap=input.closest('.sale-search-wrap');
    if(!wrap){
      wrap=document.createElement('div');
      wrap.className='sale-search-wrap';
      input.parentNode.insertBefore(wrap,input);
      wrap.appendChild(input);
      wrap.appendChild(catalog);
    }else if(catalog.parentNode!==wrap){wrap.appendChild(catalog)}
    catalog.classList.add('sale-catalog-anchor','sale-search-dropdown');
    return {input,catalog,wrap};
  }
  function closePicker(runSync=true){
    const ui=ensurePicker();
    pickerOpen=false;pickerIndex=-1;
    if(ui)ui.catalog.classList.remove('open');
    if(runSync&&pendingSync&&coreSync){pendingSync=false;setTimeout(()=>coreSync().catch(()=>{}),0)}
  }
  function chooseProduct(p){
    if(!p||!coreAdd)return;
    closePicker(false);
    coreAdd(p);
    const ui=ensurePicker();
    if(ui){ui.input.value='';search='';ui.catalog.classList.remove('open')}
    if(pendingSync&&coreSync){pendingSync=false;setTimeout(()=>coreSync().catch(()=>{}),0)}
  }
  function drawPicker(){
    const ui=ensurePicker();if(!ui)return;
    const q=(ui.input.value||'').trim().toLowerCase();
    search=ui.input.value||'';
    const all=availableProducts();
    const results=(q?all.filter(p=>searchable(p).includes(q)):all).slice(0,10);
    const prevScroll=ui.catalog.scrollTop||pickerScroll;
    ui.catalog.innerHTML=results.length?results.map((p,i)=>{
      const left=(p.alloc?.[device]||0)-(cart.find(l=>l.id===p.id)?.qty||0);
      return `<button type="button" class="sale-search-item${i===pickerIndex?' active':''}" data-kai-sale-id="${esc(p.id)}"><span><div class="sale-search-main">${esc(p.club||p.id)}</div><div class="sale-search-meta">${esc([p.id,p.size,p.grade,p.color,p.kit,p.season].filter(Boolean).join(' · '))}</div></span><span class="sale-search-stock">${left} in stock</span></button>`;
    }).join(''):'<div class="sale-search-empty">No matching jersey in stock at this counter.</div>';
    ui.catalog.classList.toggle('open',pickerOpen);
    requestAnimationFrame(()=>{ui.catalog.scrollTop=prevScroll;pickerScroll=prevScroll});
    ui.catalog.onmousedown=()=>{pickerPointer=true};
    ui.catalog.onmouseup=()=>{pickerPointer=false};
    ui.catalog.onscroll=()=>{pickerScroll=ui.catalog.scrollTop};
    ui.catalog.querySelectorAll('[data-kai-sale-id]').forEach(btn=>{
      btn.onmousedown=e=>e.preventDefault();
      btn.onclick=()=>chooseProduct(all.find(p=>p.id===btn.dataset.kaiSaleId));
    });
  }

  // Replace the old sale catalogue renderer with an anchored autocomplete.
  catalog=function(){
    const ui=ensurePicker();if(!ui)return;
    if(document.activeElement===ui.input)pickerOpen=true;
    drawPicker();
    ui.input.onfocus=()=>{pickerOpen=true;pickerIndex=-1;drawPicker()};
    ui.input.oninput=e=>{search=e.target.value;pickerOpen=true;pickerIndex=-1;drawPicker()};
    ui.input.onkeydown=e=>{
      const items=[...ui.catalog.querySelectorAll('[data-kai-sale-id]')];
      if(e.key==='ArrowDown'&&items.length){e.preventDefault();pickerOpen=true;pickerIndex=Math.min(pickerIndex+1,items.length-1);drawPicker();const active=ui.catalog.querySelector('.active');active?.scrollIntoView({block:'nearest'})}
      else if(e.key==='ArrowUp'&&items.length){e.preventDefault();pickerIndex=Math.max(pickerIndex-1,0);drawPicker();const active=ui.catalog.querySelector('.active');active?.scrollIntoView({block:'nearest'})}
      else if(e.key==='Enter'&&items.length){e.preventDefault();const idx=pickerIndex>=0?pickerIndex:0;const btn=items[idx];chooseProduct(availableProducts().find(p=>p.id===btn?.dataset.kaiSaleId))}
      else if(e.key==='Escape'){e.preventDefault();closePicker()}
    };
    ui.input.onblur=()=>setTimeout(()=>{if(!pickerPointer)closePicker()},120);
  };

  // Keep live updates from resetting the user's scroll or dropdown while selecting a jersey.
  if(coreSync){
    sync=async function(...args){
      const ui=ensurePicker();
      const interacting=pickerOpen&&(document.activeElement===ui?.input||pickerPointer||ui?.catalog.matches(':hover'));
      if(interacting){pendingSync=true;return}
      const pageY=window.scrollY;
      const dropY=ui?.catalog.scrollTop||0;
      const result=await coreSync(...args);
      requestAnimationFrame(()=>{
        window.scrollTo({top:pageY,left:0,behavior:'instant'});
        const next=ensurePicker();if(next)next.catalog.scrollTop=dropY;
      });
      return result;
    };
  }

  document.addEventListener('click',e=>{
    const wrap=document.querySelector('.sale-search-wrap');
    if(wrap&&!wrap.contains(e.target))closePicker();
  });
  window.addEventListener('scroll',()=>{const ui=ensurePicker();if(ui&&pickerOpen)ui.catalog.scrollTop=pickerScroll},{passive:true});

  // Rebuild the picker once the current New Sale view is present.
  setTimeout(()=>{try{catalog()}catch(_){ }},0);
})();
</script>
'''

# Insert at the true final body boundary so template strings elsewhere cannot be corrupted.
body_end = html.rfind('</body>')
if body_end < 0:
    raise RuntimeError('Final body tag not found')
html = html[:body_end] + css + '\n' + js + '\n' + html[body_end:]
index.write_text(html)
print('Kai Wear sales picker UI stabilized.')
