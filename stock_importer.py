import io, re, zipfile, xml.etree.ElementTree as ET
from pathlib import Path

ALIASES={
'id':['product code','product id','code','sku','id'],
'name':['product name','product','item name','item','description'],
'category':['category','product category'],
'club':['club / country','club/country','club','country','team'],
'grade':['version / grade','version/grade','version','grade','type'],
'kit':['home / away / third','home/away/third','kit','kit type','style'],
'season':['season'],'color':['colour','color'],'size':['size'],
'qty':['qty received','quantity received','qty','quantity','stock','units'],
'cost':['unit buying cost','actual unit buying cost','buying cost','unit cost','cost price','cost'],
'supplier':['supplier','supplier name'],
'paymentStatus':['payment status','payment','status'],
'note':['remarks','remark','notes','note'],
'minStock':['minimum stock level','minimum stock','min stock level','min stock','reorder level']}

def norm(v): return re.sub(r'\s+',' ',str(v or '').strip().lower().replace('_',' ').replace('-',' '))

def header_map(row):
    out={}
    for i,v in enumerate(row):
        h=norm(v)
        for key,names in ALIASES.items():
            if h in names and key not in out: out[key]=i
    return out

def number(v,default=0):
    try:return int(round(float(str(v).replace(',','').strip())))
    except Exception:return default

def xlsx_tables(raw):
    z=zipfile.ZipFile(io.BytesIO(raw)); ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'; relns='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    shared=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        rt=ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in rt.iter('{%s}si'%ns): shared.append(''.join(t.text or '' for t in si.iter('{%s}t'%ns)))
    wb=ET.fromstring(z.read('xl/workbook.xml')); rr=ET.fromstring(z.read('xl/_rels/workbook.xml.rels')); rels={x.attrib['Id']:x.attrib['Target'] for x in rr}
    out=[]
    for sh in wb.iter('{%s}sheet'%ns):
        title=sh.attrib.get('name','Sheet'); rid=sh.attrib.get('{%s}id'%relns); target=rels.get(rid,''); path=target if target.startswith('xl/') else 'xl/'+target.lstrip('/')
        if path not in z.namelist(): continue
        root=ET.fromstring(z.read(path)); rows=[]
        for r in root.iter('{%s}row'%ns):
            vals=[]
            for c in r.findall('{%s}c'%ns):
                ref=c.attrib.get('r','A1'); letters=re.match(r'[A-Z]+',ref); col=0
                if letters:
                    for ch in letters.group(0): col=col*26+ord(ch)-64
                    col-=1
                while len(vals)<=col: vals.append('')
                typ=c.attrib.get('t'); v=c.find('{%s}v'%ns); inline=c.find('{%s}is'%ns); val=''
                if typ=='s' and v is not None:
                    try: val=shared[int(v.text)]
                    except Exception: val=''
                elif typ=='inlineStr' and inline is not None: val=''.join(t.text or '' for t in inline.iter('{%s}t'%ns))
                elif v is not None: val=v.text or ''
                vals[col]=val
            if any(str(x).strip() for x in vals): rows.append(vals)
        out.append((title,rows))
    return out

def docx_tables(raw):
    z=zipfile.ZipFile(io.BytesIO(raw)); root=ET.fromstring(z.read('word/document.xml')); w='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'; rows=[]
    for tr in root.iter(w+'tr'):
        row=[]
        for tc in tr.findall(w+'tc'): row.append(' '.join((t.text or '').strip() for t in tc.iter(w+'t') if (t.text or '').strip()))
        if any(x.strip() for x in row): rows.append(row)
    return [('Word table',rows)]

def parse(raw,filename):
    ext=Path(filename).suffix.lower()
    tables=xlsx_tables(raw) if ext=='.xlsx' else docx_tables(raw) if ext=='.docx' else None
    if tables is None: raise ValueError('Upload an Excel .xlsx or Word .docx file')
    masters={}; stock=[]; generic=[]
    for title,rows in tables:
        hi=None; mapping=None
        for i,row in enumerate(rows[:30]):
            m=header_map(row)
            if len(m)>=3 and ('id' in m or 'name' in m): hi=i; mapping=m; break
        if mapping is None: continue
        parsed=[]
        for row in rows[hi+1:]:
            item={k:(str(row[idx]).strip() if idx<len(row) else '') for k,idx in mapping.items()}
            if item.get('id') or item.get('name'): parsed.append(item)
        lname=title.lower()
        if 'product' in lname and 'stock' not in lname:
            for item in parsed:
                if item.get('id'): masters[item['id'].lower()]=item
        elif 'stock' in lname or 'qty' in mapping: stock.extend(parsed)
        else: generic.extend(parsed)
    source=stock or generic; result=[]
    for item in source:
        row=masters.get(item.get('id','').lower(),{}).copy(); row.update({k:v for k,v in item.items() if str(v).strip()})
        row['qty']=number(row.get('qty')); row['cost']=number(row.get('cost')); row['minStock']=number(row.get('minStock'),5)
        if row['qty']<=0: continue
        if not row.get('id'):
            seed=(row.get('name') or row.get('club') or 'PRODUCT')+'-'+(row.get('size') or 'NA'); row['id']=re.sub(r'[^A-Z0-9]+','-',seed.upper()).strip('-')[:40]
        row.setdefault('name',row.get('club') or row['id']); row.setdefault('category','Other Sportswear'); row.setdefault('club',''); row.setdefault('grade','N/A'); row.setdefault('kit','N/A'); row.setdefault('season','N/A'); row.setdefault('color',''); row.setdefault('size','N/A'); row.setdefault('supplier',''); row.setdefault('paymentStatus','Unpaid'); row.setdefault('note','Imported stock')
        result.append(row)
    if not result: raise ValueError('No stock rows were recognized. Use headings such as Product Code, Product Name, Size, Qty Received and Unit Buying Cost.')
    return result[:1000]
