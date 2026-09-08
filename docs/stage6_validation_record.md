# Stage 6 publication validation record

## Stage 5 repository-transfer integrity repair

During the Stage 6 repository audit, one GitHub source fragment (`scripts/stage5_source/part_11.pyfrag`) was found to contain an encoded transfer payload rather than executable Python. This was a repository-transfer defect, not the code used for the validated local Stage 5 run: the local canonical analysis had been executed from the exact archived statistical script, and the 14 historical result CSVs had already reproduced byte for byte.

The fragment was restored from the exact executable Stage 5 source. The GitHub test suite was then strengthened to assemble and compile the complete Stage 5 fragment sequence. This changed the repository integrity check from a structural-only check into an executable source-integrity check. No data, model specification, estimate, p-value, table, or interpretation changed because of this repair.

## Stage 6 publication assets

Stage 6 generates all publication tables and figures directly from canonical analytical outputs:

- three main manuscript tables;
- six supplementary tables;
- four main figures; and
- one supplementary balance figure.

The cohort-flow figure derives every displayed count from the Stage 1 and Stage 2 machine-readable JSON summaries rather than hard-coded values. Table S1 reads the exact profile bit pattern as a string so leading zeroes are preserved.

The original Stage 6 validation contract required:

- Main Table 2 source counts to sum to 2,651;
- Main Table 2 primary-outcome counts to sum to 2,409;
- Main Table 3 to contain eight sensitivity analyses;
- the 2025-only global statistic to display as `31.03 (5)`;
- all exact-profile values in Table S1 to match `^[01]{4}$`;
- all five publication figures to be at least 1,600 pixels wide; and
- the machine-readable manuscript-value audit to contain zero failures.

All requirements passed during that historical Stage 6 run. The manuscript-value audit contained 41 checks and zero failures; the smallest figure width was 1,919 pixels.

## 2026-09-04 release-contract update

Independent execution in two fresh official Ubuntu 24.04 x86-64 environments
produced byte-identical Stage 6 artifacts. The official release contract now records
all 16 deterministic table, audit, manifest, and figure artifacts plus the
deterministic validation summary (17 contracted files total). The release-value
2025-only global statistic displays as `31.04 (5)`. The preserved manuscript audit
now deliberately records two pending displayed-value updates; it does not silently
treat the historical manuscript values as current. The Word files remain unchanged.

The expanded historical comparison found 9 manuscript display locations and 49
publication-table cells to synchronize after the final all-data reproduction passes.
No inferential or substantive conclusion changed. The exact rationale and release
contract are documented in `docs/numerical_reproducibility.md` and
`config/stage6_release_contract.json`.

## Word-manuscript verification

The final Word manuscript and supplement were independently compared against the generated canonical CSVs. All three main tables and all six supplementary tables matched their source CSVs cell for cell after whitespace normalization.

Both documents were rendered page by page and visually inspected after the final edits. No clipping, overlap, missing glyphs, broken tables, or header/footer defects were observed. Both documents also passed the DOCX accessibility audit with zero high-, medium-, or low-severity findings.

Stage 7.4A finalized the reproducibility wording, and Stage 7.5 finalized the four-author list, contribution statement, ethics/non-human-subjects determination, funding statement, competing-interest declaration, and AI disclosure. The resulting manuscript and supplement passed numerical, table-cell, visual, accessibility, and document-integrity review. They remain pre-submission copies because repository publication, journal submission, release creation, and persistent archival identifiers are separate future actions.
