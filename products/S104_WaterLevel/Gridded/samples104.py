# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 11:28:15 2023

@author: Farras
"""

import numpy
import datetime
from s100py import s104
water_level_height = numpy.array([[ 0.34,  0.34,  0.34,  0.34,  0.34,  0.34,  0.34,  0.34,  0.34,  0.34,
                                    0.34,  0.34,  0.34,  0.34,  0.34,  0.34,  0.34,  0.34, 0.34,  0.34],
                                  [ 0.34,  0.34,  0.34,  0.34,  0.34,  0.34,  0.34, 0.34,  0.34,  0.34,
                                    0.34,  0.34,  0.34,  0.34,  0.34,  0.34, 0.34,  0.34,  0.34,  0.34],
                                  [ 0.34,  0.34,  0.34, 0.34,  0.35,  0.35,  0.35,  0.35,  0.35,  0.35,
                                    0.35,  0.35, 0.35,  0.35,  0.35,  0.35,  0.35,  0.35,  0.35,  0.35]])

water_level_trend = numpy.array([[ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

grid_properties = {
        'maxx': 134.175,
        'minx': 134.216,
        'miny': 6.982,
        'maxy': 7.254,
        'cellsize_x': 0.013595581,
        'cellsize_y': 0.013597488,
        'nx': 3,
        'ny': 20
}

# Example metadata
metadata = {
    'horizontalCRS': 4362, #EPSG code
    'metadata': f'MD_test_s104.XML',
    'geographicIdentifier': 'RegionName',
    'waterLevelHeightUncertainty': -1.0, # Default or Unknown values
    'verticalUncertainty': -1.0, # Default or Unknown values
    'horizontalPositionUncertainty': -1.0, # Default or Unknown values
    'timeUncertainty': -1.0, # Default or Unknown values
    'waterLevelTrendThreshold': 0.2,
    'verticalCS': 6499, # EPSG code
    'verticalCoordinateBase': 2, # 2:Vertical Datum
    'verticalDatumReference': 2, # 2:EPSG
    'verticalDatum': 1027, # EPSG code
    'commonPointRule': 4, # 4:all
    'interpolationType': 10, # 10:discrete
    'typeOfWaterLevelData': 5, # 5:Hydrodynamic model forecast (F)
    'methodWaterLevelProduct': 'ADCIRC_Hydrodynamic_Model_Forecasts',
    'datetimeOfFirstRecord': '2020-09-26T16:00:00'

}

datetime_value = datetime.datetime(2020, 9, 26, 15, 0, 0)

data_coding_format = 2

update_meta = {
        'dateTimeOfLastRecord': '2020-09-26T16:00:00',
        'numberOfGroups': 1,
        'numberOfTimes': 1,
        'timeRecordInterval': 0,
        'num_instances': 1
    }

data_file = s104.utils.create_s104("test_s104_sample3.h5")

s104.utils.add_metadata(metadata, data_file)
s104.utils.add_data_from_arrays(water_level_height, water_level_trend, data_file, grid_properties, datetime_value, data_coding_format)
s104.utils.update_metadata(data_file, grid_properties, update_meta)

s104.utils.write_data_file(data_file)