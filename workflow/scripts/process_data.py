import pandas as pd
import numpy as np
import yaml

def configure_run():
    print('\n-- Reading in data sheets...')

    with open('./config/data_config.yml') as file:
        data_config = yaml.load(file, Loader=yaml.FullLoader)
    keep_dict={}
    for key,value in data_config.items():
        new_dict = data_config[key]
        for k,v in new_dict.items():
            if k == 'short':
               _name = v
               keep_dict[key] = _name

    keep_list = [x if y == 'None' else y for x,y in keep_dict.items()]

    with open('./config/model_config.yml') as file:
        contents = yaml.load(file, Loader=yaml.FullLoader)
    list_of_dicts = []
    for key,value in contents.items():
        if key == 'ForecastPeriod':
            subset_of_years = value
        elif key == 'Economies':
            subset_of_economies = value
        elif key == 'Scenario':
            scenario = value
        elif key == 'Solver':
            solver = value
        elif key == 'Name':
            run_name = value
        elif key == 'FilePaths':
            for k,v in contents['FilePaths'].items():
                if v is not None:
                    print(v)
                    _path = v
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
                    #list_of_dicts.append(_dict)
                    list_of_dicts.append(__dict)
                    #list_of_dicts.append(filtered_data)
    return subset_of_years,subset_of_economies,scenario,list_of_dicts,solver,run_name

configuration = configure_run()
subset_of_years = configuration[0]
subset_of_economies = solver = configuration[1]
scenario = configuration[2]
list_of_dicts = configuration[3]
solver = configuration[4]
run_name = configuration[5]

def combine_datasheets(list_of_dicts):
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

combined_data = combine_datasheets(list_of_dicts)

def write_inputs(combined_data):
    with pd.ExcelWriter('./data/combined_inputs.xlsx') as writer:
        for k, v in combined_data.items():
            v.to_excel(writer, sheet_name=k, index=False, merge_cells=False)
    return None

write_inputs(combined_data)

# prepare using otoole
from otoole.read_strategies import ReadExcel
from otoole.write_strategies import WriteDatafile
_path='./data/combined_inputs.xlsx'
reader = ReadExcel()
writer = WriteDatafile()

data, default_values = reader.read(_path)

# edit data (the dict of dataframes)
with open('./config/data_config.yml') as file:
    contents = yaml.load(file, Loader=yaml.FullLoader)

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



## clean up preprocessing
#
#with open('../data/preprocessed_data.txt', "r") as f:
#    lines = f.readlines()
#with open("../data/preprocessed_data2.txt", "w") as f:
#    for line in lines:
#        if ":=;" not in line:
#            line.strip("\n")
#            f.write(line)