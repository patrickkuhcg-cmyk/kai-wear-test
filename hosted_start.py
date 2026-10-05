"""Disposable hosted test: bootstrap owner privately before accepting traffic."""
import os, secrets, runpy
from pathlib import Path
from urllib.parse import urlparse
from http.server import ThreadingHTTPServer
import server

def apply_ui_patch():
    for name, run_name in [('ui_patch.py','__kai_ui_patch__'),('stock_patch.py','__kai_stock_patch__')]:
        patch = Path(__file__).with_name(name)
        if patch.exists():
            runpy.run_path(str(patch), run_name=run_name)

def bootstrap_owner():
    password=os.environ.get('KAI_OWNER_PASSWORD','')
    if len(password)<12:
        raise RuntimeError('Set KAI_OWNER_PASSWORD to a private password of at least 12 characters in the host settings.')
    server.init()
    with server.conn() as c:
        c.execute('BEGIN IMMEDIATE')
        if not c.execute('SELECT 1 FROM users').fetchone():
            salt=secrets.token_hex(16)
            c.execute('INSERT INTO users(name,salt,hash,role,display,shop,device) VALUES (?,?,?,?,?,?,?)',('owner',salt,server.password_hash(password,salt),'owner','Owner','all',None))
            server.audit(c,'owner','hosted_test_setup','Kai Wear sample workspace')

class TestHandler(server.Handler):
    def do_POST(self):
        if urlparse(self.path).path=='/api/setup':
            return self.send_json({'error':'Public setup is disabled. Sign in as owner using the password configured privately on the host.'},403)
        return super().do_POST()

if __name__=='__main__':
    os.environ.setdefault('KAI_SECURE_COOKIE','1')
    apply_ui_patch()
    bootstrap_owner()
    port=int(os.environ.get('PORT',os.environ.get('KAI_PORT','8080')))
    print('Kai Wear disposable test server starting. No credentials are logged.',flush=True)
    ThreadingHTTPServer(('0.0.0.0',port),TestHandler).serve_forever()
