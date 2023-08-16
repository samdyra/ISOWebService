from fastapi import APIRouter, Body, Request, status
from s100.s111.models import S111Product, S111ProductResponse
from h5py import enum_dtype
from s100.utils.base64_tiff import convert_base64_to_temp_tiff
from s100.constants.metadata_dict import COMMON_POINT_RULE, DATA_CODING_FORMAT, INTERPOLATION_TYPE, SEQUENCING_RULE_TYPE, VERTICAL_DATUM
import io
from osgeo import gdal, osr
from s100.utils.tiff_hdf5_s111 import tiff_hdf5_s111 as convert_tiff_to_hdf5_s111
from s100.utils.convert_base64_netcdf_tiff import save_raster_to_temp_file as convert_netcdf_to_temp_tiff
from uuid import uuid4
from fastapi.encoders import jsonable_encoder
from s100.utils.global_helper import generate_random_filename
from config.firebase import storage


router = APIRouter()


@router.post("/", response_description="Create a new s111 hdf5 file", status_code=status.HTTP_201_CREATED, response_model=S111ProductResponse)
def create_s111(request: Request, input: S111Product = Body(...)):
    # get input from request body
    metadata = input.metadata
    format_data = input.format_data

    # Surface Current Direction = deg
    # Surface Current Speed = mag

    temp_tiff_deg = convert_netcdf_to_temp_tiff(
        input.dataset_ncdf, 'Surface Current Direction')
    temp_tiff_mag = convert_netcdf_to_temp_tiff(
        input.dataset_ncdf, 'Surface Current Speed')

    dataset_deg = gdal.Open(temp_tiff_deg)
    dataset_mag = gdal.Open(temp_tiff_mag)

    deg_band_1 = dataset_deg.GetRasterBand(1)
    deg_grid_1 = deg_band_1.ReadAsArray()

    # print(dataset_deg.RasterCount)

    # calculate grid origin and res.
    # get six coefficients affine transformation
    # ulx, dxx, dxy, uly, dyx, dyy = dataset_deg.GetGeoTransform()

    # if "origin" not in metadata:
    #     # shift the gdal geotransform corner point to reference the node (pixel is center) rather than cell (pixel is area)
    #     metadata["origin"] = [ulx + dxx/2, uly + dyy/2]

    # if "res" not in metadata:
    #     metadata["res"] = [dxx, dyy]

    # if "horizontalDatumReference" not in metadata or "horizontalDatumValue" not in metadata:
    #     metadata["horizontalDatumReference"] = "EPSG"
    #     epsg = osr.SpatialReference(
    #         dataset_deg.GetProjection()).GetAttrValue("AUTHORITY", 1)
    #     try:
    #         metadata["horizontalDatumValue"] = int(epsg)
    #     except TypeError:
    #         if osr.SpatialReference(dataset_deg.GetProjection()).GetAttrValue("GEOGCS") == 'WGS 84':
    #             metadata["horizontalDatumValue"] = 4326

    # file_name = generate_random_filename(metadata['file_name'])
    # res_x, res_y = metadata["res"]
    # rows, cols = deg_grid_1.shape
    # corner_x, corner_y = metadata['origin']

    # # S-111 is node based, so distance to far corner is res * (n -1)
    # opposite_corner_x = corner_x + res_x * (cols - 1)
    # opposite_corner_y = corner_y + res_y * (rows - 1)

    # minx = min((corner_x, opposite_corner_x))
    # maxx = max((corner_x, opposite_corner_x))
    # miny = min((corner_y, opposite_corner_y))
    # maxy = max((corner_y, opposite_corner_y))

    # data_coding_format_dt = enum_dtype(DATA_CODING_FORMAT, basetype='i4')
    # vertical_datum_dt = enum_dtype(VERTICAL_DATUM, basetype='i4')
    # common_point_rule_dt = enum_dtype(COMMON_POINT_RULE, basetype='i4')
    # interpolation_type_dt = enum_dtype(INTERPOLATION_TYPE, basetype='i4')
    # sequencing_rule_type_dt = enum_dtype(SEQUENCING_RULE_TYPE, basetype='i4')

    # # create hdf5 instance in memory
    # bio = io.BytesIO()
    # convert_tiff_to_hdf5_s111(bio, {
    #     'dataset_deg': dataset_deg,
    #     'dataset_mag': dataset_mag,
    #     'maxx': maxx,
    #     'minx': minx,
    #     'maxy': maxy,
    #     'miny': miny,
    #     'metadata': metadata,
    #     'res_x': res_x,
    #     'res_y': res_y,
    #     'rows': rows,
    #     'cols': cols
    # })

    # hdf5File = bio.getvalue()

    # # upload hdf5 file to firebase storage
    # path = storage.child(f"/s111/hdf5/{file_name}.h5")
    # path.put(hdf5File)
    # url = storage.child(f"s111/hdf5/{file_name}.h5").get_url(None)

    # input = jsonable_encoder(input)
    # input["hdf5Uri"] = url

    # # generate id(s)
    # uid4 = uuid4()
    # uuid_str = str(uid4)

    # # insert new s111 to mongodb
    # new_s111 = request.app.database["s111"].insert_one({
    #     "_id": uuid_str,
    #     "hdf5Uri": input["hdf5Uri"],
    #     "geojsonUri": "",
    #     "file_name": metadata["file_name"],
    #     "user_id": input["user_id"],
    # })

    # created_s111 = request.app.database["s111"].find_one(
    #     {"_id": new_s111.inserted_id}
    # )

    # return created_s111
