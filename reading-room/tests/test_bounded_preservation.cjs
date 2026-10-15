'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),Core=require('../dist/reader-core.js');
const paths=process.argv.slice(2);assert(paths.length,'Supply the exact approved pre-feature baseline(s)');
const read=(r,p)=>fs.readFileSync(path.join(r,p)),json=(r,p)=>JSON.parse(read(r,p)),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const current=json(root,'dist/catalog.json'),manifests=json(root,'dist/sections.json').books,specs=json(root,'scripts/edition_specs.json').editions,reports=[];
for(const baselinePath of paths){
  const base=path.resolve(baselinePath);assert.notEqual(base,root);
  const pin=sha(read(base,'dist/reader-core.js'));
  assert(['a671c3615a5790e4ff0a4297153edab81d56fea540ae412d39428e03635f2bea','a1076d50c7ff38da27b923abc2e2eb9a789a90ec9da0f690c18f331669375017'].includes(pin),'Unknown pre-feature reader');
  const Original=require(path.join(base,'dist/reader-core.js')),catalog=json(base,'dist/catalog.json'),oldManifests=json(base,'dist/sections.json').books,oldSpecs=json(base,'scripts/edition_specs.json').editions;
  assert.deepEqual(current.slice(0,catalog.length),catalog);
  for(const name of ['classify','pageForOffset','sectionForOffset','validBookmark'])assert.equal(Core[name].toString(),Original[name].toString(),name+' remains literally unchanged');
  let sections=0,pages=0,bookmarkChecks=0;const assets=new Set();
  for(const book of catalog){
    assert.deepEqual(manifests[book.id],oldManifests[book.id]);assert.deepEqual(specs[book.id],oldSpecs[book.id]);
    for(const p of [book.path,book.notices,book.source_scan?.path,book.preservation_archive?.path].filter(Boolean))assets.add('dist/'+p);
    const text=read(root,'dist/'+book.path).toString('utf8'),manifest=manifests[book.id];
    for(const section of manifest.sections){
      sections++;assert.deepEqual(Core.blocksFor(text,section),Original.blocksFor(text,section));
      for(const target of [180,420,700]){
        const before=Original.paginate(text,section,target),after=Core.paginate(text,section,target);assert.deepEqual(after,before,book.id+' default pages at '+target);
        if(target!==420)continue;pages+=after.length;
        for(const offset of [section.start,section.end-1,...after.flatMap(p=>[p.start,p.end-1])]){assert(Core.validBookmark({version:2,sha256:manifest.sha256,sectionId:section.id,offset},manifest));assert.equal(Core.pageForOffset(after,offset),Original.pageForOffset(before,offset));bookmarkChecks++;}
      }
    }
  }
  for(const p of assets)assert.deepEqual(read(root,p),read(base,p),p+' original bytes');
  if(catalog.length===current.length)for(const p of ['dist/catalog.json','dist/sections.json','scripts/edition_specs.json','dist/app.js','dist/style.css','dist/index.html','dist/collection.js','dist/collections.json','dist/esoterica-register.json'])assert.deepEqual(read(root,p),read(base,p),p+' unchanged');
  reports.push({baselineReaderSha256:pin,editions:catalog.length,sections,pages,bookmarkChecks,sourceAssets:assets.size,targets:[180,420,700],allDefaultBlocksAndPagesExactlyEqual:true});
}
console.log(JSON.stringify({verified:true,reports},null,2));
