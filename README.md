# Form 20 Extraction - Dharapuram (AC101)

Extracts booth-level voting data from the Form 20 PDF for Dharapuram (AC101), Tamil Nadu, and turns it into a long-format Excel file - one row per booth per candidate.

Form 20 is published by the Election Commission of India after every election. It has the votes for each candidate at every polling booth, plus postal votes.

## Output

An Excel file with two sheets:

- **votes_long** - year, ac_no, ac_name, serial_no, booth_no, vote_type, candidate, votes (3,210 rows: 320 booths + postal, x 9 candidates + NOTA)
- **booth_summary** - total valid votes, rejected, NOTA, total and tendered votes per booth (321 rows)

## How it works

Each stage builds on the one before. `stage6.py` runs the full pipeline; the earlier files are kept to show how it was built.

| Stage | What it does |
|---|---|
| 1 | Checks the PDF is text-based and the table can be extracted with pdfplumber |
| 2 | Merges the two-row header into clean column names |
| 3 | Loops through all pages, skips repeated headers, separates booth rows from total rows |
| 4 | Converts votes to numbers and runs QA checks |
| 5 | Adds postal votes as their own booth and reshapes wide to long |
| 6 | Writes the long table and booth summary to Excel |

## QA checks

- Each booth: candidate votes add up to Total of Valid Votes
- Each booth: Valid + Rejected + NOTA = Total
- Each candidate: booth votes add up to the Total EVM row in the PDF
- EVM + Postal = Total Votes Polled
- Serial numbers run 1 to N with no gaps, booth numbers are unique
- After reshaping, each candidate's total still matches the PDF

## How to run

1. Download the Form 20 PDF from [source link] and save it as `raw_documents/AC101.pdf`
2. Install packages: `python3 -m pip install pdfplumber pandas openpyxl`
3. Run: `python3 stage6.py`
4. The Excel file is saved in `output/`

## Notes and known variations

Form 20 layouts are not the same across constituencies and elections. This version is tested on Dharapuram 2026. Other forms may need changes:

- **Rotated text** - text in certain forms can be rotated (for example, candidate names printed vertically), so headers may not extract cleanly.
- **NOTA placement** - NOTA is not always in the same place. On certain forms it is placed outside the candidate columns (as in Dharapuram, where it sits after Total of Valid Votes), so the calculations have to be adjusted to match the layout.
- **Scanned images** - some forms are scanned images with no text layer. These require conversion (OCR) before extraction, which is not covered yet.
- **Booth numbers** - booth_no is kept as text because some constituencies have booths like 45A.

See `dev_log.md` for the build notes and issues hit along the way.