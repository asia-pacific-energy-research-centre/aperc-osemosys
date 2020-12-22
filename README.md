# aperc-osemosys

The APERC Toolkit for Energy Analysis and Modeling.


## Dependencies
aperc_osemosys requires a number of dependencies, including pygraphviz, which can be difficult to install on Windows.

The easiest way to install the dependencies is to use miniconda.

1. Obtain the miniconda package
2. Add the **conda-forge** channel `conda config --add channels conda-forge`
3. Create a new Python environment

    `conda create -n myenv python=3.7 networkx datapackage graphviz xlrd glpk coincbc`

4. Use pip to install _aperc_osemosys_ `pip install apercem`

## Installation
Install _aperc_osemosys_ using pip:

    pip install apercem

To upgrade _aperc_osemosys_ using pip:

    pip install aperc_osemosys upgrade

## Documentation

Coming soon...

## Contributing

To contribute directly to the documentation of code development, you first need to install the package in *develop mode*:

    git clone http://github.com/OSeMOSYS/aperc-osemosys
    cd aperc-osemosys
    git checkout <branch you wish to use>
    python setup.py develop


## Note

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
