import pdfplumber
import pandas as pd

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