# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tools for linking Czech National Library (NKCR) authority records with Wikidata. The system downloads MARC21 authority records from NKCR, parses them, matches them to Wikidata items, and generates QuickStatements commands and wiki table reports.

The codebase is in Python 3. Comments and variable names mix Czech and English. README and user-facing output are in Czech.

## Running

```bash
# Process a single week of NKCR data and publish wiki report
python nkcr_run_one_page.py

# Process multiple weeks in batch
python nkcr_run_more_pages.py

# Import authorities into Wikibase instance
python import_autority.py
```

No test suite, linter config, or requirements.txt exists. Key dependencies: `pywikibot`, `pymarc`, `lxml`, `requests`, `MySQLdb`, `sickle`, `jinja2`, `wikibaseintegrator`.

## Architecture

Data flows through a pipeline:

```
NKCR XML files (weekly exports, e.g. 2026-wnew_m_03.xml)
    → autxmlhandler.py  (SAX-based MARCXML parser, produces AutRecord objects)
    → autrecord.py      (extends pymarc.Record with field accessors for names, dates, gender, aliases)
    → nkcr_record.py    (enriches records: date resolution, Wikidata matching)
    → create_nkcr_table.py (orchestrator: generates wiki tables + QuickStatements links)
    → wikitable.py      (Jinja2 template rendering for wikitext output)
    → Wikidata          (published via pywikibot)
```

**Entry points:** `nkcr_run_one_page.py` calls `create_nkcr_table.create_table()` which drives the whole pipeline for one week. `nkcr_run_more_pages.py` loops over multiple weeks.

**Key modules:**
- `nkcrlib.py` — utility functions: FTP download from NKCR (`ftp.nkp.cz`), date resolution from free-text notes, wiki link generation, week number calculation
- `quickstatements.py` — builds URL-encoded QuickStatements commands (labels, descriptions, aliases, dates, properties) for batch Wikidata updates
- `label_deduplicator.py` — handles label uniqueness in Wikibase

**External services:** NKCR FTP (`ftp.nkp.cz`), Wikidata API (via pywikibot), QuickStatements (`tools.wmflabs.org`), local MySQL database (`wikidata_lidi`).

## XML Data Files

Weekly export files follow the naming pattern `{year}-wnew_m_{week:02d}.xml`. These are excluded from git (`.gitignore`). The pipeline processes them by week number, with year/week logic in `nkcrlib.py`.

## Key Conventions

- Record types are distinguished by MARC field tags: persons, places, and concepts use different tag ranges
- Date handling includes precision tracking (`birth_note_precision`, `death_note_precision`) since MARC notes contain imprecise dates
- Week numbering has year-boundary edge cases with special handling (see recent commits for 2025/2026 fixes)
- `user-config.py` contains pywikibot bot configuration — do not commit credential changes
