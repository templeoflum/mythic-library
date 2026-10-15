'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),{createRequire}=require('node:module');
const source=fs.readFileSync(path.join(__dirname,'test_interactions.cjs'),'utf8'),marker='(async()=>{await tick();await tick();';
if(source.split(marker).length!==2)throw Error('Existing DOM harness changed; review before reuse');
const harness=source.slice(0,source.indexOf(marker));
const scenario=String.raw`
(async()=>{
  await tick();await tick();
  const para=n=>'Word '+('word '.repeat(n-2))+'end.\r\n\r\n';
  const heading='CHAPTER I\r\n\r\n',first=para(143),second=para(495),sub='An audited internal heading\r\n\r\n',last=para(30);
  const body=heading+first+second+sub+last,notes='NOTES\r\n\r\nSupplementary material remains separate.\r\n',text=body+notes;
  const natural=heading.length+first.length+second.length;
  const fixture={id:'bounded-dom-fixture',title:'Bounded source fixture',author:'Fixture',edition:'Audited test',path:'books/fixture.txt',source:'https://example.org/fixture',sha256:'fixture'};
  const manifest={sha256:'fixture',length:text.length,defaultSectionId:'bounded-chapter',sections:[
    {id:'bounded-chapter',label:'Chapter I',kind:'primary',start:0,end:body.length,pagination:'bounded',headingStarts:[0,natural],passageBreakStarts:[natural]},
    {id:'bounded-notes',label:'Notes',kind:'back',start:body.length,end:text.length}]};
  context.fixture=fixture;context.fixtureManifest=manifest;context.fixtureText=text;
  run('state.books.push(fixture);state.manifests[fixture.id]=fixtureManifest;state.cache.set(fixture.id,fixtureText)');
  await run('openBook(fixture.id)');assert.equal(run('state.pages.length'),3);
  for(let p=0;p<3;p++){
    run('state.page='+p+';renderPage()');assert(run('state.pages[state.page].words')<=600);
    for(const node of get('book-text').children)assert.equal(node.textContent,text.slice(Number(node.dataset.offset),Number(node.dataset.end)));
  }
  assert.equal(run('state.pages[2].start'),natural);assert.equal(get('book-text').children[0].tagName,'H2');
  run('state.page=1;renderPage();savePosition()');const offset=run('state.pages[1].start');
  run('setFont(9);closeBook()');await run('openBook(fixture.id)');assert.equal(run('state.pages[state.page].start'),offset);
  const bookmark=values.get('mythic:bookmark:v2:bounded-dom-fixture');
  run('showSection("bounded-notes");closeBook()');assert.equal(values.get('mythic:bookmark:v2:bounded-dom-fixture'),bookmark);
  await run('openBook(fixture.id)');assert.equal(run('state.section.id'),'bounded-chapter');assert.equal(run('state.pages[state.page].start'),offset);
  run('turnPage(1)');assert.equal(run('state.pages[state.page].start'),natural);run('turnPage(-1)');assert.equal(run('state.pages[state.page].start'),offset);
  run('state.page=state.pages.length-1;renderPage();turnPage(1)');assert(get('reader').hidden);
  console.log('PASS: bounded prose/heading DOM rendering, exact source spans, unchanged chapter identity, anchored passage, font changes, persisted source bookmark, supplementary isolation, backward/forward and end of chapter. DOM simulation only.');
})().catch(error=>{console.error(error);process.exitCode=1;});
`;
vm.runInNewContext(harness+scenario,{require:createRequire(path.join(__dirname,'test_interactions.cjs')),__dirname,console,process,setTimeout,clearTimeout,setImmediate,TextEncoder,TextDecoder,URLSearchParams});
