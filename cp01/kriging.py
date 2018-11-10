import os
import matplotlib.pyplot as plt
#import seaborn as sns

from shapely.geometry import Point
import pandas as pd
from datetime import datetime

import geopandas as gpd
from geopandas import GeoSeries,GeoDataFrame
import numpy as np

#อ่านค่า ฝน
rain_df=pd.read_csv('./rainfall_1981_2018.csv',encoding='cp874',dtype={'dttime': 'str'})
rain_df

rain_df['dttimeobj']=pd.to_datetime(rain_df['dttime'])
rain_df

#เพิ่ม col ปี
rain_df['Year']=rain_df['dttimeobj'].dt.strftime('%Y')

rain_df['Month']=rain_df['dttimeobj'].dt.strftime('%m')
rain_df['D']=rain_df['dttimeobj'].dt.strftime('%d')
rain_df[0:10]

rain_df[rain_df['Month']=='10']

#rain_df['normal']= np.where(pd.to_numeric(rain_df['Year'])< 2011 , 'y','n')
rain_df['s_rainy']= np.where((rain_df['Month']== '11') | (rain_df['Month']== '12'), 'y','n')

rain_df[rain_df['s_rainy']=='y']

#rain_df2=rain_df[rain_df['normal']=='y']
#all_station_by_year=rain_df[['istation_id','Year','dailyRainfall']].groupby(['istation_id','Year'],as_index=False)['dailyRainfall'].sum()
#all_station_by_year
all_station_by_year2=all_station_by_year[pd.to_numeric(all_station_by_year['Year'])<2011]
all_station_by_year2
all_station_by_year3=all_station_by_year2[['istation_id','dailyRainfall']].groupby(['istation_id'],as_index=False)['dailyRainfall'].mean()

#all_station_by_year3

# เลือกเฉพาะ ปี
#all_station_Y1981=all_station_by_year[(all_station_by_year['Year']=='2017') & (all_station_by_year['s_rainy']=='y') ]
all_station_Y1981=all_station_by_year3
#all_station_Y1981=all_station_by_year2[all_station_by_year2['s_rainy']=='n' ]
all_station_Y1981.agg({'dailyRainfall':['max','mean','min']})

# เตรียม shape สถานี
station_df=pd.read_csv('./stations.csv')

#http://pandas.pydata.org/pandas-docs/stable/merging.html
'''
pd.merge(left, right, how='inner', on=None, left_on=None, right_on=None,
         left_index=False, right_index=False, sort=True,
         suffixes=('_x', '_y'), copy=True, indicator=False,
         validate=None)
'''
all_station_Y1981_geo=pd.merge(all_station_Y1981, station_df, how='inner', on='istation_id',\
         left_index=False, right_index=False, sort=True,\
         suffixes=('_x', '_y'), copy=True, indicator=False,\
         validate=None)
all_station_Y1981_geo

geometry = [Point(xy) for xy in zip(all_station_Y1981_geo.longitude, all_station_Y1981_geo.latitude)]
all_station_Y1981_gdf = GeoDataFrame(all_station_Y1981_geo, crs={'init': 'epsg:4326'}, geometry=geometry)
all_station_Y1981_gdf=all_station_Y1981_gdf.to_crs({'init': 'epsg:32647'})
#all_station_Y1981_gdf.to_file(driver = 'ESRI Shapefile', filename= "./rain_thai/2011.shp",encoding='utf-8')


all_station_Y1981_geo.to_csv('./30_all.csv')

import pykrige.kriging_tools as kt
from pykrige.ok import OrdinaryKriging
from pykrige.uk import UniversalKriging

#from Shapely import Point
import numpy as np
'''
data = np.array([[0.3, 1.2, 0.47],
                 [1.9, 0.6, 0.56],
                 [1.1, 3.2, 0.74],
                 [3.3, 4.4, 1.47],
                 [4.7, 3.8, 1.74]])
'''
all_station_Y1981_gdf['x']=all_station_Y1981_gdf.geometry.x
all_station_Y1981_gdf['y']=all_station_Y1981_gdf.geometry.y

#x_max=round(all_station_Y1981_gdf['x'].max())+1000
#x_min=round(all_station_Y1981_gdf['x'].min())-1000

#y_max=round(all_station_Y1981_gdf['y'].max())+1000
#y_min=round(all_station_Y1981_gdf['y'].min())-1000

gridx = np.arange(210000.00, 1320000.00,3000)
gridy = np.arange(540000.00, 2300000.00,3000)

#gridx = np.arange(x_min, x_max,3000)
#gridy = np.arange(y_min, y_max,3000)

len(gridy)
#a=(x_min,x_max,y_min,y_max)
#a
#gridx
#data=list(all_station_Y1981_gdf.geometry.x)
#data

OK = OrdinaryKriging(all_station_Y1981_gdf['x'], all_station_Y1981_gdf['y'],all_station_Y1981_gdf['dailyRainfall'], variogram_model='power',
                     variogram_parameters={'scale':0.5,'nugget':1,'exponent':1},verbose=True, enable_plotting=False,nlags=4)
z, ss = OK.execute('grid', gridx, gridy)
kt.write_asc_grid(gridx, gridy, z, filename='./2014_all.asc')

