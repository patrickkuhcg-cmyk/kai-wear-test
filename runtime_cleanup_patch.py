from pathlib import Path
import runpy

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()
changes=0

def replace(old,new):
    global html,changes
    if old in html:
        html=html.replace(old,new,1)
        changes+=1
        return True
    return False

# Excel inventory: stop wrapping global render with a delayed setTimeout.
replace(
""" function enhance(){try{enhanceStockPage();excelDashboard()}catch(_){} }
 if(typeof render==='function'){const r=render;render=function(...a){const x=r.apply(this,a);setTimeout(enhance,0);return x}}
 setTimeout(enhance,0);""",
""" function enhance(){try{enhanceStockPage();excelDashboard()}catch(_){} }
 document.addEventListener('kai:rendered',enhance);
 setTimeout(enhance,0);"""
)

# Category summary: update synchronously after stockTable, and use one post-render hook.
replace(
""" if(typeof stockTable==='function'){
   const base=stockTable;
   stockTable=function(...args){const out=base.apply(this,args);setTimeout(renderCategorySummary,0);return out}
 }
 if(typeof render==='function'){
   const baseRender=render;
   render=function(...args){const out=baseRender.apply(this,args);setTimeout(renderCategorySummary,0);return out}
 }
 setTimeout(renderCategorySummary,0);""",
""" if(typeof stockTable==='function'){
   const base=stockTable;
   stockTable=function(...args){const out=base.apply(this,args);renderCategorySummary();return out}
 }
 document.addEventListener('kai:rendered',renderCategorySummary);
 setTimeout(renderCategorySummary,0);"""
)

# Clean Stock UI: no delayed category pass and no global render wrapper.
replace(
""" function enhanceCleanStock(){
   if(typeof page==='undefined'||page!=='Stock')return;
   installSearchDropdown();compactStock();setTimeout(compactCategories,0);
 }
 if(typeof stockTable==='function'){
   const baseStockTable=stockTable;
   stockTable=function(...args){const out=baseStockTable.apply(this,args);setTimeout(enhanceCleanStock,0);return out}
 }
 if(typeof render==='function'){
   const baseRender=render;
   render=function(...args){const out=baseRender.apply(this,args);setTimeout(enhanceCleanStock,0);return out}
 }
 setTimeout(enhanceCleanStock,0);""",
""" function enhanceCleanStock(){
   if(typeof page==='undefined'||page!=='Stock')return;
   installSearchDropdown();compactStock();compactCategories();
 }
 if(typeof stockTable==='function'){
   const baseStockTable=stockTable;
   stockTable=function(...args){const out=baseStockTable.apply(this,args);enhanceCleanStock();return out}
 }
 document.addEventListener('kai:rendered',enhanceCleanStock);
 setTimeout(enhanceCleanStock,0);"""
)

# Stock scope cleanup: remove whole-document observer and render wrapper.
replace(
"""  if(typeof render==='function'){
    const baseRender=render;
    render=function(...args){
      const out=baseRender.apply(this,args);
      setTimeout(keepStockControlsScoped,0);
      return out;
    };
  }

  const observer=new MutationObserver(()=>keepStockControlsScoped());
  observer.observe(document.documentElement,{childList:true,subtree:true});
  setTimeout(keepStockControlsScoped,0);""",
"""  document.addEventListener('kai:rendered',keepStockControlsScoped);
  setTimeout(keepStockControlsScoped,0);"""
)

# Stock intelligence: no whole-document observer and no global render wrapper.
replace(
""" if(typeof stockTable==='function'){
   const base=stockTable;
   stockTable=function(...args){const out=base.apply(this,args);setTimeout(enhance,0);return out}
 }
 if(typeof render==='function'){
   const base=render;
   render=function(...args){const out=base.apply(this,args);setTimeout(enhance,0);return out}
 }
 const obs=new MutationObserver(()=>{if(typeof page!=='undefined'&&page!=='Stock')removeElsewhere()});
 obs.observe(document.documentElement,{childList:true,subtree:true});
 setTimeout(enhance,0);""",
""" if(typeof stockTable==='function'){
   const base=stockTable;
   stockTable=function(...args){const out=base.apply(this,args);enhance();return out}
 }
 document.addEventListener('kai:rendered',enhance);
 setTimeout(enhance,0);"""
)

# Full Stock view: no delayed render/stockTable wrappers.
replace(
""" if(typeof render==='function'){
   const base=render;
   render=function(...args){const out=base.apply(this,args);setTimeout(applyFullView,0);return out};
 }
 if(typeof stockTable==='function'){
   const baseStock=stockTable;
   stockTable=function(...args){const out=baseStock.apply(this,args);setTimeout(applyFullView,0);return out};
 }
 setTimeout(applyFullView,0);""",
""" document.addEventListener('kai:rendered',applyFullView);
 if(typeof stockTable==='function'){
   const baseStock=stockTable;
   stockTable=function(...args){const out=baseStock.apply(this,args);applyFullView();return out};
 }
 setTimeout(applyFullView,0);"""
)

index.write_text(html)
print(f'Kai Wear runtime cleanup flattened {changes} delayed UI wrapper group(s).')

# Restore the Stock-only controls after flattening. This patch only subscribes
# to the single kai:rendered signal; it does not wrap global render or sync.
stable_stock=root/'stock_stable_controls_patch.py'
if stable_stock.exists():
    runpy.run_path(str(stable_stock),run_name='__kai_stock_stable_controls__')
