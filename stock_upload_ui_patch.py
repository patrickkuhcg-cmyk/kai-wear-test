from pathlib import Path

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

css=r'''
<style id="kai-stock-upload-style">
.kai-upload-box{grid-column:1/-1;border:1px dashed #9fc8d2;border-radius:12px;background:#f7fcfd;padding:12px;margin-bottom:4px}
.kai-upload-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}.kai-upload-head b{color:#173f4a}.kai-upload-help{font-size:11px;color:var(--muted);line-height:1.45;margin-top:4px}
.kai-upload-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.kai-upload-actions input[type=file]{max-width:100%;font-size:12px}
.kai-import-preview{margin-top:10px;max-height:250px;overflow:auto;border:1px solid #dce9ed;border-radius:9px;background:white}.kai-import-preview table{margin:0;min-width:780px}.kai-import-status{font-size:12px;margin-top:8px;color:#315763}.kai-import-status.error{color:#a32b2b}
</style>
'''

js=r'''
<script id="kai-stock-upload-script">
(()=>{
 let importRows=[];
 const oldRestock=restock;
 function toBase64(buffer){const bytes=new Uint8Array(buffer);let binary='';for(let i=0;i<bytes.length;i+=32768)binary+=String.fromCharCode(...bytes.subarray(i,Math.min(i+32768,bytes.length)));return btoa(binary)}
 function preview(rows){
   const box=document.querySelector('#kai-import-preview');if(!box)return;
   const shown=rows.slice(0,30);
   box.innerHTML=`<table><thead><tr><th>Code</th><th>Product</th><th>Category</th><th>Version</th><th>Size</th><th class="end">Qty</th><th class="end">Buying cost</th><th>Supplier</th></tr></thead><tbody>${shown.map(r=>`<tr><td>${esc(r.id||'')}</td><td>${esc(r.name||r.club||'')}</td><td>${esc(r.category||'')}</td><td>${esc(r.grade||'')}</td><td>${esc(r.size||'')}</td><td class="end">${Number(r.qty||0)}</td><td class="end">${money(Number(r.cost||0))}</td><td>${esc(r.supplier||'')}</td></tr>`).join('')}</tbody></table>${rows.length>shown.length?`<div class="tiny" style="padding:8px">Showing first ${shown.length} of ${rows.length} rows.</div>`:''}`;
 }
 async function readImport(){
   const file=document.querySelector('#kai-stock-file')?.files?.[0],status=document.querySelector('#kai-import-status'),btn=document.querySelector('#kai-read-file');
   if(!file){status.textContent='Choose an Excel (.xlsx) or Word (.docx) file first.';status.className='kai-import-status error';return}
   if(file.size>8*1024*1024){status.textContent='File is too large. Maximum import size is 8 MB.';status.className='kai-import-status error';return}
   btn.disabled=true;status.textContent='Reading and checking the file…';status.className='kai-import-status';
   try{
     const content=toBase64(await file.arrayBuffer());const result=await api('import-stock-preview',{filename:file.name,content});importRows=result.rows||[];preview(importRows);
     status.textContent=`${importRows.length} stock row${importRows.length===1?'':'s'} recognized. Review the preview, choose the destination counter below, then import.`;
     document.querySelector('#kai-import-file').disabled=!importRows.length;
   }catch(e){importRows=[];status.textContent=e.message;status.className='kai-import-status error';document.querySelector('#kai-import-file').disabled=true}
   finally{btn.disabled=false}
 }
 async function commitImport(){
   const status=document.querySelector('#kai-import-status'),btn=document.querySelector('#kai-import-file'),device=document.querySelector('#dialog-form [name="device"]')?.value;
   if(!importRows.length)return;if(!device){status.textContent='Choose the destination counter.';status.className='kai-import-status error';return}
   btn.disabled=true;status.textContent=`Adding ${importRows.length} rows to stock…`;status.className='kai-import-status';
   try{const r=await api('import-stock-commit',{device,rows:importRows});await sync();status.textContent=`Import complete: ${r.imported} stock rows added; ${r.created} new product variants created.`;toast('Stock file imported successfully');importRows=[];document.querySelector('#kai-import-file').disabled=true;setTimeout(()=>{document.querySelector('#modal')?.close();render()},700)}catch(e){status.textContent=e.message;status.className='kai-import-status error';btn.disabled=false}
 }
 function attachUpload(){
   const form=document.querySelector('#dialog-form');if(!form||form.querySelector('#kai-stock-upload'))return;const forms=form.querySelector('.forms');if(!forms)return;
   const box=document.createElement('div');box.id='kai-stock-upload';box.className='kai-upload-box';box.innerHTML=`<div class="kai-upload-head"><div><b>Upload stock file</b><div class="kai-upload-help">Import Excel <b>.xlsx</b> or Word <b>.docx</b>. Kai Wear recognizes Product Code, Product Name, Category, Club/Country, Version/Grade, Kit, Season, Size, Qty Received, Unit Buying Cost, Supplier, Payment Status and Remarks. Excel workbooks with separate <b>Products</b> and <b>StockIn</b> sheets are joined automatically by Product Code.</div></div></div><div class="kai-upload-actions"><input id="kai-stock-file" type="file" accept=".xlsx,.docx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.openxmlformats-officedocument.wordprocessingml.document"><button id="kai-read-file" type="button">Read & preview</button><button id="kai-import-file" type="button" class="primary" disabled>Import recognized stock</button></div><div id="kai-import-status" class="kai-import-status">Or continue below to enter one stock delivery manually.</div><div id="kai-import-preview" class="kai-import-preview" style="display:none"></div>`;
   forms.prepend(box);const previewBox=box.querySelector('#kai-import-preview');const observer=new MutationObserver(()=>{previewBox.style.display=previewBox.innerHTML?'block':'none'});observer.observe(previewBox,{childList:true,subtree:true});box.querySelector('#kai-read-file').onclick=readImport;box.querySelector('#kai-import-file').onclick=commitImport;
 }
 restock=function(){importRows=[];oldRestock();setTimeout(attachUpload,20)};
 addProduct=function(){restock()};
})();
</script>
'''
body=html.rfind('</body>')
if body<0:raise RuntimeError('Final body tag not found for stock upload UI')
html=html[:body]+css+'\n'+js+'\n'+html[body:]
index.write_text(html)
print('Kai Wear stock file upload UI enabled.')
