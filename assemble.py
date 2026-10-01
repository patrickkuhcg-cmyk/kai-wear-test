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
old_sell = "function canSell(){return user.role==='cashier'||(owner()&&(!live||user.saleDevices?.length>0))}"
new_sell = "function canSell(){return user.role==='cashier'||owner()}"
if old_sell not in html:
    raise RuntimeError('Owner New Sale permission patch target not found')
html = html.replace(old_sell, new_sell, 1)

old_device = "if(page==='New sale'){if(!owner())device=user.device||user.name;else if(live&&!user.saleDevices?.includes(device))device=user.saleDevices?.[0]||device;"
new_device = "if(page==='New sale'){if(!owner())device=user.device||user.name;else if(live&&!user.saleDevices?.includes(device))device=(user.saleDevices?.[0]||allowedDevices()[0]||device);"
if old_device not in html:
    raise RuntimeError('Owner sale counter fallback patch target not found')
html = html.replace(old_device, new_device, 1)

old_options = "${(live&&owner()?user.saleDevices:allowedDevices()).map(d=>`<option value=\"${d}\" ${device===d?'selected':''}>${counterName(d)}</option>`).join('')}"
new_options = "${(live&&owner()&&user.saleDevices?.length?user.saleDevices:allowedDevices()).map(d=>`<option value=\"${d}\" ${device===d?'selected':''}>${counterName(d)}</option>`).join('')}"
if old_options not in html:
    raise RuntimeError('Owner sale counter options patch target not found')
html = html.replace(old_options, new_options, 1)

index.write_text(html)

print('Kai Wear deployment sources assembled; login eye and owner New Sale enabled.')
