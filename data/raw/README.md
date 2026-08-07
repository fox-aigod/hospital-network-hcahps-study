# Archived raw data

Raw data files are deliberately excluded from Git because the CMS HCAHPS file exceeds GitHub's ordinary file-size limit and because exact source snapshots should be archived as a single citable research deposit rather than silently replaced by refreshed web files.

Place these five files in this directory using the exact filenames below:

- `hospital_network_participation.csv`
- `cms_hospital_general_information.csv`
- `HCAHPS-Hospital.csv`
- `chsp-hospital-linkage-2023.csv`
- `Ruralurbancontinuumcodes2023.csv`

Run:

```bash
python run_all.py --stage verify-raw
```

The command checks each file against `config/raw_sources.json`, including SHA-256, byte size, row count, and column count. A refreshed file with the same name is rejected if its fingerprint differs.

To build the locked ONC-CMS cohort after verification, run:

```bash
python run_all.py --stage stage1
```
