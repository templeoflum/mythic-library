'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),{createRequire}=require('node:module');
const source=fs.readFileSync(path.join(__dirname,'test_interactions.cjs'),'utf8');
const marker='(async()=>{await tick();await tick();';
if(source.split(marker).length!==2)throw Error('Existing DOM harness changed; review this test before reuse');
const harness=source.slice(0,source.indexOf(marker));
const scenario=String.raw`
(async()=>{
  await tick();await tick();await run('openBook("yoruba-legends")');
  function verify(expectedPath){
    const links=get('edition-details').children.flatMap(e=>e.children);
    const scan=links.find(e=>e.href===expectedPath&&!e.download),download=links.find(e=>e.href===expectedPath&&e.download);
    assert.equal(scan.textContent,'Open the unchanged source scan (PDF)');
    assert.equal(download.textContent,'Download the unchanged source scan (PDF)');
    assert.equal(download.download,expectedPath.split('/').pop());
  }
  verify('books/yoruba-legends-source-scan.pdf');
  assert(get('edition-details').textContent.includes('1929'),'Yoruba still has its actual edition date in catalog details');
  run('state.active={...state.active,edition:"1896 fixture edition",source_scan:{...state.active.source_scan,path:"books/1896-fixture.pdf",year:1896}};renderContents()');
  verify('books/1896-fixture.pdf');
  const label=get('edition-details').children.flatMap(e=>e.children).find(e=>e.href==='books/1896-fixture.pdf'&&!e.download).textContent;
  assert(!label.includes('1929'));assert(!label.includes('1896'),'Neutral label makes no unaudited metadata inference');
  run('state.active={...state.active,source_labels:{scan_link:"Open the verified 1896 scan (PDF)"}};renderContents()');
  assert(get('edition-details').children.flatMap(e=>e.children).some(e=>e.href==='books/1896-fixture.pdf'&&e.textContent==='Open the verified 1896 scan (PDF)'));
  run('state.active={...state.active,text_status:undefined,source_labels:{}};renderContents()');
  verify('books/1896-fixture.pdf');assert(get('edition-details').textContent.includes('Original text & notices'),'An original digital TXT may also have a companion scan');
  run('state.active={...state.active,text_status:"derived-preservation-transcription",path:"books/derived-fixture.txt",preservation_archive:{path:"books/assembled-html-css.zip"},source_labels:{text_label:"Derived reading text",text_link:"Open the derived HTML-to-text transcription",archive_label:"Assembled source bundle",archive_link:"Download the HTML and CSS preservation bundle"}};renderContents()');
  assert(get('edition-details').textContent.includes('Derived reading text'));assert(get('edition-details').textContent.includes('Assembled source bundle'));
  let links=get('edition-details').children.flatMap(e=>e.children);
  assert(links.some(e=>e.href==='books/derived-fixture.txt'&&e.textContent==='Open the derived HTML-to-text transcription'));
  assert(links.some(e=>e.href==='books/assembled-html-css.zip'&&e.textContent==='Download the HTML and CSS preservation bundle'));
  assert(!get('edition-details').textContent.includes('Original text & notices'));assert(!get('edition-details').textContent.includes('Preserved illustrated edition'));
  run('state.active.source_labels={text_label:"<b>plain label</b>",text_link:"<script>plain text only</script>",archive_label:42,archive_link:"  "};renderContents()');
  links=get('edition-details').children.flatMap(e=>e.children);
  assert(links.some(e=>e.textContent==='<script>plain text only</script>'&&e.children.length===0));
  assert(get('edition-details').textContent.includes('<b>plain label</b>'));assert(get('edition-details').textContent.includes('Preserved illustrated edition'));assert(get('edition-details').textContent.includes('Download the intact HTML and image archive'));
  console.log('PASS: neutral/explicit scan labels, unchanged source destinations/downloads, real edition date, opt-in derived-text/assembled-bundle labels, default compatibility, and safe plain-text rendering. DOM simulation only.');
})().catch(error=>{console.error(error);process.exitCode=1;});
`;
vm.runInNewContext(harness+scenario,{require:createRequire(path.join(__dirname,'test_interactions.cjs')),__dirname,console,process,setTimeout,clearTimeout,setImmediate,TextEncoder,TextDecoder,URLSearchParams});
