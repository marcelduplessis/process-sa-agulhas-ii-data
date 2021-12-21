import scipy.io as sio
import pandas as pd
import os

filePath='sds_test_data/'
file = 'SDS_Export_161221_094610'

df=pd.read_csv(filePath+file+'.csv')
mat_data = {name: col.values for name, col in df.items()}
sio.savemat(os.path.join(filePath+file+'.mat'), mat_data)
