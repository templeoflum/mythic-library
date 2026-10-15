#!/usr/bin/env python3
"""Offline additive-edition pipeline. Reuses the room's section builder and reader tests.
No network, Git writes, Sites calls, publication or access changes exist in this tool.
"""
from pathlib import Path, PurePosixPath
import argparse, copy, datetime, hashlib, json, re, shutil, subprocess, sys, tempfile, zipfile

class GateError(Exception): pass
def require(ok,msg):
    if not ok: raise GateError(msg)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p,data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
    b=Path(p).read_bytes();return {'bytes':len(b),'sha256':sha(b)}
def safe_rel(value):
    p=PurePosixPath(value);require(bool(value) and not p.is_absolute() and '..' not in p.parts and '\\' not in value and str(p)==value,'Unsafe relative path: '+value);return value
def protected_files(root):
    paths=[]
    for folder in ['dist','scripts','tests','.openai','maintenance']:
        paths.extend(p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='source-test-results.json')
    if (root/'.gitignore').exists():paths.append(root/'.gitignore')
    return {str(p.relative_to(root)):pin(p) for p in sorted(paths)}
def baseline(root):
    root=Path(root).resolve();git_state=None
    if (root/'.git').exists():
        require(subprocess.check_output(['git','status','--porcelain'],cwd=root)==b'','Cannot trust a dirty Git checkout as a new baseline')
        git_state={'commit_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root).decode().strip(),'clean':True}
    return {'schema_version':1,'git_state':git_state,'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root_hint':str(root),'collections':read(root/'dist/collections.json') if (root/'dist/collections.json').exists() else None,'catalog':read(root/'dist/catalog.json'),'sections':read(root/'dist/sections.json'),'specs':read(root/'scripts/edition_specs.json'),'files':protected_files(root)}
def import_baseline(records,files):
    d=read(records);pins=read(files);return {'schema_version':1,'captured_at':pins.get('captured_at'),'root_hint':pins.get('source'),'catalog':d['catalog'],'sections':d['sections'],'specs':d['specs'],'files':{p:v for p,v in pins['files'].items() if p not in ['REVIEW.md','tests/source-test-results.json'] and '__pycache__' not in p}}
def check_pin(path,expected,label):
    require(path.is_file(),label+' missing');require(pin(path)=={'bytes':expected['bytes'],'sha256':expected['sha256']},label+' hash/byte mismatch')
def verify_import(imp):
    require(imp.get('schema_version')==1,'Unsupported import schema')
    c,s,v=imp['catalog'],imp['spec'],imp['verification'];bid=c['id']
    require(re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',bid) is not None,'Unsafe edition id')
    require(v.get('status') in ['verified_complete_digital_edition','reviewed_derived_transcription'],'Source verification not complete')
    require(v.get('rights_scope') in ['USA_only','explicit_license'],'Missing bounded rights assessment')
    require(v.get('source_catalog')==c.get('source') and c['source'].startswith('https://'),'Catalog provenance mismatch')
    require(bool(c.get('rights')) and bool(c.get('edition')) and bool(c.get('author')),'Missing edition, creator or rights attribution')
    require(Path(v.get('report','')).is_file(),'Source verification report missing')
    require(c.get('available') is True,'Stub/unavailable catalog entry forbidden')
    require(c.get('path','').startswith('books/') and c['path'].endswith('.txt'),'Reader source must be a books/*.txt asset')
    require(c.get('sha256')==s.get('sha256'),'Catalog/spec hash mismatch')
    require(not re.search(r'/workspace/|/tmp/|file://|source-audit/',json.dumps([c,s],ensure_ascii=False)),'Private audit paths in hosted catalog')
    require(s.get('builder')=='anchored' and s.get('primarySectionCount',0)>0 and bool(s.get('primaryOpening')),'Complete anchored reading specification required')
    require(sum(x.get('kind')=='primary' for x in s.get('sections',[]))==s['primarySectionCount'],'Primary section count mismatch')
    require(any(x.get('id')==s.get('defaultSectionId') and x.get('kind')=='primary' for x in s['sections']),'Story-first primary opening required')
    targets=[]
    for a in imp['runtime_assets']:
        safe_rel(a['target']);require(a['target'].startswith('books/'),'Only book source assets may be added')
        require(PurePosixPath(a['target']).suffix in ['.txt','.zip','.pdf'],'Executable/unapproved source asset type')
        require(Path(a['source']).is_absolute(),'Source file path must be explicit and absolute')
        require(a.get('url','').startswith('https://'),'Source URL missing');check_pin(Path(a['source']),a,'Pinned source '+a['target']);targets.append(a['target'])
    require(len(targets)==len(set(targets)),'Duplicate asset target')
    expected=[c['path']]
    for k in ['preservation_archive','source_scan']:
        if c.get(k):expected.append(c[k]['path'])
    if c.get('notices'):expected.append(c['notices'])
    require(set(targets)==set(expected),'Runtime assets do not exactly match source files declared by catalog')
    asset=next(a for a in imp['runtime_assets'] if a['target']==c['path'])
    require(asset['sha256']==c['sha256'] and asset['bytes']==c['bytes'],'Reading asset/catalog pins disagree')
    require(asset['bytes']>0,'Empty reading source forbidden')
    if c.get('preservation_archive'):
        a=c['preservation_archive'];require(a==s.get('preservationArchive'),'Archive catalog/spec mismatch');src=Path(next(x['source'] for x in imp['runtime_assets'] if x['target']==a['path']));check_pin(src,a,'Preserved archive')
        with zipfile.ZipFile(src) as z:
            require(z.testzip() is None,'Preserved ZIP CRC failure')
            for name in z.namelist():safe_rel(name.rstrip('/'))
            require(sha(z.read(a['html_entry']))==a['html_sha256'],'Preserved HTML hash mismatch')
    return imp

def reconcile_collections(b,imports):
    """Promote only explicitly mapped held entries, without duplicating catalog cards."""
    if not b.get('collections'):return None
    result=copy.deepcopy(b['collections']);entries=result['entries'];mapped=set()
    require(result.get('schema_version')==1,'Unsupported collected-catalog schema')
    for imp in imports:
        key=imp.get('collection_entry_id');require(isinstance(key,str) and bool(key),'Collected catalog requires explicit collection_entry_id for each addition')
        require(key not in mapped,'Two editions cannot silently promote the same catalog entry');mapped.add(key)
        matches=[e for e in entries if e['id']==key];require(len(matches)==1,'Mapped collected entry missing or ambiguous: '+key);entry=matches[0]
        require(entry['status']!='readable' and entry.get('reader_id') is None,'Collected entry already has a readable edition: '+key)
        book=imp['catalog'];aliases=list(entry.get('aliases',[]))
        for value in [entry['title'],book['title'],book['id']]:
            if value not in aliases:aliases.append(value)
        entry.update(title=book['title'],author=book['author'],edition=book['edition'],status='readable',reader_id=book['id'],source_url=book['source'],source_note='Reviewed reading edition. '+book.get('edition_note',book['edition']),aliases=aliases,relationship='same_id' if entry['id']==book['id'] else 'specific_reviewed_edition')
    summary=result['summary'];summary['entries']=len(entries);summary['readable_editions']=sum(e['status']=='readable' for e in entries);summary['needs_source_review']=sum(e['status']=='needs-source-review' for e in entries);summary['quarantined_without_replacement']=sum(e['status']=='quarantined' for e in entries);summary['missing_normalized_text']=sum(e['status']=='missing' for e in entries)
    if 'original_work_identities_represented_by_readable_editions' in summary:summary['original_work_identities_represented_by_readable_editions']=sum(e['status']=='readable' and e.get('original_catalog_title') is not None for e in entries)
    return result

def run(cmd,cwd):
    p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True);require(p.returncode==0,'Check failed: '+str(cmd)+'\n'+p.stdout[-1200:]+p.stderr[-2000:]);return p.stdout+p.stderr

def validate(root,b,imports,full=True):
    root=Path(root).resolve();imports=[verify_import(x) for x in imports];newids=[x['catalog']['id'] for x in imports]
    require(newids and len(newids)==len(set(newids)),'At least one unique added edition required')
    oldids=[x['id'] for x in b['catalog']];require(not set(oldids)&set(newids),'Addition duplicates an existing edition')
    c=read(root/'dist/catalog.json');s=read(root/'scripts/edition_specs.json');m=read(root/'dist/sections.json')
    require(c[:len(oldids)]==b['catalog'],'Prior catalog metadata/order/shelves changed')
    require(c[len(oldids):]==[x['catalog'] for x in imports],'Unreviewed new catalog entries or metadata')
    require(set(s['editions'])==set(oldids+newids),'Edition specs deleted or unexpectedly added')
    require(set(m['books'])==set(oldids+newids),'Section manifests deleted or unexpectedly added')
    require({k:v for k,v in s.items() if k!='editions'}=={k:v for k,v in b['specs'].items() if k!='editions'},'Spec envelope changed')
    require({k:v for k,v in m.items() if k!='books'}=={k:v for k,v in b['sections'].items() if k!='books'},'Section envelope changed')
    for bid in oldids:
        require(s['editions'][bid]==b['specs']['editions'][bid],'Prior source spec changed: '+bid)
        require(m['books'][bid]==b['sections']['books'][bid],'Prior sections/bookmark anchors changed: '+bid)
    mutable={'dist/catalog.json','dist/sections.json','scripts/edition_specs.json'}
    reconciled=reconcile_collections(b,imports)
    if 'dist/collections.json' in b['files']:
        require(reconciled is not None,'Baseline lacks collected-catalog records; capture a new baseline before admission')
        require(read(root/'dist/collections.json')==reconciled,'Collected catalog differs from exact mapped promotions')
        mutable.add('dist/collections.json')
    for rel,p in b['files'].items():
        if rel not in mutable:check_pin(root/rel,p,'Prior file '+rel)
    runtime={str(p.relative_to(root)) for p in (root/'dist').rglob('*') if p.is_file()}
    expected={p for p in b['files'] if p.startswith('dist/')};addedpaths=set()
    for imp in imports:
        bid=imp['catalog']['id'];require(s['editions'][bid]==imp['spec'],'New spec differs from verified import: '+bid)
        for a in imp['runtime_assets']:
            rel='dist/'+a['target'];require(rel not in expected,'New asset overwrites existing runtime path: '+rel);require(rel not in addedpaths,'Additions collide: '+rel);addedpaths.add(rel);check_pin(root/rel,a,'Installed source '+rel)
    require(runtime==expected|addedpaths,'Hosted runtime allowlist mismatch: '+repr(sorted(runtime^(expected|addedpaths))))
    groups={}
    for book in c:groups[book['shelf']]=groups.get(book['shelf'],0)+1
    require(max(groups.values())<=4,'Shelf exceeds four editions')
    logs={}
    logs['sections']=run(['python3','scripts/build_sections.py','--check'],root)
    # Use existing runtime implementation to validate prior bookmark endpoints dynamically.
    node="""const fs=require('fs'),C=require(process.cwd()+'/dist/reader-core.js'),m=JSON.parse(fs.readFileSync('dist/sections.json'));const ids=JSON.parse(process.argv[1]);let n=0,p=0;for(const id of ids){let b=m.books[id];for(const s of b.sections)for(const offset of [s.start,s.end-1]){if(!C.validBookmark({version:2,sha256:b.sha256,sectionId:s.id,offset},b))throw Error('Broken bookmark '+s.id);n++;if(s.kind==='primary')p++;}}console.log(JSON.stringify({all:n,primary:p}));"""
    bookmarks=json.loads(run(['node','-e',node,json.dumps(oldids)],root))
    if full:
        for label,cmd in [('app-syntax',['node','--check','dist/app.js']),('core-syntax',['node','--check','dist/reader-core.js']),('core',['node','tests/test_core.cjs']),('interactions',['node','tests/test_interactions.cjs'])]:logs[label]=run(cmd,root)
        if (root/'tests/test_collected_view.cjs').exists():logs['collected-view']=run(['node','tests/test_collected_view.cjs'],root)
        if (root/'scripts/build_yoruba.py').exists():logs['derived-source']=run(['python3','scripts/build_yoruba.py','--check'],root)
    changes=[]
    for rel in sorted(mutable|addedpaths):changes.append({'path':rel,'action':'replace' if rel in b['files'] else 'add','prior':b['files'].get(rel),**pin(root/rel)})
    return {'schema_version':1,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'publication_allowed':False,'review_required':True,'baseline_editions':len(oldids),'candidate_editions':len(c),'new_editions':newids,'preserved_bookmark_endpoints':bookmarks['all'],'preserved_primary_bookmark_endpoints':bookmarks['primary'],'unchanged_baseline_files':len(b['files'])-len(mutable),'runtime_files':len(runtime),'runtime_allowlist':sorted(runtime),'baseline_content_sha256':sha(json.dumps(b,sort_keys=True,ensure_ascii=False).encode()),'import_content_sha256':[sha(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()) for x in imports],'source_audit_reports':[{'path':x['verification']['report'],**pin(x['verification']['report'])} for x in imports],'sections':sum(len(x['sections']) for x in m['books'].values()),'primary_sections':sum(sum(y['kind']=='primary' for y in x['sections']) for x in m['books'].values()),'source_transfers':changes,'full_reader_checks':full,'native_browser_verified':False,'checks':list(logs),'logs':logs}

def prepare(base,b,imports,out):
    imports=[imports] if isinstance(imports,dict) else imports
    require(bool(imports),'At least one edition import is required')
    base=Path(base).resolve();out=Path(out).resolve();require(out!=base and not out.is_relative_to(base),'Cannot prepare into or beneath base/canonical checkout');require(not out.exists() or not any(out.iterdir()),'Candidate destination must be new or empty')
    imports=[verify_import(imp) for imp in imports];ids=[imp['catalog']['id'] for imp in imports];require(len(ids)==len(set(ids)),'Duplicate added edition id')
    require(read(base/'dist/catalog.json')==b['catalog'] and read(base/'scripts/edition_specs.json')==b['specs'] and read(base/'dist/sections.json')==b['sections'],'Base differs from snapshot')
    for rel,p in b['files'].items():check_pin(base/rel,p,'Baseline '+rel)
    if 'dist/collections.json' in b['files']:require(b.get('collections')==read(base/'dist/collections.json'),'Baseline lacks current collected-catalog records')
    reconciled=reconcile_collections(b,imports)
    out.mkdir(parents=True,exist_ok=True)
    for rel in b['files']:
        target=out/safe_rel(rel);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(base/rel,target)
    catalog=copy.deepcopy(b['catalog']);specs=copy.deepcopy(b['specs'])
    for imp in imports:
        require(imp['catalog']['id'] not in [x['id'] for x in catalog],'Duplicate book')
        for asset in imp['runtime_assets']:
            target=out/'dist'/asset['target'];require(not target.exists(),'Refusing source overwrite');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(asset['source'],target)
        catalog.append(imp['catalog']);specs['editions'][imp['catalog']['id']]=imp['spec']
    dump(out/'dist/catalog.json',catalog);dump(out/'scripts/edition_specs.json',specs)
    if reconciled is not None:dump(out/'dist/collections.json',reconciled)
    run(['python3','scripts/build_sections.py'],out)
    return validate(out,b,imports,True)

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('baseline');q.add_argument('--root',required=True);q.add_argument('--output',required=True)
    q=sub.add_parser('import-baseline');q.add_argument('--records',required=True);q.add_argument('--files',required=True);q.add_argument('--output',required=True)
    q=sub.add_parser('validate');q.add_argument('--root',required=True);q.add_argument('--baseline',required=True);q.add_argument('--import-json',action='append',required=True);q.add_argument('--output',required=True);q.add_argument('--fast',action='store_true')
    q=sub.add_parser('prepare');q.add_argument('--base-root',required=True);q.add_argument('--baseline',required=True);q.add_argument('--import-json',action='append',required=True);q.add_argument('--candidate',required=True);q.add_argument('--output',required=True)
    a=p.parse_args()
    if a.command=='baseline':result=baseline(a.root)
    elif a.command=='import-baseline':result=import_baseline(a.records,a.files)
    elif a.command=='validate':result=validate(a.root,read(a.baseline),[read(x) for x in a.import_json],not a.fast)
    else:result=prepare(a.base_root,read(a.baseline),[read(x) for x in a.import_json],a.candidate)
    dump(a.output,result);print(json.dumps({k:v for k,v in result.items() if k not in ['files','catalog','sections','specs','collections','logs','source_transfers']},indent=2))
if __name__=='__main__':
    try:main()
    except (GateError,KeyError,ValueError,OSError,zipfile.BadZipFile) as e:print('GATE BLOCKED: '+str(e),file=sys.stderr);sys.exit(1)
