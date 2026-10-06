from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

css=r'''
<style id="kai-stock-filter-custom-ui-style">
.kai-stock-filter-select{position:relative;flex:1 1 170px;min-width:150px;z-index:20}
.kai-stock-filter-select.open{z-index:5200}
.kai-stock-filter-native{position:absolute!important;width:1px!important;height:1px!important;opacity:0!important;pointer-events:none!important;overflow:hidden!important;clip:rect(0 0 0 0)!important;clip-path:inset(50%)!important;white-space:nowrap!important}
.kai-stock-filter-button{width:100%;min-height:43px;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:9px 12px;border:1px solid #cfdfe4;border-radius:8px;background:#fff;color:#173f4a;font:inherit;text-align:left;cursor:pointer;box-shadow:none}
.kai-stock-filter-button:hover,.kai-stock-filter-button:focus{border-color:#84b7c2;outline:none;box-shadow:0 0 0 3px rgba(0,189,221,.10)}
.kai-stock-filter-button[aria-expanded="true"]{border-color:#55a7b8;box-shadow:0 0 0 3px rgba(0,189,221,.12)}
.kai-stock-filter-label{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.kai-stock-filter-chevron{font-size:11px;line-height:1;transition:transform .14s ease;flex:0 0 auto}
.kai-stock-filter-button[aria-expanded="true"] .kai-stock-filter-chevron{transform:rotate(180deg)}
.kai-stock-filter-menu{position:absolute;left:0;right:0;top:calc(100% + 5px);display:none;max-height:250px;overflow-y:auto;overscroll-behavior:contain;scrollbar-gutter:stable;background:#fff;color:#173f4a;border:1px solid #d4e4e8;border-radius:9px;box-shadow:0 14px 32px rgba(16,42,56,.20);padding:5px;z-index:5300}
.kai-stock-filter-select.open .kai-stock-filter-menu{display:block}
.kai-stock-filter-option{width:100%;display:block;border:0;background:#fff;color:#173f4a;text-align:left;padding:9px 10px;border-radius:6px;font:inherit;font-size:12px;cursor:pointer}
.kai-stock-filter-option:hover,.kai-stock-filter-option:focus,.kai-stock-filter-option.active{background:#eef9fb;outline:none}
.kai-stock-filter-option.selected{font-weight:750;background:#f5fbfc}
.kai-stock-filter-menu::-webkit-scrollbar{width:9px}.kai-stock-filter-menu::-webkit-scrollbar-thumb{background:#b9d3d9;border-radius:999px;border:2px solid #fff}.kai-stock-filter-menu::-webkit-scrollbar-track{background:#fff}
@media(max-width:760px){.kai-stock-filter-select{flex:1 1 145px;min-width:130px}.kai-stock-filter-menu{max-height:220px}}
</style>
'''

