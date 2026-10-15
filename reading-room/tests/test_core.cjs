'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.join(__dirname,'../dist'),Core=require(path.join(root,'reader-core.js'));
const catalog=JSON.parse(fs.readFileSync(path.join(root,'catalog.json'),'utf8'));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'sections.json'),'utf8'));
const specs=JSON.parse(fs.readFileSync(path.join(__dirname,'../scripts/edition_specs.json'),'utf8')).editions;
assert.deepEqual(catalog.map(book=>book.id).sort(),Object.keys(specs).sort());assert.deepEqual(Object.keys(manifest.books).sort(),Object.keys(specs).sort());assert.equal(manifest.offsetEncoding,'utf-16');
const report=[];
for(const book of catalog){
  const data=manifest.books[book.id],raw=fs.readFileSync(path.join(root,book.path)),text=raw.toString('utf8');
  assert.equal(crypto.createHash('sha256').update(raw).digest('hex'),book.sha256);
  if(book.preservation_archive){const archive=book.preservation_archive,preserved=fs.readFileSync(path.join(root,archive.path));assert.equal(preserved.length,archive.bytes);assert.equal(crypto.createHash('sha256').update(preserved).digest('hex'),archive.sha256);assert.deepEqual(archive,specs[book.id].preservationArchive);}
  assert.equal(raw.length,book.bytes);
  if(book.source_scan){const scan=book.source_scan,preserved=fs.readFileSync(path.join(root,scan.path));assert.equal(preserved.length,scan.bytes);assert.equal(crypto.createHash('sha256').update(preserved).digest('hex'),scan.sha256);assert.deepEqual(scan,specs[book.id].sourceScan);assert.equal(preserved.subarray(0,5).toString(),'%PDF-');}
  assert.equal(data.sha256,book.sha256);assert.equal(data.sha256,specs[book.id].sha256);assert.equal(text.length,data.length);assert.equal(data.sections.filter(section=>section.kind==='primary').length,specs[book.id].primarySectionCount);
  let rebuilt='',cursor=0,passages=0,maxWords=0,continuations=0;
  for(const section of data.sections){
    assert.equal(section.start,cursor);cursor=section.end;
    const pages=Core.paginate(text,section);assert(pages.length);
    assert.equal(pages[0].start,section.start);assert.equal(pages.at(-1).end,section.end);
    const blocks=pages.flatMap(page=>page.blocks);const segment=blocks.map(block=>block.text).join('');
    assert.equal(segment,text.slice(section.start,section.end));rebuilt+=segment;
    for(const offset of section.headingStarts||[]){assert(Number.isInteger(offset)&&offset>=section.start&&offset<section.end);assert(offset===0||text[offset-1]==='\n');assert.equal(blocks.find(block=>offset>=block.start&&offset<block.end).kind,'heading','Verified source heading must remain a heading');}
    for(let i=1;i<blocks.length;i++)assert.equal(blocks[i-1].end,blocks[i].start);
    for(const [index,page]of pages.entries()){
      assert.equal(Core.pageForOffset(pages,page.start),index);assert.equal(Core.pageForOffset(pages,page.end-1),index);
      assert.equal(page.blocks.map(block=>block.text).join(''),text.slice(page.start,page.end));
      if(index<pages.length-1)assert.notEqual(page.blocks.at(-1).kind,'heading','Heading must stay with following source text');
      for(const block of page.blocks){assert.equal(block.text,text.slice(block.start,block.end));if(block.continuation){continuations++;assert(block.paragraphStart<block.start);assert(block.kind==='paragraph'||(block.kind==='verse'&&block.explicitVerse),'Only prose or explicitly audited verse may continue');if(block.kind==='verse')assert(/[\r\n]/.test(text[block.start-1]),'Verse continuations begin at original line boundaries');}}
      if(section.kind==='primary'){passages++;maxWords=Math.max(maxWords,page.words);assert(page.words<=600,`${book.id} unbounded passage: ${page.words}`);}
    }
  }
  assert.equal(cursor,text.length);assert.deepEqual(Buffer.from(rebuilt),raw);
  const start=data.sections.find(s=>s.id===data.defaultSectionId);assert.equal(start.kind,'primary');
  const first=Core.paginate(text,start)[0].blocks.map(block=>block.text).join('');assert(first.includes(specs[book.id].primaryOpening));assert(!first.includes('PROJECT GUTENBERG'));assert(!first.includes('INTRODUCTION.'));
  const bookmark={version:2,sha256:data.sha256,sectionId:start.id,offset:start.start};assert(Core.validBookmark(bookmark,data));assert(!Core.validBookmark({...bookmark,sha256:'bad'},data));assert(!Core.validBookmark({...bookmark,offset:-1},data));assert(!Core.validBookmark({...bookmark,sectionId:'absent'},data));
  if(book.notices)assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,book.notices))).digest('hex'),data.originalSource.sha256);
  report.push({book:book.title,sections:data.sections.length,passages,maxWords,continuedParagraphFragments:continuations});
}
const anansi=manifest.books['anansi-tales'];assert.equal(anansi.sections.filter(s=>/^anansi-story-\d+$/.test(s.id)).length,149);assert.equal(anansi.sections.filter(s=>s.kind==='primary').length,151);
assert.equal(Core.classify('    First line\n    Second line\n'),'verse');assert.equal(Core.classify('A prose line\nanother wrapped line.\n'),'paragraph');
// Unsupported sentence segmentation degrades safely to full paragraphs, without source edits.
const sample=('One sentence. '.repeat(700))+'\n\n';const originalSegmenter=Intl.Segmenter;Intl.Segmenter=undefined;assert.equal(Core.paginate(sample,{start:0,end:sample.length}).flatMap(p=>p.blocks.map(b=>b.text)).join(''),sample);Intl.Segmenter=originalSegmenter;
const css=fs.readFileSync(path.join(root,'style.css'),'utf8'),html=fs.readFileSync(path.join(root,'index.html'),'utf8');assert(css.includes('prefers-reduced-motion'));assert(css.includes('max-width:66ch'));assert(css.includes('min-height:0'));assert(css.includes('@media print'));assert(!css.includes('text-align:justify'));assert(html.includes('name="viewport" content="width=device-width,initial-scale=1"'));assert(!html.includes('maximum-scale'));assert(!html.includes('user-scalable=no'));
fs.writeFileSync(path.join(__dirname,'source-test-results.json'),JSON.stringify({verified:true,books:report},null,2)+'\n');console.log(JSON.stringify(report,null,2));console.log('PASS: all source bytes, contiguous sections and passage spans, story-first starts, section counts, bounded primary passages, paragraph continuity, verse classification, bookmark validity, notice hashes, no font/viewport restrictions.');
