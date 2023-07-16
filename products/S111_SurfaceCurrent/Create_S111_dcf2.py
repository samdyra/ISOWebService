
import numpy
import h5py
from osgeo import gdal, osr

#input surface current raster dataset (dcf2)
dataset_173 = gdal.Open("wgs84_173_final.tif")
dataset_174 = gdal.Open("wgs84_174_final.tif")
dataset_175 = gdal.Open("wgs84_175_final.tif")

# fetching depth and uncert. values from dataset
deg_band_173 = dataset_173.GetRasterBand(1)
deg_grid_173 = deg_band_173.ReadAsArray()

mag_band_173 = dataset_173.GetRasterBand(2) 
mag_grid_173 = mag_band_173.ReadAsArray() #todolist : konversi satuan dari mps > knots

deg_band_174 = dataset_174.GetRasterBand(1)
deg_grid_174 = deg_band_174.ReadAsArray()

mag_band_174 = dataset_174.GetRasterBand(2) 
mag_grid_174 = mag_band_174.ReadAsArray() 

deg_band_175 = dataset_175.GetRasterBand(1)
deg_grid_175 = deg_band_175.ReadAsArray()

mag_band_175 = dataset_175.GetRasterBand(2) 
mag_grid_175 = mag_band_175.ReadAsArray() 

#input metadata
metadata = {
    'geographicIdentifier': 'Selat Alas',
    'epoch': 'G1762',
    'extent_type_code': True,
    'horizontalDatumReference': 'EPSG',
    'horizontalDatumValue': 4326,
    'issueTime': '1237',
    'issueDate': '20230409',
    'metadata': 'Not included with this dataset'}

# calculate grid origin and res.
# get six coefficients affine transformation
ulx, dxx, dxy, uly, dyx, dyy = dataset_173.GetGeoTransform()

if "origin" not in metadata:
    # shift the gdal geotransform corner point to reference the node (pixel is center) rather than cell (pixel is area)
    metadata["origin"] = [ulx + dxx/2, uly + dyy/2]
if "res" not in metadata:
    metadata["res"] = [dxx, dyy]

if "horizontalDatumReference" not in metadata or "horizontalDatumValue" not in metadata:
    metadata["horizontalDatumReference"] = "EPSG"
    epsg = osr.SpatialReference(
        dataset_173.GetProjection()).GetAttrValue("AUTHORITY", 1)
    try:
        metadata["horizontalDatumValue"] = int(epsg)
    except TypeError:
        if osr.SpatialReference(dataset_173.GetProjection()).GetAttrValue("GEOGCS") == 'WGS 84':
            metadata["horizontalDatumValue"] = 4326

res_x, res_y = metadata["res"]

rows, cols = deg_grid_173.shape
corner_x, corner_y = metadata['origin']

# S-102 is node based, so distance to far corner is res * (n -1)
opposite_corner_x = corner_x + res_x * (cols - 1)
opposite_corner_y = corner_y + res_y * (rows - 1)

minx = min((corner_x, opposite_corner_x))
maxx = max((corner_x, opposite_corner_x))
miny = min((corner_y, opposite_corner_y))
maxy = max((corner_y, opposite_corner_y))

