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

server = root / 'server.py'
server_text = server.read_text()

old_owner_guard = """                    if data.get('type')=='sale' and u['role']=='owner':
                        with conn() as c:binding=c.execute('SELECT installation FROM counters WHERE device=?',(data.get('data',{}).get('device'),)).fetchone()
                        if not binding or not binding[0] or binding[0]!=u.get('installation') or self.installation()!=u.get('installation'):return self.send_json({'error':'Owner sales require this browser to be assigned to that counter. Log in as its cashier first.'},403)
"""
if old_owner_guard not in server_text:
    raise RuntimeError('Owner sale server guard patch target not found')
server_text = server_text.replace(old_owner_guard, '', 1)

old_price_guard = """            # Prices and standard unit costs are checked against the server.
            if item.get('price')!=p[mode]:raise ValueError('Price changed. Review this offline receipt.')
            price=p[mode];subtotal+=price*q"""
new_price_guard = """            # The stored retail/wholesale price is a suggested default. The actual selling price is entered per sale.
            price=num(item.get('price'),10000,50000);subtotal+=price*q"""
if old_price_guard not in server_text:
    raise RuntimeError('Flexible selling price server patch target not found')
server_text = server_text.replace(old_price_guard, new_price_guard, 1)
server.write_text(server_text)

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
new_device = "if(page==='New sale'){if(!owner())device=user.device||user.name;else if(live&&!allowedDevices().includes(device))device=(allowedDevices()[0]||device);"
if old_device not in html:
    raise RuntimeError('Owner sale counter fallback patch target not found')
html = html.replace(old_device, new_device, 1)

old_options = "${(live&&owner()?user.saleDevices:allowedDevices()).map(d=>`<option value=\"${d}\" ${device===d?'selected':''}>${counterName(d)}</option>`).join('')}"
new_options = "${allowedDevices().map(d=>`<option value=\"${d}\" ${device===d?'selected':''}>${counterName(d)}</option>`).join('')}"
if old_options not in html:
    raise RuntimeError('Owner sale counter options patch target not found')
html = html.replace(old_options, new_options, 1)

old_sync_access = "if(e.code===401||e.code===403){blockAccess('Your access changed or session expired. Log in again. Pending receipts remain saved.');}"
new_sync_access = "if(e.code===401){blockAccess('Your session expired or account access changed. Log in again. Pending receipts remain saved.');}else if(e.code===403){toast(e.message||'This action is not permitted for this account.');}"
if old_sync_access not in html:
    raise RuntimeError('Sync access handling patch target not found')
html = html.replace(old_sync_access, new_sync_access, 1)

old_focus_guard = "if(!document.activeElement?.dataset?.qty)renderCart();"
new_focus_guard = "if(!document.activeElement?.dataset?.qty&&!document.activeElement?.dataset?.price)renderCart();"
if old_focus_guard not in html:
    raise RuntimeError('Sale input sync guard patch target not found')
html = html.replace(old_focus_guard, new_focus_guard, 1)

html = html.replace('Select jerseys, collect payment, and issue a receipt.','Select jerseys, set the selling price, and complete the sale. Receipt is optional.',1)
html = html.replace('Complete sale & receipt','Complete sale',1)
old_search = 'placeholder="Find a club, size, colour or grade…" value="${esc(search)}" aria-label="Find jersey"'
new_search = 'placeholder="Type club, size, colour or grade…" value="${esc(search)}" aria-label="Find jersey" list="sale-product-options" autocomplete="off"'
if old_search not in html:
    raise RuntimeError('Sale search box patch target not found')
html = html.replace(old_search, new_search, 1)

css_patch = r'''
.cart-line{grid-template-columns:minmax(0,1fr) 70px 135px 38px;align-items:end}
.sale-price-label{font-size:10px}
.sale-price-label input{margin-top:3px;padding:7px}
.sale-picker-help{padding:12px 14px;border:1px dashed var(--line);border-radius:8px;color:var(--muted);background:#fbfdfe}
.product-grid{display:block}
@media(max-width:700px){.cart-line{grid-template-columns:minmax(0,1fr) 64px 118px 34px}}
'''
style_end = html.find('</style>')
if style_end < 0:
    raise RuntimeError('Unable to locate style block')
