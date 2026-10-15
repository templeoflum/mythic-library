'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const R=path.join(__dirname,'..'),D=path.join(R,'dist'),Core=require(path.join(D,'reader-core.js'));
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const {preservedBytes}=require('./preserved_baseline.cjs');
const baseline=read(path.join(__dirname,'fourteen-edition-baseline.json')),pins=read(path.join(__dirname,'fourteen-baseline-files.json')).files;
const catalog=read(path.join(D,'catalog.json')),manifest=read(path.join(D,'sections.json')),specs=read(path.join(R,'scripts/edition_specs.json'));
assert.equal(baseline.catalog.length,14);assert.equal(catalog.length,15);assert.equal(Object.keys(baseline.sections.books).length,14);assert.equal(Object.keys(baseline.specs.editions).length,14);
assert.deepEqual(catalog.slice(0,14),baseline.catalog,'All fourteen catalog records remain exact, including shelves');
assert.deepEqual(catalog.slice(14).map(b=>b.id),['yoruba-legends']);
let bookmarks=0,primaryBookmarks=0;
for(const book of baseline.catalog){
  assert.deepEqual(manifest.books[book.id],baseline.sections.books[book.id],'Complete old section records: '+book.id);
  assert.deepEqual(specs.editions[book.id],baseline.specs.editions[book.id],'Complete old source specs: '+book.id);
  for(const section of baseline.sections.books[book.id].sections)for(const offset of [section.start,section.end-1]){
    assert(Core.validBookmark({version:2,sha256:book.sha256,sectionId:section.id,offset,within:.3,atTop:false},manifest.books[book.id]));bookmarks++;if(section.kind==='primary')primaryBookmarks++;
  }
}
assert.equal(bookmarks,1340);assert.equal(primaryBookmarks,1132);
const changedBaseline=new Set(['.gitignore','REVIEW.md','dist/app.js','dist/style.css','dist/catalog.json','dist/sections.json','scripts/README.md','scripts/edition_specs.json','tests/source-test-results.json','tests/test_core.cjs','tests/test_interactions.cjs','tests/test_candidate_preservation.cjs','tests/test_fourteen_preservation.cjs']);
for(const [p,pin] of Object.entries(pins))if(!changedBaseline.has(p)){const bytes=fs.readFileSync(path.join(R,p));assert.equal(bytes.length,pin.bytes);assert.equal(sha(bytes),pin.sha256,'Every other baseline file remains unchanged: '+p);}
for(const [p,h] of Object.entries(baseline.preserved_file_hashes))assert.equal(sha(preservedBytes(R,p)),h,'Old source/core unchanged: '+p);
for(const p of ['.openai/hosting.json','scripts/build_sections.py','dist/app.js','tests/eleven-edition-baseline.json','tests/thirteen-edition-baseline.json','tests/ikom-edition-audit.json'])assert.equal(sha(preservedBytes(R,p)),pins[p].sha256,'Pinned historical record or exact allowed UI transform: '+p);
const originalApp=fs.readFileSync(path.join(__dirname,'fixtures/fourteen-app.js'),'utf8'),app=fs.readFileSync(path.join(D,'app.js'),'utf8');
for(const name of ['readBookmark','loadBook','openBook','sourceNeighbors','showSection','replaceRoute','activeAnchor','restoreBookmark','savePosition','turnPage','closeDialogs','closeBook','navigateHash','setFont','setTheme']){
  const extract=s=>s.match(new RegExp('(?:async )?function '+name+'\\([\\s\\S]*?(?=\\n(?:async )?function |\\n\\$|$)'))?.[0];
  assert(extract(originalApp),'Found unchanged behavior '+name);assert.equal(extract(app),extract(originalApp),'Storage/navigation behavior unchanged: '+name);
}
assert.equal(app.match(/const storage = \{[\s\S]*?\n\};/)[0],originalApp.match(/const storage = \{[\s\S]*?\n\};/)[0]);
const shelves=new Map();for(const book of catalog){const list=shelves.get(book.shelf)||[];list.push(book.id);shelves.set(book.shelf,list);}
assert.equal(shelves.size,5);assert.deepEqual([...shelves.values()].map(x=>x.length).sort(),[2,3,3,3,4]);
assert.deepEqual(shelves.get('African & diaspora collections'),['anansi-tales','zanzibar-tales','ikom-folk-stories-from-southern-nigeria','yoruba-legends']);
const rawInput=fs.readFileSync(path.join(__dirname,'fixtures/yoruba-reading-input.json')),rawUnclear=fs.readFileSync(path.join(__dirname,'fixtures/yoruba-unresolved-input.json'));
assert.equal(sha(rawInput),'060a8ef5f51aee94777a23d0e66b6729155200f4fba4717ffcac23bcb64ff926');assert.equal(sha(rawUnclear),'b9b3b1150e18ef2050f3c9bed7c2dcba81d0055bfed8b29f7daf7dba49239bf8');
const input=JSON.parse(rawInput),unclear=JSON.parse(rawUnclear),audit=read(path.join(__dirname,'yoruba-edition-audit.json'));
const book=catalog.at(-1),m=manifest.books[book.id],spec=specs.editions[book.id],raw=fs.readFileSync(path.join(D,book.path)),text=raw.toString('utf8');
assert.equal(book.path,'books/yoruba-legends-derived-transcription.txt');assert.equal(book.text_status,'derived-scan-collated');assert.equal(book.verified,false);assert.equal(book.scan_collated,true);assert.equal(book.author,'M. I. Ogumefu, B.A.');assert.equal(book.translator,null);assert.equal(book.source,'https://archive.org/details/in.ernet.dli.2015.54438');assert(book.edition_note.includes('DERIVED'));assert(book.edition_note.includes('Four unresolved'));assert.equal(book.narrative_uncertainty_count,4);assert.equal(book.sha256,sha(raw));assert.equal(book.bytes,raw.length);assert.equal(spec.sha256,book.sha256);assert.equal(spec.textStatus,book.text_status);
const scan=fs.readFileSync(path.join(D,book.source_scan.path));assert.equal(sha(scan),'1a3c5f881de8acb126d88251d510bac1f974229c4a255c8d1c9cf02a239d5494');assert.equal(scan.length,book.source_scan.bytes);assert.equal(sha(scan),book.source_scan.sha256);assert.equal(scan.subarray(0,5).toString(),'%PDF-');assert.equal(book.source_scan.pages,98);assert.deepEqual(book.source_scan,spec.sourceScan);assert.equal(book.source_scan.source,book.source);
const primary=m.sections.filter(s=>s.kind==='primary'),extras=m.sections.filter(s=>s.kind!=='primary');assert.equal(primary.length,40);assert.equal(extras.length,8);assert.equal(m.defaultSectionId,'yoruba-legends-story-1');
let prose=0,verse=0,attribution=0,paragraphs=0,markers=0;
for(const [i,section] of primary.entries()){
  const story=input.stories[i];assert.equal(story.ordinal,i+1);assert.equal(section.id,`yoruba-legends-story-${story.ordinal}`);
  const heading=`${story.roman}. ${story.title_body}`,blocks=story.paragraphs.map(p=>p.kind==='verse'?'    '+p.text.replace(/\n/g,'\n    '):p.text);
  const expected=[heading,...blocks].join('\n\n')+'\n\n',actual=text.slice(section.start,section.end);assert.equal(actual,expected,'Exact independently collated narrative '+story.roman);
  assert.equal(sha(Buffer.from(actual)),audit.narratives[i].section_sha256);assert.equal(section.label,heading);
  for(const p of story.paragraphs){paragraphs++;if(p.kind==='prose')prose++;else if(p.kind==='verse')verse++;else if(p.kind==='attribution')attribution++;else assert.fail('Unknown block kind '+p.kind);}
  const pages=Core.paginate(text,section),rendered=pages.flatMap(p=>p.blocks);assert.equal(rendered.map(b=>b.text).join(''),actual);assert(pages.every(p=>p.words<=600));
  assert.equal(rendered.filter(b=>b.kind==='verse').length,story.paragraphs.filter(p=>p.kind==='verse').length);
  markers+=(actual.match(/\[unclear: [^\]]+\]/g)||[]).length;
}
assert.deepEqual({paragraphs,prose,verse,attribution,markers},{paragraphs:373,prose:367,verse:5,attribution:1,markers:4});
const body=suffix=>{const s=m.sections.find(s=>s.id==='yoruba-legends-'+suffix);assert(s);return text.slice(s.start,s.end);};
assert.equal(body('title'),['Yoruba Legends','M. I. Ogumefu, B.A.','London','The Sheldon Press'].join('\n\n')+'\n\n');
assert.equal(body('dedication-publication'),['To my husband','First published 1929','Printed in Great Britain'].join('\n\n')+'\n\n');
assert.equal(body('preface'),['Preface',...input.front_matter.preface.map(p=>p.text)].join('\n\n')+'\n\n');
for(const entry of input.front_matter.contents)assert(body('contents').includes(`${entry.roman}. ${entry.title_contents} — ${entry.print_start}\n`));
assert(body('contents').includes('IX. The Hunter and the Demon Polo, or, Orisa Oko'));assert(primary[8].label==='IX. Orisa Oko');assert(body('contents').includes('XX. Another Story of Leopard and His Spots'));assert.equal(primary[19].label,'XX. Another Story of Leopard’s Spots');
assert.equal(body('tortoise-divider'),'Stories of Tortoise\n\n');const divider=m.sections.find(s=>s.id==='yoruba-legends-tortoise-divider');assert.equal(primary[30].end,divider.start);assert.equal(divider.end,primary[31].start);assert.equal(divider.kind,'front');
for(const item of unclear){
  const storyBody=body('story-'+item.story_ordinal),context=body('unresolved-readings');assert(storyBody.includes(item.context));assert(storyBody.includes(item.marker));assert(context.includes(item.context));assert(context.includes('scan page '+item.pdf_pages.join(', ')));
}
assert.equal((body('unresolved-readings').match(/\[unclear:/g)||[]).length,4);assert.equal((text.match(/\[unclear:/g)||[]).length,8);
for(const item of input.metadata.normalization)assert(body('normalization').includes(item.replace('represented by page provenance','consult the original PDF for printed page context')));
for(const word of ['Olo̱fin','More̱mi','Iso̱kun','O̱yo̱','Ọmọ'])assert(text.includes(word));
assert(text.includes('a full ripe ear of corn'));assert(text.includes('The rats; his cousins'));assert(text.includes('twins,'));assert(body('editorial-note').includes('full songs'));assert(body('editorial-note').includes('No biography, separate translator'));assert(body('editorial-note').includes('rights not available'));
const oldAssets=Object.keys(pins).filter(p=>p.startsWith('dist/books/')).map(p=>p.slice('dist/books/'.length)).sort(),allAssets=fs.readdirSync(path.join(D,'books')).sort();assert.deepEqual(allAssets.filter(p=>!oldAssets.includes(p)),['yoruba-legends-derived-transcription.txt','yoruba-legends-source-scan.pdf']);
function inspect(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,e.name);if(e.isDirectory())inspect(p);else if(/\.(?:txt|json|js|html|css)$/.test(e.name)){const content=fs.readFileSync(p,'utf8');assert(!/\/workspace\/|\/tmp\/|yoruba-reading-repair|chunks\/|checks\/independent|parent_review_required|canonical_ingestion_performed/.test(content),'No private audit path/process in hosted files: '+p);}}}inspect(D);
console.log(`PASS: all fourteen catalog/spec/section records, ${oldAssets.length} original assets and ${bookmarks} bookmark endpoints preserved; exact five-hunk JavaScript / one-hunk CSS presentation exception; 40 narratives / ${paragraphs} blocks / ${verse} verses / 4 narrative uncertainties; 8 supplementary sections; original PDF hash/bytes; 3/3/3/4/2 shelves; no private audit leakage.`);