with h5py.File('111ID00ITBS100PRJCT_DCF8.h5', 'w') as f:
    # initiate dataset structure
    surf = f.create_group('/SurfaceCurrent')
    surf_01 = f.create_group('/SurfaceCurrent/SurfaceCurrent.01')
    
    surf_group_object_01 = surf_01.create_group('/SurfaceCurrent/SurfaceCurrent.01/Group_001')
    grid_01 = surf_group_object_01.create_dataset('values', dtype=[('surfaceCurrentSpeed', '<f4'), ('surfaceCurrentDirection', '<f4')], shape=deg_grid_173.shape)
    
    surf_group_object_02 = surf_01.create_group('/SurfaceCurrent/SurfaceCurrent.01/Group_002')
    grid_02 = surf_group_object_02.create_dataset('values', dtype=[('surfaceCurrentSpeed', '<f4'), ('surfaceCurrentDirection', '<f4')], shape=deg_grid_173.shape)
    
    surf_group_object_03 = surf_01.create_group('/SurfaceCurrent/SurfaceCurrent.01/Group_003')
    grid_03 = surf_group_object_03.create_dataset('values', dtype=[('surfaceCurrentSpeed', '<f4'), ('surfaceCurrentDirection', '<f4')], shape=deg_grid_173.shape)
    
    Group_F = f.create_group('Group_F')
    Group_F = f['/Group_F']

    #initiate root attrs.
    f.attrs['productSpecification'] = "INT.IHO.S-111.1.0.1"
    f.attrs['eastBoundLongitude'] = maxx
    f.attrs['westBoundLongitude'] = minx
    f.attrs['southBoundLatitude'] = miny
    f.attrs['northBoundLatitude'] = maxy
    f.attrs['depthTypeIndex'] = 2
    f.attrs['surfaceCurrentDepth'] = 0.0

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
    
    # initiate surfCurrent attribute
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(source_epsg)
    if srs.IsProjected():
        # ["Northing", "Easting"]  # row major instead of
        axes = ["Easting", "Northing"]
    else:
        # ["Latitude", "Longitude"]  # row major instead of
        axes = ["Longitude", "Latitude"]

    axis_names = surf.create_dataset('axisNames', data=axes)
    
    surf.attrs['verticalUncertainty'] = -1.0
    surf.attrs['timeUncertainty'] = -1.0
    surf.attrs.create('sequencingRule.type',data =  1)
    surf.attrs['numInstances'] = 1
    surf.attrs['horizontalPositionUncertainty'] = -1.0
    surf.attrs['dimension'] = 2
    surf.attrs['sequencingRule.scanDirection'] = ", ".join(axes)
    surf.attrs.create('interpolationType', data = 1)
    surf.attrs.create('dataCodingFormat', data = 2)
    surf.attrs.create('commonPointRule', data = 2)

    # initiate BathCov.nn attribute
    surf_01.attrs['eastBoundLongitude'] = maxx
    surf_01.attrs['westBoundLongitude'] = minx
    surf_01.attrs['southBoundLatitude'] = miny
    surf_01.attrs['northBoundLatitude'] = maxy
    
    surf_01.attrs['numberOfTimes'] = 3
    surf_01.attrs['timeRecordInterval'] = 3600
    surf_01.attrs['dateTimeOfFirstRecord'] = '2022-09-29 16:00:00Z'
    surf_01.attrs['dateTimeOfLastRecord'] = '2022-09-30 00:00:00Z'

    surf_01.attrs['gridSpacingLatitudinal'] = abs(res_y)
    surf_01.attrs['gridSpacingLongitudinal'] = abs(res_x)
    surf_01.attrs['gridOriginLatitude'] = miny
    surf_01.attrs['gridOriginLongitude'] = minx

    surf_01.attrs['numGRP'] = 3
    surf_01.attrs['numPointsLatitudinal'] = rows
    surf_01.attrs['numPointsLongitudinal'] = cols
    surf_01.attrs['startSequence'] = "0,0"

    # initiate Group.nnn attribute
    surf_group_object_01.attrs['timePoint'] = '2022-09-29 16:00:00Z'
    surf_group_object_02.attrs['timePoint'] = '2022-09-29 20:00:00Z'
    surf_group_object_03.attrs['timePoint'] = '2022-09-29 16:00:00Z'

    grid_01[:, 'surfaceCurrentDirection'] = deg_grid_173
    grid_01[:, 'surfaceCurrentSpeed'] = mag_grid_173
    
    grid_02[:, 'surfaceCurrentDirection'] = deg_grid_174
    grid_03[:, 'surfaceCurrentSpeed'] = mag_grid_174

    grid_01[:, 'surfaceCurrentDirection'] = deg_grid_175
    grid_01[:, 'surfaceCurrentSpeed'] = mag_grid_175

    # fill Group_F
    dt_dtype = h5py.special_dtype(vlen= str)
    dt = numpy.dtype([('code', dt_dtype), ('name', dt_dtype), ('uom.name', dt_dtype), ('fillValue', dt_dtype),
                      ('datatype', dt_dtype), ('lower', dt_dtype), ('upper', dt_dtype), ('closure', dt_dtype)])

    scurrent = Group_F.create_dataset('SurfaceCurrent', shape= (2,), dtype= dt)
        
    scurrent[0] = ('surfaceCurrentSpeed', 'Surface current speed', 'knots', '-9999.0', 'H5T_FLOAT', '0.0', '', 'geSemiInterval')
    scurrent[1] = ('surfaceCurrentDirection', 'Surface current direction', 'arc-degrees', '-9999.0', 'H5T_FLOAT', '-0.0', '360', 'geLtInterval')
    
    fcode = Group_F.create_dataset('featureCode', shape= (1,), dtype = dt_dtype)
    fcode[0] = ('SurfaceCurrent')