html = html[:style_end] + css_patch + '\n' + html[style_end:]

sale_patch = r'''
function saleOption(p){return `${p.club} · ${p.size} · ${p.grade} · ${p.color} · ${p.kit} · ${p.id}`}
function addSaleProduct(p){
  if(!p)return;
  const available=(p.alloc[device]||0)-(cart.find(l=>l.id===p.id)?.qty||0);
  if(available<=0){toast('No stock left for this jersey at this counter');return}
  let l=cart.find(l=>l.id===p.id);
  if(l)l.qty++;else cart.push({id:p.id,qty:1,price:p[mode],cost:p.cost});
  search='';const s=$('#search');if(s)s.value='';catalog();renderCart();
}
function catalog(){
  const input=$('#search');if(!input)return;
  const available=state.products.filter(p=>(p.alloc[device]||0)-(cart.find(l=>l.id===p.id)?.qty||0)>0);
  const matching=available.filter(matches).slice(0,8);
  $('#catalog').innerHTML=`<datalist id="sale-product-options">${available.map(p=>`<option value="${esc(saleOption(p))}">${full(p[mode])} · ${(p.alloc[device]||0)-(cart.find(l=>l.id===p.id)?.qty||0)} left</option>`).join('')}</datalist><div class="sale-picker-help">${search?`${matching.length} matching jersey${matching.length===1?'':'s'}. Choose from the suggestions above.`:'Start typing a club, size, colour, grade or code, then choose from the dropdown.'}</div>`;
  input.onchange=()=>{const q=input.value.trim().toLowerCase();const p=available.find(p=>saleOption(p).toLowerCase()===q)||available.find(p=>p.id.toLowerCase()===q);if(p)addSaleProduct(p)};
  input.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();const q=input.value.trim().toLowerCase();const exact=available.find(p=>saleOption(p).toLowerCase()===q)||available.find(p=>p.id.toLowerCase()===q);const list=available.filter(p=>Object.values(p).filter(x=>typeof x==='string').join(' ').toLowerCase().includes(q));if(exact)addSaleProduct(exact);else if(list.length===1)addSaleProduct(list[0]);}};
}
function renderCart(){
  $('#cart').innerHTML=cart.length?cart.map(l=>{const p=state.products.find(p=>p.id===l.id);return `<div class="cart-line"><span><b>${esc(p.club)}</b><br><small class="tiny">${esc(p.size+' · '+p.grade+' · '+p.color)}</small><br><small class="tiny">Suggested ${mode}: ${money(p[mode])}</small></span><input type="number" aria-label="Quantity for ${esc(p.club+' '+p.size)}" min="1" max="${p.alloc[device]}" step="1" value="${l.qty}" data-qty="${esc(l.id)}"><label class="sale-price-label">Selling price<input type="number" aria-label="Selling price for ${esc(p.club+' '+p.size)}" min="10000" max="50000" step="1000" value="${l.price}" data-price="${esc(l.id)}"></label><button class="small danger" data-remove="${esc(l.id)}" aria-label="Remove ${esc(p.club)}">×</button></div>`}).join(''):'<div class="empty">Type above and choose a jersey to start the sale.</div>';
  $$('[data-remove]').forEach(b=>b.onclick=()=>{cart=cart.filter(l=>l.id!==b.dataset.remove);catalog();renderCart()});
  $$('[data-qty]').forEach(input=>input.onchange=()=>{const l=cart.find(l=>l.id===input.dataset.qty),p=state.products.find(p=>p.id===l.id),q=Number(input.value);if(!Number.isInteger(q)||q<1||q>p.alloc[device]){toast('Choose a quantity within this counter’s allocated stock');input.value=l.qty;return}l.qty=q;catalog();renderCart()});
  $$('[data-price]').forEach(input=>input.onchange=()=>{const l=cart.find(l=>l.id===input.dataset.price),price=Number(input.value);if(!Number.isInteger(price)||price<10000||price>50000){toast('Selling price must be between UGX 10,000 and 50,000');input.value=l.price;return}l.price=price;saleTotals()});
  saleTotals();$('#complete').disabled=!cart.length;
}
function showSaleCompleted(s){
  if(!s)return;
  $('#modal').innerHTML=`<div class="panel-head"><h2>Sale completed</h2><button id="close-sale" aria-label="Close">×</button></div><div class="note"><b>${esc(s.receipt)}</b><br>The sale has been saved and stock/profit reports have been updated. Printing or downloading a receipt is optional.</div><div class="summary total"><span>Total</span><strong>${money(s.total)}</strong></div><div class="actions"><button id="close-sale-2">Close / next sale</button><button id="view-receipt">View receipt</button><button id="download-sale-receipt">Download receipt</button><button class="primary" id="print-sale-receipt">Print / save PDF</button></div>`;
  $('#modal').showModal();
  const close=()=>$('#modal').close();$('#close-sale').onclick=close;$('#close-sale-2').onclick=close;
  $('#view-receipt').onclick=()=>{close();showReceipt(s)};
  $('#print-sale-receipt').onclick=()=>{$('#print-area').innerHTML=receiptHTML(s);window.print()};
  $('#download-sale-receipt').onclick=()=>download(s.receipt+'.html','<!doctype html><html><head><meta charset="utf-8"><title>'+esc(s.receipt)+'</title><style>'+document.querySelector('style').textContent+'</style></head><body>'+receiptHTML(s)+'</body></html>','text/html');
}
async function complete(){
  if(!cart.length)return;
  const subtotal=cart.reduce((a,l)=>a+l.price*l.qty,0);
  if(cart.some(l=>!Number.isInteger(l.price)||l.price<10000||l.price>50000)){toast('Each selling price must be between UGX 10,000 and 50,000');return}
  if(!Number.isInteger(discount)||discount<0||discount>subtotal){toast('Discount must be a whole UGX amount within the subtotal');return}
  if(payment==='Credit'&&(!customer.trim()||customer.trim().toLowerCase()==='walk-in')){toast('Enter the customer name for this credit sale');return}
  $('#complete').disabled=true;
  try{
    const id=uid(),receipt='KW-'+device.replace('-T','-C')+'-'+new Date().toISOString().slice(0,10).replace(/-/g,'')+'-'+id.replace(/-/g,'').slice(0,12).toUpperCase(),data={receipt,date:now(),device,items:clone(cart),mode,discount,customer:customer.trim()||'Walk-in',payment,customerContact,staffName:user.display||user.name,amountPaid:payment==='Credit'?paidNow:undefined,tax:clone(state.tax)};
    await record({id,type:'sale',data});
    const sale=state.sales.find(s=>s.id===id);
    cart=[];discount=0;customer='';customerContact='';paidNow=0;render();showSaleCompleted(sale);
    toast(live?'Sale completed and syncing now.':'Sale completed in the local demo.');
  }catch(e){toast(e.message);$('#complete').disabled=false}
}
'''

fast_sync_patch = r'''
;(()=>{
  let kaiFastSyncBusy=false;
  async function kaiFastSync(){
    if(kaiFastSyncBusy||!navigator.onLine)return;
    try{
      if(typeof user==='undefined'||!user||typeof sync!=='function')return;
      kaiFastSyncBusy=true;
      await sync();
    }catch(_){
    }finally{
      kaiFastSyncBusy=false;
    }
  }
  setInterval(kaiFastSync,1000);
  window.addEventListener('focus',kaiFastSync);
  window.addEventListener('online',kaiFastSync);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)kaiFastSync();});
})();
'''
script_end = html.rfind('</script>')
if script_end < 0:
    raise RuntimeError('Unable to locate final script block')
html = html[:script_end] + sale_patch + '\n' + fast_sync_patch + '\n' + html[script_end:]
index.write_text(html)

print('Kai Wear deployment sources assembled; optional receipts, flexible sale pricing, searchable product picker and fast sync enabled.')
