# Raw source data

Place the exact archived public-source files in this directory. Do not rename or manually edit them.

The canonical inventory will be maintained in `docs/source_data_manifest.csv` with:

- source agency
- official dataset title
- source page
- reporting period
- archived filename
- access date
- file size
- SHA-256 checksum
- notes on licensing and redistribution

Expected source families:

1. Office of the National Coordinator for Health Information Technology hospital network participation data
2. Centers for Medicare & Medicaid Services hospital characteristics data
3. Hospital Consumer Assessment of Healthcare Providers and Systems data
4. Agency for Healthcare Research and Quality 2023 Hospital Linkage File
5. U.S. Department of Agriculture 2023 Rural-Urban Continuum Codes

Raw files are intentionally excluded from Git until their redistribution status and sizes are reviewed. The pipeline must refuse to run when a required file is missing or its checksum differs from the manifest.
