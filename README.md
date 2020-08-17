# APERC OSeMOSYS

## Project organization

Project organization is based on ideas from [_Good Enough Practices for Scientific Computing_](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005510).

1. Put each project in its own directory, which is named after the project.
2. Put external scripts or compiled programs in the `bin` directory.
3. Put raw data and metadata in a `data` directory.
4. Put text documents associated with the project in the `doc` directory.
5. Put all Docker related files in the `docker` directory.
6. Install the Conda environment into an `env` directory. 
7. Put all notebooks in the `notebooks` directory.
8. Put files generated during cleanup and analysis in a `results` directory.
9. Put project source code in the `src` directory.
10. Name all files to reflect their content or function.

## Getting started

### Creating the Conda environment

The `environment.yml` contains the necessary dependencies. You can create the 
environment in a sub-directory of your project directory by running the following command:

```bash
conda env create --prefix ./ose-env --file environment.yml
```

Once the new environment has been created you can activate the environment with the following 
command:

```bash
conda activate ./ose-env
```

Note that the `env` directory is *not* under version control as it can always be re-created from 
the `environment.yml` file as necessary.

#### Updating the Conda environment

If you add (remove) dependencies to (from) the `environment.yml` file after the environment has 
already been created, then you can update the environment with the following command.

```bash
conda env update --prefix ./ose-env --file environment.yml --prune
```

#### Listing the full contents of the Conda environment

The list of explicit dependencies for the project are listed in the `environment.yml` file. To see the full list of packages installed into the environment run the following command.

```bash
conda list --prefix ./ose-env
```

### Installing other packages

This only needs to be performed once. With the `ose-env` environment active, run the following command:

```
pip install PyYAML
```

## Running the model

### Add the data
Place all data in the `data` directory. This directory is *not* under version control.


### Configure the model run
Adjust the run parameters by updating the following fields in the `model_config.yml` file:
- `ForecastPeriod`: the forecast period. Valid years are between 2017 and 2050.
- `Economies`: the economy abbreviation.
- `Scenario`: either "Current" or "Announced".
- `Solver`: glpk. CBC is also an option but will need to be installed separately.
- `Name`: choose a descriptive name for your model run.
- `FilePaths`: comment and uncomment the files you want to run. Note that demand files must be run with the "xxx" file. Power, Refining, and Supply must be run with the "yyy" file.

### Run the model
5. Navigate to the `src` directory:
```
cd src
```

6. Run the model with the following command: 
```
python main.py
```

## Accessing results

Results are stored in the `results` directory. This directory is *not* under version control.
