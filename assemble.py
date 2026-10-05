from pathlib import Path
import base64, io, zipfile

root = Path(__file__).parent
parts = root / '.deploy_payload'
names = ['payload.part01','payload.part02','payload.part03a','payload.part03b','payload.part03c','payload.part04']
files = [parts / name for name in names]
if not all(p.exists() for p in files):
    raise RuntimeError('Kai Wear deployment payload is missing')
payload = ''.join(p.read_text().strip() for p in files)
with zipfile.ZipFile(io.BytesIO(base64.b64decode(payload))) as z:
    z.extractall(root)

server = root / 'server.py'
s = server.read_text()
owner_guard = """                    if data.get('type')=='sale' and u['role']=='owner':
                        with conn() as c:binding=c.execute('SELECT installation FROM counters WHERE device=?',(data.get('data',{}).get('device'),)).fetchone()
                        if not binding or not binding[0] or binding[0]!=u.get('installation') or self.installation()!=u.get('installation'):return self.send_json({'error':'Owner sales require this browser to be assigned to that counter. Log in as its cashier first.'},403)
"""
if owner_guard in s:
    s = s.replace(owner_guard, '', 1)
old_price = """            # Prices and standard unit costs are checked against the server.
            if item.get('price')!=p[mode]:raise ValueError('Price changed. Review this offline receipt.')
            price=p[mode];subtotal+=price*q"""
new_price = """            # Selling price is entered for the individual transaction; there is no fixed sale price.
            price=num(item.get('price'),1,1000000000);subtotal+=price*q"""
if old_price not in s:
    raise RuntimeError('Flexible sale-price server target not found')
s = s.replace(old_price, new_price, 1)
old_restock = """    elif kind=='restock':
        p=next((p for p in s['products'] if p['id']==data.get('id')),None);d=data.get('device');q=num(data.get('qty'),1,100000)
        if not p or d not in DEVICES:raise ValueError('Choose a product and counter')
        p['alloc'][d]+=q;s['movements'].append(dict(id=e['id'],product=p['id'],device=d,qty=q,date=date(data.get('date')),note=txt(data.get('note','Stock received'),150)))"""
new_restock = """    elif kind=='restock':
        p=next((p for p in s['products'] if p['id']==data.get('id')),None);d=data.get('device');q=num(data.get('qty'),1,100000)
        if not p or d not in DEVICES:raise ValueError('Choose a product and counter')
        batch_cost=num(data.get('cost'),0,1000000000)
        existing=sum(int(v or 0) for v in p.get('alloc',{}).values())
        if existing+q>0:p['cost']=int(round(((p.get('cost',0)*existing)+(batch_cost*q))/(existing+q)))
        p['alloc'][d]+=q;s['movements'].append(dict(id=e['id'],product=p['id'],device=d,qty=q,cost=batch_cost,date=date(data.get('date')),note=txt(data.get('note','Stock received'),150)))"""
if old_restock not in s:
    raise RuntimeError('Flexible receiving-cost server target not found')
s = s.replace(old_restock, new_restock, 1)
server.write_text(s)

index = root / 'static' / 'index.html'
html = index.read_text()
old_login = """<label>${setup?'Owner password (10+ characters)':'Password / counter code'}<input name="password" type="password" autocomplete="${setup?'new-password':'current-password'}" required ${setup?'minlength="10"':''}></label>"""
new_login = """<label>${setup?'Owner password (10+ characters)':'Password / counter code'}<span style="position:relative;display:block"><input id="auth-password" name="password" type="password" autocomplete="${setup?'new-password':'current-password'}" required ${setup?'minlength="10"':''} style="padding-right:48px;width:100%"><button type="button" id="toggle-password" aria-label="Show password" title="Show password" style="position:absolute;right:8px;top:50%;transform:translateY(-50%);border:0;background:transparent;padding:6px;cursor:pointer;font-size:18px;line-height:1">👁</button></span></label>"""
if old_login in html:
    html = html.replace(old_login, new_login, 1)
old_hook = "$('#export-pending').onclick=exportPending;$('#login-form').onsubmit=async e=>"
new_hook = "$('#export-pending').onclick=exportPending;$('#toggle-password').onclick=()=>{const p=$('#auth-password'),b=$('#toggle-password'),show=p.type==='password';p.type=show?'text':'password';b.textContent=show?'🙈':'👁';b.setAttribute('aria-label',show?'Hide password':'Show password');b.title=show?'Hide password':'Show password'};$('#login-form').onsubmit=async e=>"
if old_hook in html:
    html = html.replace(old_hook, new_hook, 1)
