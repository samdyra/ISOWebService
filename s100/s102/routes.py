from fastapi import APIRouter, Body, Request, status
from fastapi.encoders import jsonable_encoder
from s100.s102.models import S102ProductResponse, S102Product
from config.firebase import storage
from h5py import File, enum_dtype, special_dtype
from s100.utils.base64_tiff import convert_base64_to_temp_tiff 
from s100.constants.metadata_dict import COMMON_POINT_RULE, DATA_CODING_FORMAT, INTERPOLATION_TYPE, SEQUENCING_RULE_TYPE, VERTICAL_DATUM
import io
from osgeo import gdal, osr
import numpy
from s100.utils.hfd5_geojson import convert_hdf5_to_json
from s100.utils.tiff_hdf5_s102 import tiff_hdf5_s102 as convert_tiff_to_hdf5_s102

router = APIRouter()

@router.post("/", response_description="Create a new s102 hdf5 file", status_code=status.HTTP_201_CREATED, response_model=S102ProductResponse)
def create_s012(request: Request, input: S102Product = Body(...)):
    # get input from request body
    tiffFile = input.tiffFile
    metadata = input.metadata
    format_data = input.format_data

    data_coding_format_dt_type =  format_data['data_coding_format_dt_type']
    vertical_datum_dt_type = format_data['vertical_datum_dt_type']
    common_point_rule_dt_type = format_data['common_point_rule_dt_type']
    interpolation_type_dt_type = format_data['interpolation_type_dt_type']
    sequencing_rule_type_dt_type = format_data['sequencing_rule_type_dt_type']

    # convert base64 tiff to temp tiff
    temp_tiff = convert_base64_to_temp_tiff(tiffFile)
    dataset = gdal.Open(temp_tiff)

    # fetching depth and uncert. values from dataset
    depth_band = dataset.GetRasterBand(1)
    depth_grid = depth_band.ReadAsArray()

    uncert_band = dataset.GetRasterBand(2)
    uncert_grid = uncert_band.ReadAsArray()

    depth_grid = numpy.flipud(depth_grid)
    uncert_grid = numpy.flipud(uncert_grid)

    nodata_value = 1000000

    # calculate grid origin and res.
    # get six coefficients affine transformation
    ulx, dxx, _dxy, uly, _dyx, dyy = dataset.GetGeoTransform()

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

    data_coding_format_dt = enum_dtype(DATA_CODING_FORMAT, basetype='i4')
    vertical_datum_dt = enum_dtype(VERTICAL_DATUM, basetype='i4')
    common_point_rule_dt = enum_dtype(COMMON_POINT_RULE, basetype='i4')
    interpolation_type_dt = enum_dtype(INTERPOLATION_TYPE, basetype='i4')
    sequencing_rule_type_dt = enum_dtype(SEQUENCING_RULE_TYPE, basetype='i4')

    # create hdf5 instance in memory
    bio = io.BytesIO()
    convert_tiff_to_hdf5_s102(bio, {
        'depth_grid': depth_grid,
        'maxx': maxx,
        'minx': minx,
        'maxy': maxy,
        'miny': miny,
        'metadata': metadata,
        'vertical_datum_dt_type': vertical_datum_dt_type,
        'vertical_datum_dt': vertical_datum_dt,
        'sequencing_rule_type_dt_type': sequencing_rule_type_dt_type,
        'sequencing_rule_type_dt': sequencing_rule_type_dt,
        'interpolation_type_dt_type': interpolation_type_dt_type,
        'interpolation_type_dt': interpolation_type_dt,
        'data_coding_format_dt_type': data_coding_format_dt_type,
        'data_coding_format_dt': data_coding_format_dt,
        'common_point_rule_dt_type': common_point_rule_dt_type,
        'common_point_rule_dt': common_point_rule_dt,
        'res_x': res_x,
        'res_y': res_y,
        'uncert_grid': uncert_grid,
        'rows': rows,
        'cols': cols
    })
    
    #convert hdf5 to geojson    
    convert_hdf5_to_json(bio)

    hdf5File = bio.getvalue()

    # upload hdf5 file to firebase storage
    path = storage.child("/s102/hdf5/file.h5")
    path.put(hdf5File)
    url = storage.child("s102/hdf5/file.h5").get_url(None)

    # use url from firebase storage as hdf5Uri in response
    input = jsonable_encoder(input)
    input["hdf5Uri"] = url

    # insert new s102 to mongodb
    new_s102 = request.app.database["s102"].insert_one({
        "_id": input["_id"],
        "hdf5Uri": input["hdf5Uri"]
    })

    created_s102 = request.app.database["s102"].find_one(
        {"_id": new_s102.inserted_id}
    )

    return created_s102
