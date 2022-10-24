import pandas as pd
import matplotlib.pyplot as plt
import seaborn

# =======
tdf = pd.read_csv('original.csv',index_col='Day', parse_dates=True)

# delete useless columns and row
tdf = tdf.drop(columns=['Work unit details', 'Work unit description', 'Tags', 'Task details', 'Unnamed: 9']).drop('Total')
tdf.dropna().describe()

# facilitate to plot
tdf['Duration'] = tdf['Duration'].str.strip(' min')
pd.to_numeric(tdf['Duration'])

date = tdf.groupby['Day']


