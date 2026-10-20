const express=require('express');
const cookieParser=require('cookie-parser');
const {Pool}=require('pg');
const fetch=require('node-fetch');
const crypto=require('crypto');

const app=express();
app.use(express.json({limit:'2mb'}));
app.use(cookieParser());
app.use(express.static('public'));

const pool=new Pool({connectionString:process.env.DATABASE_URL,ssl:process.env.DATABASE_URL?{rejectUnauthorized:false}:false});
const sessions=new Set();
const PORT=process.env.PORT||3000;

async function init(){
 await pool.query(`create table if not exists messages(id bigserial primary key, channel text, contact_name text, contact_ref text, body text, intent text, created_at timestamptz default now());
 create table if not exists actions(id bigserial primary key, message_id bigint references messages(id) on delete cascade, type text, title text, draft_reply text, status text default 'pending', due_at timestamptz, created_at timestamptz default now(), resolved_at timestamptz);
 create table if not exists activity(id bigserial primary key, kind text, title text, detail text, created_at timestamptz default now());`);
}

function auth(req,res,next){
 if(req.path==='/api/login'||req.path.startsWith('/webhooks/')||req.path==='/health') return next();
 const token=req.cookies.mypa_session;
 if(!token||!sessions.has(token)) return res.status(401).json({error:'unauthorized'});
 next();
}
app.use(auth);

function classify(text){
 const t=text.toLowerCase();
 if(/urgent|emergency|asap|call me now|please call/.test(t)) return 'urgent';
 if(/meet|meeting|appointment|available|tomorrow morning|tomorrow afternoon|see you|see me/.test(t)) return 'appointment';
 if(/pay|payment|balance|deposit|ugx|\b\d+\s*k\b/.test(t)) return 'money';
 if(/remind|don't forget|dont forget|follow up|tomorrow/.test(t)) return 'reminder';
 if(/price|how much|location|where are you|open|available today/.test(t)) return 'routine';
 return 'general';
}
function suggestion(intent){
 if(intent==='urgent') return {type:'escalate',title:'Needs your attention',reply:'Your message has been marked urgent and forwarded for attention.'};
 if(intent==='appointment') return {type:'appointment',title:'Appointment request',reply:'Thanks for reaching out. I can help arrange a suitable time. What time would work best for you?'};
 if(intent==='money') return {type:'money',title:'Money-related message',reply:'Thank you for the update. I’ll make sure this is brought to attention and confirmed.'};
 if(intent==='reminder') return {type:'reminder',title:'Reminder / follow-up',reply:'Thanks. I’ll make sure this is followed up.'};
 return {type:'reply',title:'Routine conversation',reply:'Thanks for your message. I’m assisting with this and will help with the next step.'};
}

async function ingest({channel='whatsapp',name='Unknown',from='',text=''}){
 const intent=classify(text); const s=suggestion(intent);
 const m=await pool.query('insert into messages(channel,contact_name,contact_ref,body,intent) values($1,$2,$3,$4,$5) returning id',[channel,name,from,text,intent]);
 await pool.query('insert into actions(message_id,type,title,draft_reply,status) values($1,$2,$3,$4,$5)',[m.rows[0].id,s.type,s.title,s.reply,'pending']);
 return {intent,...s};
}

app.get('/health',(req,res)=>res.json({ok:true,service:'MyPA',mode:process.env.MYPA_MODE||'approval'}));
app.post('/api/login',(req,res)=>{if(String(req.body.pin||'')!==String(process.env.OWNER_PIN||'')) return res.status(401).json({error:'Wrong PIN'}); const t=crypto.randomBytes(24).toString('hex'); sessions.add(t); res.cookie('mypa_session',t,{httpOnly:true,sameSite:'lax',secure:process.env.NODE_ENV==='production',maxAge:1000*60*60*24*30}); res.json({ok:true});});
app.post('/api/logout',(req,res)=>{if(req.cookies.mypa_session)sessions.delete(req.cookies.mypa_session);res.clearCookie('mypa_session');res.json({ok:true});});

app.get('/api/home',async(req,res)=>{
 const q=await pool.query(`select a.id,a.type,a.title,a.draft_reply,a.status,a.created_at,m.contact_name,m.body,m.intent from actions a join messages m on m.id=a.message_id where a.status='pending' order by case when m.intent='urgent' then 0 when m.intent='money' then 1 else 2 end,a.created_at desc limit 20`);
 const act=await pool.query('select id,kind,title,detail,created_at from activity order by created_at desc limit 20');
 res.json({needs:q.rows,activity:act.rows});
});
app.post('/api/test/incoming',async(req,res)=>{const r=await ingest({name:req.body.name||'Test Contact',from:req.body.from||'256700000000',text:req.body.text||''});res.json(r);});
app.post('/api/actions/:id/reject',async(req,res)=>{await pool.query("update actions set status='rejected',resolved_at=now() where id=$1",[req.params.id]);res.json({ok:true});});
app.post('/api/actions/:id/approve',async(req,res)=>{
 const r=await pool.query(`select a.*,m.contact_name,m.contact_ref,m.channel from actions a join messages m on m.id=a.message_id where a.id=$1`,[req.params.id]);
 if(!r.rows[0]) return res.status(404).json({error:'Not found'});
 const item=r.rows[0]; const reply=req.body.reply||item.draft_reply; let sent=false,delivery='test-mode';
 if(item.channel==='whatsapp'&&process.env.WHATSAPP_ACCESS_TOKEN&&process.env.WHATSAPP_PHONE_NUMBER_ID&&process.env.META_GRAPH_VERSION){
   const rr=await fetch(`https://graph.facebook.com/${process.env.META_GRAPH_VERSION}/${process.env.WHATSAPP_PHONE_NUMBER_ID}/messages`,{method:'POST',headers:{Authorization:`Bearer ${process.env.WHATSAPP_ACCESS_TOKEN}`,'Content-Type':'application/json'},body:JSON.stringify({messaging_product:'whatsapp',to:item.contact_ref,type:'text',text:{body:reply}})});
   const data=await rr.json(); if(!rr.ok) return res.status(502).json({error:'WhatsApp send failed',detail:data}); sent=true;delivery=data;
 }
 await pool.query("update actions set status='approved',resolved_at=now() where id=$1",[req.params.id]);
 await pool.query('insert into activity(kind,title,detail) values($1,$2,$3)',['handled',`Handled ${item.contact_name}`,reply]);
 res.json({ok:true,sent,delivery});
});

app.get('/webhooks/whatsapp',(req,res)=>{if(req.query['hub.mode']==='subscribe'&&req.query['hub.verify_token']===process.env.WHATSAPP_VERIFY_TOKEN)return res.send(req.query['hub.challenge']);res.sendStatus(403);});
app.post('/webhooks/whatsapp',async(req,res)=>{try{for(const e of req.body.entry||[])for(const c of e.changes||[]){const v=c.value||{};const name=v.contacts?.[0]?.profile?.name||'Unknown';for(const m of v.messages||[])if(m.type==='text')await ingest({name,from:m.from,text:m.text?.body||''});}res.sendStatus(200);}catch(e){console.error(e);res.sendStatus(500);}});

app.get('*',(req,res)=>res.sendFile(require('path').join(__dirname,'public','index.html')));
init().then(()=>app.listen(PORT,()=>console.log('MyPA listening on',PORT))).catch(e=>{console.error(e);process.exit(1)});
