from pathlib import Path
import re

root=Path(__file__).parent
index=root/'static'/'index.html'
html=index.read_text()

# The legacy logout guard treats the app's internal `live` sync flag as if it
# were the browser's network status. That can stay false/stale even when the
# user is online and there are no unsynced records. Change only the connection
# part of the logout guard; preserve any pending/outbox checks in the same
# condition.
message_re=r"Reconnect before logging out"
changed=0

# Match a compact JS if-block containing the exact logout warning, then replace
# only !live in its condition with the browser's actual online state.
pat=re.compile(r"if\((?P<cond>[^\n{}]{1,320})\)\s*\{(?P<body>[^{}]{0,420}Reconnect before logging out[^{}]{0,420})\}")

def repl(m):
    global changed
    cond=m.group('cond')
    new_cond=re.sub(r'!\s*live\b','!navigator.onLine',cond)
    if new_cond==cond:
        return m.group(0)
    changed+=1
    return f"if({new_cond}){{{m.group('body')}}}"

html=pat.sub(repl,html)

# Handle terse one-line forms without braces, if present.
pat2=re.compile(r"if\((?P<cond>[^\n;]{1,260})\)\s*(?P<body>(?:toast|alert)\([^;]*Reconnect before logging out[^;]*;\s*return(?:\s+false)?;?)")
def repl2(m):
    global changed
    cond=m.group('cond')
    new_cond=re.sub(r'!\s*live\b','!navigator.onLine',cond)
    if new_cond==cond:
        return m.group(0)
    changed+=1
    return f"if({new_cond}){m.group('body')}"
html=pat2.sub(repl2,html)

# Runtime safety net: before an attempted logout, ask the existing sync routine
# to refresh the connection state once. We do not perform or fake the logout;
# the app's original handler remains authoritative.
script=r'''
<script id="kai-logout-guard-refresh">
(()=>{
  let refreshing=false;
  const isLogout=el=>{
    const b=el?.closest?.('button,a');if(!b)return null;
    const t=(b.textContent||'').trim().toLowerCase();
    return (t==='logout'||t==='log out'||/\blog\s*out\b/.test(t))?b:null;
  };
  document.addEventListener('click',async e=>{
    const b=isLogout(e.target);if(!b||refreshing||!navigator.onLine||typeof sync!=='function')return;
    // Let the normal handler run when state is already current. If the app is
    // stale/offline internally, one successful sync will refresh it before the
    // next user click, without altering pending data or session semantics.
    try{refreshing=true;await sync()}catch(_){ }finally{refreshing=false}
  },true);
})();
</script>
'''
pos=html.rfind('</body>')
if pos<0:raise RuntimeError('Final body tag not found')
html=html[:pos]+script+'\n'+html[pos:]
index.write_text(html)
print(f'Kai Wear logout guard fixed: {changed} legacy connection guard(s) now use navigator.onLine; pending checks preserved.')
