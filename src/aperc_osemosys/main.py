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
import glob
import shutil

@click.group()
def hello():
    pass

@hello.command()
def clean():
    """Delete temporary files created during the running of the model. Data sheets are not deleted.

    Warning: temporary data results files will be deleted!!!
    """
    print('\n-- Deleting temporary data and results...\n')
    subprocess.run("rm -f tmp/* results/",shell=True)

@hello.command()
@click.option('--economy','-e',type=click.Choice(
    ['01_AUS','02_BD','03_CDA','04_CHL','05_PRC','06_HKC','07_INA',
    '08_JPN','09_ROK','10_MAS','11_MEX','12_NZ','13_PNG','14_PE',
    '15_RP','16_RUS','17_SIN','18_CT','19_THA','20_USA','21_VN','APEC'],case_sensitive=False),multiple=True,
    help="Type the acronym of the economy you want to solve."
        " Multiple economies can be solved by repeating the command."
        " Use 'APEC' to solve all economies. Note that this could take a long time, especially if multiple sectors are solved.")
@click.option('--ignore','-i',type=click.Choice(
    ['01_AUS','02_BD','03_CDA','04_CHL','05_PRC','06_HKC','07_INA',
    '08_JPN','09_ROK','10_MAS','11_MEX','12_NZ','13_PNG','14_PE',
    '15_RP','16_RUS','17_SIN','18_CT','19_THA','20_USA','21_VN'],case_sensitive=False),multiple=True,help="Ignore an economy. This is useful if a sector has no data for an economy. Example: no agriculture in Hong Kong, China.")
@click.option('--sector','-s',type=click.Choice(['AGR','BLD','IND','OWN','NON','PIP','TRN','HYD','POW','REF','SUP','DEMANDS'],case_sensitive=False),
    multiple=True,help="Type the acronym of the sector you want to solve. Multiple sectors can be solved by repeating the command.")
@click.option('--mydemands', is_flag=True, help="When this is used, the demands in 'my-demands.xlsx' file are included.")
@click.option('--years','-y',type=click.IntRange(2017,2070),prompt=True,help="Enter a number between 2017 and 2070")
@click.option('--scenario','-c',default="Reference",type=click.Choice(['Reference','Net-zero','All'],case_sensitive=False),multiple=True,help="Enter your scenario. This is not case sensitive.")
@click.option('--solver','-l',default='GLPK',type=click.Choice(['GLPK'],case_sensitive=False),help="Choose a solver. At present, only GLPK is available.")
def solve(economy,ignore,sector,years,scenario,solver,mydemands):
    """Solve the model and generate a results file.

    Results are available in the folder results/[economy]/.

    You can solve the model for multiple economies and multiple sectors. Note that it is faster to solve sectors individually.

    Please copy the most recent data sheets from Integration\OSeMOSYS data sheets\2018.

    The XXX file is required for demand, refining, and supply sectors.

    Emission factors are calculated automatically for demand sectors.
    """
    tic = time.time()
    model_start = time.strftime("%Y-%m-%d-%H%M%S")
    print('\n-- Model started at {}.'.format(model_start))

    solve_state = True
    config_dict = create_config_dict(economy,ignore,sector,years,scenario,mydemands)
    keep_list = load_data_config()
    for e in config_dict['economy']:
        for c in config_dict['scenario']:
            economy = e
            scenario = c
            list_of_dicts = load_and_filter(keep_list,config_dict,economy,scenario)
            combined_data = combine_datasheets(list_of_dicts)
            combined_data = make_emissions_factors(combined_data,sector)
            write_inputs(combined_data)
            use_otoole(config_dict)
            solve_model(solve_state,solver)
            results_tables = process_results(economy)
            write_results(results_tables,economy,sector,scenario,model_start)
    toc = time.time()
    print('\n-- The model ran for {:.2f} seconds.\n'.format(toc-tic))

