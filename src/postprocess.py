import yaml
import pandas as pd 
#import pyomo.environ as pyo
from pyomo.environ import *
import time
import numpy as np

def extract(instance):
    results_dict = {}
    for v in instance.component_objects(Var, active=True): # or pyo.Var
        var_results = {}
        for index in v:
            #print ("   ",index, value(v[index]))  # doctest: +SKIP
            var_results[index] = value(v[index]) # or pyo.value
        results_dict[v.name] = var_results
    return results_dict

def make_dfs(results_dict):
#def make_dfs(results_dict,data):
    with open('./results_param.yml') as file:
        contents_var = yaml.load(file, Loader=yaml.FullLoader)
    results_dfs = {}
    for key,value in contents_var.items():
        if contents_var[key]['type'] == 'var':
            #print(key)
            _df = pd.Series(results_dict[key]).reset_index()
            indices = contents_var[key]['indices']
            _df.columns=indices
            results_dfs[key] = _df
        #elif contents_var[key]['type'] == 'param':
        #    print(key)
        #    _df = pd.Series(data[None][key]).reset_index()
        #    indices = contents_var[key]['indices']
        #    _df.columns=indices
        #    results_dfs[key] = _df
    _df = results_dfs['ProductionByTechnology']
    _df = _df.drop(['TIMESLICE'],axis=1)
    results_dfs['ProductionByTechnologyAnnual'] = _df
    return results_dfs

def pivot_results(results_dfs):
    with open('./results_param.yml') as file:
        contents_var = yaml.load(file, Loader=yaml.FullLoader)
    _result_tables = {}
    for key,value in contents_var.items():
        indices = contents_var[key]['indices']
        if 'TIMESLICE' in indices:
            #print('This one has TIMESLICE:', key)
            #unwanted_members = {'YEAR', 'VALUE','TIMESLICE'} # original
            unwanted_members = {'YEAR', 'VALUE'}
            _indices = [ele for ele in indices if ele not in unwanted_members]
            _df = results_dfs[key]
            df = pd.pivot_table(_df,index=_indices,columns='YEAR',values='VALUE',aggfunc=np.sum)
            df = df.loc[(df != 0).any(1)] # remove rows if all are zero
            _result_tables[key] = df
        elif 'TIMESLICE' not in indices:
            if contents_var[key]['type'] == 'var':
                #print(key)
                unwanted_members = {'YEAR', 'VALUE'}
                _indices = [ele for ele in indices if ele not in unwanted_members]
                _df = results_dfs[key]
                df = pd.pivot_table(_df,index=_indices,columns='YEAR',values='VALUE')
                df = df.loc[(df != 0).any(1)] # remove rows if all are zero
                _result_tables[key] = df
            elif contents_var[key]['type'] == 'param':
                #print(key)
                unwanted_members = {'YEAR', 'VALUE'}
                _indices = [ele for ele in indices if ele not in unwanted_members]
                _df = results_dfs[key]
                df = pd.pivot_table(_df,index=_indices,columns='YEAR',values='VALUE')
                df = df.loc[(df != 0).any(1)] # remove rows if all are zero
                _result_tables[key] = df
    result_tables = {k: v for k, v in _result_tables.items() if not v.empty}
    return result_tables

def write_results(results_tables, model_start,subset_of_economies,subset_of_years,run_name):
    with pd.ExcelWriter('../results/{}_{}_{}_{}_results.xlsx'.format(model_start,subset_of_economies,subset_of_years,run_name)) as writer:
    #with pd.ExcelWriter('../results/{}_{}_{}_results.xlsx'.format(model_start,subset_of_years,run_name)) as writer:
        for k, v in results_tables.items():
            v.to_excel(writer, sheet_name=k, merge_cells=False)
    return None