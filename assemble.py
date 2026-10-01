from pathlib import Path
import base64, io, zipfile

root = Path(__file__).parent
parts = root / '.deploy_payload'
names = [
    'payload.part01',
    'payload.part02',
    'payload.part03a',
    'payload.part03b',
    'payload.part03c',
    'payload.part04',
]
files = [parts / name for name in names]
if not all(p.exists() for p in files):
    raise RuntimeError('Kai Wear deployment payload is missing')
payload = ''.join(p.read_text().strip() for p in files)
data = base64.b64decode(payload)
with zipfile.ZipFile(io.BytesIO(data)) as z:
    z.extractall(root)
print('Kai Wear deployment sources assembled.')
