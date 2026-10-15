'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const R=path.join(__dirname,'..'),D=path.join(R,'dist'),Core=require(path.join(D,'reader-core.js'));
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const {preservedBytes}=require('./preserved_baseline.cjs');
const old=read(path.join(__dirname,'thirteen-edition-baseline.json')),catalog=read(path.join(D,'catalog.json')),manifest=read(path.join(D,'sections.json')),specs=read(path.join(R,'scripts/edition_specs.json')),audit=read(path.join(__dirname,'ikom-edition-audit.json'));
assert.equal(old.catalog.length,13);assert.equal(catalog.length,15);const historicalCatalog=catalog.filter(b=>b.id!=='yoruba-legends');assert.equal(historicalCatalog.length,14);let bookmarks=0;const shelfChanges=[];
for(const [p,h] of Object.entries(old.preserved_file_hashes))assert.equal(sha(preservedBytes(R,p)),h,'Preserve old core/source bytes: '+p);
for(const book of old.catalog){
 const now=catalog.find(x=>x.id===book.id);assert(now);const {shelf:a,...am}=book,{shelf:b,...bm}=now;assert.deepEqual(bm,am,'Only shelf label may change: '+book.id);if(a!==b)shelfChanges.push(book.id);
 assert.deepEqual(manifest.books[book.id],old.sections.books[book.id],'Every old section/offset/hash/attribution preserved: '+book.id);
 assert.deepEqual(specs.editions[book.id],old.specs.editions[book.id],'Every old source specification preserved: '+book.id);
 for(const section of old.sections.books[book.id].sections.filter(x=>x.kind==='primary'))for(const offset of [section.start,section.end-1]){
  const mark={version:2,sha256:book.sha256,sectionId:section.id,offset,within:.3,atTop:false};assert(Core.validBookmark(mark,manifest.books[book.id]));bookmarks++;
 }
}
assert.deepEqual(shelfChanges,['south-african-folk-tales','kaffir-xhosa-folk-lore']);assert.equal(bookmarks,1064);
const groups=new Map();for(const b of historicalCatalog){const group=groups.get(b.shelf)||[];group.push(b.id);groups.set(b.shelf,group);}
assert.equal(groups.size,5);assert([...groups.values()].every(x=>x.length<=4));assert.deepEqual([...groups.values()].map(x=>x.length).sort(),[2,3,3,3,3]);
assert.deepEqual(groups.get('Southern African collections'),['south-african-folk-tales','kaffir-xhosa-folk-lore']);
assert.deepEqual(groups.get('African & diaspora collections'),['anansi-tales','zanzibar-tales','ikom-folk-stories-from-southern-nigeria']);
assert(!old.catalog.some(b=>b.id==='yoruba-legends'));assert(!Object.keys(old.specs.editions).includes('yoruba-legends'));assert(!Object.keys(old.sections.books).includes('yoruba-legends'));assert(catalog.some(b=>b.id==='yoruba-legends'));assert(specs.editions['yoruba-legends']);assert(manifest.books['yoruba-legends']);
const id='ikom-folk-stories-from-southern-nigeria',book=catalog.find(b=>b.id===id),m=manifest.books[id],spec=specs.editions[id],raw=fs.readFileSync(path.join(D,book.path)),text=raw.toString('utf8'),p=m.sections.filter(s=>s.kind==='primary');
assert.equal(sha(raw),audit.source_sha256);assert.equal(p.length,34);assert.equal(m.sections.length,43);assert.equal(m.defaultSectionId,id+'-story-1');assert.equal(book.translator,null);assert(book.edition.includes('1913'));assert(book.rights.includes('USA'));assert(book.note.includes('1910'));assert(book.qualification_notes.some(x=>x.includes('no Lang introduction')));assert(book.qualification_notes.some(x=>x.includes('simplified English')));
for(const [i,section] of p.entries()){
 const expected=audit.narratives[i],body=text.slice(section.start,section.end);assert.equal(expected.number,i+1);assert.equal(section.start,expected.start);assert.equal(section.end,expected.end);assert.equal(sha(Buffer.from(text.slice(expected.bodyStart,expected.end))),expected.bodySha256);
 assert.equal(section.sourceAttribution.sourceEvidence,expected.provenance);assert(body.includes(expected.provenance));assert(!body.includes('*** END OF THE PROJECT'));assert(!body.includes('[Illustration: _Plate'));
 const pages=Core.paginate(text,section);assert.equal(pages.flatMap(x=>x.blocks.map(b=>b.text)).join(''),body);assert(pages.every(x=>x.words<=600));
}
assert(p[6].label.includes('local origin uncertain'));assert(p[6].sourceAttribution.display.includes('Local origin uncertain'));assert(p[6].sourceAttribution.sourceEvidence.includes('Cavally on the Kroo Coast'));assert(p[6].sourceAttribution.sourceEvidence.includes('some doubt'));
assert(text.slice(p[1].start,p[1].end).includes('_Note._'));assert(text.slice(p[15].start,p[15].end).includes('_Author’s Note._'));assert(p[26].sourceAttribution.sourceEvidence.includes('1.8.7.'));
const latin=text.slice(p[33].start,p[33].end);assert(latin.startsWith('QUOMODO EVENIT UT PENIS PRIMUM CUM VAGINA COIIT.'));assert(latin.includes('Penis autem olim rure solus habitabat'));assert(latin.includes('(Told by Ennenni'));assert(p[33].label.startsWith('Unnumbered Latin tale:'));assert.equal(p[33].sourceAttribution.languageAsPrinted,'Latin narrative; English source credit');
const preface=m.sections.find(x=>x.id===id+'-preface'),pt=text.slice(preface.start,preface.end);assert.equal(preface.kind,'front');assert(pt.includes('translated by an interpreter'));assert(pt.includes('certain passages containing\r\nobjectionable matter have been omitted'));
for(const suffix of ['plate-i','plate-ii','printer','footnotes','transcriber','license'])assert(m.sections.some(s=>s.id===id+'-'+suffix&&s.kind==='back'));
const notes=m.sections.find(s=>s.id===id+'-footnotes'),nt=text.slice(notes.start,notes.end);assert.equal([...nt.matchAll(/^\[\d+\]/gm)].length,11);assert(text.includes('THE FULL PROJECT GUTENBERG™ LICENSE'));assert(text.includes('Section 5.'));
assert.deepEqual(book.preservation_archive,spec.preservationArchive);assert.equal(sha(fs.readFileSync(path.join(D,book.preservation_archive.path))),book.preservation_archive.sha256);assert.equal(audit.archive_assets.filter(x=>x.path.endsWith('.jpg')).length,5);assert(audit.archive_assets.some(x=>x.path==='images/fig1big.jpg'));assert(audit.archive_assets.some(x=>x.path==='images/fig2big.jpg'));
console.log(`PASS: all thirteen editions, 25 old core/source asset hashes, exact metadata except two shelf labels, complete old sections/specs and ${bookmarks} bookmark endpoints preserved; all 34 Ikom bodies/provenance records, Latin ending, 11 footnotes, full archive and five small shelves verified; Yoruba absent from historical baseline; separate derived addition present.`);
