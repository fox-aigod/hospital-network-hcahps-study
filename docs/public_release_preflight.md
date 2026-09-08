# Public-release preflight record

## Scope and starting state

This record documents the Stage 7.6 metadata and governance preflight. It does
not authorize publication, tagging, release creation, data upload, DOI minting,
or Zenodo deposition.

- Starting commit: `46f36aaaf2c98dd18081b5dd2fa73978057ab978`
- Starting tree: `6d47dbd2313a98458aac33e60730f1c29dc1ff96`
- Branch: `main`
- Starting worktree: clean
- GitHub visibility: private
- Git tags: 0
- GitHub Releases: 0
- Tracked raw datasets: 0
- Tracked generated analytical outputs: 0

The five canonical raw snapshots, intermediate/processed row-level files, and
generated outputs exist only as ignored local research files. They are not Git
objects and are not candidates for automatic inclusion in a source-code release.

## Stale-metadata classification

The complete tracked tree was searched for pre-release language. Historical
statements were retained when deleting them would erase audit context.

| Classification | Location and subject | Disposition |
| --- | --- | --- |
| A — stale | `README.md`: final all-data reproduction had not run | Updated to the completed Stage 7.3R result. |
| A — stale | `README.md`: manuscript display synchronization remained pending | Updated to the completed Stage 7.4/7.4A audits. |
| A — stale | `README.md`: author list, declarations, and AI disclosure remained under review | Replaced with the locked Stage 7.5 authorship and governance record. |
| A — stale | `docs/release_validation_procedure.md`: future application of the manuscript update manifest | Updated to require comparison with the already synchronized final documents. |
| A — stale | `docs/numerical_reproducibility.md`: later document synchronization remained to be done | Updated with the completed zero-mismatch synchronization result. |
| A — stale | `docs/stage6_validation_record.md`: final declarations remained author actions | Updated with the completed Stage 7.5 governance result. |
| B — historical | `docs/reproducibility_decision_log.md`: the 2026-09-04 decision deferred synchronization until full reproduction | Retained as a dated historical fact and followed by a new entry documenting completion. |
| B — historical | `docs/stage6_validation_record.md`: the release contract recorded two expected manuscript-display differences | Retained as provenance; the later synchronization result is now explicit. |
| B — historical | Stage 4 historical hashes and historical-environment descriptions | Retained unchanged as provenance, not represented as the release gate. |
| C — current | AHRQ redistribution clarification remains pending | Retained as a release-data hold. |
| C — current | The repository is private and has no DOI, tag, GitHub Release, Zenodo record, or publication claim | Retained until those separately authorized events occur. |

No disallowed instruction, authorship placeholder, declaration placeholder, or
obsolete one-author study statement remains.

## Citation and authorship decision

`CITATION.cff` remains a CFF 1.2.0 software citation. Elechi Ubalaeze Solomon is
retained as the software/repository author. The other three final manuscript
authors are not mechanically added as software authors because their finalized
contributions do not include software or code development. The README separately
records all four study authors, affiliations, and contribution roles. No article
DOI, software version, release date, or preferred article citation is asserted
before those facts exist.

## Privacy and reachable-history audit

The audit independently inspected all refs, 51 reachable commits, every commit's
author and committer metadata, all 131 unique reachable blobs, and every historical
path. Results:

- every reachable author and committer uses `Elechi Ubalaeze Solomon` with the
  GitHub noreply address;
- no email address of any kind appears in a reachable tracked blob;
- no personal-email string, private-key header, common GitHub/AWS token pattern,
  credential-value assignment, `.env` file, private Drive URL, Codex attachment
  path, or local macOS/Linux home-directory path was found;
- no raw CSV, row-level derivative, generated output, manuscript, supplement,
  spreadsheet, archive, or private local artifact was ever tracked in reachable
  history;
- the only path under `data/raw/` in history is the intentional instructions file
  `data/raw/README.md`;
- the largest reachable blob is 19,811 bytes, and no blob exceeds 1 MiB; and
- raw filenames occur only in code, tests, manifests, and documentation needed to
  identify and verify the external inputs.

No release-blocking privacy or history finding was identified. This audit does
not rewrite history.

## Data-rights gate

The ONC/ASTP snapshot is eligible for archival redistribution with source
attribution and the AHA provenance caveat. The two CMS snapshots are eligible.
The USDA ERS snapshot is eligible with USDA ERS attribution. The AHRQ Hospital
Linkage snapshot remains on hold pending written redistribution clarification.
Any row-level derived file containing AHRQ-, IQVIA OneKey-, or AHA-linked fields
is also on hold. Aggregate estimates, tables, figures, statistical summaries,
and aggregate diagnostics may be released.

The binding file-level disposition and proposed two-record archival structure
are recorded in `docs/data_rights_and_availability.md` and
`docs/public_release_inventory.md`.

## License gate

The standard MIT text remains unchanged. It covers only original repository
software and software-oriented documentation authored for this repository. It
does not purport to license or relicense source datasets, ONC/AHA underlying
content, AHRQ/IQVIA OneKey/AHA-linked material, CMS or USDA materials under
different terms, manuscript/article content governed by later publisher terms,
third-party images or material, or publication assets assigned another license.

## Preflight conclusion

The repository source tree is suitable for a separately authorized visibility
change: it contains no raw or restricted row-level data, no private credentials
or personal contact data, and no release-blocking historical object. Tagging,
GitHub Release creation, assembly of the curated aggregate-output inventory,
Zenodo deposition, DOI registration, and journal publication remain distinct
future actions.
