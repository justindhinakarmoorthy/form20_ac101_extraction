# pyrefly: ignore [missing-import]
import pdfplumber
with pdfplumber.open("/Users/justinvanu/dharapuram/raw_documents/AC101.pdf") as pdf:
    page = pdf.pages[0]
    page.extract_tables()
    print(page.extract_tables())

# Inspected the out put , see if I get the results clean in a table 