# Form20 Data Extraction

Purpose : To Extract Data from a Form 20. The Form 20 houses booth level voting data and its published by Eelection commission of India for every electiion. 

Stage 1 : Inspecting the file manually. Made sure the its text characters by scrolling over the text. Understanding the layout as form20 tends to have varied layout structure. 
Installed packages - pdfplumber and verified its ability to extract tables using extract_tables() method. 

Stage 2 : Extracted Table and Formed headers. Verified Column headers are captured as expected. 

Inspection : Checks how many pages exists and what exists in page 2 and last 5 rows to see what exists as evm postal votes exists. 

Stage 3 : Looped through all pages and extracted the booth rows. Skipped the 2 header rows on each page. Used serial number (column 0) with isdigit() to separate booth rows from the total rows. Kept the total rows separately for QA.
Renamed columns to serial_no and booth_no. Kept booth_no as a string and trimmed it, since some constituencies have booths like 45A. Serial number is used for ordering.
Result : 320 booths, booth_no unique.
Issue : First tried row[0] is not None to find booth rows. It did not work because the total rows are not empty either. Changed to row[0].isdigit().

Stage 4 : Converted vote columns from text to integers. Ran QA checks.
Row checks - candidates add up to Total of Valid Votes. Valid + Rejected + NOTA = Total.
Column checks - booth totals match the Total EVM row for every column. EVM + Postal = Total Votes Polled.
Booth checks - serial number runs 1 to 320 with no gaps. booth_no is unique.
Result : All checks passed.
Learned : Rejected votes are added to the total, not subtracted. Confirmed using the postal row (2330 + 157 + 21 = 2508).




