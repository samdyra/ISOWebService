from typing import List
from fastapi import APIRouter, Body, Request, status, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from s100.s111.models import S111Product, S111ProductResponse
from config.firebase import storage
from h5py import enum_dtype
from s100.utils.base64_tiff import convert_base64_to_temp_tiff
from s100.constants.metadata_dict import COMMON_POINT_RULE, DATA_CODING_FORMAT, INTERPOLATION_TYPE, SEQUENCING_RULE_TYPE, VERTICAL_DATUM
import io
from osgeo import gdal, osr
import numpy
from s100.utils.tiff_hdf5_s102 import tiff_hdf5_s102 as convert_tiff_to_hdf5_s102
from s100.utils.tiff_geojson import convert_tiff_to_geojson
from s100.utils.global_helper import generate_random_filename
from uuid import uuid4


router = APIRouter()


@router.post("/", response_description="Create a new s111 hdf5 file", status_code=status.HTTP_201_CREATED, response_model=S111ProductResponse)
def create_s111(request: Request, input: S111Product = Body(...)):
    # get input from request body

    metadata = input.metadata
    format_data = input.format_data

    temp_tiff_1 = convert_base64_to_temp_tiff(input.dataset_1)
    temp_tiff_2 = convert_base64_to_temp_tiff(input.dataset_2)
    temp_tiff_3 = convert_base64_to_temp_tiff(input.dataset_3)

    dataset_1 = gdal.Open(temp_tiff_1)
    dataset_2 = gdal.Open(temp_tiff_2)
    dataset_3 = gdal.Open(temp_tiff_3)

    deg_band_1 = dataset_1.GetRasterBand(1)
    deg_grid_1 = deg_band_1.ReadAsArray()

    mag_band_1 = dataset_1.GetRasterBand(2)
    mag_grid_1 = mag_band_1.ReadAsArray()

    deg_band_2 = dataset_2.GetRasterBand(1)
    deg_grid_2 = deg_band_2.ReadAsArray()

    mag_band_2 = dataset_2.GetRasterBand(2)
    mag_grid_2 = mag_band_2.ReadAsArray()

    deg_band_3 = dataset_3.GetRasterBand(1)
    deg_grid_3 = deg_band_3.ReadAsArray()

    mag_band_3 = dataset_3.GetRasterBand(2)
    mag_grid_3 = mag_band_3.ReadAsArray()

    ulx, dxx, dxy, uly, dyx, dyy = dataset_1.GetGeoTransform()

    # generate id(s)
    user_id = input.user_id
    uid4 = uuid4()
    uuid_str = str(uid4)

    # insert new s111 to mongodb
    new_s111 = request.app.database["s111"].insert_one({
        "_id": uuid_str,
        "hdf5Uri": "",
        "geojsonUri": "",
        "file_name": "",
        "user_id": user_id,
    })

    created_s111 = request.app.database["s111"].find_one(
        {"_id": new_s111.inserted_id}
    )

    return created_s111
