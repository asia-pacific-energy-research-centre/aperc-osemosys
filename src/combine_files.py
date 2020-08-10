import pandas as pd
import numpy as np
import yaml

#def combine_files():
with open('./combine_config.yml') as file:
        specs = yaml.load(file, Loader=yaml.FullLoader)
for key,value in specs.items():
    if key == 'ForecastPeriod':
        subset_of_years = value
    elif key == 'Economies':
        subset_of_economies = value
    elif key == 'Scenario':
        scenario = value
    #elif key == 'Solver':
    #    solver = value
    elif key == 'Name':
        run_name = value
    elif key == 'FilePaths':
        files_to_combine = value
print('Combining files for {}\n'.format(run_name))

list_of_dicts = [pd.read_excel(v,sheet_name=None) for k,v in files_to_combine.items()]
#combined_data = {k:v for d in list_of_dicts for k,v in d.items()}
combined_data = {}
a_dict = list_of_dicts[0]
for key in a_dict.keys():
    list_of_dfs = []
    for _dict in list_of_dicts:
        _df = _dict[key]
        list_of_dfs.append(_df)
    _dfs = pd.concat(list_of_dfs)
    combined_data[key] = _dfs

# write results to Excel
xlsx_file = '../model runs/{}_{}_{}_{}.xlsx'.format(subset_of_economies,scenario,subset_of_years,run_name)
with pd.ExcelWriter(xlsx_file) as writer:
    for k,v in combined_data.items():
        #print(k)
        #print(v)
        v.to_excel(writer, sheet_name=k, merge_cells=False, index=False)
print('\nFinished combining files.')
#    return None

#combine_files()

# ---------------------------------------------------------
# in progress:
# ---------------------------------------------------------

#filtered_dict = {}
#for k,v in combined_data.items():
#    if 'REGION' in v.columns:
#        filtered_dict = v[v['REGION']==subset_of_economies]

# rename several sheets
#combined_data['TotalAnnualMaxCapacityInvest'] = combined_data.pop('TotalAnnualMaxCapacityInvestment')
#combined_data['TotalAnnualMinCapacityInvest'] = combined_data.pop('TotalAnnualMinCapacityInvestment')
#combined_data['TotalTechnologyAnnualActivityLo'] = combined_data.pop('TotalTechnologyAnnualActivityLowerLimit')
#combined_data['TotalTechnologyAnnualActivityUp'] = combined_data.pop('TotalTechnologyAnnualActivityUpperLimit')
#combined_data['TotalTechnologyModelPeriodActUp'] = combined_data.pop('TotalTechnologyModelPeriodActivityLowerLimit')
#combined_data['TotalTechnologyModelPeriodActLo'] = combined_data.pop('TotalTechnologyModelPeriodActivityUpperLimit')