import pandas as pd
import numpy as np
import yaml

with open('./config/results_config.yml') as file:
    contents_var = yaml.load(file, Loader=yaml.FullLoader)

results_dfs={}

for key,value in contents_var.items():
    if contents_var[key]['type'] == 'var':
        fpath = './results/'+key+'.csv'
        #print(fpath)
        _df = pd.read_csv(fpath).reset_index(drop=True)
        results_dfs[key] = _df

def pivot_results(results_dfs):
    with open('./config/results_config.yml') as file:
        contents_var = yaml.load(file, Loader=yaml.FullLoader)
    _result_tables = {}
    for key,value in contents_var.items():        
        #print(key)
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
            elif contents_var[key]['type'] == 'equ':
                #print(key)
                unwanted_members = {'YEAR', 'VALUE'}
                _indices = [ele for ele in indices if ele not in unwanted_members]
                _df = results_dfs[key]
                df = pd.pivot_table(_df,index=_indices,columns='YEAR',values='VALUE')
                #df = df.loc[(df != 0).any(1)] # remove rows if all are zero
                _result_tables[key] = df
        _result_tables[key]=_result_tables[key].fillna(0)
    result_tables = {k: v for k, v in _result_tables.items() if not v.empty}
    return result_tables

result_tables = pivot_results(results_dfs)

def write_results(results_tables):
    with pd.ExcelWriter('./results/results.xlsx') as writer:
        for k, v in results_tables.items():
            v.to_excel(writer, sheet_name=k, merge_cells=False)
    return None

write_results(result_tables)