# v1.0.0 release and draft archival metadata

The GitHub Release description below is the reviewed v1.0.0 release metadata.
The Zenodo sections remain proposals for a separately authorized archival stage.
No DOI or Zenodo record is asserted.

## GitHub Release metadata

- **Title:** v1.0.0 — Reproducible analysis release
- **Version:** v1.0.0
- **Tag:** v1.0.0 (annotated; immutable release identifier)
- **License:** MIT for original repository software and software-oriented
  documentation only; source datasets, manuscript content, third-party material,
  and separately licensed publication assets are excluded from that grant.

### Release description

This is the reviewed reproducibility release for “Association of Health
Information Network Participation Profiles With Patient-Reported Discharge
Information in U.S. Acute Care and Critical Access Hospitals: A National
Cross-Sectional Study.” It contains the source-to-results pipeline, exact
computational-environment lock, tests, source fingerprints, release contracts, and
curated aggregate results and publication assets. Independent reproduction in the
specified Ubuntu 24.04 x86-64 / CPython 3.13.14 locked environment verified all five canonical inputs and all
47 Stage 4–6 contracted artifacts; the all-data suite completed with 40 passed, 0
failed, and 0 skipped. All 95 historical inferential decisions remained stable.

The curated package preserves aggregate Stage 5/6 results, publication tables and
figures, and separately identified post-review diagnostic/provenance artifacts.
Independent external computational/statistical review and manuscript verification
were completed. Reviewer findings were independently adjudicated and corrected,
and final post-review robustness diagnostics preserved the primary scientific
conclusions. Canonical primary scientific code, results, and contracts were not
changed by the review corrections. This verification is not formal journal peer
review and does not claim journal acceptance or publication.

The final manuscript/supplement numerical audit passed 71/71 checks, and the final
table audit passed 812/812 cell checks, both with zero mismatches. The curated
release verifies 43/43 manifest artifact identities, including nine post-review
artifacts, and 46/46 checksum entries. Ordinary GitHub Actions separately validates
repository structure, locked dependency installation, and the applicable tests;
raw-data and generated-output integration tests report expected skips.

Raw and row-level data are not included in the GitHub repository. The AHRQ Hospital
Linkage snapshot and AHRQ-, IQVIA OneKey-, or AHA-linked row-level derivatives are
not redistributed while written rights clarification remains pending. Consult
`docs/data_rights_and_availability.md` and `docs/public_release_inventory.md` before
using or redistributing any external data or publication asset.

Source acquisition instructions, fingerprints, and provenance are documented
separately in the repository. The MIT License applies to original repository
software and software-oriented documentation; it does not relicense source data,
manuscript content, or third-party material. Zenodo archiving and its archival DOI
remain pending a separate stage. No Zenodo DOI or article DOI is claimed.

## Zenodo software/reproducibility record draft

- **Title:** Reproducibility software and aggregate results for the Hospital Network Participation and HCAHPS Study
- **Resource type:** Software
- **Version:** v1.0.0
- **Creator:** Elechi Ubalaeze Solomon; ORCID 0009-0002-3474-1002; Business Administration, Lee Business School, University of Nevada, Las Vegas, Las Vegas, Nevada, USA
- **Study contributors:** Chiderah Akubuiro — clinical interpretation, validation, and review; Abone Kindson — clinical interpretation, validation, literature review, and review; Mohamed Albert Tarawallie — formal analysis, validation, statistical review, and review
- **Keywords:** health information exchange; interoperability; HCAHPS; patient experience; acute care hospitals; critical access hospitals; multiple imputation; inverse probability weighting; reproducible research
- **License field:** MIT, limited to original software and software-oriented documentation
- **Rights note:** Raw datasets, restricted row-level derivatives, manuscript/article content, third-party material, and publication assets assigned another license are not licensed by MIT. The record contains no restricted row-level data.
- **Related identifier:** `https://github.com/fox-aigod/hospital-network-hcahps-study`, relation to be recorded as the source repository; add reciprocal relation to the data/provenance record only after its identifier exists

### Proposed description

Research software and aggregate reproducibility artifacts for a national
cross-sectional analysis of hospital health-information-network participation
profiles and patient-reported discharge information. The record preserves the
versioned GitHub source, official Ubuntu 24.04 x86-64 computational environment,
Stage 4–6 artifact contracts, source fingerprints, canonical aggregate Stage 5
results, publication tables and figures, aggregate diagnostics, manuscript-value
audit, and checksums. The complete all-data workflow was independently reproduced;
no primary or substantive scientific conclusion changed during release validation.

### Intended citation

Use the creator, record title, version v1.0.0, publication year supplied by Zenodo,
publisher “Zenodo,” and the DOI only after Zenodo actually mints it. No DOI or release
year is asserted in this draft.

## Zenodo data/provenance record draft

- **Title:** Source-snapshot provenance archive for the Hospital Network Participation and HCAHPS Study
- **Resource type:** Dataset
- **Version:** v1.0.0
- **Creator:** Elechi Ubalaeze Solomon; ORCID 0009-0002-3474-1002; Business Administration, Lee Business School, University of Nevada, Las Vegas, Las Vegas, Nevada, USA
- **Study contributors:** Chiderah Akubuiro — validation and clinical interpretation; Abone Kindson — validation and clinical interpretation; Mohamed Albert Tarawallie — formal analysis and validation
- **Keywords:** hospital data; health information networks; HCAHPS; CMS; ONC; ASTP; USDA Rural-Urban Continuum Codes; source provenance; checksums; reproducible research
- **License field:** No blanket MIT license. Record source-specific rights for each included snapshot; do not publish if the deposit interface would misrepresent those rights.
- **Rights note:** Include only the four snapshots currently eligible for redistribution, with required attribution and provenance. Exclude the AHRQ Hospital Linkage snapshot and all restricted row-level derivatives. Preserve the AHRQ fingerprint, citation, rights status, and acquisition instructions only.
- **Related identifier:** `https://github.com/fox-aigod/hospital-network-hcahps-study`, relation to be recorded as the associated software/source repository; add reciprocal relation to the software record only after its identifier exists

### Proposed description

Provenance package for the exact analytical source snapshots used in the Hospital
Network Participation and HCAHPS Study. Subject to a final deposit-time terms review,
the record contains the checksum-matching ONC/ASTP hospital-network-participation,
CMS Hospital General Information, CMS HCAHPS Hospital, and USDA ERS 2023 RUCC files,
plus checksums, dimensions, source citations, source-specific rights notes, and
acquisition instructions. The AHRQ Compendium Hospital Linkage file is represented
only by its fingerprint, citation, official acquisition instructions, and HOLD notice;
the file itself and restricted row-level derivatives are excluded.

### Intended citation

Use the creator, record title, version v1.0.0, publication year supplied by Zenodo,
publisher “Zenodo,” and the DOI only after Zenodo actually mints it. No DOI or release
year is asserted in this draft.

## Finalization gates

Before publishing any draft metadata, confirm the final curated aggregate-output
inventory, publication-asset rights notice, source-specific data-record license
fields, creator/contributor approval, reciprocal identifiers after they exist, and
the exact tag/commit. Do not fabricate an article DOI or preferred article citation.
