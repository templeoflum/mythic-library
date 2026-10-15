'use strict';
const $ = id => document.getElementById(id);
const state = {books:[],manifests:{},cache:new Map(),active:null,manifest:null,section:null,pages:[],page:0,text:'',request:0,font:21,returnFocus:null,ready:false};
let saveTimer;
const storage = {
  read(key,fallback){try{return JSON.parse(localStorage.getItem('mythic:'+key))??fallback;}catch{return fallback;}},
  write(key,value){try{localStorage.setItem('mythic:'+key,JSON.stringify(value));$('storage-status').textContent='Your place is saved in this browser.';return true;}catch{$('storage-status').textContent='Browser storage is unavailable. Your place will not be saved.';return false;}}
};
function element(tag,text,className){const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(className)el.className=className;return el;}
function markUnclearReadings(el,text){
  el.replaceChildren();let cursor=0;
  for(const match of text.matchAll(/\[unclear: [^\]]+\]/g)){el.append(document.createTextNode(text.slice(cursor,match.index)),element('mark',match[0],'unclear-reading'));cursor=match.index+match[0].length;}
  el.append(document.createTextNode(text.slice(cursor)));
}
function button(text,handler,className){const el=element('button',text,className);el.type='button';el.onclick=handler;return el;}
function renderShelf(){
  const shelves=$('shelves');shelves.replaceChildren();
  const groups=new Map(),palette=['#46533b','#5c493b','#3e5351','#5b4d60','#65513a','#3c5260'];
  for(const book of state.books){const name=book.shelf||'Books';if(!groups.has(name))groups.set(name,[]);groups.get(name).push(book);}
  let coverIndex=0;
  for(const [name,books] of groups){
    // Keep each shelf small as the collection grows, without adding filter controls.
    for(let first=0;first<books.length;first+=4){
      const group=element('section',undefined,'shelf-group'),heading=element('h3',name+(first?` · continued`:''),'shelf-label');
      heading.id=`shelf-group-${shelves.children.length+1}`;group.setAttribute('aria-labelledby',heading.id);
      const row=element('div',undefined,'shelf-books');
      for(const book of books.slice(first,first+4)){
        const el=button('',()=>openBook(book.id),'book');el.setAttribute('aria-label',book.author_label?`Read ${book.title}; ${book.author_label}: ${book.author}`:`Read ${book.title} by ${book.author}`);
        const cover=element('span',undefined,'cover');cover.style.setProperty('--cover',palette[coverIndex++%palette.length]);
        const title=element('strong',book.shelf_title||book.title);title.title=book.title;
        cover.append(element('span','✧','ornament'),title,element('span',book.cover_author||book.author,'author'),element('span','❦','ornament'));
        el.append(cover,element('span',book.shelf_caption||book.edition,'book-caption'));row.append(el);
      }
      group.append(heading,row);shelves.append(group);
    }
  }
  $('edition-count').textContent=state.books.some(book=>book.text_status==='derived-scan-collated')?`${state.books.length} reading editions`:`${state.books.length} verified editions`;renderResume();
}
function readBookmark(book){const value=storage.read('bookmark:v2:'+book.id,null);return ReaderCore.validBookmark(value,state.manifests[book.id])?value:null;}
function renderResume(){const last=storage.read('last',null),book=state.books.find(item=>item.id===last);$('resume').replaceChildren();$('resume').hidden=!book;if(!book)return;const text=element('p');text.append(element('small','Pick up where you left off'),document.createTextNode(book.title));$('resume').append(text,button('Continue →',()=>openBook(book.id)));}
function addDetail(term,value,url){if(!value)return;const dt=element('dt',term),dd=element('dd');if(url){const link=element('a',value);link.href=url;link.target='_blank';link.rel='noopener noreferrer';dd.append(link);}else dd.textContent=value;$('edition-details').append(dt,dd);}
function sourceLabel(book,key,fallback){const value=book.source_labels?.[key];return typeof value==='string'&&value.trim()?value:fallback;}
function renderContents(){
  $('contents-book').textContent=state.active.title;$('primary-contents').replaceChildren();$('supplementary-contents').replaceChildren();$('edition-details').replaceChildren();
  let lastGroup='';
  for(const section of state.manifest.sections){
    const target=$(section.kind==='primary'?'primary-contents':'supplementary-contents');
    if(section.kind==='primary'&&section.group&&section.group!==lastGroup){lastGroup=section.group;target.append(element('h3',section.group,'contents-group'));}
    const entry=button(section.label,()=>{savePosition();$('contents-dialog').close();showSection(section.id,0,null,true);},'contents-entry');entry.dataset.section=section.id;entry.setAttribute('aria-current',String(section.id===state.section?.id));target.append(entry);
  }
  const b=state.active;addDetail('Edition',b.edition);addDetail('Display label',b.display_title_note);addDetail('Historical title',b.bibliographic_title);addDetail(b.author_label||'Author',b.author);addDetail('Editor',b.editor);addDetail('Illustrator',b.illustrator);addDetail(b.credit_label||'Translation',b.translator);addDetail('Edition note',b.edition_note);if(b.qualification_notes?.length)addDetail('Source qualifications',b.qualification_notes.join(' '));addDetail('Rights',b.rights);addDetail('Source',b.source,b.source);if(b.text_status==='derived-scan-collated'){
    addDetail('Transcription status',b.transcription_status);
    addDetail('Derived reading text','Open the scan-collated transcription (four unresolved readings)',b.path);
  }else{
    addDetail(sourceLabel(b,'text_label','Original text & notices'),sourceLabel(b,'text_link','Open the intact source text file'),b.notices||b.path);
    if(b.notices)addDetail('Reading text','Open the complete reading text',b.path);
  }
  if(b.source_scan){
    addDetail('Original source scan',sourceLabel(b,'scan_link','Open the unchanged source scan (PDF)'),b.source_scan.path);
    const dt=element('dt','Source scan download'),dd=element('dd'),link=element('a','Download the unchanged source scan (PDF)');link.href=b.source_scan.path;link.download=b.source_scan.path.split('/').pop();link.target='_blank';link.rel='noopener noreferrer';dd.append(link);$('edition-details').append(dt,dd);
  }
  if(b.illustrated_source)addDetail('Illustrations','Open the illustrated source edition',b.illustrated_source);
  if(b.preservation_archive)addDetail(sourceLabel(b,'archive_label','Preserved illustrated edition'),sourceLabel(b,'archive_link','Download the intact HTML and image archive'),b.preservation_archive.path);
}
function updateContentsSelection(){for(const el of document.querySelectorAll('.contents-entry'))el.setAttribute('aria-current',String(el.dataset.section===state.section?.id));}
async function loadBook(book){if(state.cache.has(book.id))return state.cache.get(book.id);const response=await fetch(book.path);if(!response.ok)throw Error('Source unavailable');const bytes=await response.arrayBuffer();const text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(bytes);const manifest=state.manifests[book.id];if(text.length!==manifest.length)throw Error('Source and navigation do not match');
  // A stale cached manifest must never point at a different source edition.
  if(globalThis.crypto?.subtle){const digest=await crypto.subtle.digest('SHA-256',bytes);const hash=Array.from(new Uint8Array(digest),byte=>byte.toString(16).padStart(2,'0')).join('');if(hash!==manifest.sha256)throw Error('Source integrity check failed');}
  state.cache.set(book.id,text);return text;
}
async function openBook(id,fromHistory=false,requestedSection=null,requestedOffset=null){
  const book=state.books.find(item=>item.id===id);if(!book)return;savePosition();clearTimeout(saveTimer);if(!state.active)state.returnFocus=document.activeElement;
  closeDialogs();const token=++state.request;state.active=book;state.manifest=state.manifests[id];state.ready=false;state.pages=[];state.section=null;
  $('library').hidden=true;$('reader').hidden=false;document.body.classList.add('reading');$('reader-short-title').textContent=book.title;$('reading-context').textContent='';$('reader-heading').textContent='';$('book-text').replaceChildren();$('section-end').hidden=true;$('loading').textContent='Opening…';$('previous').disabled=true;$('next').disabled=true;$('show-contents').disabled=true;$('page-progress').textContent='';$('page-location').textContent='';$('reading-scroll').scrollTop=0;
  if(!fromHistory)history.pushState({book:id},'',`#book=${encodeURIComponent(id)}`);
  try{
    const text=await loadBook(book);if(token!==state.request)return;state.text=text;state.ready=true;const saved=readBookmark(book);
    const requested=state.manifest.sections.find(section=>section.id===requestedSection);
    const section=requested||(saved&&state.manifest.sections.find(section=>section.id===saved.sectionId))||state.manifest.sections.find(section=>section.id===state.manifest.defaultSectionId);
    const bookmark=requested?(Number.isInteger(requestedOffset)?{offset:requestedOffset,within:0,atTop:true}:null):saved;
    $('loading').textContent='';$('show-contents').disabled=false;renderContents();storage.write('last',id);showSection(section.id,bookmark?.offset??section.start,bookmark,!fromHistory);
  }catch(error){if(token!==state.request)return;state.ready=false;$('loading').textContent='This book could not be opened. Return to the shelves and try again.';}
}
function sourceNeighbors(){const sections=state.section.kind==='primary'?state.manifest.sections.filter(section=>section.kind==='primary'):state.manifest.sections;const index=sections.findIndex(section=>section.id===state.section.id);return{previous:sections[index-1],next:sections[index+1]};}
function showSection(id,offset=0,bookmark=null,updateURL=true){
  if(!state.ready)return;const section=state.manifest.sections.find(item=>item.id===id);if(!section)return;state.section=section;state.pages=ReaderCore.paginate(state.text,section);state.page=ReaderCore.pageForOffset(state.pages,offset);renderPage(bookmark,updateURL);
}
function renderPage(bookmark=null,updateURL=true){
  const page=state.pages[state.page];if(!page)return;const token=state.request,focused=document.activeElement;$('book-text').replaceChildren();
  $('reading-context').textContent=(state.section.kind==='primary'?state.active.title:'Supplementary material')+(page.blocks[0]?.continuation?' · continued':'')+(state.active.text_status==='derived-scan-collated'?' · Scan-collated transcription; 4 unresolved readings':'')+(state.section.sourceAttribution?' · '+state.section.sourceAttribution.display:'');
  $('reader-heading').textContent=state.page>0?state.section.label:'';
  page.blocks.forEach(block=>{if(!block.text.trim())return;const tag=block.kind==='heading'?'h2':'p',el=element(tag,block.text,block.kind==='verse'?'verse':block.kind==='table'?'source-table':'');el.dataset.paragraph=String(block.paragraphStart);el.dataset.offset=String(block.start);el.dataset.end=String(block.end);if(state.active.text_status==='derived-scan-collated'&&block.text.includes('[unclear:'))markUnclearReadings(el,block.text);$('book-text').append(el);});
  const neighbors=sourceNeighbors(),lastPage=state.page===state.pages.length-1;
  $('previous').disabled=state.page===0&&!neighbors.previous;$('next').disabled=false;$('next').textContent=lastPage&&!neighbors.next?'Shelves →':'Next →';
  $('previous').setAttribute('aria-label',state.page===0&&neighbors.previous?'Previous: '+neighbors.previous.label:'Previous passage');$('next').setAttribute('aria-label',lastPage?(neighbors.next?'Next: '+neighbors.next.label:'Return to shelves'):'Next passage');
  $('page-progress').textContent=`Passage ${state.page+1} of ${state.pages.length}`;$('page-location').textContent=state.section.label;
  $('section-end').hidden=!lastPage;$('end-label').textContent=lastPage?'End of '+state.section.label:'';
  updateContentsSelection();if(updateURL)replaceRoute();
  $('reading-scroll').scrollTop=0;
  requestAnimationFrame(()=>{if(token!==state.request||!state.ready)return;restoreBookmark(bookmark);if(focused!==$('previous')&&focused!==$('next'))$('reading-scroll').focus({preventScroll:true});savePosition();});
}
function replaceRoute(){history.replaceState({book:state.active.id},'',`#book=${encodeURIComponent(state.active.id)}&section=${encodeURIComponent(state.section.id)}&offset=${state.pages[state.page].start}`);}
function activeAnchor(){
  const scroller=$('reading-scroll'),rect=scroller.getBoundingClientRect(),nodes=Array.from($('book-text').children);const current=nodes.find(node=>node.getBoundingClientRect().bottom>rect.top+12)||nodes.at(-1);
  if(!current)return{offset:state.pages[state.page].start,within:0,atTop:true};const box=current.getBoundingClientRect();return{offset:Number(current.dataset.offset),within:Math.max(0,Math.min(.99,(rect.top-box.top)/Math.max(1,box.height))),atTop:scroller.scrollTop<20};
}
function restoreBookmark(bookmark){if(!bookmark||bookmark.atTop)return;const node=Array.from($('book-text').children).find(el=>Number(el.dataset.offset)===bookmark.offset);if(!node)return;const scroller=$('reading-scroll'),box=node.getBoundingClientRect(),top=scroller.getBoundingClientRect().top;scroller.scrollTop+=box.top-top+Math.max(0,Math.min(.99,bookmark.within||0))*box.height;}
function savePosition(){if(!state.ready||!state.active||!state.pages.length||state.section.kind!=='primary')return;const anchor=activeAnchor();storage.write('bookmark:v2:'+state.active.id,{version:2,sha256:state.manifest.sha256,sectionId:state.section.id,...anchor});}
function turnPage(delta){if(!state.ready)return;clearTimeout(saveTimer);savePosition();const target=state.page+delta;if(target>=0&&target<state.pages.length){state.page=target;renderPage();return;}const neighbor=sourceNeighbors()[delta<0?'previous':'next'];if(neighbor){showSection(neighbor.id,delta<0?neighbor.end-1:neighbor.start);return;}if(delta>0)closeBook();}
function closeDialogs(){for(const id of ['contents-dialog','settings-dialog'])if($(id).open)$(id).close();}
function closeBook(fromHistory=false){clearTimeout(saveTimer);savePosition();++state.request;closeDialogs();state.active=null;state.ready=false;state.pages=[];$('reader').hidden=true;$('library').hidden=false;document.body.classList.remove('reading');$('book-text').replaceChildren();if(!fromHistory)history.pushState({},'',location.pathname+location.search);renderResume();if(state.returnFocus?.isConnected)state.returnFocus.focus();}
function navigateHash(){const params=new URLSearchParams(location.hash.slice(1)),id=params.get('book');if(id){const offset=params.get('offset');return openBook(id,true,params.get('section'),offset!==null&&/^\d+$/.test(offset)?Number(offset):null);}else if(state.active)closeBook(true);}
function setFont(delta){const anchor=state.ready?activeAnchor():null;state.font=Math.max(18,Math.min(30,state.font+delta));$('book-text').style.setProperty('--reading-size',state.font+'px');$('font-size').value=state.font;$('smaller').disabled=state.font<=18;$('larger').disabled=state.font>=30;storage.write('font',state.font);requestAnimationFrame(()=>{restoreBookmark(anchor);savePosition();});}
function setTheme(night){document.body.classList.toggle('night',night);$('theme-paper').setAttribute('aria-pressed',String(!night));$('theme-night').setAttribute('aria-pressed',String(night));storage.write('night',night);}
$('back').onclick=()=>closeBook();$('previous').onclick=()=>turnPage(-1);$('next').onclick=()=>turnPage(1);
$('show-contents').onclick=()=>{$('contents-dialog').showModal();};$('close-contents').onclick=()=>$('contents-dialog').close();
$('show-settings').onclick=()=>$('settings-dialog').showModal();$('close-settings').onclick=()=>$('settings-dialog').close();
$('start-book').onclick=()=>{savePosition();$('contents-dialog').close();showSection(state.manifest.defaultSectionId);};
$('smaller').onclick=()=>setFont(-1);$('larger').onclick=()=>setFont(1);$('theme-paper').onclick=()=>setTheme(false);$('theme-night').onclick=()=>setTheme(true);
$('reading-scroll').addEventListener('scroll',()=>{clearTimeout(saveTimer);saveTimer=setTimeout(savePosition,200);});
window.addEventListener('popstate',navigateHash);window.addEventListener('pagehide',savePosition);document.addEventListener('visibilitychange',()=>{if(document.hidden)savePosition();});
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&state.active&&!$('contents-dialog').open&&!$('settings-dialog').open)closeBook();});
(async()=>{try{const [catalogResponse,sectionsResponse]=await Promise.all([fetch('catalog.json'),fetch('sections.json')]);if(!catalogResponse.ok||!sectionsResponse.ok)throw Error('Navigation unavailable');state.books=await catalogResponse.json();state.manifests=(await sectionsResponse.json()).books;for(const book of state.books)if(!state.manifests[book.id]||state.manifests[book.id].sha256!==book.sha256)throw Error('Edition mismatch');state.font=Math.max(18,Math.min(30,Number(storage.read('font',21))||21));setFont(0);setTheme(storage.read('night',false)===true);renderShelf();navigateHash();}catch{$('catalog-status').textContent='The library could not be loaded. Please reload this page.';}})();
