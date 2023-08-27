from h5py import File, special_dtype
import numpy
from typing import Dict, Union
from osgeo import osr
from s100.utils.matlab_utc import convert_to_iso8601_with_offset as convert_to_utc
from h5py import enum_dtype
from s100.constants.metadata_dict import COMMON_POINT_RULE, INTERPOLATION_TYPE, SEQUENCING_RULE_TYPE, DATA_DYNAMICITY


def tiff_hdf5_s111(bio, bio_param: Dict[str, Union[str, int]]):
    dataset_deg = bio_param['dataset_deg']
    dataset_mag = bio_param['dataset_mag']
    time = bio_param['time']
    maxx: str = bio_param['maxx']
    minx: str = bio_param['minx']
    maxy: str = bio_param['maxy']
    miny: str = bio_param['miny']
    metadata: Dict[str, Union[str, bool, int]] = bio_param['metadata']
    format_data: Dict[str, int] = bio_param['format_data']

    data_dynamicity_dt = enum_dtype(DATA_DYNAMICITY, basetype='i4')
    common_point_rule_options = enum_dtype(COMMON_POINT_RULE, basetype='i4')
    interpolation_type_options = enum_dtype(INTERPOLATION_TYPE, basetype='i4')
    sequencing_rule_type_options = enum_dtype(
        SEQUENCING_RULE_TYPE, basetype='i4')

    common_point_rule_value: int = format_data['common_point_rule_dt_type']
    interpolation_type_value: int = format_data['interpolation_type_dt_type']
    sequencing_rule_type_value: int = format_data['sequencing_rule_type_dt_type']
    data_dynamicity_dt_type: int = format_data['data_dynamicity_dt_type']

    res_x: str = bio_param['res_x']
    res_y: str = bio_param['res_y']
    rows: int = bio_param['rows']
    cols: int = bio_param['cols']

    # Use band 1 from deg to get the shape etc.
    deg_band_1 = dataset_deg.GetRasterBand(1)
    deg_grid_1 = deg_band_1.ReadAsArray()

    # group all band in array
    num_deg_bands = dataset_deg.RasterCount
    deg_band_arrays = []

    for deg_band_number in range(1, num_deg_bands + 1):
        deg_band = dataset_deg.GetRasterBand(deg_band_number)
        deg_band_array = deg_band.ReadAsArray()
        deg_band_arrays.append(deg_band_array)

    num_mag_bands = dataset_mag.RasterCount
    mag_band_arrays = []

    for mag_band_number in range(1, num_mag_bands + 1):
        mag_band = dataset_mag.GetRasterBand(mag_band_number)
        mag_band_array = mag_band.ReadAsArray()
        mag_band_arrays.append(mag_band_array)

    max_values_array = []
    min_values_array = []

    for band_array in mag_band_arrays:
        max_value = numpy.nanmax(band_array)
        min_value = numpy.nanmin(band_array)
        max_values_array.append(max_value)
        min_values_array.append(min_value)

    max_grid_value = numpy.max(max_values_array)
    min_grid_value = numpy.min(min_values_array)

    max_time_value = numpy.nanmax(time)
    min_time_value = numpy.nanmin(time)
    time_delta = time[2] - time[1]
    time_delta_in_seconds = round(time_delta * 60 * 60)

    max_time_value_utc = convert_to_utc(max_time_value)
    min_time_value_utc = convert_to_utc(min_time_value)

    with File(bio, 'w') as f:
        # initiate dataset structure
        surf = f.create_group('/SurfaceCurrent')
        surf_01 = f.create_group('/SurfaceCurrent/SurfaceCurrent.01')

        mag_array = mag_band_arrays
        deg_array = deg_band_arrays

        for idx, (mag_grid, deg_grid, single_time) in enumerate(zip(mag_array, deg_array, time), start=1):
            group_path = f'/SurfaceCurrent/SurfaceCurrent.01/Group_{idx:03}'
            surf_group_object = surf_01.create_group(group_path)

            mag_grid_rounded = numpy.round(mag_grid, decimals=2)
            deg_grid_rounded = numpy.round(deg_grid, decimals=2)

            mag_grid_no_nan = numpy.nan_to_num(mag_grid_rounded, nan=-9999.00)
            deg_grid_no_nan = numpy.nan_to_num(deg_grid_rounded, nan=-9999.0)

            grid = surf_group_object.create_dataset(
                'values', dtype=[('surfaceCurrentSpeed', '<f4'), ('surfaceCurrentDirection', '<f4')], shape=deg_grid.shape,
                compression='gzip', compression_opts=9
            )
            grid['surfaceCurrentSpeed'] = mag_grid_no_nan
            grid['surfaceCurrentDirection'] = deg_grid_no_nan
            surf_group_object.attrs['timePoint'] = convert_to_utc(single_time)

        Group_F = f.create_group('Group_F')
        Group_F = f['/Group_F']
        source_epsg = int(metadata.get("horizontalDatumValue", 0))

        # initiate root attrs.
        f.attrs['productSpecification'] = "INT.IHO.S-111.1.0.1"
        f.attrs['issueDate'] = metadata.get("issueDate", "")
        f.attrs['horizontalCRS'] = source_epsg
        f.attrs['eastBoundLongitude'] = maxx
        f.attrs['westBoundLongitude'] = minx
        f.attrs['southBoundLatitude'] = miny
        f.attrs['northBoundLatitude'] = maxy
        f.attrs['geographicIdentifier'] = metadata.get(
            "geographicIdentifier", "")
        f.attrs['metadata'] = metadata.get("metadata", "")
        f.attrs['epoch'] = metadata.get("epoch", "")
        f.attrs['depthTypeIndex'] = 2
        f.attrs['surfaceCurrentDepth'] = metadata.get("surfaceCurrentDepth", 0)
        f.attrs['issueTime'] = metadata.get("issueTime", "")
        f.attrs['verticalCS'] = metadata.get("verticalCS", 0)
        f.attrs['verticalDatumReference'] = 1
        f.attrs['verticalDatum'] = 1

        # initiate surfaceCurrent0.1 attribute
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(source_epsg)
        if srs.IsProjected():
            # ["Northing", "Easting"]  # row major instead of
            axes = ["Easting", "Northing"]
        else:
            # ["Latitude", "Longitude"]  # row major instead of
            axes = ["Longitude", "Latitude"]

        surf.create_dataset('axisNames', data=axes)

        surf.attrs.create('dataCodingFormat', data=2)  # intent hardcode
        surf.attrs['dimension'] = 2  # intent hardcode
        surf.attrs.create(
            'commonPointRule', data=common_point_rule_value, dtype=common_point_rule_options)
        surf.attrs['horizontalPositionUncertainty'] = metadata.get(
            "horizontalPositionUncertainty", 0)
        surf.attrs['verticalUncertainty'] = metadata.get(
            "verticalUncertainty", -1.0)
        surf.attrs['timeUncertainty'] = metadata.get("timeUncertainty", -1.0)
        surf.attrs['numInstances'] = num_deg_bands
        surf.attrs['methodCurrentsProduct'] = metadata.get(
            "methodCurrentsProduct", "")
        surf.attrs['minDatasetCurrentSpeed'] = min_grid_value
        surf.attrs['maxDatasetCurrentSpeed'] = max_grid_value
        surf.attrs.create('sequencingRule.type', data=sequencing_rule_type_value,
                          dtype=sequencing_rule_type_options)
        surf.attrs['sequencingRule.scanDirection'] = ", ".join(axes)
        surf.attrs.create(
            'interpolationType', data=interpolation_type_value, dtype=interpolation_type_options)

        # initiate surfCurrent.nn attribute
        surf_01.attrs['eastBoundLongitude'] = maxx
        surf_01.attrs['westBoundLongitude'] = minx
        surf_01.attrs['southBoundLatitude'] = miny
        surf_01.attrs['northBoundLatitude'] = maxy
        surf_01.attrs['numberOfTimes'] = num_deg_bands
        surf_01.attrs['timeRecordInterval'] = time_delta_in_seconds
        surf_01.attrs['dateTimeOfFirstRecord'] = min_time_value_utc
        surf_01.attrs['dateTimeOfLastRecord'] = max_time_value_utc
        surf_01.attrs['numGRP'] = num_deg_bands
        surf_01.attrs.create(
            'dataDynamicity', data=data_dynamicity_dt_type, dtype=data_dynamicity_dt)
        surf_01.attrs['gridSpacingLatitudinal'] = abs(res_y)
        surf_01.attrs['gridSpacingLongitudinal'] = abs(res_x)
        surf_01.attrs['gridOriginLatitude'] = miny
        surf_01.attrs['gridOriginLongitude'] = minx

        surf_01.attrs['numPointsLatitudinal'] = rows
        surf_01.attrs['numPointsLongitudinal'] = cols
        surf_01.attrs['startSequence'] = "0,0"

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