def create_config_dict(economy,ignore,sector,years,scenario,mydemands):
    """
    Create dictionary `config_dict` containing specifications for model run.
    """
    config_dict = {}
    demand_sectors = ['AGR','BLD','IND','OWN','NON','PIP','TRN']
    hyd_sector = ['HYD']
    pow_sector = ['POW']
    ref_and_sup = ['REF','SUP']
    if sector[0]=="DEMANDS" or sector[0]=="demands":
        _sector = demand_sectors
    else:
        _sector = [s for s in sector]
    #print(_sector)
    if any(s in _sector for s in demand_sectors):
        _sector.append('XXX')
    elif any(s in _sector for s in hyd_sector):
        _sector.append('XXX')
    elif any(s in _sector for s in ref_and_sup):
        _sector.append('XXX')
    #else:
    #    _sector.append('YYY')
    if mydemands:
        _sector.append('DEM')
    config_dict['sector'] = _sector
    if economy[0]=='APEC' or economy[0]=='apec':
        _economy = ['01_AUS','02_BD','03_CDA','04_CHL','05_PRC','06_HKC','07_INA','08_JPN','09_ROK','10_MAS','11_MEX','12_NZ','13_PNG','14_PE','15_RP','16_RUS','17_SIN','18_CT','19_THA','20_USA','21_VN']
    else:
        _economy = [e for e in economy]
    __economy = [e for e in _economy if e not in ignore]
    if scenario[0]=='All' or scenario[0]=='all':
        scenario = ['Reference','Net-zero']
    _scenario = [c for c in scenario]
    config_dict['economy'] = __economy
    config_dict['years'] = years
    config_dict['scenario'] = _scenario
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

def load_and_filter(keep_list,config_dict,economy,scenario):
    """
    Load data sets according to specified sectors.

    Filters data based on scenario, years, and economies.
    """
    subset_of_economies = economy
    scenario = scenario
    print('Solving {} scenario...\n'.format(scenario))
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
    try:
        os.mkdir('./tmp')
    except OSError:
        #print ("Creation of the directory %s failed" % path)
        pass
    else:
        print ("Successfully created the directory %s " % 'tmp')
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
    with pd.ExcelWriter('./tmp/combined_data.xlsx') as writer:
        for k, v in combined_data.items():
            v.to_excel(writer, sheet_name=k, index=False, merge_cells=False)
    return None

def demand_emissions(df_data_sheet,emission_map):
    df_EmissionActivityRatio = df_data_sheet.merge(right = emission_map, left_on= ["FUEL"], right_index=True)
    df_EmissionActivityRatio.iloc[:,4:-1] = df_EmissionActivityRatio.iloc[:,4:-1].mul(df_EmissionActivityRatio.loc[:,"Carbon content(kg/GJ)"],axis =0 )*1000
    #df_EmissionActivityRatio = df_EmissionActivityRatio.set_index("REGION","TECHNOLOGY","FUEL").groupby(["REGION","TECHNOLOGY"]).sum()
    #df_EmissionActivityRatio = df_EmissionActivityRatio.reset_index()
    df_EmissionActivityRatio["EMISSION"] = df_EmissionActivityRatio["FUEL"].astype(str) + "_CO2"
    df_EmissionActivityRatio = df_EmissionActivityRatio.drop(["FUEL","Carbon content(kg/GJ)"],axis =1 )
    df_EmissionActivityRatio["MODE_OF_OPERATION"] = 1
    #df_EmissionActivityRatio["UNITS"] = "Mt CO2 per PJ"
    #df_EmissionActivityRatio["NOTES"] = np.nan
    return df_EmissionActivityRatio

