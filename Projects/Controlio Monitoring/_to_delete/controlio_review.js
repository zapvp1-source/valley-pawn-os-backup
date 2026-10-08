// Controlio weekly review — paste into the built-in browser (Claude_Browser javascript_tool) while on app.controlio.net (signed in).
// Uses the dashboard's own signed-in session; no API plan or token handling needed. Returns a compact JSON summary.
// Set window.__START / window.__END (YYYY-MM-DD) before running, else defaults to last 7 days.
(async () => {
  const tok = localStorage.getItem('we.token'); if (!tok) return {error: 'NOT_SIGNED_IN'};
  const H = {headers: {Authorization: 'Bearer ' + tok}}, B = 'https://backend.controlio.net/api/v1/';
  const end = window.__END || new Date().toISOString().slice(0,10);
  const start = window.__START || new Date(Date.now()-7*864e5).toISOString().slice(0,10);
  async function j(p){ for (let a=0;a<5;a++){ try{ const r=await fetch(B+p,H); if(r.status===401) return {error:'NOT_SIGNED_IN'}; if(r.ok) return await r.json(); }catch(e){} await new Promise(s=>setTimeout(s,1500*(a+1))); } return {data:[],error:'FETCH_FAIL '+p}; }
  const users=(await j('users?limit=1000')).data||[], comps=(await j('computers?limit=1000')).data||[], cats=(await j('categories?limit=1000')).data||[];
  const q=`start_time=${start}&end_time=${end}`; const acts=(await j('statistics/activities?'+q+'&limit=10000')).data||[];
  const STORE={CUSTOMER:'Culpeper','DESKTOP-8AQ6MAG':'Culpeper','DESKTOP-3A145AR':'Culpeper',ROANOKE1:'Roanoke',ROANOKE2:'Roanoke','DESKTOP-24O21VQ':'Roanoke',LEX1:'Lexington',LEX2:'Lexington',HARRISONBURG1:'Harrisonburg',HARRISONBURG2:'Harrisonburg',BORO1:'Waynesboro',BORO2:'Waynesboro','DESKTOP-RCLD341':'Waynesboro'};
  const comp={}; comps.forEach(c=>comp[c.id]={name:c.name,store:STORE[c.name]||'UNMAPPED',last:c.last_upload_time,deleted:c.deleted});
  const cat={}; cats.forEach(c=>cat[c.id]=c.name); const act={}; acts.forEach(a=>act[a.activity_id]={n:a.activity_name,c:cat[a.category_id]||'?'});
  const et=s=>new Date(new Date(s.replace(/\.\d+$/,'')+'Z').getTime()-4*3600e3); // EDT; switch to -5 after first Sunday of November
  const closed=(store,d)=>{const w=d.getUTCDay(), ds=d.toISOString().slice(0,10); if(w===0)
