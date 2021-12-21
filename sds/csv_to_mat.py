import scipy.io as sio
import pandas as pd
import os

fname = 'aws/aws_20211215_20211220'
# fname = 'SDS_Export_161221_094610'

df=pd.read_csv(fname+'.csv')
mat_data = {name: col.values for name, col in df.items()}
sio.savemat(os.path.join(fname+'.mat'), mat_data)