import pandas as pd
import numpy as np
import yaml
import os
from pathlib import Path
from otoole.read_strategies import ReadExcel
from otoole.write_strategies import WriteDatafile
import click
import subprocess
import time
import importlib.resources as resources

@click.group()
def hello():
    pass

@hello.command()
def clean():
    """Delete temporary files created during the running of the model. Data sheets are not deleted.

    Warning: temporary data results files will be deleted!!!
    """
    print('\n-- Deleting temporary data and results...\n')
    subprocess.run("rm -f results/tmp/*.csv results/*.xlsx results/tmp/*.sol results/*.log data/*.lp data/datafile_from_python.txt data/model.txt data/combined_inputs.xlsx *.done",shell=True)

@hello.command()
@click.option('--economy','-e',type=click.Choice(
    ['01_AUS','02_BD','03_CDA','04_CHL','05_PRC','06_HKC','07_INA',
    '08_JPN','09_ROK','10_MAS','11_MEX','12_NZ','13_PNG','14_PE',
    '15_RP','16_RUS','17_SIN','18_CT','19_THA','20_USA','21_VN','APEC'],case_sensitive=False),prompt=True)
@click.option('--sector','-s',type=click.Choice(['demand','supply'],case_sensitive=False),prompt=True,help="Choose 'demand' for all demand sectors.\n Choose 'supply' for hydrogen, power, refining, and supply sectors.")
@click.option('--ignore','-i',type=click.Choice(['AGR','BLD','IND','OWN','NON','PIP','TRN','HYD','POW','REF','SUP','DEM'],case_sensitive=False),multiple=True,help="Ignore a sector(s). It is possible to ignore multiple sectors by repeating the option.")
@click.option('--years','-y',type=click.IntRange(2017,2050),prompt=True,help="Enter a number between 2017 and 2050")
@click.option('--scenario','-c',default="Current",type=click.Choice(['Current','Announced','Climate'],case_sensitive=False),help="Enter your scenario")
@click.option('--solver','-l',default='GLPK',type=click.Choice(['GLPK'],case_sensitive=False),help="Choose a solver.")
def solve(economy,sector,years,scenario,ignore,solver):
    """Solve the model and generate a results file.

    Results are available in results/[economy]/results.xlsx.
    """
    tic = time.time()
    model_start = time.strftime("%Y-%m-%d-%H%M%S")
    print('\n-- Model started at {}.'.format(model_start))

    solve_state = True
    config_dict = create_config_dict(economy,sector,years,scenario,ignore)
    keep_list = load_data_config()
    list_of_dicts = load_and_filter(keep_list,config_dict)
    combined_data = combine_datasheets(list_of_dicts)
    write_inputs(combined_data)
    use_otoole(config_dict)
    solve_model(solve_state,solver)
    results_tables = combine_results(economy)
    write_results(results_tables,economy,sector,model_start)

    toc = time.time()
    print('\n-- The model ran for {:.2f} seconds.\n'.format(toc-tic))

@hello.command()
@click.option('--economy','-e',type=click.Choice(
    ['01_AUS','02_BD','03_CDA','04_CHL','05_PRC','06_HKC','07_INA',
    '08_JPN','09_ROK','10_MAS','11_MEX','12_NZ','13_PNG','14_PE',
    '15_RP','16_RUS','17_SIN','18_CT','19_THA','20_USA','21_VN','APEC'],case_sensitive=False),prompt=True)
@click.option('--sector','-s',type=click.Choice(['demand','supply'],case_sensitive=False),prompt=True,help="Choose 'demand' for all demand sectors.\n Choose 'supply' for hydrogen, power, refining, and supply sectors.")
@click.option('--ignore','-i',type=click.Choice(['AGR','BLD','IND','OWN','NON','PIP','TRN','HYD','POW','REF','SUP'],case_sensitive=False),multiple=True,help="Ignore a sector(s).")
@click.option('--years','-y',type=click.IntRange(2017,2050),default=2050,help="Type a number between 2017 and 2050")
@click.option('--scenario','-c',default="Current",type=click.Choice(['Current','Announced','Climate'],case_sensitive=False),help="Enter your scenario")
def validate(economy,sector,years,scenario,ignore):
    """
    Validate data for a sector. This step builds the model file but does not solve the model.
    """
    solver=None
    solve_state = False
    print('\n-- validating data')
    print('\n   model will stop after validation and will not solve.\n')
    config_dict = create_config_dict(economy,sector,years,scenario,ignore)
    keep_list = load_data_config()
    list_of_dicts = load_and_filter(keep_list,config_dict)
    combined_data = combine_datasheets(list_of_dicts)
    write_inputs(combined_data)
    use_otoole(config_dict)
    solve_model(solve_state,solver)

