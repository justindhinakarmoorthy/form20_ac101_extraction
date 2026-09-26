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

print(len(df))
print(df['booth_no'].is_unique)
print(df.tail(3))
print(totals)