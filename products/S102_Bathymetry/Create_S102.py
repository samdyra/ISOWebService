# -*- coding: utf-8 -*-
"""
Created on Wed May 31 22:23:50 2023

@author: alvin

1. Try catch block for null uncertainty band
2. Metadata could be more dynamic
"""

import numpy
import h5py
from osgeo import gdal, osr
import json

# enter bathy raster dataset
dataset = gdal.Open("Bathy_SelatAlas.tif")

# additional metadata
metadata = {
    'geographicIdentifier': 'Selat Alas',
    'epoch': 'G1762',
    'extent_type_code': True,
    'horizontalDatumReference': 'EPSG',
    'horizontalDatumValue': 4326,
    'issueTime': '1237',
    'issueDate': '20230409',
    'metadata': '102ID00_ITBS100PROJECT.xml'
    }

# fetching depth and uncert. values from dataset
depth_band = dataset.GetRasterBand(1)
depth_grid = depth_band.ReadAsArray()

uncert_band = dataset.GetRasterBand(2)
uncert_grid = uncert_band.ReadAsArray()

depth_grid = numpy.flipud(depth_grid)
uncert_grid = numpy.flipud(uncert_grid)

nodata_value = 1000000
depth_nodata_value = 1000000

# calculate grid origin and res.
# get six coefficients affine transformation
ulx, dxx, dxy, uly, dyx, dyy = dataset.GetGeoTransform()

if "origin" not in metadata:
    # shift the gdal geotransform corner point to reference the node (pixel is center) rather than cell (pixel is area)
    metadata["origin"] = [ulx + dxx/2, uly + dyy/2]
if "res" not in metadata:
    metadata["res"] = [dxx, dyy]

if "horizontalDatumReference" not in metadata or "horizontalDatumValue" not in metadata:
    metadata["horizontalDatumReference"] = "EPSG"
    epsg = osr.SpatialReference(
        dataset.GetProjection()).GetAttrValue("AUTHORITY", 1)
    try:
        metadata["horizontalDatumValue"] = int(epsg)
    except TypeError:
        if osr.SpatialReference(dataset.GetProjection()).GetAttrValue("GEOGCS") == 'WGS 84':
            metadata["horizontalDatumValue"] = 4326

res_x, res_y = metadata["res"]

rows, cols = depth_grid.shape
corner_x, corner_y = metadata['origin']

# S-102 is node based, so distance to far corner is res * (n -1)
opposite_corner_x = corner_x + res_x * (cols - 1)
opposite_corner_y = corner_y + res_y * (rows - 1)

minx = min((corner_x, opposite_corner_x))
maxx = max((corner_x, opposite_corner_x))
miny = min((corner_y, opposite_corner_y))
maxy = max((corner_y, opposite_corner_y))

VERTICAL_DATUM = {'meanLowWaterSprings' : 1,
                    'meanLowerLowWaterSprings' : 2,
                    'meanSeaLevel' : 3,
                    'lowestLowWater' : 4,
                    'meanLowWater' : 5,
                    'lowestLowWaterSprings' : 6,
                    'approximateMeanLowWaterSprings' : 7,
                    'indianSpringLowWater' : 8,
                    'lowWaterSprings' : 9,
                    'approximateLowestAdtonomicalTide' : 10,
                    'nearlyLowestLowWater' : 11,
                    'meanLowerLowWater' : 12,                
                    'lowWater' : 13,
                    'approximateMeanLowWater' : 14,
                    'approximateMeanLowerLowWater' : 15,
                    'meanHighWater' : 16,
                    'meanHighWaterSprings' : 17,
                    'highWater' : 18,
                    'approximateMeanSeaLevel' : 19,
                    'highWaterSprings' : 20,
                    'meanHigherHighWater' : 21,
                    'equinoctialSpringLowWater' : 22,
                    'lowestAdtonomicalTide' : 23,
                    'localDatum' : 24,
                    'internationalGreatLakesDatum1985' : 25,
                    'meanWaterLevel' : 26,
                    'lowerLowWaterLargeTide' : 27,
                    'higherHighWaterLargeTide' : 28,
                    'nearlyHighestHighWater' : 29,
                    'highestAdtonomicalTide' : 30
                    }
