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
if old_product not in s:
    raise RuntimeError('Excel product-model server target not found')
s = s.replace(old_product, new_product, 1)

old_move = """        p['alloc'][d]+=q;s['movements'].append(dict(id=e['id'],product=p['id'],device=d,qty=q,cost=batch_cost,date=date(data.get('date')),note=txt(data.get('note','Stock received'),150)))"""
new_move = """        p['alloc'][d]+=q;s['movements'].append(dict(id=e['id'],product=p['id'],device=d,qty=q,cost=batch_cost,date=date(data.get('date')),supplier=txt(data.get('supplier',''),90),paymentStatus=txt(data.get('paymentStatus',''),40),note=txt(data.get('note','Stock received'),150)))"""
if old_move not in s:
    raise RuntimeError('Excel stock-in movement target not found')
s = s.replace(old_move, new_move, 1)

server.write_text(s)
print('Kai Wear Excel inventory data model enabled.')
