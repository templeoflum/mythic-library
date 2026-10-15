#!/usr/bin/env python3
"""Strict source-anchor and policy validation for the opt-in pagination mode."""
import copy
import unittest
from test_verse_specs import FormatSpecs


class BoundedSpecs(FormatSpecs):
    def configure(self):
        self.spec['pagination'] = 'bounded'
        self.spec['sections'][1]['headingAnchors'].append({'line': 'Caption text'})
        self.spec['sections'][1]['passageBreakAnchors'] = [{'line': 'Caption text'}]

    def test_policies_and_exact_break(self):
        self.configure()
        self.spec['sections'][0]['pagination'] = 'legacy'
        result = self.build()
        self.assertNotIn('pagination', result['sections'][0])
        primary = result['sections'][1]
        self.assertEqual(primary['pagination'], 'bounded')
        self.assertEqual(primary['passageBreakStarts'], [primary['textFormatRanges'][0]['end']])
        self.assertEqual([s['id'] for s in result['sections']], ['front', 'book-1', 'notes'])

    def test_default_manifest_stays_legacy(self):
        for section in self.build()['sections']:
            self.assertNotIn('pagination', section)
            self.assertNotIn('passageBreakStarts', section)

    def test_bad_policies_and_breaks(self):
        self.configure()
        mutations = [
            ('unknown edition policy', lambda s: s.update(pagination='relaxed')),
            ('unknown section policy', lambda s: s['sections'][1].update(pagination='relaxed')),
            ('non-string policy', lambda s: s.update(pagination=True)),
            ('explicit bounded required', lambda s: s['sections'][1].update(pagination='legacy')),
            ('raw numeric anchor', lambda s: s['sections'][1].update(passageBreakAnchors=[42])),
            ('missing line', lambda s: s['sections'][1].update(passageBreakAnchors=[{}])),
            ('wrong source line', lambda s: s['sections'][1].update(passageBreakAnchors=[{'line': 'Absent'}])),
            ('section opening', lambda s: s['sections'][1].update(passageBreakAnchors=[{'line': 'BOOK I.'}])),
            ('section end', lambda s: s['sections'][1].update(passageBreakAnchors=[{'line': 'NOTES'}])),
            ('not audited as heading', lambda s: s['sections'][1].update(passageBreakAnchors=[{'line': 'Second verse line'}])),
            ('duplicate break', lambda s: s['sections'][1]['passageBreakAnchors'].append({'line': 'Caption text'})),
            ('bad occurrence', lambda s: s['sections'][1]['passageBreakAnchors'][0].update(occurrence=-1)),
            ('bad count', lambda s: s['sections'][1]['passageBreakAnchors'][0].update(count=2)),
            ('not list', lambda s: s['sections'][1].update(passageBreakAnchors={})),
        ]
        for label, mutate in mutations:
            with self.subTest(label=label):
                spec = copy.deepcopy(self.spec)
                mutate(spec)
                with self.assertRaises(ValueError):
                    self.build(spec)


if __name__ == '__main__':
    unittest.main()
