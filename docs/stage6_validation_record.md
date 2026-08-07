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

The locked Stage 6 validation contract requires:

- Main Table 2 source counts to sum to 2,651;
- Main Table 2 primary-outcome counts to sum to 2,409;
- Main Table 3 to contain eight sensitivity analyses;
- the 2025-only global statistic to display as `31.03 (5)`;
- all exact-profile values in Table S1 to match `^[01]{4}$`;
- all five publication figures to be at least 1,600 pixels wide; and
- the machine-readable manuscript-value audit to contain zero failures.

All requirements passed during the final Stage 6 run. The manuscript-value audit contained 41 checks and zero failures; the smallest figure width was 1,919 pixels.

## Word-manuscript verification

The final Word manuscript and supplement were independently compared against the generated canonical CSVs. All three main tables and all six supplementary tables matched their source CSVs cell for cell after whitespace normalization.

Both documents were rendered page by page and visually inspected after the final edits. No clipping, overlap, missing glyphs, broken tables, or header/footer defects were observed. Both documents also passed the DOCX accessibility audit with zero high-, medium-, or low-severity findings.

The documents remain pre-submission copies because final author declarations, institutional ethics/non-human-subjects determination, funding and competing-interest statements, public repository release, and persistent archival DOI are still author actions.
