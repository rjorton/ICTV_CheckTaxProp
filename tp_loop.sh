#!/bin/bash

echo "Simple loop - loop over .xls and .xlsx files in the Excel folder - commands look for programs/data files in the folder up ../"

for file in *.xls*; do  
	
	stub="${file%.xls*}"
	echo "${file} -> ${stub}"
 
	java -jar ../ICTV_CheckProp.jar ${file}

	python ../check_taxprop_2021.py ../MSL_2021_expanded.csv ../MSL-all-2021_unique.txt ${stub}_tpms.txt > ${stub}_tpms_errors.txt 

done
