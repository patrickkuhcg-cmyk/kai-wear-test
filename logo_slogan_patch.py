from pathlib import Path

root=Path(__file__).parent
static=root/'static'
phrases=[
    'WEAR IT. LIVE IT. LOVE IT.',
    'WEAR IT. LIVE IT. LOVE IT',
    'Wear It. Live It. Love It.',
    'Wear It. Live It. Love It',
    'Wear it. live it. love it.',
    'Wear it. live it. love it',
]
replacement='Wear Your Passion'
changed=0
for p in static.glob('*.svg'):
    try:
        txt=p.read_text()
    except Exception:
        continue
    new=txt
    for old in phrases:
        new=new.replace(old,replacement)
    if new!=txt:
        p.write_text(new)
        changed+=1
index=static/'index.html'
if index.exists():
    txt=index.read_text()
    new=txt
    for old in phrases:
        new=new.replace(old,replacement)
    if new!=txt:
        index.write_text(new)
        changed+=1
print(f'Kai Wear logo slogan updated to "{replacement}" in {changed} generated asset(s).')
