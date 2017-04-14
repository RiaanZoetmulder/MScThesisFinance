# MScThesisFinance
## 0.prerequisites

## 1. Parsing
Example command: python main.py --mode=parse --years 1994
## 2. Linking

### Preliminiaries
Make sure that you first parse the statements. Then do the following: 

- a) Ensure that you have a wharton WRDS account. 
- b) Got to the CRSP/Compustat merged section and find linking table.
- c) Do a query for CIK numbers, SIC codes and CUSIP codes. Ensure that you also select link type code in variables otherwise it won't work. Download the file as a .csv.
- d) create a folder called linking_table in the data folder, rename your downloaded file linking_table.csv and place it in the folder you just created.

Now you can run the linking process.

Command format: python main.py --model=link --years [years]
Example command: python main.py --mode=link --years 1994
