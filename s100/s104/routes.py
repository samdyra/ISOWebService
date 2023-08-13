from fastapi import APIRouter, Body, Request, status
from s100.s104.models import S104Product, S104ProductResponse
from h5py import enum_dtype
from s100.utils.base64_tiff import convert_base64_to_temp_tiff
from s100.constants.metadata_dict import COMMON_POINT_RULE, DATA_CODING_FORMAT, INTERPOLATION_TYPE, SEQUENCING_RULE_TYPE, VERTICAL_DATUM
import io
from osgeo import gdal, osr
# from s100.utils.tiff_hdf5_s111 import tiff_hdf5_s111 as convert_tiff_to_hdf5_s111
from uuid import uuid4
from fastapi.encoders import jsonable_encoder
from s100.utils.global_helper import generate_random_filename
from config.firebase import storage


router = APIRouter()


@router.post("/", response_description="Create a new s104 hdf5 file", status_code=status.HTTP_201_CREATED, response_model=S104ProductResponse)
def create_s104(request: Request, input: S104Product = Body(...)):
    # get input from request body
    metadata = input.metadata

    # generate id(s)
    uid4 = uuid4()
    uuid_str = str(uid4)

    input = jsonable_encoder(input)
    input["hdf5Uri"] = ""

    # insert new s104 to mongodb
    new_s1104 = request.app.database["s104"].insert_one({
        "_id": uuid_str,
        "hdf5Uri": input["hdf5Uri"],
        "geojsonUri": "",
        "file_name": metadata["file_name"],
        "user_id": input["user_id"],
    })

    created_s104 = request.app.database["s104"].find_one(
        {"_id": new_s1104.inserted_id}
    )

    return created_s104
