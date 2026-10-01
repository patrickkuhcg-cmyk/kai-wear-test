from pathlib import Path

root=Path(__file__).parent
parts=root/'.deploy_parts'

def assemble(prefix, destination):
    files=sorted(parts.glob(prefix+'.part*'))
    if not files:
        raise RuntimeError(f'No deployment parts found for {prefix}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(''.join(p.read_text() for p in files))

assemble('server', root/'server.py')
assemble('index', root/'static'/'index.html')
print('Kai Wear deployment sources assembled.')
