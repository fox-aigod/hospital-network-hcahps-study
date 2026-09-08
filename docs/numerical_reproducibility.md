# Numerical reproducibility and release contracts

## Historical evidence

The original Stage 4 analysis was validated against four exact output hashes. Those
hashes remain verbatim in `config/stage4_analysis_spec.json` under
`historical_reference_output_sha256`. They are genuine evidence for the earlier
validated analysis, not errors and not values to discard.

The original numerical backend was not recorded completely. Later release testing
found that Stage 4 logistic-model output is sensitive at floating-point precision to
the platform and numerical backend. Preserved manuscript evidence identified CPython
3.13.5 and the documented direct package versions as the historical software
environment. Controlled replays on macOS arm64 and Ubuntu 24.04 x86-64, both using
CPython 3.13.5, reproduced zero of the four historical hashes. Other plausible
historical environments tested in Stages 7.3B and 7.3B2 also failed to recover the
original bytes. The unrecorded original backend therefore cannot be reconstructed
from the surviving evidence.

The historical hashes remain provenance references, but they are not the v1.0.0
execution gate. They are not expected to reproduce outside the unrecovered original
numerical backend.

## Official release environment

The normative release environment is Ubuntu 24.04 LTS on x86-64, CPython 3.13.14,
pip 26.2.1, four logical CPUs, and the exact package set in
`requirements-lock.txt`. `config/computational_environment.json` records the
complete environment contract, including the OpenBLAS version, architecture,
threading layer, and thread count. CPython 3.13.5 is retained only as historical
manuscript-environment provenance; it is not a superior release target because it
did not recover the historical Stage 4 bytes.

Two fresh, independent Ubuntu 24.04 x86-64 QEMU environments were built from the
same checksum-verified official image. In both environments the source was CPython
3.13.14 from its signature-verified release archive, pip was 26.2.1, the locked
wheel set was identical, and all five raw-source checksums matched. Independent
execution produced byte-identical scientific results for all 14 Stage 4 artifacts,
all 16 Stage 5 artifacts, and all 16 Stage 6 generated publication artifacts. The
deterministic Stage 6 validation summary is separately reproduced and brings its
complete release-contract inventory to 17 files. The release contracts require exact
byte reproduction in this environment and fail closed on an environment mismatch.
Cross-platform bitwise identity is not claimed.

## Scientific reconciliation

The expanded historical comparator audit recovered 1,110 scientific values and 95
unique hypothesis tests from the preserved results workbook. Comparing those values
with the independently reproduced official-release results found no changes in
significance decisions, estimate signs, confidence-interval conclusions, FDR
decisions, primary scientific conclusions, or substantive manuscript conclusions.
The comparison did find 699 full-precision numerical differences. At publication
precision, 9 manuscript display locations and 49 publication-table cells require
synchronization to the release values. No figure interpretation changed.

The final release values therefore come from fresh execution of the unchanged
scientific pipeline in the fully specified official environment. The historical
workbook and hashes remain comparator and provenance evidence. The separately
reviewed Stage 7.4 and 7.4A work synchronized the manuscript and supplement to those
release values and clarified the reproducibility wording. Its final numerical audit
passed 41/41 checks with zero mismatches, its table-cell audit found zero mismatches,
and no figure or scientific conclusion changed.
