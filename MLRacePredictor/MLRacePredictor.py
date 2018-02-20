# Import libraries necessary for this project
import numpy as np
import pandas as pd
from IPython.display import display # Allows the use of display() for DataFrames
import datetime
import time

pd.set_option('display.max_rows', 500)

# Pretty display for notebooks
%matplotlib inline

# Display a description of the dataset
pd.set_option('display.max_columns', 500)

# Load the wholesale customers dataset
try:
    all_data = pd.read_csv("marathonData.csv")
    print "Running dataset has {} samples with {} features each.".format(*data.shape)
except:
    print "Dataset could not be loaded. Is the dataset missing?"
    
data = all_data[[
    '5K','half','marathon','marathonTrainDis12',
    'marathonTrainDis3','marathonTrainPaceSec12',
    'marathonTrainDays12','marathonDate','halfDate','5KDate']].dropna()


data = data.replace(0,np.nan).dropna()
data = data.replace('null',np.nan).dropna()

data.reset_index(drop=True, inplace=True)

data = data.drop(['marathonDate','halfDate','5KDate'], axis=1)

x = time.strptime('2:24:31','%H:%M:%S')
seconds = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
print seconds

def timeToSeconds(t):
    t = t.split('.')[0]
    try:
        x = time.strptime(t,'%H:%M:%S')
        return datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
    except:
        x = time.strptime(t,'%M:%S')
        return datetime.timedelta(minutes=x.tm_min,seconds=x.tm_sec).total_seconds()

data['5K'] = data['5K'].map(lambda x: timeToSeconds(x))
data['half'] = data['half'].map(lambda x: timeToSeconds(x))
data['marathon'] = data['marathon'].map(lambda x: timeToSeconds(x))

#data['distance'] = data['distance'].map(lambda x: x.split(" ")[0])
display(data)