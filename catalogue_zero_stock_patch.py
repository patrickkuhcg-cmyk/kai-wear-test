from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

# After a clean-start reset, catalogue variants remain valid products even when
# their on-hand quantity is zero. Stock intelligence should therefore report
# catalogue variants, not only variants that currently have units in stock.
old="active=all.filter(p=>units(p)>0).length"
new="active=all.length"
if old in html:
    html=html.replace(old,new,1)

old_label="<span>Active variants</span>"
new_label="<span>Product variants</span>"
if old_label in html:
    html=html.replace(old_label,new_label,1)

index.write_text(html)
print('Kai Wear catalogue-preservation view enabled: zero-stock products remain searchable and counted as product variants.')
