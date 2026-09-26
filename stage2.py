import pdfplumber
import pandas as pd


#Open and Extract Table 
with pdfplumber.open("/Users/justinvanu/dharapuram/raw_documents/AC101.pdf") as pdf:
    page = pdf.pages[0] # pages 0 - Python counts it as first page 
    tables = page.extract_tables() # Extract all the tables in the page

# Splitting the table into parts

table = tables[0] #first and only table in the page 
top = table[0] #first row in the table 
bottom = table[1] # as per layout this is where the candidate name is housed
data_rows = table[2:] # table 2 is the count of the votes ":" means everthing from here onward

# Building Clean header Names

names = [] # Starts with an empty list (This will house our column names)
for t, b in zip(top, bottom): # pairs the two columns together column by column. Each time round the loop, t is the top cell and b is the bottom cell.
    value = b if b is not None else t # keeps the bottom value if there is one, otherwise the top. There is noting under serial_no so it just keeps serial_no
    names.append(value.replace('\n', ' ')) # Remove the break between the lines  

df = pd.DataFrame(data_rows, columns=names)
print(names)
print(len(names))
print(df.head())
print(names[13]) # Just a Quality check to see if NOTA is Captured and the Column numbers is extracted as expected. 14th Column is nota. 
