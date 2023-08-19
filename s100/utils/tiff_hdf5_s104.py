from h5py import File, special_dtype
import numpy
from h5py import enum_dtype
from typing import Dict, Union
from osgeo import osr
from s100.utils.matlab_utc import convert_to_iso8601_with_offset as convert_to_utc
from s100.constants.message import MESSAGE
from s100.constants.metadata_dict import COMMON_POINT_RULE, DATA_CODING_FORMAT, INTERPOLATION_TYPE, SEQUENCING_RULE_TYPE, VERTICAL_DATUM


def tiff_hdf5_s104(bio, bio_param: Dict[str, Union[str, int]]):
    dataset = bio_param['dataset']
    time = bio_param['time']
    maxx: str = bio_param['maxx']
    minx: str = bio_param['minx']
    maxy: str = bio_param['maxy']
    miny: str = bio_param['miny']
    metadata: Dict[str, Union[str, bool, int]] = bio_param['metadata']
    interpolation_type_dt = enum_dtype(INTERPOLATION_TYPE, basetype='i4')
    sequencing_rule_type_dt = enum_dtype(SEQUENCING_RULE_TYPE, basetype='i4')
    sequencing_rule_type_dt_type: int = bio_param['sequencing_rule_type_dt_type']
    interpolation_type_dt_type: int = bio_param['interpolation_type_dt_type']
    res_x: str = bio_param['res_x']
    res_y: str = bio_param['res_y']
    rows: int = bio_param['rows']
    cols: int = bio_param['cols']

    band_1 = dataset.GetRasterBand(1)
    grid_1 = band_1.ReadAsArray()

    # group all band in array
    num_bands = dataset.RasterCount
    band_arrays = []
    # timezz = convert_to_utc(time[13])

    for band_number in range(1, num_bands + 1):
        band = dataset.GetRasterBand(band_number)
        band_array = band.ReadAsArray()
        band_arrays.append(band_array)

    with File(bio, 'w') as f:
        # initiate root attrs.
        f.attrs['productSpecification'] = "INT.IHO.S-104.1.2" or MESSAGE['err_message']
        f.attrs['eastBoundLongitude'] = maxx or MESSAGE['err_message']
        f.attrs['westBoundLongitude'] = minx or MESSAGE['err_message']
        f.attrs['southBoundLatitude'] = miny or MESSAGE['err_message']
        f.attrs['northBoundLatitude'] = maxy or MESSAGE['err_message']

        f.attrs['issueDate'] = metadata.get(
            "issueDate", MESSAGE['err_message'])
        f.attrs['horizontalCRS'] = metadata.get(
            "horizontalDatumReference", "EPSG")
        f.attrs['geographicIdentifier'] = metadata.get(
            "geographicIdentifier", MESSAGE['err_message'])
        f.attrs['metadata'] = metadata.get("metadata", MESSAGE['err_message'])
        f.attrs['epoch'] = metadata.get("epoch", MESSAGE['err_message'])
        f.attrs['issueTime'] = metadata.get(
            "issueTime", MESSAGE['err_message'])
        f.attrs['waterLevelTrendThreshold'] = metadata.get(
            "waterLevelTrendThreshold", MESSAGE['err_message'])
        f.attrs['verticalCS'] = metadata.get(
            "verticalCS", MESSAGE['err_message'])
        f.attrs['verticalDatumReference'] = metadata.get(
            "verticalDatumReference", MESSAGE['err_message'])
        f.attrs['verticalDatum'] = metadata.get(
            "verticalDatum", MESSAGE['err_message'])

        # initiate WaterLevel attribute
        WaterLevel = f.create_group('/WaterLevel')
        WaterLevel.create_dataset('axisNames', data=axes)

        source_epsg = int(metadata.get("horizontalDatumValue", 4326))
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(source_epsg)
        if srs.IsProjected():

            axes = ["Easting", "Northing"]
        else:
            axes = ["Longitude", "Latitude"]

        WaterLevel.attrs.create('dataCodingFormat', data=2)
        WaterLevel.attrs['dimension'] = 2
        WaterLevel.attrs.create('commonPointRule', data=4)
        WaterLevel.attrs['horizontalPositionUncertainty'] = metadata.get(
            'horizontalPositionUncertainty', MESSAGE['err_message'])
        WaterLevel.attrs['verticalUncertainty'] = metadata.get(
            'verticalUncertainty', MESSAGE['err_message'])
        WaterLevel.attrs['timeUncertainty'] = metadata.get(
            'timeUncertainty', MESSAGE['err_message'])
        WaterLevel.attrs['numInstances'] = 1
        WaterLevel.attrs['methodCurrentsProduct'] = metadata.get(
            'methodCurrentsProduct', MESSAGE['err_message'])

        # TODO: these attributes is on the array data, calculate it first
        WaterLevel.attrs['minDatasetHeight'] = MESSAGE['err_message']
        WaterLevel.attrs['maxDatasetHeight'] = MESSAGE['err_message']

        WaterLevel.attrs.create(
            'sequencingRule.type', data=sequencing_rule_type_dt_type, dtype=sequencing_rule_type_dt)
        WaterLevel.attrs['sequencingRule.scanDirection'] = ", ".join(axes)

        WaterLevel.attrs.create(
            'interpolationType', data=interpolation_type_dt_type, dtype=interpolation_type_dt)

        # initiate WaterLevel.nn attribute
        WaterLevel_01 = f.create_group('/WaterLevel/WaterLevel.01')

        WaterLevel_01.attrs['eastBoundLongitude'] = maxx
        WaterLevel_01.attrs['westBoundLongitude'] = minx
        WaterLevel_01.attrs['southBoundLatitude'] = miny
        WaterLevel_01.attrs['northBoundLatitude'] = maxy
        WaterLevel_01.attrs['numberOfTimes'] = 3
        WaterLevel_01.attrs['timeRecordInterval'] = 3600
        WaterLevel_01.attrs['dateTimeOfFirstRecord'] = '2022-09-29 16:00:00Z'
        WaterLevel_01.attrs['dateTimeOfLastRecord'] = '2022-09-30 00:00:00Z'

        WaterLevel_01.attrs['gridSpacingLatitudinal'] = abs(res_y)
        WaterLevel_01.attrs['gridSpacingLongitudinal'] = abs(res_x)
        WaterLevel_01.attrs['gridOriginLatitude'] = miny
        WaterLevel_01.attrs['gridOriginLongitude'] = minx

        WaterLevel_01.attrs['numGRP'] = 3
        WaterLevel_01.attrs['numPointsLatitudinal'] = rows
        WaterLevel_01.attrs['numPointsLongitudinal'] = cols
        WaterLevel_01.attrs['startSequence'] = "0,0"

        # initiate Group.nnn attribute
        grid_array = band_arrays
        # T0D0: There is indication that the resulting group values are inversed. check it again with all s111 data.
        for idx, (value_grid, single_time) in enumerate(zip(grid_array, time), start=1):
            group_path = f'/WaterLevel/WaterLevel.01/Group_{idx:03}'
            surf_group_object = WaterLevel_01.create_group(group_path)
            grid = surf_group_object.create_dataset(
                'values', dtype=[('surfaceCurrentSpeed', '<f4')], shape=value_grid.shape
            )
            grid['surfaceCurrentSpeed'] = value_grid
            surf_group_object.attrs['timePoint'] = convert_to_utc(single_time)

        # fill Group_F
        Group_F = f.create_group('Group_F')
        Group_F = f['/Group_F']

        dt_dtype = special_dtype(vlen=str)
        dt = numpy.dtype([('code', dt_dtype), ('name', dt_dtype), ('uom.name', dt_dtype), ('fillValue', dt_dtype),
                          ('datatype', dt_dtype), ('lower', dt_dtype), ('upper', dt_dtype), ('closure', dt_dtype)])

        scurrent = Group_F.create_dataset(
            'WaterLevel', shape=(2,), dtype=dt)

        scurrent[0] = ('surfaceCurrentSpeed', 'Surface current speed',
                       'knots', '-9999.0', 'H5T_FLOAT', '0.0', '', 'geSemiInterval')
        scurrent[1] = ('surfaceCurrentDirection', 'Surface current direction',
                       'arc-degrees', '-9999.0', 'H5T_FLOAT', '-0.0', '360', 'geLtInterval')

        fcode = Group_F.create_dataset(
            'featureCode', shape=(1,), dtype=dt_dtype)
        fcode[0] = ('WaterLevel')
