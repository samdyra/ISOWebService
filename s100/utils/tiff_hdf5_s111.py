from h5py import File, special_dtype
import numpy
from typing import Dict, Union
from osgeo import osr


def tiff_hdf5_s111(bio, bio_param: Dict[str, Union[str, int]]):
    deg_grid_1 = bio_param['deg_grid_1']
    deg_grid_2 = bio_param['deg_grid_2']
    deg_grid_3 = bio_param['deg_grid_3']
    mag_grid_1 = bio_param['mag_grid_1']
    mag_grid_2 = bio_param['mag_grid_2']
    mag_grid_3 = bio_param['mag_grid_3']
    maxx: str = bio_param['maxx']
    minx: str = bio_param['minx']
    maxy: str = bio_param['maxy']
    miny: str = bio_param['miny']
    metadata: Dict[str, Union[str, bool, int]] = bio_param['metadata']
    # vertical_datum_dt_type: int = bio_param['vertical_datum_dt_type']
    # vertical_datum_dt: numpy.dtype = bio_param['vertical_datum_dt']
    # sequencing_rule_type_dt_type: int = bio_param['sequencing_rule_type_dt_type']
    # sequencing_rule_type_dt: numpy.dtype = bio_param['sequencing_rule_type_dt']
    # interpolation_type_dt_type: int = bio_param['interpolation_type_dt_type']
    # interpolation_type_dt: numpy.dtype = bio_param['interpolation_type_dt']
    # data_coding_format_dt_type: int = bio_param['data_coding_format_dt_type']
    # data_coding_format_dt: numpy.dtype = bio_param['data_coding_format_dt']
    # common_point_rule_dt_type: int = bio_param['common_point_rule_dt_type']
    # common_point_rule_dt: numpy.dtype = bio_param['common_point_rule_dt']
    res_x: str = bio_param['res_x']
    res_y: str = bio_param['res_y']
    rows: int = bio_param['rows']
    cols: int = bio_param['cols']

    with File(bio, 'w') as f:
        # initiate dataset structure
        surf = f.create_group('/SurfaceCurrent')
        surf_01 = f.create_group('/SurfaceCurrent/SurfaceCurrent.01')

        surf_group_object_01 = surf_01.create_group(
            '/SurfaceCurrent/SurfaceCurrent.01/Group_001')
        grid_01 = surf_group_object_01.create_dataset('values', dtype=[(
            'surfaceCurrentSpeed', '<f4'), ('surfaceCurrentDirection', '<f4')], shape=deg_grid_1.shape)

        surf_group_object_02 = surf_01.create_group(
            '/SurfaceCurrent/SurfaceCurrent.01/Group_002')
        grid_02 = surf_group_object_02.create_dataset('values', dtype=[(
            'surfaceCurrentSpeed', '<f4'), ('surfaceCurrentDirection', '<f4')], shape=deg_grid_1.shape)

        surf_group_object_03 = surf_01.create_group(
            '/SurfaceCurrent/SurfaceCurrent.01/Group_003')
        grid_03 = surf_group_object_03.create_dataset('values', dtype=[(
            'surfaceCurrentSpeed', '<f4'), ('surfaceCurrentDirection', '<f4')], shape=deg_grid_1.shape)

        Group_F = f.create_group('Group_F')
        Group_F = f['/Group_F']

        # initiate root attrs.
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
        surf.attrs.create('sequencingRule.type', data=1)
        surf.attrs['numInstances'] = 1
        surf.attrs['horizontalPositionUncertainty'] = -1.0
        surf.attrs['dimension'] = 2
        surf.attrs['sequencingRule.scanDirection'] = ", ".join(axes)
        surf.attrs.create('interpolationType', data=1)
        surf.attrs.create('dataCodingFormat', data=2)
        surf.attrs.create('commonPointRule', data=2)

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

        grid_01[:, 'surfaceCurrentDirection'] = deg_grid_1
        grid_01[:, 'surfaceCurrentSpeed'] = mag_grid_1

        grid_02[:, 'surfaceCurrentDirection'] = deg_grid_2
        grid_03[:, 'surfaceCurrentSpeed'] = mag_grid_2

        grid_01[:, 'surfaceCurrentDirection'] = deg_grid_3
        grid_01[:, 'surfaceCurrentSpeed'] = mag_grid_3

        # fill Group_F
        dt_dtype = special_dtype(vlen=str)
        dt = numpy.dtype([('code', dt_dtype), ('name', dt_dtype), ('uom.name', dt_dtype), ('fillValue', dt_dtype),
                          ('datatype', dt_dtype), ('lower', dt_dtype), ('upper', dt_dtype), ('closure', dt_dtype)])

        scurrent = Group_F.create_dataset(
            'SurfaceCurrent', shape=(2,), dtype=dt)

        scurrent[0] = ('surfaceCurrentSpeed', 'Surface current speed',
                       'knots', '-9999.0', 'H5T_FLOAT', '0.0', '', 'geSemiInterval')
        scurrent[1] = ('surfaceCurrentDirection', 'Surface current direction',
                       'arc-degrees', '-9999.0', 'H5T_FLOAT', '-0.0', '360', 'geLtInterval')

        fcode = Group_F.create_dataset(
            'featureCode', shape=(1,), dtype=dt_dtype)
        fcode[0] = ('SurfaceCurrent')