html = html.replace("function canSell(){return user.role==='cashier'||(owner()&&(!live||user.saleDevices?.length>0))}", "function canSell(){return user.role==='cashier'||owner()}", 1)
html = html.replace("if(page==='New sale'){if(!owner())device=user.device||user.name;else if(live&&!user.saleDevices?.includes(device))device=user.saleDevices?.[0]||device;", "if(page==='New sale'){if(!owner())device=user.device||user.name;else if(live&&!allowedDevices().includes(device))device=(allowedDevices()[0]||device);", 1)
html = html.replace("${(live&&owner()?user.saleDevices:allowedDevices()).map(d=>`<option value=\"${d}\" ${device===d?'selected':''}>${counterName(d)}</option>`).join('')}", "${allowedDevices().map(d=>`<option value=\"${d}\" ${device===d?'selected':''}>${counterName(d)}</option>`).join('')}", 1)
html = html.replace("if(e.code===401||e.code===403){blockAccess('Your access changed or session expired. Log in again. Pending receipts remain saved.');}", "if(e.code===401){blockAccess('Your session expired or account access changed. Log in again. Pending receipts remain saved.');}else if(e.code===403){toast(e.message||'This action is not permitted for this account.');}", 1)
html = html.replace("if(!document.activeElement?.dataset?.qty)renderCart();", "if(!document.activeElement?.dataset?.qty&&!document.activeElement?.dataset?.price)renderCart();", 1)
html = html.replace('Select jerseys, collect payment, and issue a receipt.','Search a jersey, enter the actual selling price, and complete the sale. Receipt is optional.',1)
html = html.replace('Complete sale & receipt','Complete sale',1)
html = html.replace('placeholder="Find a club, size, colour or grade…" value="${esc(search)}" aria-label="Find jersey"', 'placeholder="Search jersey: club, code, size, colour, grade…" value="${esc(search)}" aria-label="Find jersey" autocomplete="off"', 1)
css_patch = r'''
.cart-line{grid-template-columns:minmax(0,1fr) 72px 145px 38px;align-items:end}
.sale-price-label{font-size:10px}.sale-price-label input{margin-top:3px;padding:7px}
.sale-results{display:grid;gap:6px;margin-top:8px;max-height:330px;overflow:auto}
.sale-result{width:100%;text-align:left;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:#fff;color:inherit}
.sale-result:hover,.sale-result:focus{border-color:var(--accent);background:#f7fcfd}.sale-result small{color:var(--muted)}
.sale-picker-help{padding:10px 12px;border:1px dashed var(--line);border-radius:8px;color:var(--muted);background:#fbfdfe}
@media(max-width:700px){.cart-line{grid-template-columns:minmax(0,1fr) 62px 116px 34px}.sale-result{grid-template-columns:1fr}}
'''
style_end = html.find('</style>')
if style_end < 0: raise RuntimeError('Style block not found')
html = html[:style_end] + css_patch + '\n' + html[style_end:]
patch = r'''
function saleSearchText(p){return `${p.id} ${p.club} ${p.season} ${p.kit} ${p.color} ${p.size} ${p.grade}`.toLowerCase()}
function addSaleProduct(p){if(!p)return;const available=(p.alloc[device]||0)-(cart.find(l=>l.id===p.id)?.qty||0);if(available<=0){toast('No stock left for this jersey at this counter');return}let l=cart.find(l=>l.id===p.id);if(l)l.qty++;else cart.push({id:p.id,qty:1,price:'',cost:p.cost});search='';const input=$('#search');if(input)input.value='';catalog();renderCart()}
function catalog(){const input=$('#search');if(!input)return;const q=(input.value||search||'').trim().toLowerCase();search=input.value||'';const available=state.products.filter(p=>(p.alloc[device]||0)-(cart.find(l=>l.id===p.id)?.qty||0)>0);const matching=(q?available.filter(p=>saleSearchText(p).includes(q)):available).slice(0,12);$('#catalog').innerHTML=`<div class="sale-picker-help">${q?`${matching.length} match${matching.length===1?'':'es'} — click the jersey you want.`:'Type in the search box, or choose from the available jerseys below.'}</div><div class="sale-results">${matching.map(p=>{const left=(p.alloc[device]||0)-(cart.find(l=>l.id===p.id)?.qty||0);return `<button type="button" class="sale-result" data-sale-pick="${esc(p.id)}"><span><b>${esc(p.club)}</b><br><small>${esc(p.id+' · '+p.size+' · '+p.grade+' · '+p.color+' · '+p.kit)}</small></span><span class="badge">${left} in stock</span></button>`}).join('')||'<div class="empty">No matching jersey in stock at this counter.</div>'}</div>`;$$('[data-sale-pick]').forEach(b=>b.onclick=()=>addSaleProduct(state.products.find(p=>p.id===b.dataset.salePick)));input.oninput=e=>{search=e.target.value;catalog()};input.onkeydown=e=>{if(e.key==='Enter'&&matching.length){e.preventDefault();addSaleProduct(matching[0])}}}
function renderCart(){$('#cart').innerHTML=cart.length?cart.map(l=>{const p=state.products.find(p=>p.id===l.id);return `<div class="cart-line"><span><b>${esc(p.club)}</b><br><small class="tiny">${esc(p.id+' · '+p.size+' · '+p.grade+' · '+p.color)}</small><br><small class="tiny">Avg cost: ${owner()?money(p.cost):'hidden'}</small></span><input type="number" aria-label="Quantity for ${esc(p.club+' '+p.size)}" min="1" max="${p.alloc[device]}" step="1" value="${l.qty}" data-qty="${esc(l.id)}"><label class="sale-price-label">Actual selling price<input type="number" aria-label="Selling price for ${esc(p.club+' '+p.size)}" min="1" step="1" value="${l.price}" placeholder="Enter price" data-price="${esc(l.id)}"></label><button class="small danger" data-remove="${esc(l.id)}" aria-label="Remove ${esc(p.club)}">×</button></div>`}).join(''):'<div class="empty">Search above and choose a jersey to start the sale.</div>';$$('[data-remove]').forEach(b=>b.onclick=()=>{cart=cart.filter(l=>l.id!==b.dataset.remove);catalog();renderCart()});$$('[data-qty]').forEach(input=>input.onchange=()=>{const l=cart.find(l=>l.id===input.dataset.qty),p=state.products.find(p=>p.id===l.id),q=Number(input.value);if(!Number.isInteger(q)||q<1||q>p.alloc[device]){toast('Choose a quantity within this counter’s available stock');input.value=l.qty;return}l.qty=q;catalog();renderCart()});$$('[data-price]').forEach(input=>input.oninput=()=>{const l=cart.find(l=>l.id===input.dataset.price);l.price=input.value===''?'':Number(input.value);saleTotals()});saleTotals();$('#complete').disabled=!cart.length}
function showSaleCompleted(s){if(!s)return;$('#modal').innerHTML=`<div class="panel-head"><h2>Sale completed</h2><button id="close-sale" aria-label="Close">×</button></div><div class="note"><b>${esc(s.receipt)}</b><br>Sale saved. Stock and profit reports are updated. Receipt printing is optional.</div><div class="summary total"><span>Total</span><strong>${money(s.total)}</strong></div><div class="actions"><button id="close-sale-2">Close / next sale</button><button id="view-receipt">View receipt</button><button id="download-sale-receipt">Download receipt</button><button class="primary" id="print-sale-receipt">Print / save PDF</button></div>`;$('#modal').showModal();const close=()=>$('#modal').close();$('#close-sale').onclick=close;$('#close-sale-2').onclick=close;$('#view-receipt').onclick=()=>{close();showReceipt(s)};$('#print-sale-receipt').onclick=()=>{$('#print-area').innerHTML=receiptHTML(s);window.print()};$('#download-sale-receipt').onclick=()=>download(s.receipt+'.html','<!doctype html><html><head><meta charset="utf-8"><title>'+esc(s.receipt)+'</title><style>'+document.querySelector('style').textContent+'</style></head><body>'+receiptHTML(s)+'</body></html>','text/html')}
async function complete(){if(!cart.length)return;if(cart.some(l=>!Number.isInteger(Number(l.price))||Number(l.price)<=0)){toast('Enter the actual selling price for every jersey');return}cart.forEach(l=>l.price=Number(l.price));const subtotal=cart.reduce((a,l)=>a+l.price*l.qty,0);if(!Number.isInteger(discount)||discount<0||discount>subtotal){toast('Discount must be a whole UGX amount within the subtotal');return}if(payment==='Credit'&&(!customer.trim()||customer.trim().toLowerCase()==='walk-in')){toast('Enter the customer name for this credit sale');return}$('#complete').disabled=true;try{const id=uid(),receipt='KW-'+device.replace('-T','-C')+'-'+new Date().toISOString().slice(0,10).replace(/-/g,'')+'-'+id.replace(/-/g,'').slice(0,12).toUpperCase(),data={receipt,date:now(),device,items:clone(cart),mode,discount,customer:customer.trim()||'Walk-in',payment,customerContact,staffName:user.display||user.name,amountPaid:payment==='Credit'?paidNow:undefined,tax:clone(state.tax)};await record({id,type:'sale',data});const sale=state.sales.find(s=>s.id===id);cart=[];discount=0;customer='';customerContact='';paidNow=0;render();showSaleCompleted(sale);toast(live?'Sale completed and syncing now.':'Sale completed in the local demo.')}catch(e){toast(e.message);$('#complete').disabled=false}}
function newStockCode(club,size){return ('J-'+String(club||'ITEM').replace(/[^a-z0-9]/gi,'').slice(0,10)+'-'+String(size||'NA').replace(/[^a-z0-9]/gi,'').slice(0,5)+'-'+Date.now().toString(36)).toUpperCase()}
function restock(){const existingOptions=state.products.map(p=>`<option value="${esc(p.id)}">${esc(p.id+' · '+productLabel(p)+' · '+p.color)}</option>`).join('');showForm('Receive new stock',`<div class="full note"><b>Add inventory here.</b><br>Choose an existing jersey to add more units, or choose New jersey / variant to create it and receive its first stock.</div><label class="full">Stock type<select name="kind"><option value="existing">Existing jersey / variant</option><option value="new">New jersey / variant</option></select></label><label class="full">Existing jersey<select name="id"><option value="">-- choose existing jersey --</option>${existingOptions}</select></label><label>Product code (new item)<input name="newId" type="text" placeholder="Leave blank to auto-create"></label><label>Club / team<input name="club" type="text" placeholder="e.g. Arsenal"></label><label>Season<input name="season" type="text" placeholder="e.g. 2026/27"></label><label>Kit<input name="kit" type="text" placeholder="Home / Away / Third"></label><label>Colour<input name="color" type="text"></label><label>Size<input name="size" type="text" placeholder="S / M / L / XL"></label><label>Originality / grade<input name="grade" type="text" placeholder="Replica / Original / other"></label><label>Counter allocation<select name="device">${allowedDevices().map(d=>`<option value="${d}">${counterName(d)}</option>`).join('')}</select></label><label>Quantity received<input name="qty" type="number" min="1" step="1" value="1" required></label><label>Actual buying cost per jersey (UGX)<input name="cost" type="number" min="0" step="1" placeholder="Enter this batch cost" required></label><label class="full">Supplier / note<input name="note" type="text" value="Stock received" required></label>`,async f=>{const v=Object.fromEntries(f),qty=Number(v.qty),cost=Number(v.cost);if(!Number.isInteger(qty)||qty<1)throw new Error('Enter the quantity received');if(!Number.isInteger(cost)||cost<0)throw new Error('Enter the actual buying cost for this batch');let id=v.id;if(v.kind==='new'){for(const k of ['club','season','kit','color','size','grade'])if(!String(v[k]||'').trim())throw new Error('Complete the new jersey details');id=String(v.newId||'').trim()||newStockCode(v.club,v.size);await onlineEvent('product',{id,club:v.club.trim(),season:v.season.trim(),kit:v.kit.trim(),color:v.color.trim(),size:v.size.trim(),grade:v.grade.trim(),cost,retail:0,wholesale:0})}else if(!id)throw new Error('Choose the existing jersey');await onlineEvent('restock',{id,device:v.device,qty,cost,date:now(),note:v.note||'Stock received'})})}
function addProduct(){restock()}
'''
fast_sync = r'''
;(()=>{let busy=false;async function go(){if(busy||!navigator.onLine)return;try{if(typeof user==='undefined'||!user||typeof sync!=='function')return;busy=true;await sync()}catch(_){}finally{busy=false}}setInterval(go,1000);window.addEventListener('focus',go);window.addEventListener('online',go);document.addEventListener('visibilitychange',()=>{if(!document.hidden)go()})})();
'''
script_end = html.rfind('</script>')
if script_end < 0: raise RuntimeError('Final script block not found')
html = html[:script_end] + patch + '\n' + fast_sync + '\n' + html[script_end:]
index.write_text(html)
print('Kai Wear deployment sources assembled; flexible batch cost, flexible sale price, inventory receiving, working search/dropdown and fast sync enabled.')
