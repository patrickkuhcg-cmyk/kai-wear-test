from pathlib import Path

root = Path(__file__).parent
server = root / 'server.py'
s = server.read_text()

old_product = """    elif kind=='product':
        p={k:txt(data.get(k),90) for k in ['id','club','season','kit','color','size','grade']}
        if any(x['id']==p['id'] for x in s['products']):raise ValueError('Product code already exists')
        for k in ['cost','retail','wholesale']:p[k]=num(data.get(k))
        p['alloc']={d:0 for d in DEVICES};s['products'].append(p)
"""
new_product = """    elif kind=='product':
        p={k:txt(data.get(k),90) for k in ['id','name','category','club','season','kit','color','size','grade']}
        if any(x['id']==p['id'] for x in s['products']):raise ValueError('Product code already exists')
        p['minStock']=num(data.get('minStock',5),0,100000)
        for k in ['cost','retail','wholesale']:p[k]=num(data.get(k),0,1000000000)
        p['alloc']={d:0 for d in DEVICES};s['products'].append(p)
"""
if old_product in s:
    s = s.replace(old_product, new_product, 1)
elif new_product not in s:
    raise RuntimeError('Excel product-model server target not found')

old_move = """        p['alloc'][d]+=q;s['movements'].append(dict(id=e['id'],product=p['id'],device=d,qty=q,cost=batch_cost,date=date(data.get('date')),note=txt(data.get('note','Stock received'),150)))"""
new_move = """        p['alloc'][d]+=q;s['movements'].append(dict(id=e['id'],product=p['id'],device=d,qty=q,cost=batch_cost,date=date(data.get('date')),supplier=txt(data.get('supplier',''),90),paymentStatus=txt(data.get('paymentStatus',''),40),note=txt(data.get('note','Stock received'),150)))"""
if old_move in s:
    s = s.replace(old_move, new_move, 1)
elif new_move not in s:
    raise RuntimeError('Excel stock-in movement target not found')

if 'def migrate_excel_inventory_state():' not in s:
    marker='def password_hash(p,s):'
    if marker not in s:
        raise RuntimeError('Unable to install Excel inventory migration')
    migration = '''def migrate_excel_inventory_state():
    with conn() as c:
        row=c.execute('SELECT payload FROM state WHERE id=1').fetchone()
        if not row:return
        data=json.loads(row[0]);changed=False
        for p in data.get('products',[]):
            grade=str(p.get('grade') or '').strip()
            if grade=='Replica':
                p['grade']='Fan/Net Version';grade='Fan/Net Version';changed=True
            if not p.get('category'):
                if grade=='Original':cat='Original Jerseys'
                elif grade=='Fan/Net Version':cat='Fan/Net Version Jerseys'
                elif grade=='Copy':cat='Copy Jerseys'
                elif grade=='Vintage':cat='Vintage Jerseys'
                elif str(p.get('size') or '').startswith('Kids '):cat="Children's Jersey Sets"
                else:cat='Other Sportswear'
                p['category']=cat;changed=True
            if not p.get('name'):
                bits=[str(p.get('club') or '').strip(),str(p.get('kit') or '').strip(),'Jersey',str(p.get('season') or '').strip()]
                p['name']=' '.join(x for x in bits if x and x!='N/A').strip();changed=True
            if p.get('season')=='2026/27':p['season']='2026/2027';changed=True
            if p.get('season')=='2025/26':p['season']='2025/2026';changed=True
            if 'minStock' not in p:p['minStock']=5;changed=True
        if changed:
            data['revision']=int(data.get('revision',0))+1
            c.execute('UPDATE state SET payload=? WHERE id=1',(json.dumps(data),))

'''
    s=s.replace(marker,migration+marker,1)

server.write_text(s)
print('Kai Wear Excel inventory data model enabled.')
