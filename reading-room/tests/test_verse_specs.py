#!/usr/bin/env python3
"""Exercise source-anchored, opt-in rendering metadata without editing any edition."""
import copy
import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('verse_section_builder', ROOT / 'scripts/build_sections.py')
builder = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = builder
spec.loader.exec_module(builder)


class FormatSpecs(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.old_dist = builder.DIST
        builder.DIST = Path(self.temp.name)
        self.addCleanup(setattr, builder, 'DIST', self.old_dist)
        self.text = '\ufeffTitle 🕮\r\n\r\nBOOK I.\r\n\r\nFirst unindented verse line\r\nSecond verse line\r\n\r\nCaption text\r\n\r\nNOTES\r\n\r\nA wrapped note\r\ncontinues here.\r\n'
        self.raw = self.text.encode('utf-8')
        self.path = builder.DIST / 'fixture.txt'
        self.path.write_bytes(self.raw)
        self.book = {'id': 'verse-fixture', 'path': 'fixture.txt', 'bytes': len(self.raw), 'sha256': hashlib.sha256(self.raw).hexdigest()}
        self.spec = {'builder': 'anchored', 'sha256': self.book['sha256'], 'defaultSectionId': 'book-1', 'sections': [
            {'id': 'front', 'label': 'Title', 'kind': 'front', 'textFormat': 'prose'},
            {'id': 'book-1', 'label': 'Book I', 'kind': 'primary', 'line': 'BOOK I.', 'headingAnchors': [{'line': 'BOOK I.'}], 'textFormatRanges': [{'format': 'verse', 'start': {'line': 'First unindented verse line'}, 'end': {'line': 'Caption text'}}]},
            {'id': 'notes', 'label': 'Notes', 'kind': 'back', 'line': 'NOTES', 'textFormat': 'auto'}]}

    def build(self, spec=None):
        builder.SPECS[self.book['id']] = self.spec if spec is None else spec
        self.addCleanup(builder.SPECS.pop, self.book['id'], None)
        result = builder.anchored(builder.Source(self.book))
        self.assertEqual(self.path.read_bytes(), self.raw)
        return result

    def test_exact_ranges_and_utf16(self):
        result = self.build()
        primary = result['sections'][1]
        span = primary['textFormatRanges'][0]
        self.assertEqual(span['start'], builder.utf16_length(self.text[:self.text.index('First unindented')]))
        self.assertEqual(span['end'], builder.utf16_length(self.text[:self.text.index('Caption text')]))
        self.assertEqual(span['format'], 'verse')
        self.assertNotIn('textFormat', primary)
        self.assertEqual(primary['headingStarts'], [primary['start']])
        self.assertNotIn('textFormat', result['sections'][2])

    def test_edition_section_and_range_defaults(self):
        self.spec['textFormat'] = 'verse'
        result = self.build()
        self.assertEqual(result['sections'][0]['textFormat'], 'prose')
        self.assertEqual(result['sections'][1]['textFormat'], 'verse')
        self.assertNotIn('textFormat', result['sections'][2])
        self.spec['sections'][1]['textFormatRanges'][0].pop('end')
        primary = self.build()['sections'][1]
        self.assertEqual(primary['textFormatRanges'][0]['end'], primary['end'])

    def test_omitted_metadata_keeps_old_manifest_shape(self):
        for item in self.spec['sections']:
            item.pop('textFormat', None)
            item.pop('textFormatRanges', None)
        for section in self.build()['sections']:
            self.assertNotIn('textFormat', section)
            self.assertNotIn('textFormatRanges', section)

    def test_reject_invalid_metadata(self):
        mutations = [
            ('unknown edition format', lambda s: s.update(textFormat='poetry')),
            ('unknown section format', lambda s: s['sections'][1].update(textFormat='poetry')),
            ('unknown range format', lambda s: s['sections'][1]['textFormatRanges'][0].update(format='poetry')),
            ('missing source anchor', lambda s: s['sections'][1]['textFormatRanges'][0]['start'].update(line='Not present')),
            ('not whole source line', lambda s: s['sections'][1]['textFormatRanges'][0]['start'].update(line='First unindented')),
            ('raw offsets forbidden', lambda s: s['sections'][1]['textFormatRanges'][0].update(start=42)),
            ('outside section', lambda s: s['sections'][1]['textFormatRanges'][0]['start'].update(line='A wrapped note')),
            ('end outside section', lambda s: s['sections'][1]['textFormatRanges'][0]['end'].update(line='A wrapped note')),
            ('empty range', lambda s: s['sections'][1]['textFormatRanges'][0]['end'].update(line='First unindented verse line')),
            ('negative occurrence', lambda s: s['sections'][1]['textFormatRanges'][0]['start'].update(occurrence=-1)),
            ('bad expected count', lambda s: s['sections'][1]['textFormatRanges'][0]['start'].update(count=2)),
            ('overlap', lambda s: s['sections'][1]['textFormatRanges'].append(copy.deepcopy(s['sections'][1]['textFormatRanges'][0]))),
        ]
        for label, mutate in mutations:
            with self.subTest(label=label):
                changed = copy.deepcopy(self.spec)
                mutate(changed)
                with self.assertRaises(ValueError):
                    self.build(changed)


if __name__ == '__main__':
    unittest.main()
