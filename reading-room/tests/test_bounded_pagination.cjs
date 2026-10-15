'use strict';
const assert=require('node:assert/strict'),Core=require('../dist/reader-core.js');
const paragraph=n=>'Word '+('word '.repeat(n-2))+'end.\r\n\r\n';
const heading=n=>('HEADING '.repeat(n)).trim()+'\r\n\r\n';
const section=(text,extra={})=>({id:'fixture',kind:'primary',start:0,end:text.length,...extra});
function verify(text,part,target=420){
  const pages=Core.paginate(text,part,target),blocks=pages.flatMap(p=>p.blocks);
  assert.equal(blocks.map(b=>b.text).join(''),text.slice(part.start,part.end));
  let cursor=part.start;
  for(const b of blocks){assert.equal(b.start,cursor);assert.equal(b.text,text.slice(b.start,b.end));cursor=b.end;if(b.continuation)assert(b.paragraphStart<b.start);}
  assert.equal(cursor,part.end);
  for(const [i,p] of pages.entries()){
    assert.equal(Core.pageForOffset(pages,p.start),i);assert.equal(Core.pageForOffset(pages,p.end-1),i);
    assert.equal(p.blocks.map(b=>b.text).join(''),text.slice(p.start,p.end));
    if(i<pages.length-1)assert.notEqual(p.blocks.at(-1).kind,'heading','Keep heading with following text');
  }
  return pages;
}
for(const [a,b] of [[143,495],[135,488]]){
  const text=paragraph(a)+paragraph(b);
  assert.equal(verify(text,section(text)).length,1,'Legacy behavior remains unchanged');
  const pages=verify(text,section(text,{pagination:'bounded'}));
  assert.equal(pages.length,2);assert.deepEqual(pages.map(p=>p.words),[a,b]);
}
const chained=heading(5)+paragraph(190)+heading(3)+paragraph(221)+heading(4)+paragraph(338);
assert.equal(Math.max(...verify(chained,section(chained)).map(p=>p.words)),761);
const chainPages=verify(chained,section(chained,{pagination:'bounded'}));assert(chainPages.every(p=>p.words<=525));assert(chainPages.every(p=>p.blocks.some(b=>b.kind!=='heading')));
const adjacent=paragraph(300)+heading(3)+heading(4)+paragraph(350);
const adjacentPages=verify(adjacent,section(adjacent,{pagination:'bounded'}));
assert.equal(adjacentPages.length,2);assert.deepEqual(adjacentPages[1].blocks.map(b=>b.kind),['heading','heading','paragraph']);
const long=paragraph(101).replace(/\r\n\r\n$/,' ')+paragraph(501);
assert.equal(verify(long,section(long))[0].words,602,'Legacy sentence minimum reproduces the long-paragraph overflow');
const longPages=verify(long,section(long,{pagination:'bounded'}));assert(longPages.every(p=>p.words<=525));assert.equal(longPages[1].blocks[0].paragraphStart,0);assert(longPages[1].blocks[0].continuation);
const intro='\ufeffA title 🕮\r\n\r\n',one=paragraph(70),subheading='A verified mixed-case subheading\r\n\r\n',two=paragraph(70),text=intro+one+subheading+two;
const start=intro.length+one.length;
const anchored=section(text,{pagination:'bounded',headingStarts:[start],passageBreakStarts:[start]});
const anchoredPages=verify(text,anchored);assert.equal(anchoredPages.length,2);assert.equal(anchoredPages[1].start,start);assert.equal(anchoredPages[1].blocks[0].kind,'heading');
assert.equal(verify(text,{...anchored,pagination:'legacy'}).length,1,'Legacy policy does not silently activate passage-break metadata');
// Exact whole-line anchors can isolate a natural heading even without a blank source line.
const tight='Introductory source words.\r\nA mixed-case title\r\n\r\nFollowing source prose.\r\n';
const cut=tight.indexOf('A mixed-case');const tightPages=verify(tight,section(tight,{pagination:'bounded',headingStarts:[cut],passageBreakStarts:[cut]}));assert.equal(tightPages.length,2);assert.equal(tightPages[1].start,cut);
// No permission to rewrite an irreducible sentence or an unaudited verse block.
const irreducible=paragraph(620);assert(verify(irreducible,section(irreducible,{pagination:'bounded'})).some(p=>p.words>600),'Source gate must still reject an irreducible oversized sentence');
const saved=Intl.Segmenter;Intl.Segmenter=undefined;try{assert.equal(verify(long,section(long,{pagination:'bounded'}))[0].words,602);}finally{Intl.Segmenter=saved;}
const sample=paragraph(20)+heading(2)+paragraph(100);
for(const target of [180,420,700])verify(sample,section(sample,{pagination:'bounded'}),target);
console.log('PASS: explicit bounded policy, both Grimm regressions, chained/adjacent heading groups, sentence minimum-fill regression, exact anchored passage breaks, CRLF/BOM/UTF-16, source identities, no orphan headings, legacy default and strict irreducible-source gate.');
