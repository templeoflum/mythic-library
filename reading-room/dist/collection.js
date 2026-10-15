'use strict';
// Inventory metadata stays separate from the exact, reviewed reading editions.
// No reading source or bookmark is loaded or changed while browsing this view.
(() => {
  const get = id => document.getElementById(id);
  const labels = Object.freeze({readable:'Reading edition available','needs-source-review':'Needs source review',quarantined:'Quarantined source',missing:'Source missing'});
  let inventory = null, activeRegister = 'main';
  const cache = new Map(), pending = new Map();
  const registers = Object.freeze({
    main:{url:'collections.json',label:'main collection',unit:'catalog entries'},
    esoterica:{url:'esoterica-register.json',label:'esoterica register',unit:'registered file slots'}
  });
  const mainScope=get('collection-scope').textContent;
  function showScope() {
    const separate=activeRegister==='esoterica';
    get('collection-scope').textContent=separate?'A separate historical shelf register, counted by file slot rather than unique work. Three readable Plato editions already appear in the main collection.':mainScope;
    get('collection-scope-note').textContent=separate?'Other registered source files have not been recovered into the cloud collection. Descriptions are not fresh completeness or rights verification. These slots are never added to the main collection total.':'The separate esoterica register is available in the Register selector. Its overlapping entries are not added to this count.';
  }
  const make = (tag, text, className) => {const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;};
  const normalize = value => String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();
  function safeURL(value) {
    if(typeof value!=='string')return null;
    try {const url=new URL(value);if(url.protocol!=='https:'||url.username||url.password||!url.hostname.includes('.')||/^(localhost|127\.|0\.|\[)/i.test(url.hostname))return null;return url.href;}catch{return null;}
  }
  function validate(data, catalog, register) {
    if(data?.schema_version!==1||!Array.isArray(data.entries)||!Array.isArray(catalog)||!data.entries.length)throw Error('Invalid inventory');
    const ids=new Set(), readers=new Set(), catalogIds=new Set(catalog.map(book=>book.id));
    const counts=Object.fromEntries(Object.keys(labels).map(status=>[status,0]));
    for(const entry of data.entries) {
      if(!entry||typeof entry.id!=='string'||!entry.id||ids.has(entry.id)||typeof entry.title!=='string'||!entry.title||typeof entry.tradition!=='string'||!Object.hasOwn(labels,entry.status))throw Error('Invalid entry');
      ids.add(entry.id);counts[entry.status]++;
      if(!Array.isArray(entry.aliases)||!entry.aliases.every(value=>typeof value==='string')||typeof entry.source_note!=='string')throw Error('Invalid provenance');
      for(const key of ['author','edition','original_catalog_title'])if(entry[key]!=null&&typeof entry[key]!=='string')throw Error('Invalid metadata');
      if(/\/workspace\/|\/tmp\/|file:\/\/|source-audit\/|[A-Z]:\\/i.test(JSON.stringify(entry)))throw Error('Private source location');
      if(entry.status==='readable') {
        if(typeof entry.reader_id!=='string'||!catalogIds.has(entry.reader_id)||readers.has(entry.reader_id))throw Error('Invalid reading edition');
        readers.add(entry.reader_id);
      }else if(entry.reader_id!==null)throw Error('Unreviewed reading action');
    }
    if(register==='main') {
      if(readers.size!==catalogIds.size||data.summary?.entries!==data.entries.length||data.summary?.readable_editions!==counts.readable||data.summary?.needs_source_review!==counts['needs-source-review']||data.summary?.quarantined_without_replacement!==counts.quarantined||data.summary?.missing_normalized_text!==counts.missing)throw Error('Inventory counts disagree');
    }else{
      if(data.summary?.registered_file_slots!==data.entries.length||data.summary?.overlapping_readable_editions!==counts.readable||data.summary?.not_recovered_file_slots!==counts.missing||counts.readable+counts.missing!==data.entries.length)throw Error('Register counts disagree');
      const slots=new Set();
      for(const entry of data.entries){
        if(typeof entry.register_id!=='string'||!entry.register_id||slots.has(entry.register_id))throw Error('Invalid register slot');slots.add(entry.register_id);
        if(entry.status==='readable'&&(entry.overlaps_main_catalog!==true||entry.overlap_reader_id!==entry.reader_id))throw Error('Unconfirmed readable overlap');
        if(entry.status!=='readable'&&(entry.overlaps_main_catalog!==false||entry.overlap_reader_id!==null))throw Error('Unconfirmed register status');
      }
    }
    return {entries:data.entries,counts,register,scope_note:typeof data.scope_note==='string'?data.scope_note:''};
  }
  function readerReady(id) {
    const book=typeof state!=='undefined'&&state.books.find(item=>item.id===id);
    return Boolean(book&&state.manifests[id]?.sha256===book.sha256&&get('shelves').children.length);
  }
  function render() {
    if(!inventory)return;
    const query=normalize(get('collection-search').value).trim(), status=get('collection-status-filter').value||'all', tradition=get('collection-tradition-filter').value||'all';
    const terms=query.split(/\s+/).filter(Boolean);
    const entries=inventory.entries.filter(entry=>{
      const haystack=normalize([entry.title,entry.original_catalog_title,entry.author,entry.edition,entry.tradition,...entry.aliases].filter(Boolean).join(' '));
      return (status==='all'||entry.status===status)&&(tradition==='all'||entry.tradition===tradition)&&terms.every(term=>haystack.includes(term));
    });
    get('collection-summary').textContent=activeRegister==='main'?`${inventory.entries.length} catalog entries · ${inventory.counts.readable} reading editions · ${inventory.counts['needs-source-review']} need source review · ${inventory.counts.quarantined} quarantined · ${inventory.counts.missing} missing text`:`${inventory.entries.length} registered file slots · ${inventory.counts.readable} already-readable editions (also in the main collection) · ${inventory.counts.missing} source files not recovered`;
    get('collection-load-status').textContent=`Showing ${entries.length} of ${inventory.entries.length} ${registers[activeRegister].unit}.`;
    const results=get('collection-results');results.replaceChildren();
    if(!entries.length){results.append(make('p','No entries match these filters. Try another title or clear a filter.','collection-empty'));return;}
    for(const entry of entries) {
      const card=make('article',undefined,'collection-card');card.dataset.entryId=entry.id;card.dataset.status=entry.status;
      const statusLabel=activeRegister==='esoterica'?(entry.status==='readable'?'Already-readable edition':'File not recovered'):labels[entry.status];
      const badge=make('span',statusLabel,'collection-badge');badge.dataset.status=entry.status;card.append(badge,make('h3',entry.title),make('p',entry.tradition.replace(/-/g,' '),'collection-tradition'));
      if(entry.author&&entry.author!=='Unknown')card.append(make('p',entry.author));
      if(entry.original_catalog_title&&entry.original_catalog_title!==entry.title)card.append(make('p','Collected work: '+entry.original_catalog_title,'collection-original-title'));
      if(entry.edition)card.append(make('p',entry.edition,'collection-edition'));
      card.append(make('p',entry.source_note,'collection-source-note'));
      if(entry.status==='readable') {
        const read=make('button',activeRegister==='main'?'Read this edition →':'Open existing reading edition →','collection-action');read.type='button';read.dataset.readerId=entry.reader_id;read.setAttribute('aria-label','Read '+entry.title+'; reviewed edition');read.onclick=()=>{if(!readerReady(entry.reader_id)){get('collection-load-status').textContent=get('catalog-status').textContent?'The reading shelf is unavailable. Return to Read now and reload the page.':'The reading shelf is still loading. Please try Read again when it is ready.';return;}return openBook(entry.reader_id);};card.append(read);
      }
      const source=safeURL(entry.source_url);
      const aliases=entry.aliases.filter(alias=>normalize(alias)!==normalize(entry.title)&&alias!==entry.id);
      if(source||aliases.length) {
        const details=make('details');details.append(make('summary','Source & catalog details'));
        if(aliases.length)details.append(make('p','Also listed as: '+aliases.join('; ')));
        if(source){const link=make('a',entry.status==='readable'?'Verified edition source':'Recorded source; review pending');link.href=source;link.target='_blank';link.rel='noopener noreferrer';details.append(link);}
        card.append(details);
      }
      results.append(card);
    }
  }
  function activate(data) {
    inventory=data;
    const select=get('collection-tradition-filter');select.replaceChildren();const all=make('option','All traditions');all.value='all';select.append(all);
    for(const tradition of [...new Set(inventory.entries.map(entry=>entry.tradition))].sort((a,b)=>a.localeCompare(b))){const option=make('option',tradition.replace(/-/g,' '));option.value=tradition;select.append(option);}
    select.value='all';get('collection-retry').hidden=true;render();
  }
  async function load() {
    const register=activeRegister;
    if(cache.has(register)){if(inventory!==cache.get(register))activate(cache.get(register));else render();return;}
    get('collection-load-status').textContent=`Loading the ${registers[register].label}…`;get('collection-retry').hidden=true;
    if(pending.has(register))return pending.get(register);
    const request=(async()=>{
      try {
        const responses=await Promise.all([fetch(registers[register].url),fetch('catalog.json')]);
        if(responses.some(response=>!response.ok))throw Error('Inventory unavailable');
        const [data,catalog]=await Promise.all(responses.map(response=>response.json()));const checked=validate(data,catalog,register);cache.set(register,checked);
        if(activeRegister===register)activate(checked);
      }catch{
        if(activeRegister===register){inventory=null;get('collection-results').replaceChildren();get('collection-summary').textContent='';get('collection-load-status').textContent=`The ${registers[register].label} could not be loaded. Your reading shelf is still available.`;get('collection-retry').hidden=false;}
      }finally{pending.delete(register);}
    })();
    pending.set(register,request);return request;
  }
  function switchRegister() {
    const selected=get('collection-register-filter').value;
    if(!Object.hasOwn(registers,selected)||selected===activeRegister)return;
    activeRegister=selected;inventory=null;get('collection-search').value='';get('collection-status-filter').value='all';get('collection-tradition-filter').value='all';get('collection-results').replaceChildren();get('collection-summary').textContent='';showScope();return load();
  }
  function show(collected) {
    get('reading-shelf-panel').hidden=collected;get('collected-panel').hidden=!collected;
    get('view-reading').setAttribute('aria-pressed',String(!collected));get('view-collected').setAttribute('aria-pressed',String(collected));
    get('skip-library').href=collected?'#collection-search':'#shelves';get('skip-library').textContent=collected?'Skip to collected works':'Skip to books';
    if(collected)return load();
  }
  get('collection-register-filter').value='main';get('collection-register-filter').addEventListener('change',switchRegister);
  get('view-reading').onclick=()=>show(false);get('view-collected').onclick=()=>show(true);get('collection-retry').onclick=load;
  get('collection-search').addEventListener('input',render);get('collection-status-filter').addEventListener('change',render);get('collection-tradition-filter').addEventListener('change',render);
})();
