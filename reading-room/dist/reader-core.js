/* Reader pagination is a view over source offsets. Source files are never edited. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ReaderCore = api;
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  const words = text => (text.match(/\S+/g) || []).length;
  function classify(text) {
    const trimmed = text.trim(), lines = trimmed.split(/\r?\n/);
    if (trimmed.length < 180 && lines.length <= 2 && (
      /^(?:BOOK [IVX]+\.|[\d]+\.\s+[^a-z]+|[A-Z][A-Z\s.,’'—&:;!?()\d-]+)$/.test(trimmed) ||
      /^[a-z]\.\s+[^\n]{1,100}$/.test(trimmed))) return 'heading';
    if (lines.length > 2 && lines.filter(line => /\S\s{3,}\S/.test(line)).length >= lines.length / 2) return 'table';
    if (lines.length > 1 && text.split(/\r?\n/).filter(line => /^ {2,}\S/.test(line)).length >= lines.length / 2) return 'verse';
    return 'paragraph';
  }
  function blocksFor(text, section) {
    const blocks = [], ranges = section.textFormatRanges || [];
    const boundaries = [...new Set([section.start, ...ranges.flatMap(range => [range.start, range.end]), ...(section.pagination==='bounded'?section.passageBreakStarts||[]:[]), section.end])].sort((a,b)=>a-b);
    // Include the separator in each raw span. Together the spans recover the source exactly.
    const pattern = /[\s\S]+?(?:(?:\r?\n)[ \t]*(?:\r?\n)+|$)/g;
    for(let i=0;i<boundaries.length-1;i++){
      const from=boundaries[i],to=boundaries[i+1],slice=text.slice(from,to);
      const format=ranges.find(range=>from>=range.start&&from<range.end)?.format||section.textFormat||'auto';
      for (const match of slice.matchAll(pattern)) {
        const raw = match[0];
        const start=from+match.index,end=start+raw.length;
        const auditedHeading=(section.headingStarts||[]).some(offset=>offset>=start&&offset<end);
        const kind=auditedHeading?'heading':format==='verse'?'verse':format==='prose'?'paragraph':classify(raw);
        const block={start,end,text:raw,kind,words:words(raw)};
        // Only source-audited, opt-in verse uses the new line-aware pagination.
        if(kind==='verse'&&format==='verse'){block.explicitVerse=true;block.verseLines=raw.split(/\r\n|\r|\n/).filter(line=>line.trim()).length;}
        blocks.push(block);
      }
    }
    return blocks;
  }
  function passageBlocks(text, section, targetWords) {
    const originals=blocksFor(text,section), result=[];
    for(const block of originals){
      if(block.explicitVerse){
        const lines=block.text.match(/[^\r\n]*(?:\r\n|\r|\n|$)/g).filter(Boolean);
        if(block.words>targetWords*1.25||block.verseLines>48){
          let start=0,part='',count=0,lineCount=0;
          const finish=()=>{if(!part)return;result.push({...block,start:block.start+start,end:block.start+start+part.length,text:part,words:count,verseLines:lineCount,paragraphStart:block.start,continuation:start>0});start+=part.length;part='';count=0;lineCount=0;};
          // Split a long stanza only at original line ends; never reflow or rewrite a line.
          for(const line of lines){const size=words(line);if(part&&size>0&&(count+size>targetWords||lineCount>=48))finish();part+=line;count+=size;if(size)lineCount++;}
          finish();continue;
        }
      }
      if(block.kind!=='paragraph'||block.words<=targetWords*1.25||typeof Intl.Segmenter!=='function'){result.push({...block,paragraphStart:block.start,continuation:false});continue;}
      // A long source paragraph can span reader pages, as it can in print.
      // Segment only at complete source sentences; retain its original identity and every character.
      const sentences=Array.from(new Intl.Segmenter('en',{granularity:'sentence'}).segment(block.text));
      let start=0,part='',count=0;
      const finish=()=>{if(!part)return;result.push({start:block.start+start,end:block.start+start+part.length,text:part,kind:block.kind,words:count,paragraphStart:block.start,continuation:start>0});start+=part.length;part='';count=0;};
      for(const sentence of sentences){const size=words(sentence.segment);if(part&&count+size>targetWords*.85&&(count>=targetWords*.35||section.pagination==='bounded'))finish();part+=sentence.segment;count+=size;}
      finish();
    }
    return result;
  }
  function paginate(text, section, targetWords = 420) {
    const blocks = passageBlocks(text, section, targetWords), pages = [];
    const bounded=section.pagination==='bounded',breaks=new Set(bounded?section.passageBreakStarts||[]:[]);
    let group = [], size = 0, verseLines = 0;
    const finish = () => { if (!group.length) return; pages.push({start:group[0].start,end:group.at(-1).end,blocks:group,words:size}); group=[];size=0;verseLines=0; };
    for (const block of blocks) {
      if(breaks.has(block.start)&&group.length&&group.at(-1).kind!=='heading')finish();
      // Keep a trailing heading group with the following text when explicit policy allows it.
      // Legacy text without bounded pagination or explicit verse remains untouched.
      if(group.at(-1)?.kind==='heading'&&
        ((block.explicitVerse&&(verseLines+block.verseLines>48||size+block.words>targetWords*1.25))||
          (bounded&&block.kind!=='heading'&&size+block.words>targetWords*1.25))){
        let firstHeading=group.length;while(firstHeading>0&&group[firstHeading-1].kind==='heading')firstHeading--;
        if(firstHeading>0){const headings=group.splice(firstHeading),headingWords=headings.reduce((sum,item)=>sum+item.words,0);size-=headingWords;finish();group=headings;size=headingWords;}
      }
      const last=group.at(-1);
      // Keep headings with following text. Audited long verse was split only at line ends.
      if(group.length&&last.kind!=='heading'&&last.words>0&&
        (size>=targetWords||((size>=targetWords*.35||bounded)&&size+block.words>targetWords*1.25)||
          (block.explicitVerse&&(verseLines+block.verseLines>48||size+block.words>targetWords*1.25)))) finish();
      group.push(block); size += block.words;verseLines += block.verseLines||0;
    }
    finish();
    return pages;
  }
  function pageForOffset(pages, offset) {
    let found = pages.findIndex(page => offset >= page.start && offset < page.end);
    return found >= 0 ? found : offset >= pages.at(-1)?.end ? pages.length - 1 : 0;
  }
  function sectionForOffset(sections, offset) {return sections.find(section => offset >= section.start && offset < section.end) || null;}
  function validBookmark(value, manifest) {
    return value && value.version === 2 && value.sha256 === manifest.sha256 &&
      Number.isInteger(value.offset) && value.offset >= 0 && value.offset < manifest.length &&
      manifest.sections.some(section => section.id === value.sectionId && value.offset >= section.start && value.offset < section.end);
  }
  return {words,classify,blocksFor,passageBlocks,paginate,pageForOffset,sectionForOffset,validBookmark};
});
