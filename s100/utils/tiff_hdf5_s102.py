from h5py import File, special_dtype
import numpy
from typing import Dict, Union
from osgeo import osr

def tiff_hdf5_s102(bio, bio_param: Dict[str, Union[str, int]]):
  nodata_value = 1000000
  depth_grid: numpy.ndarray = bio_param['depth_grid']
  shape: tuple = depth_grid.shape
  maxx: str = bio_param['maxx']
  minx: str = bio_param['minx']
  maxy: str = bio_param['maxy']
  miny: str = bio_param['miny']
  metadata: Dict[str, Union[str, bool, int]] = bio_param['metadata']
  vertical_datum_dt_type: int = bio_param['vertical_datum_dt_type']
  vertical_datum_dt: numpy.dtype = bio_param['vertical_datum_dt']
  sequencing_rule_type_dt_type: int = bio_param['sequencing_rule_type_dt_type']
  sequencing_rule_type_dt: numpy.dtype = bio_param['sequencing_rule_type_dt']
  interpolation_type_dt_type: int = bio_param['interpolation_type_dt_type']
  interpolation_type_dt: numpy.dtype = bio_param['interpolation_type_dt']
  data_coding_format_dt_type: int = bio_param['data_coding_format_dt_type']
  data_coding_format_dt: numpy.dtype = bio_param['data_coding_format_dt']
  common_point_rule_dt_type: int = bio_param['common_point_rule_dt_type']
  common_point_rule_dt: numpy.dtype = bio_param['common_point_rule_dt']
  res_x: str = bio_param['res_x']
  res_y: str = bio_param['res_y']
  uncert_grid: numpy.ndarray = bio_param['uncert_grid']
  rows: int = bio_param['rows']
  cols: int = bio_param['cols']
  


  with File(bio, 'w') as f:
        # initiate dataset structure
        bathy = f.create_group('/BathymetryCoverage')
        bathy_01 = f.create_group('/BathymetryCoverage/BathymetryCoverage.01')
        bathy_group_object = f.create_group('/BathymetryCoverage/BathymetryCoverage.01/Group_001')
        grid = bathy_group_object.create_dataset('values', dtype=[('depth', '<f4'), ('uncertainty', '<f4')], shape=shape)
        Group_F = f.create_group('Group_F')
        Group_F = f['/Group_F']

        # Initiate root attribute
        f.attrs['productSpecification'] = "INT.IHO.S-102.2.1"
        f.attrs['eastBoundLongitude'] = maxx
        f.attrs['westBoundLongitude'] = minx
        f.attrs['southBoundLatitude'] = miny
        f.attrs['northBoundLatitude'] = maxy
        f.attrs.create('verticalDatum',data =  vertical_datum_dt_type, dtype = vertical_datum_dt)

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

        bathy.create_dataset('axisNames', data=axes)
        
        bathy.attrs['verticalUncertainty'] = -1.0
        bathy.attrs.create('sequencingRule.type',data =  sequencing_rule_type_dt_type, dtype = sequencing_rule_type_dt)
        bathy.attrs['numInstances'] = 1
        bathy.attrs['horizontalPositionUncertainty'] = -1.0
        bathy.attrs['dimension'] = 2
        bathy.attrs['sequencingRule.scanDirection'] = ", ".join(axes)
        bathy.attrs.create('interpolationType', data = interpolation_type_dt_type, dtype= interpolation_type_dt)
        bathy.attrs.create('dataCodingFormat', data = data_coding_format_dt_type, dtype = data_coding_format_dt)
        bathy.attrs.create('commonPointRule', data = common_point_rule_dt_type, dtype= common_point_rule_dt)

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
        dt_dtype = special_dtype(vlen= str)
        dt = numpy.dtype([('code', dt_dtype), ('name', dt_dtype), ('uom.name', dt_dtype), ('fillValue', dt_dtype),
                        ('datatype', dt_dtype), ('lower', dt_dtype), ('upper', dt_dtype), ('closure', dt_dtype)])

        batcov = Group_F.create_dataset('BathymetryCoverage', shape= (2,), dtype= dt)
        
        batcov[0] = ('depth', 'Depth', 'metres', '1000000', 'H5T_FLOAT', '-12000', '12000', 'closedInterval')
        batcov[1] = ('uncertainty', 'Uncertainty', 'metres', '1000000', 'H5T_FLOAT', '-12000', '12000', 'closedInterval')
        
        fcode = Group_F.create_dataset('featureCode', shape= (1,), dtype = dt_dtype)
        fcode[0] = ('BathymetryCoverage')