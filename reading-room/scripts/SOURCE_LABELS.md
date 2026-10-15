# Source-link descriptions

Verified catalog records may provide a `source_labels` object with these optional
plain-text strings:

- `text_label`: edition-details term for the source text/notices link
- `text_link`: link text for the existing `notices || path` destination
- `archive_label`: edition-details term for the preservation archive
- `archive_link`: link text for the existing `preservation_archive.path`
- `scan_link`: link text for the existing original PDF scan

Use these to distinguish derived text from an original digital text, or an
assembled HTML/CSS preservation bundle from an original illustrated archive.
They do not change verification, source pins, URLs, rights, archive validation,
or transcription status. Keep the source qualifications in the catalog/spec
aligned with the actual preserved assets. Missing, blank or non-string labels
fall back to the existing text/archive descriptions. All labels are rendered as
safe text nodes; markup is never interpreted.

The default original-scan link is neutral: `Open the unchanged source scan (PDF)`.
It no longer assigns the 1929 Yoruba date to another source. Actual verified
dates remain in edition details; an explicit `scan_link` can include a date
only after source verification. The download link and filename remain unchanged.
Any verified catalog entry with `source_scan` gets these links, including an
original digital TXT with a separate companion print scan; scan access is not
tied to one transcription status.
This is a separately reviewed presentation change, independent of verse layout.

Check with `node tests/test_scan_label_dom.cjs` and the full reader DOM tests.