# emissions factors
def make_emissions_factors(combined_data,sector):
    demand_sectors = ['AGR','BLD','IND','OWN','NON','PIP','TRN']
    if sector[0]=="DEMANDS" or sector[0]=="demands":
        _sector = demand_sectors
    else:
        _sector = [s for s in sector]
    if any(s in _sector for s in demand_sectors):
        with resources.open_text('aperc_osemosys','emissions_factors.csv') as open_file:
            Emission_egeda = pd.read_csv(open_file)
        #Emission_egeda=pd.read_csv('./data/emissions_factors.csv')
        Emission_egeda = Emission_egeda.set_index(['FUEL'])
        #print(Emission_egeda.info())
    
        df_emissions_activity = pd.DataFrame()
        start_cols = ['REGION','TECHNOLOGY','EMISSION','MODE_OF_OPERATION']
        end_cols =  [*range(2017,2071)]
        all_cols = start_cols + end_cols
    
        #input_activity = pd.read_excel('./tmp/combined_data.xlsx', sheet_name = "InputActivityRatio", header=0)
        input_activity = combined_data['InputActivityRatio']
        #print(input_activity.info())
        try: 
            EmissionActivityRatio = demand_emissions(input_activity,Emission_egeda)
            EmissionActivityRatio = EmissionActivityRatio[all_cols]
            #EmissionActivityRatio.to_excel(data['Output_location']+ "EmissionActivityRatio" + paths+".xlsx" ,index= False)
        except:
            EmissionActivityRatio = demand_emissions(input_activity,Emission_egeda)
            #EmissionActivityRatio["SCENARIO"] = "Net-zero"
            EmissionActivityRatio = EmissionActivityRatio[all_cols]
            #df_emissions_activity = pd.concat([df_emissions_activity,EmissionActivityRatio])
            #EmissionActivityRatio["SCENARIO"] = "Reference"
            ##EmissionActivityRatio.to_excel(data['Output_location']+ "EmissionActivityRatio" + paths+".xlsx" ,index= False)
        df_emissions_activity = pd.concat([df_emissions_activity,EmissionActivityRatio])
        df_emissions_activity = df_emissions_activity[~df_emissions_activity.TECHNOLOGY.str.contains("NE_")]
        # CCS
        df_emissions_activity = df_emissions_activity.reset_index(drop = True)
        df_CCS = df_emissions_activity[df_emissions_activity["TECHNOLOGY"].str.contains('ccs')]
        df_captured  = df_emissions_activity.iloc[df_CCS.index]
        
        df_captured.iloc[:,7:] *= 0.8
        df_captured.loc[:,"EMISSION"] = df_captured["EMISSION"].str.replace("CO2","CCS",regex = True )
        df_emissions_activity.iloc[df_CCS.index,7:] *= 0.2
        df_emissions_activity = pd.concat([df_emissions_activity,df_captured])

        df_emissions_activity.to_excel('./tmp/emissions_activity.xlsx' ,index= False)
        combined_data['EMISSION'] = df_emissions_activity[['EMISSION']].drop_duplicates()
        combined_data['EmissionActivityRatio'] = df_emissions_activity
    return combined_data

def use_otoole(config_dict):
    """
    Use otoole to create OSeMOSYS data package.
    """
    subset_of_years = config_dict['years']
    # prepare using otoole
    _path='./tmp/combined_data.xlsx'
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
    
    output_file = './tmp/datafile_from_python.txt'
    
    writer.write(filtered_data2, output_file, default_values)
    return

def solve_model(solve_state,solver):
    """
    Solve OSeMOSYS model.

    Currently only GLPK solver is supported.
    """
    path = "./tmp/"
    try:
        os.mkdir(path)
    except OSError:
        #print ("Creation of the directory %s failed" % path)
        pass
    else:
        print ("Successfully created the directory %s " % path)
    if solve_state == True:
        model_text = resources.read_text('aperc_osemosys','osemosys-fast_1_0.txt')
        f = open('tmp/model.txt','w')
        f.write('%s\n'% model_text)
        f.close()
        if solver == 'GLPK':
            subprocess.run("glpsol -d tmp/datafile_from_python.txt -m tmp/model.txt",shell=True)
        elif solver == 'CBC':
            print("Sorry, CBC is not supported at this time. Please use GLPK.")
            subprocess.run("glpsol -d tmp/datafile_from_python.txt -m tmp/model.txt --wlp tmp/model.lp --check",shell=True)
            subprocess.run("cbc tmp/model.lp solve -solu tmp/results.sol",shell=True)
    else:
        subprocess.run("glpsol -d tmp/datafile_from_python.txt -m tmp/model.txt --wlp tmp/model.lp --check",shell=True)
    return None