DATA_CODING_FORMAT = {'Time series at fixed stations': 1,
                        'Regularly-gridded arrays': 2,
                        'Ungeorectified gridded arrays': 3,
                        'Moving platform': 4,
                        'Irregular grid': 5,
                        'Variable cell size': 6,
                        'TIN': 7}
COMMON_POINT_RULE = {'average': 1,
                        'low': 2,
                        'high': 3,
                        'all': 4}

INTERPOLATION_TYPE = {'basicWeightedMean': 1,
                        'shoalestDepth': 2,
                        'tpuWeightedMean': 3,
                        'cube': 4,
                        'nearestNeighbour': 5,
                        'naturalNeighbour': 6,
                        'polynomialTendency': 7,
                        'spline': 8,
                        'kriging': 9}

SEQUENCING_RULE_TYPE = {'linear': 1,
                        'boudtophedonic': 2,
                        'CantorDiagonal': 3,
                        'spiral': 4,
                        'Morton': 5,
                        'Hilbert': 6}

GRIDDING_METHOD = {'nearestneighbor': 1,
                        'linear': 2,
                        'quadratic': 3,
                        'cubic': 4,
                        'bilinear': 5,
                        'biquadratic': 6,
                        'bicubic': 7,
                        'lostarea': 8,
                        'barycentric': 9,
                        'discrete': 10}

data_coding_format_dt = h5py.enum_dtype(DATA_CODING_FORMAT, basetype='i4')
vertical_datum_dt = h5py.enum_dtype(VERTICAL_DATUM, basetype='i4')
common_point_rule_dt = h5py.enum_dtype(COMMON_POINT_RULE, basetype='i4')
interpolation_type_dt = h5py.enum_dtype(INTERPOLATION_TYPE, basetype='i4')
# gm_dt = h5py.enum_dtype(GRIDDING_METHOD, basetype='i4')
sequencing_rule_type_dt = h5py.enum_dtype(SEQUENCING_RULE_TYPE, basetype='i4')

