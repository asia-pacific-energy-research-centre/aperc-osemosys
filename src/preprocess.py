import pandas as pd
import numpy as np
import yaml

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

def create_data_dict(combined_data,subset_of_years,subset_of_economies,scenario):
    # rename several sheets
    combined_data['TotalAnnualMaxCapacityInvestment'] = combined_data.pop('TotalAnnualMaxCapacityInvest') 
    combined_data['TotalAnnualMinCapacityInvestment'] = combined_data.pop('TotalAnnualMinCapacityInvest') 
    combined_data['TotalTechnologyAnnualActivityLowerLimit'] = combined_data.pop('TotalTechnologyAnnualActivityLo') 
    combined_data['TotalTechnologyAnnualActivityUpperLimit'] = combined_data.pop('TotalTechnologyAnnualActivityUp') 
    combined_data['TotalTechnologyModelPeriodActivityLowerLimit'] = combined_data.pop('TotalTechnologyModelPeriodActLo') 
    combined_data['TotalTechnologyModelPeriodActivityUpperLimit'] = combined_data.pop('TotalTechnologyModelPeriodActUp') 

    with open('./data_config.yml') as file:
        contents = yaml.load(file, Loader=yaml.FullLoader)
    
    ## filter combined_data by scenario and return filtered_data
    #filtered_data = {}
    #for key,value in contents.items():
    #    __df = combined_data[key]
    #    if contents[key]['type'] == 'param':
    #        if 'SCENARIO' in __df.columns:
    #            ___df = __df[__df['SCENARIO']==scenario].drop(['SCENARIO'],axis=1)
    #            filtered_data[key] = ___df
    #        else:
    #            filtered_data[key] = __df
    #    else:
    #        filtered_data[key] = __df

    dict_of_df = {}
    for key,value in contents.items():
        if contents[key]['type'] == 'param':
            if ('YEAR' in contents[key]['indices']):
                id_list = contents[key]['indices']
                id_list.remove('YEAR')
                _df = combined_data[key].drop(['UNITS','NOTES'],axis=1)
                dict_of_df[key] = pd.melt(_df,id_vars=id_list,var_name='YEAR',value_name='VALUES').replace({np.nan:''})
                contents[key]['indices'].append('YEAR')
            else:
                _df = combined_data[key]
                _df = _df.rename(columns={'VALUE':'VALUES'})
                dict_of_df[key] = _df
        else:
            if contents[key]['dtype'] == 'str':
                _df = combined_data[key]
                _df = _df.rename(columns={'VALUE':'VALUES'})
                dict_of_df[key] = _df
            else:
                _df = combined_data[key]
                _df = _df.rename(columns={'VALUE':'VALUES'})
                dict_of_df[key] = _df

    # drop duplicates
    for key,value in contents.items():
        if contents[key]['type'] == 'set':
            _df = dict_of_df[key]
            _df = _df.reset_index(drop=True)
            _df = _df.drop_duplicates(subset=['VALUES'])
            dict_of_df[key] = _df

    # adjust the model horizon
    for key,value in contents.items():
        if contents[key]['type'] == 'param':
            __df = dict_of_df[key]
            if 'YEAR' in __df.columns:
                #print('param')
                #print(key)
                #display(__df)
                ___df = __df[__df['YEAR']<=subset_of_years]
                dict_of_df[key] = ___df
        elif contents[key]['type'] == 'set':
            __df = dict_of_df[key]
            if key == 'YEAR':
                #print('set')
                #print(key)
                #display(__df)
                ___df = __df[__df['VALUES']<=subset_of_years]
                dict_of_df[key] = ___df

    # select a subset of economies
    for key,value in contents.items():
        if contents[key]['type'] == 'param':
            __df = dict_of_df[key]
            if 'REGION' in __df.columns:
                ___df = __df[__df['REGION']==subset_of_economies]
                #___df = __df[__df['REGION'].isin(subset_of_economies)]
                dict_of_df[key] = ___df
        elif contents[key]['type'] == 'set':
            __df = dict_of_df[key]
            if 'REGION' in __df.columns:
                ___df = __df[__df['REGION']==subset_of_economies]
                #___df = __df[__df['REGION'].isin(subset_of_economies)]
                dict_of_df[key] = ___df
            if 'RR' in __df.columns:
                ___df = __df[__df['RR']==subset_of_economies]
                #___df = __df[__df['RR'].isin(subset_of_economies)]
                dict_of_df[key] = ___df
            elif key == 'REGION':
                ___df = __df[__df['VALUES']==subset_of_economies]
                #___df = __df[__df['VALUES'].isin(subset_of_economies)]
                dict_of_df[key] = ___df

    # create the pyomo dict
    data_dict = {}
    for key,value in contents.items():
        if contents[key]['type'] == 'param':
            index_list = contents[key]['indices']
            data_dict[key] = dict_of_df[key].set_index(index_list).VALUES.to_dict()
        else:
            data_dict[key] = {None: dict_of_df[key]["VALUES"].values.tolist()}
    data = {None: data_dict}
    return data

def write_inputs(combined_data, model_start,subset_of_economies,subset_of_years,run_name):
    combined_data_copy = combined_data
    with pd.ExcelWriter('../results/{}_{}_{}_{}_inputs.xlsx'.format(model_start,subset_of_economies,subset_of_years,run_name)) as writer:
    #with pd.ExcelWriter('../results/{}_{}_{}_inputs.xlsx'.format(model_start,subset_of_years,run_name)) as writer:
        for k, v in combined_data_copy.items():
            v.to_excel(writer, sheet_name=k, index=False, merge_cells=False)
    return None