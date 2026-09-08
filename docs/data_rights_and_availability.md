# Data rights and availability

This document records the repository's current source-by-source archival position. It is a provenance and release-governance record, not a claim of ownership over third-party material or a substitute for source-specific terms.

## Scope of the MIT License

The repository's MIT License applies to the original software source code and software-oriented documentation authored for this repository.

The MIT License does not grant rights to or relicense:

- third-party raw datasets;
- agency or other source datasets;
- AHA-derived or AHA-linked source material;
- IQVIA OneKey-derived or OneKey-linked source material;
- AHRQ Compendium source material;
- any other externally sourced material governed by its own terms;
- manuscript or article content, for which the eventual publisher's license will control; or
- generated publication assets if a different license is later assigned to them.

Including a checksum, citation, acquisition script, transformation, linkage key, or derived identifier does not change the rights that apply to the original source material. Nothing in this repository claims ownership of a third-party dataset or grants a separate license to an underlying third-party database.

## Snapshot-date semantics

The `2026-08-05` date in `config/raw_sources.json` is the manifest snapshot/freeze date—the recorded analytical snapshot date used to identify the study files. It is not represented as the original retrieval or download date for every dataset. No source-specific historical date should be overwritten or inferred from that manifest date without contemporaneous evidence.

## Source-by-source archival position

### ONC/ASTP — hospital network participation

- Study file: `hospital_network_participation.csv`
- Current position: **Eligible for archival redistribution with source attribution and explicit provenance caveat.**

The agency-published file incorporates information associated with the AHA IT Survey. Archiving this file must attribute the agency source and preserve that provenance caveat. It must not imply ownership of, or a separate license to, the underlying AHA database.

### CMS — Hospital General Information

- Study file: `cms_hospital_general_information.csv`
- Current position: **Eligible for archival redistribution.**

The archival record should preserve the source citation, exact study filename, checksum, and analytical-snapshot provenance.

### CMS — HCAHPS Hospital

- Study file: `HCAHPS-Hospital.csv`
- Current position: **Eligible for archival redistribution.**

The archival record should preserve the source citation, exact study filename, checksum, and analytical-snapshot provenance.

### USDA ERS — 2023 Rural-Urban Continuum Codes

- Study file: `Ruralurbancontinuumcodes2023.csv`
- Current position: **Eligible for archival redistribution with USDA Economic Research Service attribution.**

### AHRQ — Compendium 2023 Hospital Linkage File

- Study file: `chsp-hospital-linkage-2023.csv`
- Current position: **HOLD — written redistribution clarification pending.**

The public AHRQ file incorporates or links information from third-party sources, including IQVIA OneKey and AHA information. At this stage:

- do not place the AHRQ raw snapshot in a public archive;
- do not publicly distribute row-level derived datasets or row-level linkage/QC datasets that reproduce selected AHRQ, IQVIA OneKey, or AHA-linked fields; and
- preserve all applicable source and third-party provenance statements while written clarification is sought.

Aggregate statistical results, model estimates, tables, figures, and aggregate diagnostics may remain part of the reproducibility release. This position does not make a broader legal conclusion about the source material.

## Public-release boundary

The current release disposition is:

- ONC/ASTP snapshot: eligible with source attribution and the AHA provenance caveat above;
- CMS Hospital General Information snapshot: eligible;
- CMS HCAHPS Hospital snapshot: eligible;
- USDA ERS RUCC snapshot: eligible with USDA ERS attribution;
- AHRQ Hospital Linkage snapshot: **HOLD — do not redistribute without written clarification**; and
- any row-level analytical or linkage file containing AHRQ-, IQVIA OneKey-, or AHA-linked fields: **HOLD — do not redistribute without written clarification**.

The hold does not restrict the release of source code, source fingerprints,
acquisition instructions, aggregate model results, publication tables, figures,
statistical summaries, or aggregate diagnostics. No public package may include the
AHRQ raw snapshot or a restricted row-level derivative.

The planned archival structure uses two records. A data/provenance record will
contain the four eligible source snapshots, their checksums, citations, provenance,
terms, and acquisition instructions; it will include only the AHRQ fingerprint,
citation, and acquisition instructions while the hold remains. A separate
software/reproducibility record will contain the reviewed code snapshot,
computational environment, release contracts, source fingerprint manifest,
canonical aggregate results, publication tables and figures, aggregate diagnostics,
manuscript audit, and release checksums. Neither record has been created.

## Machine-readable record

`config/data_rights.json` records the same current dispositions in a simple auditable schema. `config/raw_sources.json` separately records the exact analytical filenames, checksums, dimensions, and official landing pages. Neither file establishes a blanket repository-wide data license.
