'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const Core=require('../dist/reader-core.js');
const section=(text,extra={})=>({id:'fixture',kind:'primary',start:0,end:text.length,...extra});
function check(text,part,target=420){
  const pages=Core.paginate(text,part,target),blocks=pages.flatMap(p=>p.blocks);
  assert.equal(blocks.map(b=>b.text).join(''),text.slice(part.start,part.end));
  let cursor=part.start;
  for(const block of blocks){assert.equal(block.start,cursor);assert.equal(block.text,text.slice(block.start,block.end));cursor=block.end;}
  assert.equal(cursor,part.end);
  for(const [i,page] of pages.entries()){
    assert.equal(Core.pageForOffset(pages,page.start),i);assert.equal(Core.pageForOffset(pages,page.end-1),i);
    assert.equal(page.blocks.map(b=>b.text).join(''),text.slice(page.start,page.end));
    assert(page.blocks.reduce((sum,b)=>sum+(b.verseLines||0),0)<=48,'Audited verse pages have at most 48 original nonempty lines');
    if(i<pages.length-1)assert.notEqual(page.blocks.at(-1).kind,'heading');
  }
  return {pages,blocks};
}
const poem='Of Mans First Disobedience, and the Fruit\r\nOf that Forbidden Tree, whose mortal tast\r\nBrought Death into the World, and all our woe,\r\n\r\nSing Heav’nly Muse\r\nAnd tell the tale.\r\n';
assert.equal(Core.classify(poem.split('\r\n\r\n')[0]),'paragraph','Unindented verse is not guessed from line length');
const explicit=check(poem,section(poem,{textFormat:'verse'}));
assert(explicit.blocks.every(b=>b.kind==='verse'&&b.explicitVerse));assert.equal(explicit.blocks.length,2);
assert(explicit.blocks[0].text.endsWith('\r\n\r\n'),'Stanza separator remains in its source block');
const wrapped='This is ordinary wrapped prose with no indentation,\nwhich continues over a second line and ends here.\n';
assert.equal(check(wrapped,section(wrapped)).blocks[0].kind,'paragraph');
assert.equal(check(wrapped,section(wrapped,{textFormat:'prose'})).blocks[0].kind,'paragraph');
const deceptive='    Two indented prose lines are editorial notes,\n    not proof that their author composed a poem.\n';
assert.equal(check(deceptive,section(deceptive,{textFormat:'prose'})).blocks[0].kind,'paragraph');
assert.equal(check(deceptive,section(deceptive)).blocks[0].kind,'verse','Legacy indentation detection is unchanged');
const upper='ALL CAPS POETIC WORDS\nSECOND POETIC LINE\n';
assert.equal(check(upper,section(upper,{textFormat:'verse'})).blocks[0].kind,'verse','Explicit verse beats uppercase/table heuristics');
const front='\uFEFFFront matter 🕮\r\n\r\n',heading='BOOK I.\r\n\r\n',caption='[Illustration: THE SHIP.]\r\n\r\n',notes='NOTES.\r\n\r\n'+deceptive;
const mixed=front+heading+poem+caption+notes,begin=front.length+heading.length,end=begin+poem.length;
const mixedPart=section(mixed,{headingStarts:[front.length],textFormatRanges:[{start:begin,end,format:'verse'},{start:end+caption.length,end:mixed.length,format:'prose'}]});
const mixture=check(mixed,mixedPart).blocks;
assert.equal(mixture.find(b=>b.start===front.length).kind,'heading');
assert(mixture.filter(b=>b.start>=begin&&b.start<end).every(b=>b.kind==='verse'));
assert(mixture.filter(b=>b.start<begin||b.start>=end).every(b=>b.kind!=='verse'));
const tight='Wrapped prose at the start.\nVerse starts without a blank line\nVerse ends right here\nWrapped prose after it.\n';
const lo=tight.indexOf('Verse starts'),hi=tight.indexOf('Wrapped prose after');
assert.deepEqual(check(tight,section(tight,{textFormatRanges:[{start:lo,end:hi,format:'verse'}]})).blocks.map(b=>b.kind),['paragraph','verse','paragraph']);
// Explicit auto ranges opt back into historical heuristics within a verse section.
assert.equal(check(wrapped,section(wrapped,{textFormat:'verse',textFormatRanges:[{start:0,end:wrapped.length,format:'auto'}]})).blocks[0].kind,'paragraph');
for(const newline of ['\n','\r\n','\r']){
  const long=Array.from({length:137},(_,i)=>`Line ${i} holds seven small words here.`).join(newline)+newline+newline;
  const result=check(long,section(long,{textFormat:'verse'}));
  assert(result.pages.length>=3);assert(result.blocks.some(b=>b.continuation));
  for(const b of result.blocks){assert.equal(b.paragraphStart,0);assert(b.words<=420);assert(b.end===long.length||long.slice(0,b.end).endsWith(newline));if(newline==='\r\n')assert.notEqual(long[b.end-1],'\r');}
}
const sparse=('word\n'.repeat(130))+'\n';assert.equal(check(sparse,section(sparse,{textFormat:'verse'})).pages.length,3,'Short lines also have bounded pages');
const stanzas=Array.from({length:6},()=>('word\n'.repeat(12))+'\n').join('');
const stanzaResult=check(stanzas,section(stanzas,{textFormat:'verse'}));assert.equal(stanzaResult.blocks.length,6);assert(stanzaResult.blocks.every(b=>!b.continuation));assert.equal(stanzaResult.pages.length,2);
// A correctly audited illustration heading must not glue two full verse pages together.
const firstVerse='Verse before the illustrated heading.\n'.repeat(46)+'\n',captionOne='GREEK GALLEY\n\n',middleVerse='Verse between the headings.\n'.repeat(6)+'\n',captionTwo='PROSERPINE\n\n',lastVerse='Verse after the illustrated heading.\n'.repeat(48)+'\n';
const captioned=firstVerse+captionOne+middleVerse+captionTwo+lastVerse;
const captionResult=check(captioned,section(captioned,{textFormat:'verse',headingStarts:[firstVerse.length,firstVerse.length+captionOne.length+middleVerse.length]}));
assert.equal(captionResult.pages.length,3);assert.equal(captionResult.pages[1].blocks[0].kind,'heading');assert.equal(captionResult.pages[2].blocks[0].kind,'heading');
assert(captionResult.pages.every(p=>p.blocks.some(b=>b.kind==='verse')),'Caption movement never creates a heading-only page');
const enormousLine='word '.repeat(800)+'\n';assert.equal(check(enormousLine,section(enormousLine,{textFormat:'verse'})).blocks.length,1,'A single irreducible source line is never rewritten to satisfy a word cap');
const save=Intl.Segmenter;Intl.Segmenter=undefined;try{check(poem,section(poem,{textFormat:'verse'}));check(sparse,section(sparse,{textFormat:'verse'}));}finally{Intl.Segmenter=save;}
const css=fs.readFileSync(path.join(__dirname,'../dist/style.css'),'utf8');
assert.match(css,/#book-text p\{white-space:normal/);assert.match(css,/#book-text \.verse\{white-space:pre-line/);assert(css.includes('overflow-wrap:break-word'));
console.log('PASS: unindented verse opt-in, prose isolation, captions/notes/front matter, explicit overrides, stanza identity, CRLF/CR/LF and UTF-16 preservation, line-only pagination, sparse-line bounds, and unchanged prose CSS. Rendering not inferred from these assertions.');
