from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

# Wording-only edits: Kai Wear sells multiple sportswear product types, not jerseys only.
replacements=[
    ('Search a jersey, enter the actual selling price, and complete the sale. Receipt is optional.',
     'Search a product, enter the actual selling price, and complete the sale. Receipt is optional.'),
    ('Search jersey: club, code, size, colour, grade…',
     'Search product: name, code, category, club, size, colour, version…'),
    ('Search jersey: club, code, size, colour, grade...',
     'Search product: name, code, category, club, size, colour, version...'),
    ('Search above and choose a jersey to start the sale.',
     'Search above and choose a product to start the sale.'),
    ('Best-selling jerseys','Best-selling products'),
]

changed=0
for old,new in replacements:
    count=html.count(old)
    if count:
        html=html.replace(old,new)
        changed+=count

index.write_text(html)
print(f'Kai Wear product wording updated in {changed} place(s); UI logic unchanged.')
