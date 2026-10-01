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

index = root / 'static' / 'index.html'
html = index.read_text()
old = """<label>${setup?'Owner password (10+ characters)':'Password / counter code'}<input name="password" type="password" autocomplete="${setup?'new-password':'current-password'}" required ${setup?'minlength="10"':''}></label>"""
new = """<label>${setup?'Owner password (10+ characters)':'Password / counter code'}<span style="position:relative;display:block"><input id="auth-password" name="password" type="password" autocomplete="${setup?'new-password':'current-password'}" required ${setup?'minlength="10"':''} style="padding-right:48px;width:100%"><button type="button" id="toggle-password" aria-label="Show password" title="Show password" style="position:absolute;right:8px;top:50%;transform:translateY(-50%);border:0;background:transparent;padding:6px;cursor:pointer;font-size:18px;line-height:1">👁</button></span></label>"""
if old not in html:
    raise RuntimeError('Login password field patch target not found')
html = html.replace(old, new, 1)

old_hook = "$('#export-pending').onclick=exportPending;$('#login-form').onsubmit=async e=>"
new_hook = "$('#export-pending').onclick=exportPending;$('#toggle-password').onclick=()=>{const p=$('#auth-password'),b=$('#toggle-password'),show=p.type==='password';p.type=show?'text':'password';b.textContent=show?'🙈':'👁';b.setAttribute('aria-label',show?'Hide password':'Show password');b.title=show?'Hide password':'Show password'};$('#login-form').onsubmit=async e=>"
if old_hook not in html:
    raise RuntimeError('Login password toggle hook target not found')
html = html.replace(old_hook, new_hook, 1)
index.write_text(html)

print('Kai Wear deployment sources assembled and login eye enabled.')
