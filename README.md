# aperc-osemosys

The APERC Toolkit for Energy Analysis and Modeling.

## Description
This is the package development repository. 

Are you looking to run the model? Head over to [this repository](https://github.com/asia-pacific-energy-research-centre/Outlook) and follow the instructions.

## Dependencies
_aperc-osemosys_ requires a number of dependencies. To install, copy and paste the following in your command line:

`conda create --prefix ./env python=3.7 networkx datapackage graphviz xlrd glpk`

## Documentation

Coming soon...

## Contributing

To contribute directly to the code development, you first need to install the package in *develop mode*:

    git clone http://github.com/OSeMOSYS/aperc-osemosys
    cd aperc-osemosys
    git checkout <branch you wish to use>
    python setup.py develop

## Note

This project makes use of the OSeMOSYS model, which can be obtained [here](https://github.com/OSeMOSYS).

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
