"""Disposable hosted test: bootstrap owner privately before accepting traffic."""
import os, secrets, runpy, json, base64
from pathlib import Path
from urllib.parse import urlparse
from http.server import ThreadingHTTPServer

ROOT=Path(__file__).parent
SERVER_PATCH=ROOT/'excel_server_patch.py'
if SERVER_PATCH.exists():
    runpy.run_path(str(SERVER_PATCH), run_name='__kai_excel_server_patch__')

import server
from stock_importer import parse as parse_stock_file

BUILD_LABEL='Excel Inventory Model v16.2.5 · Clean Zero Start · 05 Oct 2026'
RESET_VERSION='kai-clean-zero-start-20261005-v1'

def apply_ui_patch():
    # Flat architecture: each subsystem is loaded once. Stock is owned by the
    # v16 runtime; duplicate legacy Stock-control generators are retired.
    for name, run_name in [
        ('core_runtime_capture_patch.py','__kai_core_runtime_capture__'),
        ('ui_patch.py','__kai_ui_patch__'),
        ('stock_patch.py','__kai_stock_patch__'),
        ('excel_ui_patch.py','__kai_excel_ui_patch__'),
        ('runtime_cleanup_patch.py','__kai_runtime_cleanup__'),
        ('stock_runtime_v16_patch.py','__kai_stock_runtime_v16__'),
        ('page_stability_patch.py','__kai_page_stability_v16__'),
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
    sw.write_text("""const CACHE='kai-wear-excel-inventory-v16-2-5-clean-zero-start-20261005';
self.addEventListener('install',e=>{self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));self.clients.claim()});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin||u.pathname.startsWith('/api/'))return;if(e.request.mode==='navigate'||u.pathname==='/'||u.pathname.endsWith('/index.html')){e.respondWith(fetch(e.request,{cache:'no-store'}).then(r=>{const copy=r.clone();caches.open(CACHE).then(c=>c.put('./index.html',copy));return r}).catch(()=>caches.match('./index.html')));return;}e.respondWith(fetch(e.request).then(r=>{if(r.ok){const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy))}return r}).catch(()=>caches.match(e.request)))});
""")
    print('Kai Wear fresh app shell enforced: '+BUILD_LABEL,flush=True)


def reset_business_data_once():
    """Create a clean business starting point exactly once.

    Accounts/access and the product catalogue are preserved. Stock quantities,
    weighted costs, and transaction/history collections are reset. The marker
    prevents later restarts/deploys from wiping newly entered business data.
    """
    with server.LOCK:
        with server.conn() as c:
            row=c.execute('SELECT payload FROM state WHERE id=1').fetchone()
            if not row:
                return
            data=json.loads(row[0])
            if data.get('_cleanStartVersion')==RESET_VERSION:
                return

            # Preserve product identity/category metadata, but start inventory
            # and accounting cost values at zero.
            for p in data.get('products',[]):
                alloc=p.get('alloc')
                if isinstance(alloc,dict):
                    p['alloc']={k:0 for k in alloc.keys()}
                p['cost']=0
                if 'retail' in p:p['retail']=0
                if 'wholesale' in p:p['wholesale']=0

            # Clear operational records while leaving settings/access intact.
            transaction_lists=(
                'sales','movements','expenses','payments','creditPayments',
                'credits','receipts','cashups','cashReconciliations',
                'reconciliations','stockAdjustments','adjustments','returns',
                'refunds','transfers','taxEntries','taxPayments'
            )
            for key in transaction_lists:
                if isinstance(data.get(key),list):
                    data[key]=[]

            # Any direct numeric opening balances should start at zero if they
            # exist in this build. Do not alter tax-rate/settings structures.
            for key in ('openingCash','openingBalance','cashBalance','creditBalance'):
                if key in data and isinstance(data[key],(int,float)):
                    data[key]=0

            data['_cleanStartVersion']=RESET_VERSION
            data['revision']=int(data.get('revision',0))+1
            c.execute('UPDATE state SET payload=? WHERE id=1',(json.dumps(data),))
            server.audit(c,'owner','clean_start_reset','Business records reset to zero; accounts and product catalogue preserved')
    try:server.notify()
    except Exception:pass
    print('Kai Wear clean zero start applied once: stock and business records reset; accounts preserved.',flush=True)


def bootstrap_owner():
    password=os.environ.get('KAI_OWNER_PASSWORD','')
    if len(password)<12:
        raise RuntimeError('Set KAI_OWNER_PASSWORD to a private password of at least 12 characters in the host settings.')
    server.init()
    if hasattr(server,'migrate_excel_inventory_state'):
        server.migrate_excel_inventory_state()
        print('Kai Wear legacy sample products normalized to Excel category, version and size standards.',flush=True)
    reset_business_data_once()
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

    def _json_body(self,limit=12_000_000):
        if 'application/json' not in self.headers.get('Content-Type',''):
            raise ValueError('JSON required')
        length=int(self.headers.get('Content-Length',0))
        if not 0<length<=limit:raise ValueError('Invalid request size')
        return json.loads(self.rfile.read(length))

    def do_POST(self):
        path=urlparse(self.path).path
        if path=='/api/setup':
            return self.send_json({'error':'Public setup is disabled. Sign in as owner using the password configured privately on the host.'},403)
        if path=='/api/import-stock-preview':
            try:
                u=self.user()
                if not u:return self.send_json({'error':'Login required'},401)
                if u['role']!='owner':return self.send_json({'error':'Owner login required for bulk stock import'},403)
                data=self._json_body();raw=base64.b64decode(str(data.get('content','')),validate=True)
                if len(raw)>8_000_000:raise ValueError('File is too large. Maximum import size is 8 MB.')
                rows=parse_stock_file(raw,str(data.get('filename','')))
                return self.send_json({'rows':rows,'count':len(rows)})
            except (ValueError,TypeError,KeyError) as e:return self.send_json({'error':str(e)},400)
            except Exception:return self.send_json({'error':'Kai Wear could not read this stock file'},400)
        if path=='/api/import-stock-commit':
            try:
                u=self.user()
                if not u:return self.send_json({'error':'Login required'},401)
                if u['role']!='owner':return self.send_json({'error':'Owner login required for bulk stock import'},403)
                data=self._json_body(4_000_000);rows=data.get('rows');device=data.get('device')
                if not isinstance(rows,list) or not 1<=len(rows)<=1000:raise ValueError('No valid import rows supplied')
                if device not in server.DEVICES:raise ValueError('Choose the destination counter')
                created=0;imported=0
                with server.LOCK:
                    with server.conn() as c:
                        c.execute('BEGIN IMMEDIATE');state=json.loads(c.execute('SELECT payload FROM state WHERE id=1').fetchone()[0])
                        for r in rows:
                            pid=str(r.get('id','')).strip()[:90]
                            if not pid:continue
                            p=next((x for x in state['products'] if str(x.get('id','')).lower()==pid.lower()),None)
                            if not p:
                                pdata={
                                  'id':pid,'name':str(r.get('name') or r.get('club') or pid)[:90],
                                  'category':str(r.get('category') or 'Other Sportswear')[:90],
                                  'club':str(r.get('club') or 'N/A')[:90],'season':str(r.get('season') or 'N/A')[:90],
                                  'kit':str(r.get('kit') or 'N/A')[:90],'color':str(r.get('color') or 'N/A')[:90],
                                  'size':str(r.get('size') or 'N/A')[:90],'grade':str(r.get('grade') or 'N/A')[:90],
                                  'minStock':int(r.get('minStock') or 5),'cost':int(r.get('cost') or 0),'retail':0,'wholesale':0}
                                server.apply(state,{'id':secrets.token_urlsafe(12),'type':'product','data':pdata},u['role'],u['name'],u);created+=1
                            q=int(r.get('qty') or 0);cost=int(r.get('cost') or 0)
                            if q<1:continue
                            rdata={'id':pid,'device':device,'qty':q,'cost':max(0,cost),'date':server.timestamp(),'supplier':str(r.get('supplier') or '')[:90],'paymentStatus':str(r.get('paymentStatus') or 'Unpaid')[:40],'note':str(r.get('note') or 'Imported stock')[:150] or 'Imported stock'}
                            server.apply(state,{'id':secrets.token_urlsafe(12),'type':'restock','data':rdata},u['role'],u['name'],u);imported+=1
                        c.execute('UPDATE state SET payload=? WHERE id=1',(json.dumps(state),));server.audit(c,u['name'],'stock_import',f'{imported} rows / {created} new products')
                server.notify();return self.send_json({'ok':True,'imported':imported,'created':created})
            except (ValueError,TypeError,KeyError) as e:return self.send_json({'error':str(e)},400)
            except Exception:return self.send_json({'error':'Kai Wear could not complete this stock import'},500)
        return super().do_POST()


if __name__=='__main__':
    os.environ.setdefault('KAI_SECURE_COOKIE','1')
    apply_ui_patch()
    force_fresh_app_shell()
    bootstrap_owner()
    port=int(os.environ.get('PORT',os.environ.get('KAI_PORT','8080')))
    print('Kai Wear disposable test server starting. No credentials are logged.',flush=True)
    ThreadingHTTPServer(('0.0.0.0',port),TestHandler).serve_forever()
