import yaml
import pandas as pd

def configure_run():
    print('\n-- Reading in data sheets...')

    with open('.\data_config.yml') as file:
        data_config = yaml.load(file, Loader=yaml.FullLoader)
    keep_dict={}
    for key,value in data_config.items():
        new_dict = data_config[key]
        for k,v in new_dict.items():
            if k == 'short':
               _name = v
               keep_dict[key] = _name

    keep_list = [x if y == 'None' else y for x,y in keep_dict.items()]

    with open('./model_config.yml') as file:
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
                    __dict = {k: filtered_data[k] for k in keep_list}
                    #list_of_dicts.append(_dict)
                    list_of_dicts.append(__dict)
                    #list_of_dicts.append(filtered_data)
    return subset_of_years,subset_of_economies,scenario,list_of_dicts,solver,run_name
