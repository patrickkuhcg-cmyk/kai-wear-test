from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

css=r'''
<style id="kai-stock-nested-content-style">
.kai-stock-product-accordion,.kai-stock-category-accordion{display:grid;gap:6px;margin:8px 0 0}
.kai-stock-product-accordion details,.kai-stock-category-accordion details{border:1px solid #dce9ed;border-radius:9px;background:#fff;overflow:hidden}
.kai-stock-product-accordion summary,.kai-stock-category-accordion summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:minmax(0,1fr) auto auto;align-items:center;gap:10px;padding:9px 11px;font-size:12px;color:#173f4a}
.kai-stock-product-accordion summary::-webkit-details-marker,.kai-stock-category-accordion summary::-webkit-details-marker{display:none}
.kai-stock-product-accordion summary::after,.kai-stock-category-accordion summary::after{content:'▾';font-size:10px;opacity:.75;transition:transform .14s ease}
.kai-stock-product-accordion details[open] summary::after,.kai-stock-category-accordion details[open] summary::after{transform:rotate(180deg)}
.kai-stock-acc-name{min-width:0;font-weight:750;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.kai-stock-acc-meta{font-size:10px;color:var(--muted);white-space:nowrap}.kai-stock-acc-total{font-weight:800;white-space:nowrap}
.kai-stock-acc-body{border-top:1px solid #edf3f5;background:#fbfdfe;padding:9px 11px}.kai-stock-acc-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px 12px}.kai-stock-acc-grid div{min-width:0}.kai-stock-acc-grid small{display:block;color:var(--muted);font-size:9px}.kai-stock-acc-grid b{display:block;font-size:11px;overflow-wrap:anywhere}
.kai-stock-category-items{display:grid;gap:5px;max-height:220px;overflow:auto;overscroll-behavior:contain;padding-right:3px}.kai-stock-category-item{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;padding:7px 8px;border:1px solid #e6eef0;border-radius:7px;background:#fff}.kai-stock-category-item b{font-size:11px}.kai-stock-category-item small{display:block;font-size:9px;color:var(--muted);margin-top:2px}.kai-stock-category-item span{font-size:10px;font-weight:750;white-space:nowrap}
.kai-stock-original-table-hidden,.kai-stock-original-cats-hidden{display:none!important}
@media(max-width:760px){.kai-stock-product-accordion summary,.kai-stock-category-accordion summary{grid-template-columns:minmax(0,1fr) auto auto;gap:7px;padding:9px}.kai-stock-acc-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.kai-stock-acc-meta{display:none}}
</style>
'''

