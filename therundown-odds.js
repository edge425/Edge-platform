// EDGE secure odds feed. Never expose the upstream key or raw response.
const SPORTS = {NFL:2, MLB:3, NBA:4, NCAAB:5, NHL:6, NCAAF:1};
const BOOKS = {19:'DraftKings',23:'FanDuel',22:'BetMGM'};
const cache = new Map();
const allowed = (s) => String(s||'').slice(0,30);
function quote(p,book){
 for(const line of p.lines||[]){const q=line.prices?.[book];
  if(!q || q.closed_at || q.price==null || Number(q.price)===0.0001)continue;
  return {price:Number(q.price),line:line.value,updatedAt:q.updated_at||null};
 }return null;
}
function parseEvent(e,sport){
 const teams=e.teams||[];const away=teams.find(t=>t.is_away)||teams[0],home=teams.find(t=>t.is_home)||teams[1];
 if(!away||!home)return null;
 const markets=new Map((e.markets||[]).map(m=>[Number(m.market_id),m]));
 const out={id:String(e.event_id),sport,away:[away.name,away.mascot].filter(Boolean).join(' '),home:[home.name,home.mascot].filter(Boolean).join(' '),date:e.event_date,status:e.score?.event_status||'Scheduled',books:{}};
 for(const [book,name] of Object.entries(BOOKS)){
  const bookOut={name,ml:[null,null],spread:[null,null],total:[null,null]};
  for(const [marketId,key] of [[1,'ml'],[2,'spread'],[3,'total']]){
   for(const p of markets.get(marketId)?.participants||[]){
    let idx=-1;
    if(marketId===3){idx=Number(p.id)===9||String(p.name).toLowerCase()==='over'?0:Number(p.id)===10||String(p.name).toLowerCase()==='under'?1:-1}
    else {idx=String(p.id)===String(away.team_id)?0:String(p.id)===String(home.team_id)?1:-1}
    if(idx!==-1)bookOut[key][idx]=quote(p,book);
   }
  }
  if([...bookOut.ml,...bookOut.spread,...bookOut.total].some(Boolean))out.books[book]=bookOut;
 }
 return out;
}
exports.handler=async(event)=>{
 const sport=allowed(event.queryStringParameters?.sport||'NBA');
 if(!SPORTS[sport])return {statusCode:400,body:JSON.stringify({error:'Unsupported sport'})};
 const key=process.env.THERUNDOWN_API_KEY;
 if(!key)return {statusCode:503,body:JSON.stringify({error:'API key not configured'})};
 const today=new Date().toISOString().slice(0,10);
 const cacheKey=`${sport}:${today}`;const hit=cache.get(cacheKey);
 if(hit && Date.now()-hit.time<300000)return {statusCode:200,headers:{'Content-Type':'application/json','Cache-Control':'public, max-age=240'},body:hit.body};
 try{
  const url=`https://therundown.io/api/v2/sports/${SPORTS[sport]}/events/${today}?market_ids=1%2C2%2C3&affiliate_ids=19%2C23%2C22&main_line=true`;
  const response=await fetch(url,{headers:{'X-TheRundown-Key':key,'Accept':'application/json'}});
  if(!response.ok)return {statusCode:502,headers:{'Content-Type':'application/json'},body:JSON.stringify({error:`Odds provider returned ${response.status}`})};
  const raw=await response.json();
  const result={sport,asOf:new Date().toISOString(),delayed:true,events:(raw.events||[]).map(e=>parseEvent(e,sport)).filter(Boolean)};
  const body=JSON.stringify(result);cache.set(cacheKey,{time:Date.now(),body});
  return {statusCode:200,headers:{'Content-Type':'application/json','Cache-Control':'public, max-age=240'},body};
 }catch(err){return {statusCode:502,headers:{'Content-Type':'application/json'},body:JSON.stringify({error:'Unable to retrieve sportsbook odds'})}}
};
