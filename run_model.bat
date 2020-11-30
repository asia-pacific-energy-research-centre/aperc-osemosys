call conda activate ./ose-env

python ./workflow/scripts/process_data.py

glpsol -d ./data/datafile_from_python.txt -m ./workflow/model/osemosys-fast.txt -o ./results/solution.sol

python ./workflow/scripts/process_results.py
