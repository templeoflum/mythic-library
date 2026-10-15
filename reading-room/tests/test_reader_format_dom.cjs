'use strict';
// Reuse the existing reader's DOM simulation; this is not rendered-browser QA.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),{createRequire}=require('node:module');
const source=fs.readFileSync(path.join(__dirname,'test_interactions.cjs'),'utf8');
const marker='(async()=>{await tick();await tick();';
if(source.split(marker).length!==2)throw Error('Existing DOM harness changed; review this test before reuse');
const harness=source.slice(0,source.indexOf(marker));
const scenario=String.raw`
(async()=>{
  await tick();await tick();
  const front='A wrapped source introduction\nthat remains ordinary prose.\n\n';
  const heading='BOOK I.\n\n',verse=('Unindented verse has seven words per line.\n'.repeat(117))+'\n';
  const caption='[Illustration: THE SHIP.]\n\n',last='BOOK II.\n\nThe final line\nOf this small test.\n\n',notes='NOTES\n\nA wrapped editorial note\ncontinues on this line.\n';
  const text=front+heading+verse+caption+last+notes;
  const start=front.length,next=start+heading.length+verse.length+caption.length,back=next+last.length;
  const fixture={id:'verse-dom-fixture',title:'Verified verse fixture',author:'Fixture',edition:'Audited verse test',path:'books/fixture.txt',source:'https://example.org/fixture',sha256:'fixture'};
  const manifest={sha256:'fixture',length:text.length,defaultSectionId:'fixture-book-1',sections:[
    {id:'fixture-front',label:'Introduction',kind:'front',start:0,end:start},
    {id:'fixture-book-1',label:'Book I',kind:'primary',start,end:next,headingStarts:[start],textFormatRanges:[{start:start+heading.length,end:start+heading.length+verse.length,format:'verse'}]},
    {id:'fixture-book-2',label:'Book II',kind:'primary',start:next,end:back,headingStarts:[next],textFormat:'verse'},
    {id:'fixture-notes',label:'Notes',kind:'back',start:back,end:text.length,textFormat:'prose'}]};
  context.fixture=fixture;context.fixtureManifest=manifest;context.fixtureText=text;
  run('state.books.push(fixture);state.manifests[fixture.id]=fixtureManifest;state.cache.set(fixture.id,fixtureText)');
  await run('openBook(fixture.id)');
  assert.equal(run('state.section.id'),'fixture-book-1');
  assert.equal(get('book-text').children[0].tagName,'H2');
  assert(get('book-text').children.some(n=>n.className==='verse'&&n.textContent.includes('\n')));
  for(const section of manifest.sections){
    run('showSection('+JSON.stringify(section.id)+')');
    for(let p=0;p<run('state.pages.length');p++){
      run('state.page='+p+';renderPage()');
      for(const node of get('book-text').children){
        assert.equal(node.textContent,text.slice(Number(node.dataset.offset),Number(node.dataset.end)));
        if(section.kind!=='primary')assert.notEqual(node.className,'verse');
        if(node.textContent.includes('[Illustration:'))assert.notEqual(node.className,'verse');
      }
    }
  }
  run('showSection("fixture-book-1");turnPage(1)');
  assert(get('reading-context').textContent.includes('continued'));
  const offset=run('state.pages[state.page].start');
  run('setFont(9);closeBook()');await run('openBook(fixture.id)');
  assert.equal(run('state.pages[state.page].start'),offset);
  const saved=values.get('mythic:bookmark:v2:verse-dom-fixture');
  run('showSection("fixture-notes");closeBook()');assert.equal(values.get('mythic:bookmark:v2:verse-dom-fixture'),saved);
  await run('openBook(fixture.id)');assert.equal(run('state.section.id'),'fixture-book-1');assert.equal(run('state.pages[state.page].start'),offset);
  run('state.page=state.pages.length-1;renderPage();turnPage(1)');assert.equal(run('state.section.id'),'fixture-book-2');
  run('turnPage(-1)');assert.equal(run('state.section.id'),'fixture-book-1');assert.equal(run('state.page'),run('state.pages.length-1'));
  console.log('PASS: explicit verse DOM source spans, heading/caption/prose separation, continuation, source bookmarks/font changes, supplementary isolation and book crossings. DOM simulation only.');
})().catch(error=>{console.error(error);process.exitCode=1;});
`;
vm.runInNewContext(harness+scenario,{require:createRequire(path.join(__dirname,'test_interactions.cjs')),__dirname,console,process,setTimeout,clearTimeout,setImmediate,TextEncoder,TextDecoder,URLSearchParams});
