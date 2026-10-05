from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()
changes=0

old="""  function availableProducts(){
    return (state?.products||[]).filter(p=>((p.alloc?.[device]||0)-(cart.find(l=>l.id===p.id)?.qty||0))>0);
  }"""
new="""  function availableProducts(){
    // Show the full preserved catalogue in New Sale, including zero-stock items.
    // Stock availability is still enforced when the user tries to select one.
    return (state?.products||[]);
  }"""
if old in html:
    html=html.replace(old,new,1);changes+=1

old_choose="""  function chooseProduct(p){
    if(!p||!coreAdd)return;
    touchInteraction();
    closePicker(false);
    coreAdd(p);
    const ui=ensurePicker();
    if(ui){ui.input.value='';search='';ui.catalog.classList.remove('open')}
  }"""
new_choose="""  function chooseProduct(p){
    if(!p||!coreAdd)return;
    const left=(p.alloc?.[device]||0)-(cart.find(l=>l.id===p.id)?.qty||0);
    if(left<=0){
      toast('This product is in the catalogue but currently has 0 stock. Receive stock before selling it.');
      pickerOpen=true;
      drawPicker();
      return;
    }
    touchInteraction();
    closePicker(false);
    coreAdd(p);
    const ui=ensurePicker();
    if(ui){ui.input.value='';search='';ui.catalog.classList.remove('open')}
  }"""
if old_choose in html:
    html=html.replace(old_choose,new_choose,1);changes+=1

html=html.replace('No matching product in current inventory.','No matching product in the catalogue.',1)

# Expand search coverage to the full sportswear catalogue metadata.
old_search="""    return `${p.id||''} ${p.club||''} ${p.season||''} ${p.kit||''} ${p.color||''} ${p.size||''} ${p.grade||''}`.toLowerCase();"""
new_search="""    return `${p.id||''} ${p.name||''} ${p.category||''} ${p.club||''} ${p.season||''} ${p.kit||''} ${p.color||''} ${p.size||''} ${p.grade||''}`.toLowerCase();"""
if old_search in html:
    html=html.replace(old_search,new_search,1);changes+=1

index.write_text(html)
print(f'Kai Wear New Sale catalogue dropdown enabled ({changes} source updates).')
