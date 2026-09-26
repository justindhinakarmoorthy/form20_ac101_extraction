import pdfplumber
import pandas as pd
import os

PDF_PATH = "/Users/justinvanu/dharapuram/raw_documents/AC101.pdf"

booth_rows = []   # every booth row, from every page
total_rows = []   # the 3 summary rows at the end. This is being used for Qa 

with pdfplumber.open(PDF_PATH) as pdf:

    # header: built once from page 1 (same as Stage 2)
    first_table = pdf.pages[0].extract_tables()[0]
    names = []
    for t, b in zip(first_table[0], first_table[1]):
        value = b if b is not None else t
        names.append(value.replace('\n', ' '))

    # loop over every page
    for page in pdf.pages:
        table = page.extract_tables()[0]
        rows = table[2:]                  # skipping header for the next pages as they get repeated. 2: means 2 and there on 
        for row in rows:
            if row[0].isdigit():       
                booth_rows.append(row)
            else:
                total_rows.append(row)

df = pd.DataFrame(booth_rows, columns=names)
totals = pd.DataFrame(total_rows, columns=names)

df = df.rename(columns={'Serial No.': 'serial_no',
                        'Serial No. Of Polling Station': 'booth_no'})
df['booth_no'] = df['booth_no'].str.strip()

# --- Stage 4: text -> numbers
vote_cols = df.columns[2:]                    # BLANK: every column from position 2 onward
df[vote_cols] = df[vote_cols].astype(int)
totals[vote_cols] = totals[vote_cols].astype(int)
df['serial_no'] = df['serial_no'].astype(int)

print(df.dtypes)

# --- Stage 4: QA checks ---

# candidate columns: position 2 up to (not including) 'Total of Valid Votes'
end = df.columns.get_loc('Total of Valid Votes')
cand_cols = df.columns[2:end]

# the 3 total rows, picked by position
evm    = totals[vote_cols].iloc[0]   # Total EVM Votes
postal = totals[vote_cols].iloc[1]   # Total Postal Ballot Votes
polled = totals[vote_cols].iloc[2]   # Total Votes Polled

# ROW checks (left to right): one True/False per booth
df['check_valid'] = df[cand_cols].sum(axis=1) == df['Total of Valid Votes']
df['check_total'] = (df['Total of Valid Votes'] + df['No. Of Rejected Votes'] + df['NOTA']) == df['Total']

# COLUMN checks (top to bottom): one True/False per column
check_evm    = df[vote_cols].sum(axis=0) == evm
check_polled = (evm + postal) == polled

# BOOTH checks
check_serial = df['serial_no'].tolist() == list(range(1, len(df) + 1))

# summary
print("Row: candidates = valid        :", df['check_valid'].all())
print("Row: valid + rejected + NOTA   :", df['check_total'].all())
print("Col: booths add up to EVM row  :", check_evm.all())
print("Col: EVM + postal = polled     :", check_polled.all())
print("Booths: serial 1..N, no gaps   :", check_serial)
print("Booths: booth_no unique        :", df['booth_no'].is_unique)

# show anything that failed
print(df.loc[~df['check_valid'] | ~df['check_total'], ['serial_no', 'booth_no']])
print(check_evm[~check_evm])

# --- Stage 5, step 1: add the postal row as its own "booth" ---

df = df.drop(columns=['check_valid', 'check_total'])   # QA passed, remove helper columns
df['vote_type'] = 'EVM'                                 # every booth row so far is EVM

postal_row = totals.iloc[[1]].copy()                    # row 1 = Total Postal Ballot Votes
postal_row = postal_row.rename(columns={'Serial No.': 'serial_no',
                                        'Serial No. Of Polling Station': 'booth_no'})
postal_row['serial_no'] = len(df) + 1                   # 321, so it sorts after the last booth
postal_row['booth_no'] = 'Postal'
postal_row['vote_type'] = 'Postal'

df = pd.concat([df, postal_row], ignore_index=True)     # stack the postal row under the booths

print(len(df))
print(df.tail(2))


# turning wide into long format 

# --- Stage 5, step 2: melt wide -> long ---

long = df.melt(id_vars=['serial_no', 'booth_no', 'vote_type'],   # columns that stay as they are
               value_vars=list(cand_cols) + ['NOTA'],             # columns that become rows
               var_name='candidate',                              # new column: who
               value_name='votes')                                # new column: how many

long = long.sort_values('serial_no', kind='stable').reset_index(drop=True)

print(len(long))
print(long.head(10))

# adding meta data for future 

# --- Stage 5, step 3: constituency details + final check ---

AC_NO = 101
AC_NAME = 'Dharapuram'
YEAR = 2026        # change this if the PDF is from a different election

long['year'] = YEAR
long['ac_no'] = AC_NO
long['ac_name'] = AC_NAME

long = long[['year', 'ac_no', 'ac_name', 'serial_no', 'booth_no',
             'vote_type', 'candidate', 'votes']]        # put the columns in a sensible order

# final check: each candidate's long-format total = the Total Votes Polled row
cand_totals = long.groupby('candidate', sort=False)['votes'].sum()
check_long = (cand_totals == polled[cand_totals.index]).all()

print("Long totals match polled row:", check_long)
print(cand_totals)
print(long.head(3))


# --- Stage 6: write to Excel ---

booth_summary = df[['serial_no', 'booth_no', 'vote_type',
                    'Total of Valid Votes', 'No. Of Rejected Votes',
                    'NOTA', 'Total', 'No. Of Tendered Votes']]

OUTPUT_DIR = "/Users/justinvanu/dharapuram/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)                    # create the folder if it isn't there
OUT_FILE = f"{OUTPUT_DIR}/AC{AC_NO}_{AC_NAME}_{YEAR}_long.xlsx"

with pd.ExcelWriter(OUT_FILE) as writer:
    long.to_excel(writer, sheet_name='votes_long', index=False)
    booth_summary.to_excel(writer, sheet_name='booth_summary', index=False)

print("Saved:", OUT_FILE)