with h5py.File('102ID00ITBS100PRJCT.h5', mode= 'w') as f:
    # initiate dataset structureforigi
    bathy = f.create_group('/BathymetryCoverage')
    bathy_01 = f.create_group('/BathymetryCoverage/BathymetryCoverage.01')
    bathy_group_object = f.create_group('/BathymetryCoverage/BathymetryCoverage.01/Group_001')
    grid = bathy_group_object.create_dataset('values', dtype=[('depth', '<f4'), ('uncertainty', '<f4')], shape= depth_grid.shape)
    Group_F = f.create_group('Group_F')
    Group_F = f['/Group_F']

    # Initiate root attribute
    f.attrs.create('extentTypeCode', data = True, dtype='?')  
    f.attrs['productSpecification'] = "INT.IHO.S-102.2.1"
    f.attrs['eastBoundLongitude'] = maxx
    f.attrs['westBoundLongitude'] = minx
    f.attrs['southBoundLatitude'] = miny
    f.attrs['northBoundLatitude'] = maxy
    f.attrs.create('verticalDatum',data =  3, dtype = vertical_datum_dt)

    # these names are taken from the S100/S102 attribute names
    if "horizontalDatumReference" in metadata:
        f.attrs['horizontalDatumReference'] = metadata.get(
            "horizontalDatumReference", "EPSG")
    if "horizontalDatumValue" in metadata:
        source_epsg = int(metadata.get("horizontalDatumValue", 0))
        f.attrs['horizontalDatumValue'] = source_epsg
    if "epoch" in metadata:
        # e.g. "G1762"  this is the 2013-10-16 WGS84 used by CRS
        f.attrs['epoch'] = metadata.get("epoch", "")
    if "geographicIdentifier" in metadata:
        f.attrs['geographicIdentifier'] = metadata.get(
            "geographicIdentifier", "")
    if "issueDate" in metadata:
        f.attrs['issueDate'] = metadata.get("issueDate", "")
    if "metadata" in metadata:
        f.attrs['metadata'] = metadata.get("metadata", "")
    if "issueTime" in metadata:
        f.attrs['issueTime'] = metadata.get("issueTime", "")

    # initiate BathCov attribute
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(source_epsg)
    if srs.IsProjected():
        # ["Northing", "Easting"]  # row major instead of
        axes = ["Easting", "Northing"]
    else:
        # ["Latitude", "Longitude"]  # row major instead of
        axes = ["Longitude", "Latitude"]

    axis_names = bathy.create_dataset('axisNames', data=axes)
    
    bathy.attrs['verticalUncertainty'] = -1.0
    bathy.attrs.create('sequencingRule.type',data =  1, dtype = sequencing_rule_type_dt)
    bathy.attrs['numInstances'] = 1
    bathy.attrs['horizontalPositionUncertainty'] = -1.0
    bathy.attrs['dimension'] = 2
    bathy.attrs['sequencingRule.scanDirection'] = ", ".join(axes)
    bathy.attrs.create('interpolationType', data = 1, dtype= interpolation_type_dt)
    bathy.attrs.create('dataCodingFormat', data = 2, dtype = data_coding_format_dt)
    bathy.attrs.create('commonPointRule', data = 1, dtype= common_point_rule_dt)

    # initiate BathCov.nn attribute
    bathy_01.attrs['eastBoundLongitude'] = maxx
    bathy_01.attrs['westBoundLongitude'] = minx
    bathy_01.attrs['southBoundLatitude'] = miny
    bathy_01.attrs['northBoundLatitude'] = maxy

    bathy_01.attrs['gridSpacingLatitudinal'] = abs(res_y)
    bathy_01.attrs['gridSpacingLongitudinal'] = abs(res_x)

    bathy_01.attrs['gridOriginLatitude'] = miny
    bathy_01.attrs['gridOriginLongitude'] = minx

    #bathy_01.create_attribute('startSequence', data = '', dtype='f8')
    bathy_01.attrs['numPointsLatitudinal'] = rows
    bathy_01.attrs['numPointsLongitudinal'] = cols
    bathy_01.attrs['startSequence'] = "0,0"
    bathy_01.attrs['numGRP'] = 1

    # initiate Group_nnn attribute
    if uncert_grid is None:
        uncert_grid = numpy.full(
            depth_grid.shape, nodata_value, dtype=numpy.float32)
    try:
        uncertainty_max = uncert_grid[uncert_grid != nodata_value].max()
        uncertainty_min = uncert_grid[uncert_grid != nodata_value].min()
    
    except ValueError:
        uncertainty_max = uncertainty_min = nodata_value
    # ValueError caused by uncertainty array where (all values == nodata)
        
    bathy_01.attrs['numPointsLatitudinal'] = rows
    bathy_01.attrs['numPointsLongitudinal'] = cols
    bathy_01.attrs['startSequence'] = "0,0"

    depth_max = depth_grid[depth_grid != nodata_value].max()
    depth_min = depth_grid[depth_grid != nodata_value].min()
    bathy_group_object.attrs['maximumDepth'] = depth_max
    bathy_group_object.attrs['minimumDepth'] = depth_min
    bathy_group_object.attrs['maximumUncertainty'] = uncertainty_max
    bathy_group_object.attrs['minimumUncertainty'] = uncertainty_min

    grid[:, 'depth'] = depth_grid
    grid[:, 'uncertainty'] = uncert_grid

    # fill Group_F        
    dt_dtype = h5py.special_dtype(vlen= str)
    dt = numpy.dtype([('code', dt_dtype), ('name', dt_dtype), ('uom.name', dt_dtype), ('fillValue', dt_dtype),
                      ('datatype', dt_dtype), ('lower', dt_dtype), ('upper', dt_dtype), ('closure', dt_dtype)])

    batcov = Group_F.create_dataset('BathymetryCoverage', shape= (2,), dtype= dt)
    
    batcov[0] = ('depth', 'Depth', 'metres', '1000000', 'H5T_FLOAT', '-12000', '12000', 'closedInterval')
    batcov[1] = ('uncertainty', 'Uncertainty', 'metres', '1000000', 'H5T_FLOAT', '-12000', '12000', 'closedInterval')
    
    fcode = Group_F.create_dataset('featureCode', shape= (1,), dtype = dt_dtype)
    fcode[0] = ('BathymetryCoverage')
    