js=r'''
<script id="kai-stock-filter-custom-ui-script">
(()=>{
  const IDS=['excel-category','grade','size'];
  const isStock=()=>typeof page!=='undefined'&&page==='Stock';
  let openWrap=null;

  function close(wrap,focus=false){
    if(!wrap)return;
    wrap.classList.remove('open');
    const btn=wrap.querySelector('.kai-stock-filter-button');
    btn?.setAttribute('aria-expanded','false');
    if(openWrap===wrap)openWrap=null;
    if(focus)btn?.focus();
  }
  function closeAll(except=null){
    document.querySelectorAll('.kai-stock-filter-select.open').forEach(w=>{if(w!==except)close(w)});
  }
  function optionData(select){return [...select.options].map((o,i)=>({value:o.value,label:o.textContent||o.value,index:i,selected:o.selected}))}
  function refresh(select,wrap){
    if(!select||!wrap)return;
    const btn=wrap.querySelector('.kai-stock-filter-button'),menu=wrap.querySelector('.kai-stock-filter-menu');
    const data=optionData(select),selected=data.find(o=>o.value===select.value)||data[0];
    const label=selected?.label||'Choose';
    const lab=btn?.querySelector('.kai-stock-filter-label');if(lab)lab.textContent=label;
    if(btn)btn.title=label;
    if(menu){
      menu.innerHTML=data.map((o,i)=>`<button type="button" class="kai-stock-filter-option${o.value===select.value?' selected':''}" role="option" aria-selected="${o.value===select.value?'true':'false'}" data-index="${i}" data-value="${esc(o.value)}">${esc(o.label)}</button>`).join('');
      menu.querySelectorAll('.kai-stock-filter-option').forEach(item=>item.onclick=e=>{
        e.preventDefault();e.stopPropagation();
        const value=item.dataset.value??'';
        if(select.value!==value){select.value=value;select.dispatchEvent(new Event('change',{bubbles:true}))}
        refresh(select,wrap);close(wrap,true);
      });
    }
  }
  function open(select,wrap){
    closeAll(wrap);refresh(select,wrap);wrap.classList.add('open');openWrap=wrap;
    const btn=wrap.querySelector('.kai-stock-filter-button');btn?.setAttribute('aria-expanded','true');
    requestAnimationFrame(()=>{const menu=wrap.querySelector('.kai-stock-filter-menu'),chosen=menu?.querySelector('.selected');if(chosen)chosen.scrollIntoView({block:'nearest'})});
  }
  function mountOne(select){
    if(!select)return;
    let wrap=select.closest('.kai-stock-filter-select');
    if(wrap){refresh(select,wrap);return}
    wrap=document.createElement('div');wrap.className='kai-stock-filter-select';wrap.dataset.for=select.id;
    select.parentNode.insertBefore(wrap,select);wrap.appendChild(select);select.classList.add('kai-stock-filter-native');
    const btn=document.createElement('button');btn.type='button';btn.className='kai-stock-filter-button';btn.setAttribute('role','combobox');btn.setAttribute('aria-haspopup','listbox');btn.setAttribute('aria-expanded','false');btn.innerHTML='<span class="kai-stock-filter-label"></span><span class="kai-stock-filter-chevron">▼</span>';
    const menu=document.createElement('div');menu.className='kai-stock-filter-menu';menu.setAttribute('role','listbox');
    wrap.appendChild(btn);wrap.appendChild(menu);
    btn.onclick=e=>{e.preventDefault();e.stopPropagation();wrap.classList.contains('open')?close(wrap):open(select,wrap)};
    btn.onkeydown=e=>{
      if(['ArrowDown','ArrowUp','Enter',' '].includes(e.key)){e.preventDefault();if(!wrap.classList.contains('open'))open(select,wrap);const items=[...menu.querySelectorAll('.kai-stock-filter-option')];if(!items.length)return;let i=items.findIndex(x=>x.classList.contains('active'));if(i<0)i=items.findIndex(x=>x.classList.contains('selected'));if(e.key==='ArrowDown')i=Math.min(items.length-1,Math.max(0,i+1));else if(e.key==='ArrowUp')i=Math.max(0,i<0?0:i-1);else if((e.key==='Enter'||e.key===' ')&&i>=0){items[i].click();return}items.forEach(x=>x.classList.remove('active'));items[i]?.classList.add('active');items[i]?.scrollIntoView({block:'nearest'})}
      else if(e.key==='Escape'){e.preventDefault();close(wrap,true)}
    };
    select.addEventListener('change',()=>refresh(select,wrap));
    menu.addEventListener('wheel',e=>e.stopPropagation(),{passive:true});menu.addEventListener('touchmove',e=>e.stopPropagation(),{passive:true});
    refresh(select,wrap);
  }
  function mount(){
    if(!isStock())return;
    // Run after the Stock runtime/integrity pass has finished populating custom values.
    setTimeout(()=>{if(!isStock())return;IDS.forEach(id=>mountOne(document.getElementById(id)))},0);
  }
  document.addEventListener('kai:rendered',mount);
  document.addEventListener('pointerdown',e=>{if(openWrap&&!openWrap.contains(e.target))closeAll()},true);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&openWrap)close(openWrap,true)},true);
  setTimeout(mount,0);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear Stock Category, Version and Size filters now use stable scrollable in-page dropdowns instead of native browser popups.')
