# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 15:28:23 2023

@author: Farras
"""

import pandas as pd
import numpy as np
import h5py

# DEFINE ARRAYS OF WATER LEVEL DATA

df1 = pd.read_excel('bnoa.xlsx')
df2 = pd.read_excel('penida.xlsx')
df3 = pd.read_excel('lembar.xlsx')
df4 = pd.read_excel('carik.xlsx')
df5 = pd.read_excel('tjluar.xlsx')
df6 = pd.read_excel('benete.xlsx')
pos = pd.read_excel('geometryValues.xlsx')

group01 = np.array(df1)
group02 = np.array(df2)
group03 = np.array(df3)
group04 = np.array(df4)
group05 = np.array(df5)
group06 = np.array(df6)
posi = np.array(pos)

# CREATE THE WATER LEVEL DATASET 
with h5py.File('104ID00ITBS100PRJCT_DCF8_v1.h5', 'w') as hdf: #name of HDF5 data file
    # MAIN METADATA
    hdf.attrs['eastBoundLongitude'] = '0'
    hdf.attrs['geographicIdentifier'] = 'Description'
    hdf.attrs['horizontalCRS'] = '4326'
    hdf.attrs['issueDate'] = '20230409'
    hdf.attrs['issueTime'] = '1237'
    hdf.attrs['northBoundLatitude'] = '-8'
    hdf.attrs['productSpecification'] = 'INT.IHO.S-104.0.8'
    hdf.attrs['southBoundLatitude'] = '-9'
    hdf.attrs['verticalCS'] = '6499'
    hdf.attrs['verticalCoordinateBase'] = '2'
    hdf.attrs['verticalDatum'] = '10'
    hdf.attrs['verticalDatumReference'] = '1'
    hdf.attrs['waterLevelTrendThreshold'] = '0.1' #Threshold for water level trend
    hdf.attrs['westBoundLongitude'] = '-2.5'
    
    ## GROUP F
    Group_F = hdf.create_group('Group_F')
    dt_dtype = h5py.special_dtype(vlen= str)
    dt = np.dtype([('code', dt_dtype), ('name', dt_dtype), ('uom.name', dt_dtype), ('fillValue', dt_dtype),
                      ('datatype', dt_dtype), ('lower', dt_dtype), ('upper', dt_dtype), ('closure', dt_dtype)])

    watlev = Group_F.create_dataset('Waterlevel', shape= (3,), dtype= dt)
    
    watlev[0] = ('waterLevelHeight', 'Water level height', 'meters', '-9999', 'H5T_FLOAT', '-99.99', '-99.99','closedInterval')
    watlev[1] = ('waterLevelTrend', 'Water level trend', '', '0', 'H5T_ENUM', '', '','')
    watlev[2] = ('waterLevelTime', 'Water level time', 'DateTime', '', 'H5T_C_S1', '19000101T000000Z', '21500101T000000Z','closedInterval')
        
    fcode = Group_F.create_dataset('featureCode', shape= (1,), dtype = dt_dtype)
    fcode[0] = ('Waterlevel')
    
    
    ## WATER LEVEL
    WaterLevel = hdf.create_group('WaterLevel') 
    #INPUT METADATA FOR WATERLEVEL
    WaterLevel.attrs['commonPointRule'] = '4'
    WaterLevel.attrs['dataCodingFormat'] = '1'
    WaterLevel.attrs['dimension'] = '2'
    WaterLevel.attrs['horizontalPositionUncertainty'] = '-1'
    WaterLevel.attrs['maxDatasetHeight'] = '1.980956008'
    WaterLevel.attrs['numInstances'] = '1'
    WaterLevel.attrs['pickPriorityType'] = '2'
    WaterLevel.attrs['timeUncertainty'] = '-1'
    WaterLevel.attrs['verticalUncertainty'] = '-1'
    
    # WATER LEVEL.01
    WaterLevel01 = hdf.create_group('WaterLevel/WaterLevel.01')
    # INPUT METADATA FOR WATER LEVEL.01
    WaterLevel01.attrs['dateTimeOfFirstRecord'] = '20230301T000000Z'
    WaterLevel01.attrs['dateTimeOfLastRecord'] = '20230303T23550Z'
    WaterLevel01.attrs['eastBoundLongitude'] = '117'
    WaterLevel01.attrs['northBoundLatitude'] = '-8'
    WaterLevel01.attrs['numGRP'] = '6'
    WaterLevel01.attrs['numberOfStations'] = '6'
    WaterLevel01.attrs['numberOfTimes'] = '864'
    WaterLevel01.attrs['southBoundLatitude'] = '-9'
    WaterLevel01.attrs['timeRecordInterval'] = '300'
    WaterLevel01.attrs['typeOfWaterLevelData'] = '2'
    WaterLevel01.attrs['westBoundLongitude'] = '115'
    
    # GROUP 001 (BENOA)
    Group_001 = hdf.create_group('WaterLevel/WaterLevel.01/Group_001')
    Group_001.create_dataset('values', data = group01)
    # INPUT METADATA FOR GROUP 001
    Group_001.attrs['endDateTime'] = '20230303T23550Z'
    Group_001.attrs['numberOfTimes'] = '864'
    Group_001.attrs['startDateTime'] = '20230301T000000Z'
    Group_001.attrs['stationIdentification'] = 'BNOA'
    Group_001.attrs['timeIntervalIndex'] = '1'
    Group_001.attrs['timeRecordInterval'] = '300'
    
    # GROUP 002 (NUSA PENIDA)
    Group_002 = hdf.create_group('WaterLevel/WaterLevel.01/Group_002')
    Group_002.create_dataset('values', data = group02)
    # INPUT METADATA FOR GROUP 002
    Group_002.attrs['endDateTime'] = '20230303T23550Z'
    Group_002.attrs['numberOfTimes'] = '864'
    Group_002.attrs['startDateTime'] = '20230301T000000Z'
    Group_002.attrs['stationIdentification'] = 'NUSA'
    Group_002.attrs['timeIntervalIndex'] = '1'
    Group_002.attrs['timeRecordInterval'] = '300'
    
    # GROUP 003 (LEMBAR)    
    Group_003 = hdf.create_group('WaterLevel/WaterLevel.01/Group_003')
    Group_003.create_dataset('values', data = group03)
    # INPUT METADATA FOR GROUP 003
    Group_003.attrs['endDateTime'] = '20230303T23550Z'
    Group_003.attrs['numberOfTimes'] = '864'
    Group_003.attrs['startDateTime'] = '20230301T000000Z'
    Group_003.attrs['stationIdentification'] = 'LMBR'
    Group_003.attrs['timeIntervalIndex'] = '1'
    Group_003.attrs['timeRecordInterval'] = '300'
    
    # GROUP 004 (CARIK)    
    Group_004 = hdf.create_group('WaterLevel/WaterLevel.01/Group_004')
    Group_004.create_dataset('values', data = group04)
    
    # INPUT METADATA FOR GROUP 004
    Group_004.attrs['endDateTime'] = '20230303T23550Z'
    Group_004.attrs['numberOfTimes'] = '864'
    Group_004.attrs['startDateTime'] = '20230301T000000Z'
    Group_004.attrs['stationIdentification'] = 'CRIK'
    Group_004.attrs['timeIntervalIndex'] = '1'
    Group_004.attrs['timeRecordInterval'] = '300'
    
    # GROUP 005 (TJ LUAR)
    Group_005 = hdf.create_group('WaterLevel/WaterLevel.01/Group_005')
    Group_005.create_dataset('values', data =group05)
    # INPUT METADATA FOR GROUP 005
    Group_005.attrs['endDateTime'] = '20230303T23550Z'
    Group_005.attrs['numberOfTimes'] = '864'
    Group_005.attrs['startDateTime'] = '20230301T000000Z'
    Group_005.attrs['stationIdentification'] = 'TJLR'
    Group_005.attrs['timeIntervalIndex'] = '1'
    Group_005.attrs['timeRecordInterval'] = '300'
    
    # GROUP 006 (BENETE)
    Group_006 = hdf.create_group('WaterLevel/WaterLevel.01/Group_006')
    Group_006.create_dataset('values', data = group06)
    # INPUT METADATA FOR GROUP 006
    Group_006.attrs['endDateTime'] = '20230303T23550Z'
    Group_006.attrs['numberOfTimes'] = '864'
    Group_006.attrs['startDateTime'] = '20230301T000000Z'
    Group_006.attrs['stationIdentification'] = 'BNTE'
    Group_006.attrs['timeIntervalIndex'] = '1'
    Group_006.attrs['timeRecordInterval'] = '300'
    
    # POSITIONING
    Positioning = hdf.create_group('WaterLevel/WaterLevel.01/Positioning')
    Positioning.create_dataset('geometryValues', data = pos)
    