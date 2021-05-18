# ICTV_CheckTaxProp
python script to check an ICTV Taxonomic Proposal (TP) for errors

Given an ICTV (2021) Taxonomic Proposal excel file (.xlsx):

```
java -jar ../ICTV_CheckProp.jar my_tp.xlsx
```

This will convert the excel to a text tab delimited file called my_tp_tpms.txt

Then run the python checker:

```
python check_taxprop_2021.py MSL_2021_expanded.csv MSL-all-2021_unique.txt my_tp_tpms.txt
```

This uses two data files from this repo - the MSL_2021_expanded.csv which is the 2021 ICTV MSL expanded to include non-species ranks on separate lines, and MSL-all_unique.txt which is a list of all taxon names that have existsed in the ICTV across all MSLS.

Any errors to do with the proposal will be outputted to the terminal window. The script will check that created/renamed taxons do not re-use existing names, that taxon paths/parents are correct, that higher taxons are not left emopty, etc

There is a simple bash script provided to loop over all excel files that you place within the Excels folder, within that folder simply type:

```
sh ../tp_loop.sh
```
This relies on the Excels folder being within the ICTV_CheckTaxProp folder, as it is looking for the scripts and data files in the folder up (../)
