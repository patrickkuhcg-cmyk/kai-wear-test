from pathlib import Path
import re

root=Path(__file__).parent
static=root/'static'
replacement='Wear Your Passion'
phrase_patterns=[
    r'WEAR\s*IT[.\s]*LIVE\s*IT[.\s]*LOVE\s*IT[.]?',
    r'Wear\s*It[.\s]*Live\s*It[.\s]*Love\s*It[.]?',
    r'Wear\s*it[.\s]*live\s*it[.\s]*love\s*it[.]?',
]

def replace_phrase(text):
    out=text
    for pat in phrase_patterns:
        out=re.sub(pat,replacement,out,flags=re.I)
    return out

changed=0
for p in static.glob('*.svg'):
    try:txt=p.read_text()
    except Exception:continue
    new=replace_phrase(txt)
    # Some generated logo SVGs render the old slogan as paths rather than text.
    # For Kai Wear logo assets only, place the new slogan cleanly over the
    # original slogan zone without disturbing the rest of the vector artwork.
    name=p.name.lower()
    if replacement not in new and any(k in name for k in ('kai','wear','logo')):
        m=re.search(r'viewBox=["\']\s*([\-\d.]+)\s+([\-\d.]+)\s+([\d.]+)\s+([\d.]+)\s*["\']',new,re.I)
        if m and '</svg>' in new:
            x0,y0,w,h=map(float,m.groups())
            y=y0+h*0.875
            overlay=(f'<g id="kai-wear-passion-slogan">'
                     f'<rect x="{x0}" y="{y}" width="{w}" height="{h*0.125}" fill="#ffffff"/>'
                     f'<text x="{x0+w/2}" y="{y0+h*0.955}" text-anchor="middle" '
                     f'font-family="Arial,Helvetica,sans-serif" font-size="{h*0.045}" '
                     f'font-weight="700" fill="#173f4a">{replacement}</text></g>')
            new=new.replace('</svg>',overlay+'</svg>',1)
    if new!=txt:
        p.write_text(new);changed+=1

index=static/'index.html'
if index.exists():
    txt=index.read_text()
    new=replace_phrase(txt)
    runtime=r'''
<script id="kai-brand-slogan-runtime">
(()=>{
 const brand='Wear Your Passion';
 const rx=/wear\s*it[.\s]*live\s*it[.\s]*love\s*it\.?/ig;
 function swapText(root=document){
   const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
   const nodes=[];while(w.nextNode())nodes.push(w.currentNode);
   nodes.forEach(n=>{if(rx.test(n.nodeValue||'')){rx.lastIndex=0;n.nodeValue=(n.nodeValue||'').replace(rx,brand)}else rx.lastIndex=0});
 }
 if(typeof receiptHTML==='function'&&!receiptHTML.__kaiBrandWrapped){
   const base=receiptHTML;
   const wrapped=function(...args){const out=base.apply(this,args);return typeof out==='string'?out.replace(rx,brand):out};
   wrapped.__kaiBrandWrapped=true;receiptHTML=wrapped;
 }
 const apply=()=>swapText(document);
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',apply,{once:true});else apply();
 new MutationObserver(apply).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>
'''
    if 'kai-brand-slogan-runtime' not in new:
        pos=new.rfind('</body>')
        if pos>=0:new=new[:pos]+runtime+'\n'+new[pos:]
    if new!=txt:
        index.write_text(new);changed+=1

print(f'Kai Wear branding updated to "{replacement}" across generated logo assets, login UI and receipt HTML ({changed} asset(s) changed).')
