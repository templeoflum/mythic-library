#!/usr/bin/env python3
"""Build the clearly derived Yoruba reading asset from the pinned scan collation.

No OCR is used to generate prose. Original audit inputs stay outside dist. The
unchanged facsimile and the two review inputs are independently byte/hash pinned.
Run this builder before build_sections.py; --check never modifies output files.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = 'https://archive.org/details/in.ernet.dli.2015.54438'
# Exact repair inputs and original PDF; these pins are not derived from catalog.
INPUT_PINS = {'tests/fixtures/yoruba-reading-input.json': {'bytes': 230277, 'sha256': '060a8ef5f51aee94777a23d0e66b6729155200f4fba4717ffcac23bcb64ff926'}, 'tests/fixtures/yoruba-unresolved-input.json': {'bytes': 3995, 'sha256': 'b9b3b1150e18ef2050f3c9bed7c2dcba81d0055bfed8b29f7daf7dba49239bf8'}, 'dist/books/yoruba-legends-source-scan.pdf': {'bytes': 2113867, 'sha256': '1a3c5f881de8acb126d88251d510bac1f974229c4a255c8d1c9cf02a239d5494'}}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def pinned(path):
    raw = (ROOT / path).read_bytes()
    pin = INPUT_PINS[path]
    if len(raw) != pin['bytes'] or sha(raw) != pin['sha256']:
        raise ValueError('Pinned input changed: ' + path)
    return raw

def build():
    data = json.loads(pinned('tests/fixtures/yoruba-reading-input.json'))
    unresolved = json.loads(pinned('tests/fixtures/yoruba-unresolved-input.json'))
    pinned('dist/books/yoruba-legends-source-scan.pdf')
    meta, front, stories = data['metadata'], data['front_matter'], data['stories']
    assert len(stories) == 40 and len(front['preface']) == 4 and len(unresolved) == 4
    assert [s['ordinal'] for s in stories] == list(range(1, 41))
    pieces, sections, records = [], [], []

    def section(suffix, label, kind, heading, blocks, group=None):
        entry = {'id': 'yoruba-legends-' + suffix, 'label': label, 'kind': kind}
        if pieces:
            entry['line'] = heading
        entry['headingAnchors'] = [{'line': heading}]
        if group:
            entry['group'] = group
        sections.append(entry)
        piece = '\n\n'.join([heading, *blocks]) + '\n\n'
        pieces.append(piece)
        return piece

    section('title', 'Original title, credit and publisher', 'front', front['title'],
            [front['credited_author'], front['publication_place'], front['publisher']])
    section('dedication-publication', 'Dedication and publication statement', 'front',
            front['dedication'], ['First published ' + str(front['first_published']), front['printer_statement']])
    section('preface', 'Complete original preface (four paragraphs)', 'front', 'Preface',
            [p['text'] for p in front['preface']])
    contents = []
    for entry in front['contents']:
        if entry['ordinal'] == 32:
            contents.append('Stories of Tortoise')
        contents.append(f"{entry['roman']}. {entry['title_contents']} — {entry['print_start']}")
    section('contents', 'Original contents and printed page numbers', 'front', 'Contents', contents)

    for story in stories:
        n = story['ordinal']
        if n == 32:
            section('tortoise-divider', 'Stories of Tortoise: original part divider', 'front',
                    'Stories of Tortoise', [])
            # The same printed divider also appears in the original contents.
            sections[-1]['count'] = 2
            sections[-1]['occurrence'] = 1
            sections[-1]['headingAnchors'][0].update(count=2, occurrence=1)
        heading = f"{story['roman']}. {story['title_body']}"
        # Whitespace indentation makes original verse lineation render as verse;
        # every character of the collated stanza remains unchanged after indent.
        blocks = [('    ' + p['text'].replace('\n', '\n    ')) if p['kind'] == 'verse'
                  else p['text'] for p in story['paragraphs']]
        piece = section(f'story-{n}', heading, 'primary', heading, blocks,
                        'Stories of Tortoise' if n >= 32 else None)
        records.append({'ordinal': n, 'roman': story['roman'], 'title_body': story['title_body'],
                        'title_contents': story['title_contents'], 'pdf_start': story['pdf_start'],
                        'pdf_end': story['pdf_end'], 'blocks': blocks,
                        'block_kinds': [p['kind'] for p in story['paragraphs']],
                        'section_sha256': sha(piece.encode()),
                        'paragraph_count': len(blocks)})

    status = ('DERIVED scan-collated reading transcription. All forty narratives were '
              'independently collated against the identified 1929 scan. Four unresolved '
              'readings remain explicitly marked in narratives IV, XVI, XXXI and XXXVIII. '
              'This is not an original clean source TXT or a typographic facsimile.')
    qualifications = [status, 'Source scan: ' + SOURCE_URL, meta['editorial_context'],
        meta['facsimile_material'].replace('original PDF and page images', 'original PDF'),
        'The original contents and body have different titles in IX (The Hunter and the Demon Polo, or, Orisa Oko / Orisa Oko) and XX (Another Story of Leopard and His Spots / Another Story of Leopard’s Spots). Both forms are retained.',
        'Completeness means the forty narratives as printed, not complete oral performances or a complete living tradition. The preface explicitly says that full songs cannot be given.',
        'The only author credit used is the printed M. I. Ogumefu, B.A. No biography, separate translator or parallel Yoruba original is inferred.',
        meta['catalog_title_discrepancy'], meta['catalog_page_discrepancy'],
        'The USA-only assessment is based on this edition’s 1929 publication date. Internet Archive metadata itself says rights not available. Other jurisdictions have not been assessed; no worldwide public-domain claim is made.']
    section('editorial-note', 'Editorial source and transcription qualifications', 'back',
            'Editorial source and transcription qualifications', qualifications)
    normalization = [note.replace('represented by page provenance', 'consult the original PDF for printed page context') for note in meta['normalization']] + [
        'Verse is indented for the reader while retaining each printed stanza’s line divisions. Original contents page numbers use a readable separator. Section labels and this editorial apparatus are additional navigation material.',
        'The four uncertainty markers in narrative text are editorial. Their repetition in the uncertainty register does not represent additional unresolved readings.']
    section('normalization', 'Editorial normalization policy', 'back', 'Editorial normalization policy', normalization)
    contexts = []
    for item in unresolved:
        contexts.append(f"{item['roman']}. {item['title']}; paragraph {item['paragraph_index_1_based']}; scan page {', '.join(map(str, item['pdf_pages']))}.")
        contexts.append(item['context'])
        details = [d for group in item['page_log_details'] for d in group]
        for detail in details:
            explanation = detail.get('detail') or detail.get('reason')
            # Collation process and local proof filenames belong to private audit,
            # not a public reading asset; retain only the actual uncertainty.
            if item['story_ordinal'] == 16:
                explanation = 'medicine-men is fully legible. An irregular damaged mark follows men before to make. It may be punctuation or a stray print/scan mark; no punctuation has been guessed.'
            elif item['story_ordinal'] == 31:
                explanation = 'A rounded dark mark joins the lower-right edge of the second si. Its form does not securely distinguish a damaged printed comma from incidental ink.'
            elif item['story_ordinal'] == 38:
                explanation = 'The lower period-like mark and separate upper curl do not establish the intended punctuation securely; no punctuation is guessed.'
            if explanation:
                contexts.append(explanation)
    section('unresolved-readings', 'Exact contexts of the four unresolved readings', 'back',
            'Four unresolved readings: exact contexts', contexts)
    text = ''.join(pieces).removesuffix('\n')  # One terminal newline; no empty EOF block.
    assert sum(p['text'].count('[unclear:') for s in stories for p in s['paragraphs']) == 4
    assert text.count('[unclear:') == 8
    for prohibited in ['/workspace/', '/tmp/', 'checks/', 'chunks/', 'parent_review', 'canonical_ingestion', 'quarantine']:
        assert prohibited not in text
    scan_pin = INPUT_PINS['dist/books/yoruba-legends-source-scan.pdf']
    audit = {'input_pins': INPUT_PINS, 'source_url': SOURCE_URL,
        'source_scan': {'path': 'books/yoruba-legends-source-scan.pdf', **scan_pin,
                        'source': SOURCE_URL, 'pages': 98},
        'reading_asset': {'path': 'books/yoruba-legends-derived-transcription.txt',
                          'sha256': sha(text.encode()), 'bytes': len(text.encode())},
        'status': status, 'primary_count': 40, 'narrative_uncertainty_count': 4,
        'supplementary_uncertainty_repetitions': 4, 'narratives': records,
        'preface_paragraphs': [p['text'] for p in front['preface']],
        'unresolved': [{k: item[k] for k in ('story_ordinal', 'roman', 'title', 'paragraph_index_1_based', 'pdf_pages', 'marker', 'context')} for item in unresolved],
        'sections': sections, 'qualifications': qualifications, 'normalization': normalization}
    return {ROOT / 'dist/books/yoruba-legends-derived-transcription.txt': text.encode(),
            ROOT / 'tests/yoruba-edition-audit.json': (json.dumps(audit, ensure_ascii=False, indent=2) + '\n').encode()}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, raw in build().items():
        if args.check:
            if not path.exists() or path.read_bytes() != raw:
                raise ValueError('Generated file differs: ' + str(path.relative_to(ROOT)))
        else:
            path.write_bytes(raw)
        print(('Verified ' if args.check else 'Generated ') + str(path.relative_to(ROOT)) + ' ' + sha(raw))
    print('Pinned original PDF and both collation inputs verified.')
