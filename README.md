# INSTRUCTIONS
This README contains the following sections:

### Table of Contents

0. Before you begin
1. Getting set up for the first time
2. Prepare the model
3. Run the demand sectors
4. Run the Power, Refining, and Supply Sectors
5. Understanding the results file
6. Updating the model code

### Quick start guide
For experienced users:

`conda activate ./ose-env`

`python ./workflow/scripts/process_data.py`

`glpsol -d ./data/datafile_from_python.txt -m ./workflow/model/osemosys-fast.txt -o ./results/solution.sol`

`python ./workflow/scripts/process_results.py`

## 0. Before you begin

You will need several software programs on your computer:

[Visual Studio Code](https://code.visualstudio.com/) – this is a text editor that makes it easy to modify the configuration files (more on this later).

[Miniconda](https://docs.conda.io/en/latest/miniconda.html) – this is a package manager for Python. We create a specific environment (set of programs and their versions) to run the code. You want the Python 3.8 version. During installation, the installer will ask if you want to add conda to the default PATH variable. Select **YES**.

[GitHub Desktop](https://desktop.github.com/) – an easy way to grab code from GitHub. You will need to create a free account.

[Windows Terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701?activetab=pivot:overviewtab) – *Recommended*. A modern command line terminal for Windows. You can use the built in Command Prompt too.

The following instructions assume you have installed Visual Studio Code, Miniconda, and GitHub Desktop.

## 1. Getting set up for the first time
### 1.1. Download the model files

Create a folder called `GitHub` on your computer in your user directory. For example, `C:\Users\ShinzoAbe\GitHub`.

***Note***: it is recommended to create the `GitHub` folder in the location above and **not** in OneDrive.

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

We need to install two more pieces of software that is not available in Miniconda. Copy and paste to your Command Prompt:

`pip install -r ./workflow/envs/requirements.txt`

Once it is complete, we are ready to run the model. ***You do not need to repeat these steps.***

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

#### The XXX and YYY files
The `xxx` and `yyy` files are very important. `xxx` is required when running the demand sectors separately from supply, refining, and power. The reason is that xxx contains other default parameters, such as the region list, year list, discount rate, etc. `xxx` also contains backstop technologies that produce all the necessary input fuels (e.g., oil, natural gas, electricity etc) that the power, refining, and supply sectors produce.

`yyy` contains the same information for running the Power, Refining, and Supply sectors.

***Note***: do not use both `XXX` and `YYY` at the same time.

### 2.3. Configure years and economy

We can tell the model which economies, sectors, and years to run.

- Open Visual Studio Code. Go to File > "Open Folder...". Select the `aperc-osemosys` folder.
- Open the file called `model_config.yml`. It is located in `aperc-osemosys\config`.
- Change the ending year for the projection using `EndYear`. For example: `2050`.
- Change the economy using `Economies`. For example: `21_VN`.

***Note***: Only one economy can be run at a time.

## 3. Run the demand sectors

Comment out `POW`, `REF`, `SUP`, `YYY` using `#`. Your `model_config.yml` file should look like (subsitute your own year and one economy):

```yml
# Enter a single year below:
EndYear: 2050 #2050

# Enter a single economy using a name from the list:
# 01_AUS, 02_BD, 03_CDA, 04_CHL, 05_PRC, 06_HKC, 07_INA,
# 08_JPN, 09_ROK, 10_MAS, 11_MEX, 12_NZ, 13_PNG, 14_PE, 
# 15_RP, 16_RUS, 17_SIN, 18_CT, 19_THA, 20_USA, 21_VN
Economy: 21_VN

# Choose the scenario:
Scenario: Current #Current or Announced

# Choose the sectors you want to run:
FilePaths:
### Demand sectors:
    AGR: './data/data-sheet-agriculture.xlsx'
    BLD: './data/data-sheet-buildings.xlsx'
    IND: './data/data-sheet-industry.xlsx'
    TRN: './data/data-sheet-transport.xlsx'
    OWN: './data/data-sheet-ownuse.xlsx'
    PIP: './data/data-sheet-pipeline transport.xlsx'
    NON: './data/data-sheet-nonspecified.xlsx'
    XXX: './data/data-sheet-xxx.xlsx' # this must be included with any demand sector(s). Do not include if running the sectors below.

### Transformation and supply sectors:
    #POW: './data/data-sheet-power.xlsx'
    #REF: './data/data-sheet-refining.xlsx'
    #SUP: './data/data-sheet-supply.xlsx'
    #YYY: './data/data-sheet-yyy.xlsx' # this must be included when running POW, REF, SUP
```

***Note***: You do not need to run all demand sectors. You can run with just the sectors you are interested in. ***However, be sure to include XXX.***

***Note***: do not use both `XXX` and `YYY` at the same time.

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

## 4. Run the Power, Refining, and Supply Sectors
### 4.1. Add the fuel demands to the yyy file

- In the `results.xslx` file, `copy` the results from `UseAnnual`. Do not copy the header row.
- In `data-sheet-yyy.xlsx`, paste the results in the `AccumulatedAnnualDemand` tab.
- Shift the cells with numbers _right_ two columns so the "Notes" and "Units" columns are empty.
- `Cut` the results for `10_electricity_Dx` and paste in the `SpecifiedAnnualDemand` tab. Ensure that the "Units" and "Notes" columns do not have numbers.
- Delete the empty row in the `AccumulatedAnnualDemand` tab.
- Save the file.
- Rename `results.xslx` to `results_demand.xslx`. ***Note***: "results" must be lowercase.

### 4.2. Configure the model for Power, Refining, and Supply sectors
- In the `model_config.yml` file, comment out the Demand sector files using `#` and uncomment the data files for power, refining, and supply. Your `model_config.yml` file should look like:

```yml
# Enter a single year below:
EndYear: 2050 #2050

# Enter a single economy using a name from the list:
# 01_AUS, 02_BD, 03_CDA, 04_CHL, 05_PRC, 06_HKC, 07_INA,
# 08_JPN, 09_ROK, 10_MAS, 11_MEX, 12_NZ, 13_PNG, 14_PE, 
# 15_RP, 16_RUS, 17_SIN, 18_CT, 19_THA, 20_USA, 21_VN
Economy: 21_VN

# Choose the scenario:
Scenario: Current #Current or Announced

# Choose the sectors you want to run:
FilePaths:
### Demand sectors:
    #AGR: './data/data-sheet-agriculture.xlsx'
    #BLD: './data/data-sheet-buildings.xlsx'
    #IND: './data/data-sheet-industry.xlsx'
    #TRN: './data/data-sheet-transport.xlsx'
    #OWN: './data/data-sheet-ownuse.xlsx'
    #PIP: './data/data-sheet-pipeline transport.xlsx'
    #NON: './data/data-sheet-nonspecified.xlsx'
    #XXX: './data/data-sheet-xxx.xlsx' # this must be included with any demand sector(s). Do not include if running the sectors below.

### Transformation and supply sectors:
    POW: './data/data-sheet-power.xlsx'
    REF: './data/data-sheet-refining.xlsx'
    SUP: './data/data-sheet-supply.xlsx'
    YYY: './data/data-sheet-yyy.xlsx' # this must be included when running POW, REF, SUP
```

***Note***: it is recommended to run Power, Refining, Supply, and YYY together.

***Note***: do not use `XXX` and `YYY` at the same time.

### 4.3. Run the Power, Refining, and Supply sectors
Run the following code:

`python ./workflow/scripts/process_data.py`

When it finishes, copy and paste:

`glpsol -d ./data/datafile_from_python.txt -m ./workflow/model/osemosys-fast.txt -o ./results/solution.sol`

Finally, copy and paste:

`python ./workflow/scripts/process_results.py`

Results are saved in `./results/` in a file called `results.xlsx`. Rename `results.xslx` to `results_supply.xslx` (or a name of your choice as long as it contains the word "results").  ***Note***: "results" must be lowercase.

### 4.4. Visualize the results (optional)
Follow the instructions using the [8th_outlook_visualisations](https://github.com/asia-pacific-energy-research-centre/8th_outlook_visualisations) repository to visualize the results. You will need the results files:
- `results_demands.xslx`
- `results_supply.xslx`

***Note***: You can open another Command Prompt to perform the charting commands (i.e., you do not need to close the `ose-env` environment.)

## 5. Understanding the results file
The results file produced by running `python ./workflow/scripts/process_results.py` in Steps **3.1** and **4.3** contains many useful parameters. Below is a description of each of the results. Please refer to the [OSeMOSYS Documention](https://osemosys.readthedocs.io/en/latest/manual/Structure%20of%20OSeMOSYS.html#variables) for a full description of the parameters and model variables.

#### AccumulatedNewCapacity
This is a running sum of all new capacity additions. It is cumulative each year. It is not the total capacity annual, which is capture in the **TotalCapacityAnnual** result (see below).

#### CapitalInvestment
This is the investment in new capacity in 2017 USD million. It is the product of Capital Cost and capacity investment (**NewCapacity**).

#### NewCapacity
Amount of installed capacity for a technology in each year. It is not cumulative. The product of **NewCapacity** and the Capital Cost is the **CapitalInvstment**.

#### Production
Production of a fuel in a TIMESLICE. It is the *output* activity of a technology. For a breakdown of fuel production by technology see **ProductionByTechnology**.

#### ProductionByTechnology
Production of a fuel by a technology in a TIMESLICE. It is the *output* activity of a technology. This result is used to create the TPES results.

#### ProductionByTechnologyAnnual
Annual production of a fuel by technology and TIMESLICE.

#### TotalCapacityAnnual
The total installed capacity in each year. It is the sum of Residual Capacity and **NewCapacity**.

#### TotalTechnologyAnnualActivity
The annual activity (operation) of a technology. This is useful for checking which technologies are operational. Technologies with zero activity for all years are omitted.

#### UseByTechnology
Consumption (use) of a fuel by a technology in a TIMESLICE. It is the *input* activity of a technology. This result is used to create the FED results.

#### UseAnnual
Annual consumption (use) of a fuel.

## 6. Updating the model code
The model code will be updated periodically. Thus, it is recommended to use GitHub Desktop to keep the files in sync. In GitHub Desktop, click `Pull origin` to automatically sync your computer with GitHub.
