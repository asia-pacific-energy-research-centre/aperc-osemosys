# INSTRUCTIONS

## 0. Before you begin

You will need several software programs on your computer:

[Visual Studio Code](https://code.visualstudio.com/) – this is a text editor that makes it easy to modify the configuration files (more on this later).

[Miniconda](https://docs.conda.io/en/latest/miniconda.html) – this is a package manager for Python. We create a specific environment (set of programs and their versions) to run the code. You want the Python 3.8 version. During installation, the installer will ask if you want to add conda to the default PATH variable. Select **YES**.

[GitHub Desktop](https://desktop.github.com/) – an easy way to grab code from GitHub. You will need to create a free account.

[Windows Terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701?activetab=pivot:overviewtab) – *Optional*. A modern command line terminal for Windows. You can use the built in Command Prompt too.

The following instructions assume you have installed Visual Studio Code, Miniconda, and GitHub Desktop.

## 1. Getting set up for the first time
### 1.1. Download the model files

Create a folder called `GitHub` on your computer in your user directory. For example, `C:\Users\ShinzoAbe\GitHub`.

Once you have installed the software above, you will need to download the model code. Visit https://github.com/asia-pacific-energy-research-centre/aperc-osemosys . Note the README file that is there. To download the code, click the green “↓ Code” button.

Click “Open with GitHub Desktop”. GitHub Desktop will open. If it is your first time opening the app, you may need to log in with your account.

You will see a dialogue asking you where to save the model files.

Where it says "Local path", choose the "GitHub folder you created above. Click "Clone". When it is finished you can close the app.

### 1.2. Create the Python environment with dependencies.

We will now install all the software that our model requires. In your Command Prompt, navigate to the `aperc-osemosys` folder containing the model files. *Hint*: you can use `cd` to **c**hange **d**irectories. For example, `cd GitHub\aperc-osemosys`.

Once you are in the `aperc-osemosys` directory, copy and paste the following code:

`conda env create --prefix ./ose-env --file ./workflow/envs/ose-env.yml`

Miniconda is now collecting all the programs it needs. This step will take a while.

nnce complete, using the Command Prompt, in your aperc-osemosys directory, copy and paste:

`conda activate ./ose-env`

We need to install one more piece of software that is not available in Miniconda. Copy and paste to your Command Prompt:

`pip install otoole`

Once it is complete, we are ready to run the model. You will not need to repeat these steps.

## 2. Prepare the model
### 2.1. Activate the environment

From now on, when you want to run the model you must first activate the environment. If you are coming from the steps above, your environment is already active. If not, in the Command Prompt, in your aperc-osemosys directory, copy and paste:

`conda activate ./ose-env`

You are now in the active environment called `ose-env`. You can check your command prompt to confirm that is says `ose-env`.

### 2.2. Add the data files

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
- data-sheet-xxx
- data-sheet-yyy

The `xxx` and `yyy` files are very important. `xxx` is required when running the demand sectors separately from supply, refining, and power. The reason is that xxx contains other default parameters, such as the region list, year list, discount rate, etc. `xxx` also contains backstop technologies that produce all the necessary input fuels (e.g., oil, natural gas, electricity etc) that the power, refining, and supply sectors produce.

`yyy` contains the same information for running the Power, Refining, and Supply sectors.

### 2.3. Configure years and economy

We can tell the model which economies, sectors, and years to run.

- Open Visual Studio Code. Go to File > "Open Folder...". Select the `aperc-osemosys` folder.
- Open the file called `model_config.yml`. It is located in `aperc-osemosys\config`.
- Change the ending year for the projection using `EndYear`. For example: `2050`.
- Change the economy using `Economies`. For example: `21_VN`.

## 3. Run the demand sectors

Comment out `POW`, `REF`, `SUP`, `YYY` using `#`. Your `model_config.yml` file should look like (subsitute your own year and economy):

```yml
EndYear: 2050 #2017-2050
Economies: 21_VN #01_AUS, 02_BD, 03_CDA, 04_CHL, 05_PRC, 06_HKC, 07_INA, 08_JPN, 09_ROK, 10_MAS, 11_MEX, 12_NZ, 13_PNG, 14_PE, 15_RP, 16_RUS, 17_SIN, 18_CT, 19_THA, 20_USA, 21_VN
Scenario: Current #Current or Announced
FilePaths:
### Demand sectors:
    AGR: './data/data-sheet-agriculture.xlsx'
    BLD: './data/data-sheet-buildings.xlsx'
    IND: './data/data-sheet-industry.xlsx'
    TRN: './data/data-sheet-transport.xlsx'
    OWN: './data/data-sheet-ownuse.xlsx'
    PIP: './data/data-sheet-pipeline transport.xlsx'
    NON: './data/data-sheet-nonspecified.xlsx'
    XXX: './data/data-sheet-xxx.xlsx'

### Transformation and supply sectors:
    #POW: './data/data-sheet-power.xlsx'
    #REF: './data/data-sheet-refining.xlsx'
    #SUP: './data/data-sheet-supply.xlsx'
    #YYY: './data/data-sheet-yyy.xlsx'
```

*Note*: You do not need to run all demand sectors. You can run with just the sectors you are interested in. ***However, be sure to include XXX.***

### 3.1. Run the demand sectors
Run the following code to read in the data files:

`python ./workflow/scripts/process_data.py`

When it finishes, copy and paste the following command to run the model:

`glpsol -d ./data/datafile_from_python.txt -m ./workflow/model/osemosys-fast.txt -o ./results/solution.sol`

Finally, copy and paste the following command to process the results:

`python ./workflow/scripts/process_results.py`

Results are saved in `./results/`. There are three files:
- The combined results file is named `results.xlsx`.
- `.csv` files for each result parameter (these are all in the `results.xlsx` file)
- a `.sol` file with the solver solution output.

### 3.2. Chart the results (optional)
Follow the instructions using the [8th_outlook_visualisations](https://github.com/asia-pacific-energy-research-centre/8th_outlook_visualisations) repository to visualize the results. You will need the results file created above:
- `results_demands.xslx`

## 4. Run the Power, Refining, and Supply Sectors
### 4.1. Add the fuel demands to the yyy file

- In the `results.xslx` file, `copy` the results from `UseAnnual`. 
- In `data-sheet-yyy.xlsx`, paste the results in the `AccumulatedAnnualDemand` tab.
- `Cut` the results for `10_electricity_Dx` and paste in the `SpecifiedAnnualDemand` tab.
- Delete the empty row in the `AccumulatedAnnualDemand` tab.
- rename `results.xslx` to `results_demand.xslx`

### 4.2. Configure the model for Power, Refining, and Supply sectors
- In the `model_config.yml` file, comment out the Demand sector files using `#` and uncomment the data files for power, refining, and supply. Your `model_config.yml` file should look like:

```yml
EndYear: 2050 #2017-2050
Economies: 21_VN #01_AUS, 02_BD, 03_CDA, 04_CHL, 05_PRC, 06_HKC, 07_INA, 08_JPN, 09_ROK, 10_MAS, 11_MEX, 12_NZ, 13_PNG, 14_PE, 15_RP, 16_RUS, 17_SIN, 18_CT, 19_THA, 20_USA, 21_VN
Scenario: Current #Current or Announced
FilePaths:
### Demand sectors:
    #AGR: './data/data-sheet-agriculture.xlsx'
    #BLD: './data/data-sheet-buildings.xlsx'
    #IND: './data/data-sheet-industry.xlsx'
    #TRN: './data/data-sheet-transport.xlsx'
    #OWN: './data/data-sheet-ownuse.xlsx'
    #PIP: './data/data-sheet-pipeline transport.xlsx'
    #NON: './data/data-sheet-nonspecified.xlsx'
    #XXX: './data/data-sheet-xxx.xlsx'

### Transformation and supply sectors:
    POW: './data/data-sheet-power.xlsx'
    REF: './data/data-sheet-refining.xlsx'
    SUP: './data/data-sheet-supply.xlsx'
    YYY: './data/data-sheet-yyy.xlsx'
```

*Note*: it is recommended to run Power, Refining, Supply, and YYY together.

### 4.3. Run the Power, Refining, and Supply sectors
Run the following code:

`python ./workflow/scripts/process_data.py`

When it finishes, copy and paste:

`glpsol -d ./data/datafile_from_python.txt -m ./workflow/model/osemosys-fast.txt -o ./results/solution.sol`

Finally, copy and paste:

`python ./workflow/scripts/process_results.py`

Results are saved in `./results/` in a file called `results.xlsx`. Rename `results.xslx` to `results_supply.xslx` (or a name of your choice as long as it contains the word "results").

### 4.4. Visualize the results (optional)
Follow the instructions using the [8th_outlook_visualisations](https://github.com/asia-pacific-energy-research-centre/8th_outlook_visualisations) repository to visualize the results. You will need the two results files created above:
- `results_demands.xslx`
- `results_supply.xslx`
