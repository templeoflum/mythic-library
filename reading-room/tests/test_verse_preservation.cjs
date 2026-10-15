'use strict';
// Supply the exact pre-feature checkout, not a historical fixed-count projection.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),base=path.resolve(process.argv[2]||'');
assert(process.argv[2],'Usage: node tests/test_verse_preservation.cjs PINNED_BASELINE_ROOT');
assert.notEqual(base,root);
const read=(r,p)=>fs.readFileSync(path.join(r,p)),json=(r,p)=>JSON.parse(read(r,p)),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
assert.equal(sha(read(base,'dist/reader-core.js')),'a1076d50c7ff38da27b923abc2e2eb9a789a90ec9da0f690c18f331669375017','Baseline is the reviewed pre-feature reader');
const Original=require(path.join(base,'dist/reader-core.js')),Core=require('../dist/reader-core.js');
for(const name of ['classify','pageForOffset','sectionForOffset','validBookmark'])assert.equal(Core[name].toString(),Original[name].toString(),`${name} stays literally unchanged`);
for(const file of ['dist/catalog.json','dist/sections.json','scripts/edition_specs.json','dist/style.css','dist/index.html','dist/collection.js','dist/collections.json','dist/esoterica-register.json'])assert.deepEqual(read(root,file),read(base,file),file+' remains byte-identical');
const catalog=json(base,'dist/catalog.json'),manifests=json(base,'dist/sections.json').books;
let sectionCount=0,pageCount=0,bookmarks=0,assets=0;
const assetPaths=new Set();
for(const book of catalog){
  for(const p of [book.path,book.notices,book.source_scan?.path,book.preservation_archive?.path].filter(Boolean))assetPaths.add('dist/'+p);
  const text=read(root,'dist/'+book.path).toString('utf8'),manifest=manifests[book.id];
  assert.equal(sha(read(root,'dist/'+book.path)),book.sha256);
  for(const section of manifest.sections){
    sectionCount++;
    assert.deepEqual(Core.blocksFor(text,section),Original.blocksFor(text,section),book.id+' original blocks');
    for(const target of [180,420,700]){
      const before=Original.paginate(text,section,target),after=Core.paginate(text,section,target);
      assert.deepEqual(after,before,book.id+' exact pagination at '+target);
      if(target!==420)continue;
      pageCount+=after.length;
      for(const offset of [section.start,section.end-1,...after.flatMap(p=>[p.start,p.end-1])]){
        const mark={version:2,sha256:manifest.sha256,sectionId:section.id,offset,within:.3,atTop:false};
        assert(Core.validBookmark(mark,manifest));assert.equal(Core.pageForOffset(after,offset),Original.pageForOffset(before,offset));bookmarks++;
      }
    }
  }
}
for(const file of assetPaths){assert.deepEqual(read(root,file),read(base,file),file+' remains byte-identical');assets++;}
console.log(JSON.stringify({verified:true,editions:catalog.length,sections:sectionCount,pages:pageCount,bookmarkChecks:bookmarks,sourceAssets:assets,targets:[180,420,700],allPriorBlocksAndPagesExactlyEqual:true,bookmarkFunctionsLiterallyUnchanged:true}));