def process_results(economy):
    """
    Combine OSeMOSYS solution files and write as the result as an Excel file where each result parameter is a tab in the Excel file.
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

    results_df={}
    for key,value in contents_var.items():
        if contents_var[key]['type'] == 'var':
            fpath = './tmp/'+key+'.csv'
            #print(fpath)
            _df = pd.read_csv(fpath).reset_index(drop=True)
            results_df[key] = _df
    results_dfs = {}
    results_dfs = {k:v for (k,v) in results_df.items() if not v.empty}
    _result_tables = {}
    for key,value in results_dfs.items():
        indices = contents_var[key]['indices']
        _df = results_dfs[key]
        if 'TIMESLICE' in indices:
            unwanted_members = {'YEAR', 'VALUE'}
            _indices = [ele for ele in indices if ele not in unwanted_members]
            df = pd.pivot_table(_df,index=_indices,columns='YEAR',values='VALUE',aggfunc=np.sum)
            df = df.loc[(df != 0).any(1)] # remove rows if all are zero
            _result_tables[key] = df
        elif 'TIMESLICE' not in indices:
            if contents_var[key]['type'] == 'var':
                unwanted_members = {'YEAR', 'VALUE'}
                _indices = [ele for ele in indices if ele not in unwanted_members]
                df = pd.pivot_table(_df,index=_indices,columns='YEAR',values='VALUE')
                df = df.loc[(df != 0).any(1)] # remove rows if all are zero
                _result_tables[key] = df
            elif contents_var[key]['type'] == 'param':
                unwanted_members = {'YEAR', 'VALUE'}
                _indices = [ele for ele in indices if ele not in unwanted_members]
                df = pd.pivot_table(_df,index=_indices,columns='YEAR',values='VALUE')
                df = df.loc[(df != 0).any(1)] # remove rows if all are zero
                _result_tables[key] = df
            elif contents_var[key]['type'] == 'equ':
                unwanted_members = {'YEAR', 'VALUE'}
                _indices = [ele for ele in indices if ele not in unwanted_members]
                df = pd.pivot_table(_df,index=_indices,columns='YEAR',values='VALUE')
                #df = df.loc[(df != 0).any(1)] # remove rows if all are zero
                _result_tables[key] = df
        _result_tables[key]=_result_tables[key].fillna(0)
    results_tables = {k: v for k, v in _result_tables.items() if not v.empty}
    return results_tables

def write_results(results_tables,economy,sector,scenario,model_start):
    scenario = scenario.lower()
    _sector = "_".join(sector)
    if bool(results_tables):
        with pd.ExcelWriter('./results/{}/{}_results_{}_{}_{}.xlsx'.format(economy,economy,_sector,scenario,model_start)) as writer:
            for k, v in results_tables.items():
                v.to_excel(writer, sheet_name=k, merge_cells=False)
        print('\n-- Results are available in the folder /results/{} \n'.format(economy))
    return None

@hello.command()
@click.argument('input')
@click.argument('output')
@click.option('--scenario','-c',type=click.Choice(['Reference','Net-zero'],case_sensitive=False), help="Select results matching Reference or Net-zero.")
@click.option('--prefix','-p', help="Add a prefix to the output filename, such as the economy name.")
def combine(input,output,scenario,prefix):
    """
    Combine results files.

    'input' is the folder of results you want to combine to one file. 'input' is relative to the top level directory.

    'output' is the directory where you want to save the single file of combined results.

    'scenario' can be either Reference or Net-zero.

    'prefix' should be an economy abbreviation, e.g. 03_CDA.
    """
    try:
        os.mkdir(output)
    except OSError:
        pass
    else:
        print ("Successfully created the directory %s " % output)
    model_start = time.strftime("%Y-%m-%d-%H%M%S")
    files = glob.glob(os.path.join(input,"*.xlsx"))
    scenario = scenario.lower()
    _files = [k for k in files if scenario in k]
    list_of_dicts = []
    for f in _files:
        print('Combining {}'.format(f))
        _dict = pd.read_excel(f,sheet_name=None)
        list_of_dicts.append(_dict)
    with resources.open_text('aperc_osemosys','results_config.yml') as open_file:
        contents_var = yaml.load(open_file, Loader=yaml.FullLoader)
    combined_data = {}
    a_dict = list_of_dicts[0]
    for key in a_dict.keys(): #AccumulatedNewCapacity, CapitalInvestment, etc
        indices = contents_var[key]['indices']
        unwanted_members = {'YEAR', 'VALUE'}
        _indices = [ele for ele in indices if ele not in unwanted_members]
        list_of_dfs = []
        for _dict in list_of_dicts: #AccumulatedNewCapacity, AccumulatedNewCapacity, CapitalInvestment, CapitalInvestment, etc, etc
            try:
                _df = _dict[key]
                list_of_dfs.append(_df)
            except:
                pass
        _dfs = pd.concat(list_of_dfs).groupby(_indices).sum().reset_index()
        combined_data[key] = _dfs
        __path = prefix+'_'+scenario+'_results_{}.xlsx'.format(model_start)
    _path = os.path.join(output,__path)
    with pd.ExcelWriter(_path) as writer:
        for k, v in combined_data.items():
            v.to_excel(writer, sheet_name=k, index=False, merge_cells=False)
    return None

@hello.command()
@click.argument('path_from')
@click.argument('path_to')
def move(path_from,path_to):
    """
    Moves files from subdirectories from PATH_FROM to PATH_TO.

    An example use case is moving results files from multiple economy folders within /results. You can set PATH_FROM to results and PATH_TO to results/apec.
    """
    try:
        os.mkdir(path_to)
    except OSError:
        pass
    else:
        print ("Successfully created the directory %s " % path_to)
    for root, dirs, files in os.walk(path_from):
        for file in files:
          path_file = os.path.join(root,file)
          if root != path_to:
            shutil.copy2(path_file,path_to)