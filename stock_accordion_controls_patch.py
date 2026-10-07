from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

css=r'''
<style id="kai-stock-accordion-controls-style">
#kai-s16-expand,#kai-s16-cats{display:inline-flex;align-items:center;justify-content:center;gap:7px}
.kai-stock-caret{font-size:10px;line-height:1;opacity:.8}
</style>
'''

js=r'''
<script id="kai-stock-accordion-controls-script">
(()=>{
  const isStock=()=>typeof page!=='undefined'&&page==='Stock';

  function decorate(){
    if(!isStock())return;
    const expand=document.getElementById('kai-s16-expand');
    const collapse=document.getElementById('kai-s16-collapse');
    const cats=document.getElementById('kai-s16-cats');
    const fullOpen=!!collapse;
    const catsOpen=!!document.querySelector('.kai-s16-cats.open');

    if(expand){
      expand.setAttribute('aria-expanded',fullOpen?'true':'false');
      expand.innerHTML=fullOpen
        ? 'Hide full stock <span class="kai-stock-caret">▴</span>'
        : 'View all stock / Expand <span class="kai-stock-caret">▾</span>';
    }
    if(collapse){
      // The main button now performs both open and close actions.
      collapse.style.display='none';
      collapse.setAttribute('aria-hidden','true');
    }
    if(cats){
      cats.setAttribute('aria-expanded',catsOpen?'true':'false');
      cats.innerHTML=catsOpen
        ? 'Hide category breakdown <span class="kai-stock-caret">▴</span>'
        : 'Show category breakdown <span class="kai-stock-caret">▾</span>';
    }
  }

  // When the full-stock section is already open, turn the existing primary
  // control into the close action by forwarding to the original Collapse
  // button. When closed, the original v16 handler remains untouched.
  document.addEventListener('click',e=>{
    if(!isStock())return;
    const btn=e.target.closest?.('#kai-s16-expand');
    if(!btn)return;
    const collapse=document.getElementById('kai-s16-collapse');
    if(collapse){
      e.preventDefault();
      e.stopImmediatePropagation();
      collapse.click();
      setTimeout(decorate,0);
    }
  },true);

  document.addEventListener('click',e=>{
    if(!isStock())return;
    if(e.target.closest?.('#kai-s16-cats'))setTimeout(decorate,0);
  });

  document.addEventListener('kai:rendered',()=>setTimeout(decorate,0));
  setTimeout(decorate,0);
})();
</script>
'''

pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+css+'\n'+js+'\n'+html[pos:]
index.write_text(html)
print('Kai Wear Stock full-list and category controls now use consistent dropdown accordion toggles.')
