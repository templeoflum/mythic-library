'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const R=path.join(__dirname,'..'),D=path.join(R,'dist'),Core=require(path.join(D,'reader-core.js'));
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const {preservedBytes}=require('./preserved_baseline.cjs');
const old=read(path.join(__dirname,'eleven-edition-baseline.json')),catalog=read(path.join(D,'catalog.json')),manifest=read(path.join(D,'sections.json')),specs=read(path.join(R,'scripts/edition_specs.json'));
assert.equal(old.catalog.length,11);assert.equal(catalog.length,15);const historicalCatalog=catalog.filter(b=>b.id!=='yoruba-legends');assert.equal(historicalCatalog.length,14);let bookmarks=0;
for(const [p,h] of Object.entries(old.preserved_file_hashes))assert.equal(sha(preservedBytes(R,p)),h,'Preserve baseline bytes: '+p);
for(const book of old.catalog){
 const now=catalog.find(x=>x.id===book.id);assert(now);const {shelf:oldShelf,...oldMetadata}=book,{shelf:newShelf,...newMetadata}=now;assert.deepEqual(newMetadata,oldMetadata,'Only shelf label may change: '+book.id);
 assert.deepEqual(manifest.books[book.id],old.sections.books[book.id],'Preserve every prior section ID/offset/hash: '+book.id);
 assert.deepEqual(specs.editions[book.id],old.specs.editions[book.id],'Preserve prior source spec: '+book.id);
 for(const section of old.sections.books[book.id].sections.filter(x=>x.kind==='primary'))for(const offset of [section.start,section.end-1]){
  const bookmark={version:2,sha256:book.sha256,sectionId:section.id,offset,within:.3,atTop:false};assert(Core.validBookmark(bookmark,manifest.books[book.id]));bookmarks++;
 }
}
const groups=new Map();for(const b of historicalCatalog){const books=groups.get(b.shelf)||[];books.push(b.id);groups.set(b.shelf,books);}
assert.equal(groups.size,5);assert([...groups.values()].every(x=>x.length<=4));assert.deepEqual([...groups.values()].map(x=>x.length).sort(),[2,3,3,3,3]);
assert.deepEqual(groups.get('African & diaspora collections'),['anansi-tales','zanzibar-tales','ikom-folk-stories-from-southern-nigeria']);
const z=catalog.find(b=>b.id==='zanzibar-tales'),x=catalog.find(b=>b.id==='kaffir-xhosa-folk-lore');assert.equal(z.author_label,'Translator');assert.equal(z.author,'George W. Bateman');assert.equal(z.illustrator,'Walter Bobbett');
assert.equal(x.title,'Xhosa folk-lore (Theal, 1886)');assert(x.bibliographic_title.startsWith('Kaffir folk-lore: A selection'));assert(x.display_title_note.includes('descriptive'));assert(x.edition.includes('Second edition'));assert(x.edition.includes('1886'));assert.equal(x.translator,null);
const ztext=fs.readFileSync(path.join(D,z.path),'utf8'),zm=manifest.books[z.id],zp=zm.sections.filter(s=>s.kind==='primary'),romans=['I','II','III','IV','V','VI','VII','VIII','IX','X'];assert.equal(zp.length,10);
for(const [i,s] of zp.entries()){const body=ztext.slice(s.start,s.end);assert(body.includes('\r\n'+romans[i]+'.\r\n')||body.startsWith(romans[i]+'.\r\n'));assert(!new RegExp('(?:^|\\n)'+(romans[i+1]||'XI')+'\\.\\r?$','m').test(body));}
assert(ztext.slice(zp[0].start,zp[0].end).startsWith('ZANZIBAR TALES.'));assert(ztext.slice(zp.at(-1).start,zp.at(-1).end).includes('Hasseeboo was loved by all as a great physician.'));assert(!ztext.slice(zp.at(-1).start,zp.at(-1).end).includes('*** END'));
const xt=fs.readFileSync(path.join(D,x.path),'utf8'),xm=manifest.books[x.id],xp=xm.sections.filter(s=>s.kind==='primary');assert.equal(xp.length,23);const variant=xp[1];assert(variant.label.includes('Barolong / Sechuana'));assert.equal(variant.sourceAttribution.peopleAsPrinted,'Barolongs');assert.equal(variant.sourceAttribution.languageAsPrinted,'Sechuana');assert(xt.slice(variant.start,variant.end).includes(variant.sourceAttribution.sourceEvidence));assert.equal(xm.sections.filter(s=>s.id.includes('-note-')).length,13);assert(xm.sections.some(s=>s.id.endsWith('-footnotes')&&s.kind==='back'));assert(xm.sections.some(s=>s.id.endsWith('-proverbs')&&s.kind==='back'));
assert.equal(xp.filter(s=>s.label.includes('Kenkebe')).length,2);assert.equal(xp.filter(s=>s.label.includes('Bird That Made Milk')).length,2);
assert(xt.includes('Ndahlangana Nonothloya.')&&xt.includes('We cooked each other,')&&xt.includes('Ndahamba ndayakuva indaba,')&&xt.includes('About rain from the girls.'));
for(const b of [z,x]){assert(b.preservation_archive);assert.equal(b.preservation_archive.sha256,sha(fs.readFileSync(path.join(D,b.preservation_archive.path))));assert(b.qualification_notes.length>=8);assert(b.rights.includes('USA'));assert(b.qualification_notes.some(x=>x.includes('No page-by-page')));}
console.log(`PASS: all eleven source assets, section manifests, source specs and ${bookmarks} prior bookmark endpoints preserved; historical 3/3/3/3/2 shelves; all new tale boundaries, individual attribution, creator roles, notices, preserved archives and qualifiers checked.`);
