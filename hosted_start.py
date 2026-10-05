"""Disposable hosted test: bootstrap owner privately before accepting traffic."""
import os, secrets, runpy
from pathlib import Path
from urllib.parse import urlparse
from http.server import ThreadingHTTPServer

ROOT=Path(__file__).parent
SERVER_PATCH=ROOT/'excel_server_patch.py'
if SERVER_PATCH.exists():
    runpy.run_path(str(SERVER_PATCH), run_name='__kai_excel_server_patch__')

import server

BUILD_LABEL='Excel Inventory Model v5 · 05 Oct 2026'

def apply_ui_patch():
    for name, run_name in [
        ('ui_patch.py','__kai_ui_patch__'),
        ('stock_patch.py','__kai_stock_patch__'),
        ('model_patch.py','__kai_model_patch__'),
        ('excel_ui_patch.py','__kai_excel_ui_patch__'),
    ]:
        patch = ROOT/name
        if patch.exists():
            runpy.run_path(str(patch), run_name=run_name)


def force_fresh_app_shell():
    index=ROOT/'static'/'index.html'
    html=index.read_text()
    old='id="kai-build-marker"'
    if old in html:
        import re
        html=re.sub(r'<div id="kai-build-marker"[^>]*>.*?</div>','',html,count=1,flags=re.S)
    marker=f'''<div id="kai-build-marker" style="position:fixed;right:12px;bottom:10px;z-index:9998;background:#0f2d38;color:#dff8ff;border:1px solid #2f6170;border-radius:999px;padding:5px 9px;font:600 10px/1.2 system-ui;box-shadow:0 2px 8px rgba(0,0,0,.12)">{BUILD_LABEL}</div>'''
    body_end=html.rfind('</body>')
    if body_end>=0:
        html=html[:body_end]+marker+'\n'+html[body_end:]
    index.write_text(html)

    sw=ROOT/'static'/'sw.js'
    sw.write_text("""const CACHE='kai-wear-excel-inventory-v5-20261005';
self.addEventListener('install',e=>{self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));self.clients.claim()});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin||u.pathname.startsWith('/api/'))return;if(e.request.mode==='navigate'||u.pathname==='/'||u.pathname.endsWith('/index.html')){e.respondWith(fetch(e.request,{cache:'no-store'}).then(r=>{const copy=r.clone();caches.open(CACHE).then(c=>c.put('./index.html',copy));return r}).catch(()=>caches.match('./index.html')));return;}e.respondWith(fetch(e.request).then(r=>{if(r.ok){const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy))}return r}).catch(()=>caches.match(e.request)))});
""")
    print('Kai Wear fresh app shell enforced: '+BUILD_LABEL,flush=True)


def bootstrap_owner():
    password=os.environ.get('KAI_OWNER_PASSWORD','')
    if len(password)<12:
        raise RuntimeError('Set KAI_OWNER_PASSWORD to a private password of at least 12 characters in the host settings.')
    server.init()
    if hasattr(server,'migrate_excel_inventory_state'):
        server.migrate_excel_inventory_state()
        print('Kai Wear legacy sample products normalized to Excel category, version and size standards.',flush=True)
    with server.conn() as c:
        c.execute('BEGIN IMMEDIATE')
        if not c.execute('SELECT 1 FROM users').fetchone():
            salt=secrets.token_hex(16)
            c.execute('INSERT INTO users(name,salt,hash,role,display,shop,device) VALUES (?,?,?,?,?,?,?)',('owner',salt,server.password_hash(password,salt),'owner','Owner','all',None))
            server.audit(c,'owner','hosted_test_setup','Kai Wear sample workspace')


class TestHandler(server.Handler):
    def end_headers(self):
        path=urlparse(self.path).path
        if path in ('/','/index.html','/sw.js'):
            self.send_header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma','no-cache')
            self.send_header('Expires','0')
        return super().end_headers()

    def do_POST(self):
        if urlparse(self.path).path=='/api/setup':
            return self.send_json({'error':'Public setup is disabled. Sign in as owner using the password configured privately on the host.'},403)
        return super().do_POST()


if __name__=='__main__':
    os.environ.setdefault('KAI_SECURE_COOKIE','1')
    apply_ui_patch()
    force_fresh_app_shell()
    bootstrap_owner()
    port=int(os.environ.get('PORT',os.environ.get('KAI_PORT','8080')))
    print('Kai Wear disposable test server starting. No credentials are logged.',flush=True)
    ThreadingHTTPServer(('0.0.0.0',port),TestHandler).serve_forever()
