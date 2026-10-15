#!/usr/bin/env python3
"""Bounded UI-change gate: retain every reviewed reading source and engine byte."""
from pathlib import Path
import argparse, hashlib, json, re
p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);p.add_argument('--inventory',required=True);p.add_argument('--output',required=True);p.add_argument('--register-inventory');a=p.parse_args()
R=Path(__file__).resolve().parents[1];base=json.loads(Path(a.baseline).read_text());inventory=json.loads((R/'dist/collections.json').read_text());catalog=json.loads((R/'dist/catalog.json').read_text());changes=({'dist/index.html','dist/style.css','dist/collection.js','tests/test_collected_view.cjs','tests/test_collection_integrity.py'} if a.register_inventory else {'dist/index.html','dist/style.css','.gitignore'});new_runtime=({'dist/esoterica-register.json'} if a.register_inventory else {'dist/collection.js','dist/collections.json'})
def pin(path):
 b=path.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
for rel,expected in base['files'].items():
 if rel not in changes:assert pin(R/rel)==expected,'Changed preserved file '+rel
assert catalog==base['catalog'];assert json.loads((R/'dist/sections.json').read_text())==base['sections'];assert json.loads((R/'scripts/edition_specs.json').read_text())==base['specs']
assert (R/'dist/collections.json').read_bytes()==Path(a.inventory).read_bytes(),'Runtime inventory differs from reviewed source'
actual={str(x.relative_to(R)) for x in (R/'dist').rglob('*') if x.is_file()};expected={x for x in base['files'] if x.startswith('dist/')}|new_runtime;assert actual==expected,actual^expected
entries=inventory['entries'];assert len(entries)==len({e['id'] for e in entries});statuses=['readable','needs-source-review','quarantined','missing'];counts={s:sum(e['status']==s for e in entries) for s in statuses};assert sum(counts.values())==len(entries)
readable=[e for e in entries if e['status']=='readable'];assert len(readable)==len(catalog);assert {e['reader_id'] for e in readable}=={b['id'] for b in catalog};assert all(e['reader_id'] is None for e in entries if e['status']!='readable')
summary=inventory['summary'];assert summary['entries']==len(entries);assert summary['readable_editions']==counts['readable'];assert summary['needs_source_review']==counts['needs-source-review'];assert summary['quarantined_without_replacement']==counts['quarantined'];assert summary['missing_normalized_text']==counts['missing']
assert not re.search(r'/workspace/|/tmp/|file://|source-audit/|[A-Z]:\\',json.dumps(inventory,ensure_ascii=False),re.I),'Private path in runtime inventory'
ids=[e['original_work_id'] for e in entries if e['original_catalog_title'] is not None];assert len(ids)==summary['original_catalog_works']==len(set(ids))
result={'passed':True,'baseline_commit':base.get('git_state',{}).get('commit_sha'),'reading_editions_unchanged':len(catalog),'preserved_bookmark_endpoints':2*sum(len(book['sections']) for book in base['sections']['books'].values()),'preserved_primary_bookmark_endpoints':2*sum(sum(section['kind']=='primary' for section in book['sections']) for book in base['sections']['books'].values()),'preserved_file_hashes':len(base['files'])-len(changes),'runtime_files':len(actual),'catalog_entries':len(entries),'statuses':counts,'original_work_identities':len(ids),'no_fake_read_actions_in_data':True,'no_private_paths':True,'runtime_inventory_sha256':pin(R/'dist/collections.json')['sha256'],'runtime_allowlist':sorted(actual),'ui_change_allowlist':sorted(changes),'new_runtime_allowlist':sorted(new_runtime),'native_browser_verified':False}
if a.register_inventory:
 register=json.loads((R/'dist/esoterica-register.json').read_text());assert (R/'dist/esoterica-register.json').read_bytes()==Path(a.register_inventory).read_bytes(),'Register differs from reviewed source'
 slots=register['entries'];assert len(slots)==len({e['id'] for e in slots})==len({e['register_id'] for e in slots});overlap=[e for e in slots if e['status']=='readable'];missing=[e for e in slots if e['status']=='missing'];assert len(overlap)+len(missing)==len(slots)
 assert all(e['reader_id'] in {b['id'] for b in catalog} and e['overlaps_main_catalog'] is True and e['overlap_reader_id']==e['reader_id'] for e in overlap);assert len({e['reader_id'] for e in overlap})==len(overlap)
 assert all(e['reader_id'] is None and e['overlaps_main_catalog'] is False and e['overlap_reader_id'] is None for e in missing)
 assert register['summary']=={'registered_file_slots':len(slots),'overlapping_readable_editions':len(overlap),'not_recovered_file_slots':len(missing)}
 assert not re.search(r'/workspace/|/tmp/|file://|source-audit/|[A-Z]:\\',json.dumps(register,ensure_ascii=False),re.I),'Private register path'
 result['separate_register']={'file_slots':len(slots),'overlapping_readable_editions':len(overlap),'missing_file_slots':len(missing),'reader_ids':sorted(e['reader_id'] for e in overlap),'added_reading_editions':0,'unique_work_count_not_claimed':True,'runtime_sha256':pin(R/'dist/esoterica-register.json')['sha256']}
Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if 'allowlist' not in k},indent=2))