js=r'''
<script id="kai-stock-nested-content-script">
(()=>{
  const isStock=()=>typeof page!=='undefined'&&page==='Stock';
  const clean=s=>String(s||'').trim();
  const units=p=>Object.values(p?.alloc||{}).reduce((a,v)=>a+Number(v||0),0);
  const pname=p=>clean(p?.name||p?.club||p?.id||'Product');

  function addField(grid,label,value){
    const d=document.createElement('div'),s=document.createElement('small'),b=document.createElement('b');
    s.textContent=label;b.textContent=clean(value)||'—';d.append(s,b);grid.appendChild(d);
  }

  function buildProductAccordion(host){
    const wrap=host.querySelector('.table-wrap');
    if(!wrap)return;
    const tbody=wrap.querySelector('tbody');if(!tbody)return;
    let acc=host.querySelector(':scope > .kai-stock-product-accordion');
    if(acc)acc.remove();
    acc=document.createElement('div');acc.className='kai-stock-product-accordion';
    [...tbody.querySelectorAll('tr')].forEach(tr=>{
      const c=[...tr.children].map(td=>clean(td.textContent));
      if(!c.length)return;
      const d=document.createElement('details');
      const sum=document.createElement('summary');
      const name=document.createElement('span');name.className='kai-stock-acc-name';name.textContent=c[0]||'Product';
      const meta=document.createElement('span');meta.className='kai-stock-acc-meta';meta.textContent=[c[3],c[6]].filter(Boolean).join(' · ');
      const total=document.createElement('span');total.className='kai-stock-acc-total';total.textContent=(c[9]||'0')+' units';
      sum.append(name,meta,total);d.appendChild(sum);
      const body=document.createElement('div');body.className='kai-stock-acc-body';
      const grid=document.createElement('div');grid.className='kai-stock-acc-grid';
      addField(grid,'Category',c[1]);addField(grid,'Club / Country',c[2]);addField(grid,'Version',c[3]);addField(grid,'Kit',c[4]);
      addField(grid,'Season',c[5]);addField(grid,'Size',c[6]);addField(grid,'Shop 1',c[7]);addField(grid,'Shop 2',c[8]);
      addField(grid,'Total',c[9]);addField(grid,'Status',c[10]);
      body.appendChild(grid);d.appendChild(body);acc.appendChild(d);
    });
    wrap.classList.add('kai-stock-original-table-hidden');wrap.insertAdjacentElement('afterend',acc);
  }

  function categoryProducts(name){
    if(typeof state==='undefined')return [];
    const n=clean(name).toLowerCase();
    return (state?.products||[]).filter(p=>clean(p?.category||'Other Sportswear').toLowerCase()===n);
  }

  function buildCategoryAccordion(host){
    const source=host.querySelector('.kai-s16-cats.open');
    const old=host.querySelector('.kai-stock-category-accordion');if(old)old.remove();
    if(!source){host.querySelector('.kai-s16-cats')?.classList.remove('kai-stock-original-cats-hidden');return}
    const acc=document.createElement('div');acc.className='kai-stock-category-accordion';
    [...source.querySelectorAll('.kai-s16-cat')].forEach(card=>{
      const name=clean(card.querySelector('span')?.textContent||card.dataset.cat);
      const unitText=clean(card.querySelector('b')?.textContent||'0');
      const variantText=clean(card.querySelector('small')?.textContent||'');
      const d=document.createElement('details'),sum=document.createElement('summary');
      const n=document.createElement('span');n.className='kai-stock-acc-name';n.textContent=name;
      const meta=document.createElement('span');meta.className='kai-stock-acc-meta';meta.textContent=variantText;
      const total=document.createElement('span');total.className='kai-stock-acc-total';total.textContent=unitText+' units';
      sum.append(n,meta,total);d.appendChild(sum);
      const body=document.createElement('div');body.className='kai-stock-acc-body';
      const items=document.createElement('div');items.className='kai-stock-category-items';
      const ps=categoryProducts(name);
      if(ps.length){ps.forEach(p=>{
        const row=document.createElement('div');row.className='kai-stock-category-item';
        const left=document.createElement('div'),b=document.createElement('b'),sm=document.createElement('small'),q=document.createElement('span');
        b.textContent=pname(p);sm.textContent=[p.id,p.grade,p.size,p.kit].filter(Boolean).join(' · ');q.textContent=units(p)+' units';
        left.append(b,sm);row.append(left,q);items.appendChild(row);
      })}else{
        const empty=document.createElement('div');empty.className='tiny';empty.textContent='No product variants in this category.';items.appendChild(empty)
      }
      body.appendChild(items);d.appendChild(body);acc.appendChild(d);
    });
    source.classList.add('kai-stock-original-cats-hidden');source.insertAdjacentElement('afterend',acc);
  }

  function enhance(){
    if(!isStock())return;
    const host=document.querySelector('#stock-table');if(!host)return;
    buildProductAccordion(host);buildCategoryAccordion(host);
  }

  // The v16 Stock runtime sometimes redraws its own panel directly rather than
  // calling the global render event, so refresh this presentation after the
  // specific controls and filters that can rebuild Stock content.
  document.addEventListener('click',e=>{
    if(!isStock())return;
    if(e.target.closest?.('#kai-s16-expand,#kai-s16-collapse,#kai-s16-cats,[data-cat],.kai-stock-filter-option'))setTimeout(enhance,0);
  },true);
  document.addEventListener('input',e=>{if(isStock()&&e.target?.id==='search')setTimeout(enhance,0)},true);
  document.addEventListener('change',e=>{if(isStock()&&['excel-category','grade','size'].includes(e.target?.id))setTimeout(enhance,0)},true);
  document.addEventListener('kai:rendered',()=>setTimeout(enhance,0));
  setTimeout(enhance,0);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear expanded Stock content now uses compact nested product and category accordions.')
