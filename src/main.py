# ------------------------------------------------------------------------------------------------------------------
# APERC Energy Model
# updated: 2020_08_09 / David WOGAN
#
# To run:
# 1. edit the path to data sheets in model_config.yml
# 2. adjust the number of years and economies to solve
# 3. add a description and version to the 'Name' field
# 4. run this script: `python main.py`
#
# ------------------------------------------------------------------------------------------------------------------
from __future__ import division
import pandas as pd
import numpy as np
from pyomo.environ import *
from pyomo.core import *
from pyomo.opt import SolverFactory,SolverStatus,TerminationCondition
import sys
import time
import cloudpickle

sys.path.insert(0, './')
from model_code import define_osemosys
from preprocess import *
from postprocess import *
from configure_run import *
from pyutilib.services import TempfileManager
TempfileManager.tempdir = '../tmp'
#TempfileManager.tempdir = '~/Documents/mytemp'

tic = time.time()
model_start = time.strftime("%Y-%m-%d-%H%M%S")
print('\n-- Model started at {}.'.format(model_start))

# ------------------------------------------------------------------------------------------------------------------
# configure the model
# ------------------------------------------------------------------------------------------------------------------
configuration = configure_run()
subset_of_years = configuration[0]
subset_of_economies = solver = configuration[1]
scenario = configuration[2]
list_of_dicts = configuration[3]
solver = configuration[4]
run_name = configuration[5]

print('\n-- Running model: {}, {}, {}, 2017-{}, using {}...'.format(run_name,subset_of_economies,scenario,subset_of_years,solver))

# ------------------------------------------------------------------------------------------------------------------
# load model data
# ------------------------------------------------------------------------------------------------------------------

# combine data
combined_data = combine_datasheets(list_of_dicts)

# write combined input data files to one Excel for inspection
write_inputs(combined_data, model_start,subset_of_economies,subset_of_years,run_name)

# put in dict structure
data = create_data_dict(combined_data,subset_of_years,subset_of_economies,scenario)

# ------------------------------------------------------------------------------------------------------------------
# create abstract pyomo osemosys model
# ------------------------------------------------------------------------------------------------------------------
print('\n-- Reading in the OSeMOSYS formulation...')
model = define_osemosys()

# ------------------------------------------------------------------------------------------------------------------
# create model instance
# ------------------------------------------------------------------------------------------------------------------
print('\n-- Creating the model instance...')
instance = model.create_instance(data)
#instance.write(
#    '../results/{}_{}_{}_{}.lp'.format(model_start,run_name,subset_of_economies,scenario),
##    io_options={'symbolic_solver_labels':True}
#    )

#with open('../model runs/{}_{}_{}_{}.pkl'.format(model_start,subset_of_economies,scenario,run_name),mode='wb') as file:
#    cloudpickle.dump(instance,file)

print('\n-- Sending to the solver...')
print('\n-- Solving with {}...\n'.format(solver))

opt = SolverFactory(solver)
if solver == 'cbc':
    opt.options["primalT"]=1e-6 # CBC options
    opt.options["dualT"]=1e-6 # CBC options
elif solver == 'glpk':
    opt = SolverFactory('glpk')
    #opt.options["--nopresol"] # GLPK options
    #opt.options["TolBnd = 1e-6"] # GLPK options

results = opt.solve(instance,tee=True,report_timing=True,keepfiles=False)

#print('\nStoring the results as a json file...') # optional
## so we can write all levels to a results.json file
#instance.solutions.store_to(results)
#results.write(filename='../model runs/{}_py_results_{}_{}.json'.format(model_start,subset_of_economies,sectors), format='json')

# ------------------------------------------------------------------------------------------------------------------
# extract results
# ------------------------------------------------------------------------------------------------------------------
print('\n-- Extracting the results...')

results_dict = extract(instance)

print('\n-- Processing the results...')

# write both results and a few input parameters to the results file
results_dfs = make_dfs(results_dict)

result_tables = pivot_results(results_dfs)

print('\n-- Writing results...')

write_results(result_tables, model_start,subset_of_economies,subset_of_years,run_name)
toc = time.time()

print('\n-- The model ran for {:.2f} seconds.'.format(toc-tic))
print('\n-- Finished running model: {}, {}, {}, {}, 2017-{}, using {}.\n'.format(model_start,run_name,subset_of_economies,scenario,subset_of_years,solver))

