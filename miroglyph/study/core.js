(function(root){
'use strict';
const DEFAULT_ID='object.sampling-theorem',MAX_ROUTE=100;
function related(data,id){
 const records=new Map(data.records.map(r=>[r.id,r])),out=new Map();
 for(const e of data.edges){if(e.from!==id&&e.to!==id)continue;const forward=e.from===id,other=records.get(forward?e.to:e.from);if(!other)continue;
 let category,label;
 if(forward&&e.field==='source'){category='sources';label='Source cited';}
 else if(!forward&&e.field==='source'){category='next';label='Cited by';}
 else if(forward&&e.field==='depends-on'||!forward&&e.field==='used-by'){category='foundations';label='Dependency';}
 else if(!forward&&e.field==='depends-on'||forward&&e.field==='used-by'){category='next';label='Used by';}
 else if(e.field==='field'){category=forward?'foundations':'next';label=forward?'In this field':'Field member';}
 else if(other.fields.type==='source'){category='sources';label=e.field==='body reference'?'Text reference':'Linked source';}
 else {category='next';label=e.field==='body reference'?(forward?'Mentions':'Mentioned by'):'Linked record';}
 const prior=out.get(other.id),priority=({'source':0,'depends-on':1,'used-by':2,'field':3,'links':4,'body reference':5}[e.field]??6);
 // Keep every evidence item even when a later, stronger relation becomes primary.
 if(!prior||priority<prior.priority)out.set(other.id,{record:other,category,label,edge:e,forward,priority,evidence:prior?[...prior.evidence,e]:[e]});else prior.evidence.push(e);
 }
 return [...out.values()].sort((a,b)=>a.priority-b.priority||data.records.indexOf(a.record)-data.records.indexOf(b.record));
}
function plain(s){return s.replace(/\[\[([^\]]+)\]\]/g,'$1').replace(/\[([^\]]+)\]\([^)]*\)/g,'$1').replace(/\*\*/g,'').replace(/\*/g,'').replace(/^\s*[^\n]+? — /,'').trim();}
function shortQuote(r){const s=plain(r.excerpt),words=s.split(/\s+/);return words.length>27?words.slice(0,27).join(' ')+'…':s;}
function cleanState(s,ids){
 const input=Array.isArray(s?.route)?s.route:[],at=Number.isInteger(s?.index)?Math.max(0,Math.min(s.index,input.length-1)):0;
 let route=[],index=0;
 input.forEach((id,i)=>{if(ids.has(id)){route.push(id);if(i<=at)index=route.length-1;}});
 const start=Math.max(0,route.length-MAX_ROUTE);route=route.slice(start);index=Math.max(0,Math.min(index-start,route.length-1));
 return {route,index,pins:Array.isArray(s?.pins)?[...new Set(s.pins.filter(id=>ids.has(id)))].slice(0,2):[]};
}
function cleanDialog(d,ids,edgeCount,pins,current){
 if(!d||typeof d!=='object')return null;
 if(['read','provenance'].includes(d.type))return {type:d.type,record:ids.has(d.record)?d.record:current,...(d.type==='read'&&Number.isInteger(d.paragraph)&&d.paragraph>=0?{paragraph:d.paragraph}:{})};
 if(d.type==='edge')return Number.isInteger(d.edge)&&d.edge>=0&&d.edge<edgeCount?{type:'edge',edge:d.edge}:null;
 if(['compare','pins'].includes(d.type))return pins.length===2&&new Set(pins).size===2&&!(d.type==='pins'&&pins.includes(current))?{type:d.type}:null;
 return ['shelf','route','connections'].includes(d.type)?{type:d.type}:null;
}
function parseLocation(hash,ids,edgeCount,pins=[]){
 const params=new URLSearchParams(hash.replace(/^#/,'')),record=ids.has(params.get('record'))?params.get('record'):null;
 const urlPins=params.getAll('pin').filter(id=>ids.has(id)),resolvedPins=urlPins.length?[...new Set(urlPins)].slice(0,2):pins;
 const edge=params.get('edge'),view=cleanDialog({type:params.get('view'),record:params.get('target'),paragraph:/^\d+$/.test(params.get('paragraph')||'')?Number(params.get('paragraph')):null,edge:edge!==null&&/^\d+$/.test(edge)?Number(edge):null},ids,edgeCount,resolvedPins,record||DEFAULT_ID);
 return {record,dialog:view,pins:resolvedPins};
}
function locationHash(current,dialog,pins){
 const params=new URLSearchParams({record:current});
 if(dialog){params.set('view',dialog.type);if(['read','provenance'].includes(dialog.type)&&dialog.record!==current)params.set('target',dialog.record);if(Number.isInteger(dialog.paragraph))params.set('paragraph',dialog.paragraph);if(dialog.type==='edge')params.set('edge',dialog.edge);if(dialog.type==='compare')pins.forEach(id=>params.append('pin',id));}
 return params.toString();
}
// Analytic alias representative; not a finite-window reconstruction algorithm.
function samplingModel(rate){
 const fs=Math.min(24,Math.max(2,Number.isFinite(Number(rate))?Math.round(Number(rate)):12)),frequency=3,phase=.35;
 const signedFrequency=((frequency+fs/2)%fs+fs)%fs-fs/2;
 const original=t=>Math.cos(2*Math.PI*frequency*t+phase);
 const equivalent=t=>Math.cos(2*Math.PI*signedFrequency*t+phase);
 const boundary=Math.abs(Math.abs(signedFrequency)-fs/2)<1e-10;
 const samples=Array.from({length:2*fs+1},(_,n)=>({t:n/fs,value:original(n/fs)}));
 return {rate:fs,frequency,phase,signedFrequency,apparentFrequency:Math.abs(signedFrequency),boundary,aliased:fs<2*frequency,samples,original,equivalent};
}
const api={samplingModel,related,plain,shortQuote,cleanState,cleanDialog,parseLocation,locationHash,DEFAULT_ID,MAX_ROUTE};if(typeof module==='object')module.exports=api;else root.STUDY_CORE=api;
})(typeof window!=='undefined'?window:globalThis);
