# Instructions

## Step 1. Create the environment with dependencies.

In your command prompt, navigate to the `aperc-osemosys` folder and enter:

`conda env create --prefix ./ose-env --file ./workflow/envs/ose-env.yml`

## Step 2. Activate the environment.
`conda activate ./ose-env`

# Step 3. Add the otoole package.

`pip install otoole`

## Step 4. Add the data.
Copy the following data sheets from the Integration folder to `./data/`:
- data-sheet-agriculture
- data-sheet-buildings
- data-sheet-industry
- data-sheet-nonspecified
- data-sheet-ownuse
- data-sheet-pipeline-transport
- data-sheet-power
- data-sheet-refining
- data-sheet-supply
- data-sheet-transport
- data-sheet-yyy

## Step 5. Configure the model run.
In your favorite text editor (e.g., Visual Studio Code), modify the following:
- open `./config/model_config.yml`
- Change the forecast period. For example: `2020`.
- Change the economy. For example: `01_AUS`.

## Step 6. Create the data for OSeMOSYS.

`python ./workflow/scripts/process_data.py`

## Step 7. Solve the model.

`glpsol -d ./data/datafile_from_python.txt -m ./workflow/model/osemosys-fast.txt -o ./results/solution.sol`

## Step 8. Process the results.

`python ./workflow/scripts/process_results.py`

Results are saved in `./results/`. The combined results file is named `results.xlsx`. Other files are created:
- csv files for each result parameter
- a `.sol` file with the solver solution output.