def create_config_dict(economy,sector,years,scenario,ignore):
    """
    Create dictionary `config_dict` containing specifications for model run.
    """
    demand_sectors = ['AGR','BLD','IND','NON','OWN','PIP','TRN','XXX']
    supply_sectors = ['DEM','HYD','POW','REF','SUP','YYY']
    config_dict = {}
    if sector == 'demand':
        config_dict['sector'] = [s for s in demand_sectors if s not in ignore]
    elif sector == 'supply':
        config_dict['sector'] = [s for s in supply_sectors if s not in ignore]
    config_dict['economy'] = economy
    config_dict['years'] = years
    config_dict['scenario'] = scenario
    return config_dict

def load_data_config():
    """
    Load the model config file with filepaths.
    """
    print('\n-- Reading in data configuration...\n')

    with resources.open_text('aperc_osemosys','data_config.yml') as open_file:
        data_config = yaml.load(open_file, Loader=yaml.FullLoader)

    keep_dict={}
    for key,value in data_config.items():
        new_dict = data_config[key]
        for k,v in new_dict.items():
            if k == 'short':
               _name = v
               keep_dict[key] = _name

    keep_list = [x if y == 'None' else y for x,y in keep_dict.items()]

    print('    ...successfully read in data configuration\n')
    return keep_list

def load_and_filter(keep_list,config_dict):
    """
    Load data sets according to specified sectors.

    Filters data based on scenario, years, and economies.
    """
    subset_of_economies = config_dict['economy']
    scenario = config_dict['scenario']
    with resources.open_text('aperc_osemosys','model_config.yml') as open_file:
        contents = yaml.load(open_file, Loader=yaml.FullLoader)

    list_of_dicts = []
    for key,value in contents.items():
        if key in config_dict['sector']:
            _mypath = Path(value)
            if _mypath.exists():
                print(value)
                _path = value
                _dict = pd.read_excel(_path,sheet_name=None) # creates dict of dataframes
                __dict = {k: _dict[k] for k in keep_list}
                filtered_data = {}
                for key,value in __dict.items():
                    __df = __dict[key]
                    if 'SCENARIO' in __df.columns:
                        ___df = __df[__df['SCENARIO']==scenario].drop(['SCENARIO'],axis=1)
                        ____df = ___df.loc[(___df != 0).any(1)] # remove rows if all are zero
                        filtered_data[key] = ____df
                    else:
                        filtered_data[key] = __df
                for key,value in filtered_data.items():
                    __df = filtered_data[key]
                    if 'REGION' in __df.columns:
                        ___df = __df[__df['REGION']==subset_of_economies]
                        ____df = ___df.loc[(___df != 0).any(1)] # remove rows if all are zero
                        filtered_data[key] = ____df
                    else:
                        filtered_data[key] = __df
                for key,value in filtered_data.items():
                    __df = filtered_data[key]
                    if key == 'REGION':
                        ___df = __df[__df['VALUE']==subset_of_economies]
                        ____df = ___df.loc[(___df != 0).any(1)] # remove rows if all are zero
                        filtered_data[key] = ____df
                    else:
                        filtered_data[key] = __df
                for key,value in filtered_data.items():
                    __df = filtered_data[key]
                    if 'UNITS' in __df.columns:
                        ___df = __df.drop(['UNITS'],axis=1)
                        ____df = ___df.loc[(___df != 0).any(1)] # remove rows if all are zero
                        filtered_data[key] = ____df
                for key,value in filtered_data.items():
                    __df = filtered_data[key]
                    if 'NOTES' in __df.columns:
                        ___df = __df.drop(['NOTES'],axis=1)
                        ____df = ___df.loc[(___df != 0).any(1)] # remove rows if all are zero
                        filtered_data[key] = ____df
                __dict = {k: filtered_data[k] for k in keep_list}
                list_of_dicts.append(__dict)
    return list_of_dicts

