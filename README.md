# Mythic Library

A curated collection of public domain mythological and ancient texts, with emphasis on:
- **Original texts** (in source languages where available)
- **Scholarly transliterations** (for texts in ancient scripts)
- **Authenticated translations** (prioritizing scholarly consensus and fidelity)

## Project Goals

1. **Comprehensive sourcing**: Locate freely available PDFs from Internet Archive, Project Gutenberg, sacred-texts.com, Perseus Digital Library, and other repositories
2. **Verification**: Programmatic tests to verify content authenticity and completeness
3. **Comparative analysis**: Track multiple translations for scholarly comparison
4. **Provenance tracking**: Cite all sources with full metadata

## Directory Structure

```
mythic-library/
├── texts/                    # Organized text collections
│   ├── mesopotamian/         # Sumerian, Akkadian, Babylonian
│   ├── egyptian/             # Ancient Egyptian
│   ├── greek/                # Ancient Greek
│   ├── roman/                # Latin texts
│   ├── norse/                # Old Norse, Icelandic
│   ├── celtic/               # Irish, Welsh
│   ├── indian/               # Sanskrit, Pali
│   ├── persian/              # Avestan, Old Persian
│   ├── chinese/              # Classical Chinese
│   └── other/                # Other traditions
├── sources/                  # Source tracking and metadata
│   ├── master_catalog.csv    # Master list of all texts
│   ├── translations.csv      # Translation tracking
│   └── sources.json          # Detailed source metadata
├── scripts/                  # Acquisition and verification tools
│   ├── fetch/                # Scripts to download from various sources
│   ├── verify/               # Content verification tools
│   └── compare/              # Translation comparison tools
├── tests/                    # Verification tests
└── docs/                     # Documentation
```

## Source Repositories

Primary sources we search:
- [Internet Archive](https://archive.org) - Vast collection of scanned books
- [Project Gutenberg](https://gutenberg.org) - Public domain ebooks
- [Sacred Texts](https://sacred-texts.com) - Religious and mythological texts
- [Perseus Digital Library](https://www.perseus.tufts.edu) - Greek and Latin with originals
- [ETCSL](https://etcsl.orinst.ox.ac.uk) - Electronic Text Corpus of Sumerian Literature
- [CDLI](https://cdli.ucla.edu) - Cuneiform Digital Library Initiative

## Verification Approach

Each text acquisition includes:
1. **Source citation**: Full URL, access date, original publication info
2. **Checksum**: SHA-256 hash of downloaded content
3. **Cross-reference**: Compare against known chapter/line counts
4. **Scholarly validation**: Note academic consensus on translation quality

## Usage

```bash
# Fetch a text from Internet Archive
python scripts/fetch/internet_archive.py --id "epic-of-gilgamesh"

# Verify a downloaded text
python scripts/verify/verify_text.py texts/mesopotamian/gilgamesh/

# Compare translations
python scripts/compare/diff_translations.py --text gilgamesh --versions all
```

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on adding new texts.

## License

All texts in this collection are in the public domain. Scripts and tooling are MIT licensed.
