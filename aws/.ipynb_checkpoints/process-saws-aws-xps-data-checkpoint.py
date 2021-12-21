from glob import glob
import pandas as pd
import numpy as np
import tabula # install module as: pip install tabula-py
import fitz # install modules as: pip install pymupdf
import xarray as xr
import scipy.io as sio
import os


filePath='/Users/marcel/Google Drive/Projects/code-repos/process-sa-agulhas-ii-data/aws/aws_test_data/'
files=sorted(glob(filePath+'*.xps')) # list all the xps files

# covert the xps to pdf and save a copy of each
for f in files:
    xps = fitz.open(f)
    pdfbytes = xps.convert_to_pdf()
    pdf = fitz.open("pdf", pdfbytes)
    pdf.save(filePath+str(f)[-13:-4]+".pdf")
    
# now let's get a list of those pdf files
files_pdf = [f.replace('xps', 'pdf') for f in files]

# now convert the pdf files to csv
for f in files_pdf:
    tabula.read_pdf(f, pages='all', silent=True)
    tabula.io.convert_into_by_batch(filePath, output_format='csv', pages='all', silent=True)
    
# now let's get a list of those csv files
files_csv = [f.replace('pdf', 'csv') for f in files_pdf]

# read in csv files, rename headers and concatenate all to a pandas dataframe
headers=['Time', 'Temperature', 'DewPoint',  'SeaTemp', 'Humidity', 'WindSpeed', 'WindGust', 'WindDir', 'Pressure', 'Salinity', 'Latitude', 'Longitude']

for i,f in enumerate(files_csv):
    
    df=pd.read_csv(f)
    df.columns=headers
    
    for ii,t in enumerate(df.Time):
    
        if 'Page' in t:
            df=df.drop([ii])
            
        elif 'Date/Time' in t:
            df=df.drop([ii])
            
        else:
            yr=t[:4]
            mn=t[5:7]
            dy=t[8:10]
            ms=t[11:]
      
            time = np.datetime64(yr+'-'+mn+'-'+dy+' '+ms)
      
            df['Time'][ii] = time
        
    if i==0:
        
        df_main = df
        
    if i>0:
        
        df_main = pd.concat([df_main, df])
        
# now we need to make sure all negative value are correct as tabula doesn't pick up the negatives from the pdf

var = ['Temperature', 'DewPoint', 'SeaTemp', 'Latitude', 'Longitude']

for v in var:
    
    for i in range(df_main.shape[0]):
        
        if 'nan' in str(df_main[v].values[i]):
            continue    
                    
        elif '\xad' in str(df_main[v].values[i]):
            df_main[v].values[i] = -1*np.array(df_main[v].values[i][1:]).astype(float)
        
        else:    
            df_main[v].values[i] = np.array(df_main[v].values[i][1:]).astype(float)
            
    df_main[v] = df_main[v].astype(float)
    
headers=['Temperature', 'DewPoint',  'SeaTemp', 'Humidity', 'WindSpeed', 'WindGust', 'WindDir', 'Pressure', 'Salinity', 'Latitude', 'Longitude']

# make all values floats
for h in headers:
    
    df_main[h] = df_main[h].astype(float)
    
yr_end=str(df_main.Time.iloc[-1])[:4]
mn_end=str(df_main.Time.iloc[-1])[5:7]
dy_end=str(df_main.Time.iloc[-1])[8:10]

yr_srt=str(df_main.Time.iloc[0])[:4]
mn_srt=str(df_main.Time.iloc[0])[5:7]
dy_srt=str(df_main.Time.iloc[0])[8:10]
    
df_main.to_csv(filePath+'aws_'+yr_srt+mn_srt+dy_srt+'_'+yr_end+mn_end+dy_end+'.csv', index=False)

# now let's put it in an xarray dataset so we can give it some metadata 
ds = df_main.to_xarray()

ds.attrs['vessel']     = 'S.A. Agulhas II'
ds.attrs['data_owner'] = 'South African Weather Service'
ds.attrs['department'] = 'Meteorological Laboratory'
ds.attrs['data_type']  = 'Automatic Weather Station'
ds.attrs['date_start'] = str(ds.Time[0].values)
ds.attrs['date_end']   = str(ds.Time[-1].values)

yr_end=str(ds.Time[-1].values)[:4]
mn_end=str(ds.Time[-1].values)[5:7]
dy_end=str(ds.Time[-1].values)[8:10]

yr_srt=str(ds.Time[0].values)[:4]
mn_srt=str(ds.Time[0].values)[5:7]
dy_srt=str(ds.Time[0].values)[8:10]

ds.to_netcdf(filePath+'aws_'+yr_srt+mn_srt+dy_srt+'_'+yr_end+mn_end+dy_end+'.nc')

# now we can also save it to a matfile if we wish 
mat_data = {name: col.values for name, col in df_main.items()}
sio.savemat(os.path.join(filePath+'aws_'+yr_srt+mn_srt+dy_srt+'_'+yr_end+mn_end+dy_end+'.mat'), mat_data)