def combine_datasheets(list_of_dicts):
    """
    Combine individual data sheets into one datasheet.

    Combined datasheet will be written to Excel then processed by otoole.
    """
    combined_data = {}
    a_dict = list_of_dicts[0]
    for key in a_dict.keys():
        list_of_dfs = []
        for _dict in list_of_dicts:
            _df = _dict[key]
            list_of_dfs.append(_df)
        _dfs = pd.concat(list_of_dfs)
        _dfs = _dfs.drop_duplicates()
        combined_data[key] = _dfs
    return combined_data

def write_inputs(combined_data):
    """
    Write dictionary of combined data to Excel workbook.
    """
    with pd.ExcelWriter('./data/combined_data.xlsx') as writer:
        for k, v in combined_data.items():
            v.to_excel(writer, sheet_name=k, index=False, merge_cells=False)
    return None

def use_otoole(config_dict):
    """
    Use otoole to create OSeMOSYS data package.
    """
    subset_of_years = config_dict['years']

    # prepare using otoole
    _path='./data/combined_data.xlsx'
    reader = ReadExcel()
    writer = WriteDatafile()
    
    data, default_values = reader.read(_path)
    
    # edit data (the dict of dataframes)
    with resources.open_text('aperc_osemosys','data_config.yml') as open_file:
        contents = yaml.load(open_file, Loader=yaml.FullLoader)
    
    filtered_data2 = {}
    for key,value in contents.items():
        _df = data[key]
        if contents[key]['type'] == 'param':
            if ('YEAR' in contents[key]['indices']):
                #print('parameters with YEAR are.. {}'.format(key))
                _df2 = _df.query('YEAR < @subset_of_years+1')
                filtered_data2[key] = _df2
            else:
                #print('parameters without YEAR are.. {}'.format(key))
                filtered_data2[key] = _df
        elif contents[key]['type'] == 'set':
            if key == 'YEAR':
                _df2 = _df.query('VALUE < @subset_of_years+1')
                filtered_data2[key] = _df2
            else:
                #print('sets are.. {}'.format(key))
                filtered_data2[key] = _df
        else:
            filtered_data2[key] = _df
    
    output_file = './data/datafile_from_python.txt'
    
    writer.write(filtered_data2, output_file, default_values)
    return

def solve_model(solve_state,solver):
    """
    Solve OSeMOSYS model.

    Currently only GLPK solver is supported.
    """
    path = "./results/tmp/"
    try:
        os.mkdir(path)
    except OSError:
        #print ("Creation of the directory %s failed" % path)
        pass
    else:
        print ("Successfully created the directory %s " % path)
    
    if solve_state == True:
        model_text = resources.read_text('aperc_osemosys','osemosys-fast.txt')
        f = open('data/model.txt','w')
        f.write('%s\n'% model_text)
        f.close()
        subprocess.run("glpsol -d data/datafile_from_python.txt -m data/model.txt",shell=True)
    else:
        subprocess.run("glpsol -d data/datafile_from_python.txt -m data/model.txt --check",shell=True)
    return None

def combine_results(economy):
    """
    Combine model solution and write as the result as an Excel file.
    """
    print('\n-- Preparing results...')
    parent_directory = "./results/"
    child_directory = economy
    path = os.path.join(parent_directory,child_directory)
    try:
        os.mkdir(path)
    except OSError:
        #print ("Creation of the directory %s failed" % path)
        pass
    else:
        print ("Successfully created the directory %s " % path)

    with resources.open_text('aperc_osemosys','results_config.yml') as open_file:
        contents_var = yaml.load(open_file, Loader=yaml.FullLoader)

        results_dfs={}
    for key,value in contents_var.items():
        if contents_var[key]['type'] == 'var':
            fpath = './results/tmp/'+key+'.csv'
            #print(fpath)
            _df = pd.read_csv(fpath).reset_index(drop=True)
            results_dfs[key] = _df
    with resources.open_text('aperc_osemosys','results_config.yml') as open_file:
        contents = yaml.load(open_file, Loader=yaml.FullLoader)
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

def write_results(results_tables,economy,sector,model_start):
    with pd.ExcelWriter('./results/{}/{}_{}_{}.xlsx'.format(economy,economy,sector,model_start)) as writer:
        for k, v in results_tables.items():
            v.to_excel(writer, sheet_name=k, merge_cells=False)
    print('\n-- Results are available in the folder /results/{}'.format(economy))
    return None