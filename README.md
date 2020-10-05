# 1. Instructions

## Step 1. Clone this repository.

Click the green "Code" button to download this code to your computer. It is recommended to use GitHub Desktop.

## Step 2. Create the environment with dependencies.

In your command prompt, navigate to the `aperc-osemosys` folder and enter:

`conda env create --prefix ./ose-env --file ./workflow/envs/ose-env.yml`

## Step 3. Activate the environment.
`conda activate ./ose-env`

## Step 4. Add the otoole package.

`pip install otoole`

## Step 5. Add the data.
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

## Step 6. Configure the model run.
In your favorite text editor (e.g., Visual Studio Code), modify the following:
- open `./config/model_config.yml`
- Change the forecast period. For example: `2020`.
- Change the economy. For example: `01_AUS`.

See Section 2 below for an example.

## Step 7. Create the data for OSeMOSYS.

`python ./workflow/scripts/process_data.py`

## Step 8. Solve the model.

`glpsol -d ./data/datafile_from_python.txt -m ./workflow/model/osemosys-fast.txt -o ./results/solution.sol`

## Step 9. Process the results.

`python ./workflow/scripts/process_results.py`

Results are saved in `./results/`. The combined results file is named `results.xlsx`. Other files are created:
- `.csv` files for each result parameter
- a `.sol` file with the solver solution output.

# 2. Example
The following is an example `model_config.yml` configuration. This run is for Canada for the years 2017-2025 for all sectors excluding bio-refining:

```yml
ForecastPeriod: 2025 #2017-2050
Economies: 03_CDA #['01_AUS','17_SIN','20_USA','03_CDA','05_PRC','16_RUS','10_MAS','07_INA','15_RP','19_THA','21_VN','08_JPN','09_ROK','18_CT','06_HKC',14_PE] # see data sheets for economy abbreviations
Scenario: Current #Current or Announced
Solver: glpk # glpk or cbc
Name: Canada_test #CombinedPowRefSup 
FilePaths:
### Demand sectors:
    AGR: './data/data-sheet-agriculture.xlsx'
    BLD: './data/data-sheet-buildings.xlsx'
    IND: './data/data-sheet-industry.xlsx'
    TRN: './data/data-sheet-transport.xlsx'
    OWN: './data/data-sheet-ownuse.xlsx'
    PIP: './data/data-sheet-pipeline transport.xlsx'
    NON: './data/data-sheet-nonspecified.xlsx'

### Transformation and supply sectors:
    POW: './data/data-sheet-power.xlsx'
    REF: './data/data-sheet-refining.xlsx'
    SUP: './data/data-sheet-supply.xlsx'
    YYY: './data/data-sheet-yyy.xlsx'
```