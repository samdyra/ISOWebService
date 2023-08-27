from fastapi import APIRouter, Body, Request, status, HTTPException, Response
from typing import List
from s100.s111.models import S111Product, S111ProductResponse
import io
from osgeo import gdal
from s100.utils.tiff_hdf5_s111 import tiff_hdf5_s111 as convert_tiff_to_hdf5_s111
from s100.utils.convert_base64_netcdf_tiff import save_raster_to_temp_file as convert_netcdf_to_temp_tiff
from uuid import uuid4
from fastapi.encoders import jsonable_encoder
from s100.utils.global_helper import generate_random_filename
from config.firebase import storage
from s100.utils.tiff_geojson_111 import convert_tiff_to_geojson


router = APIRouter()


@router.post("/", response_description="Create a new s111 hdf5 file", status_code=status.HTTP_201_CREATED, response_model=S111ProductResponse)
def create_s111(request: Request, input: S111Product = Body(...)):
    # get input from request body
    metadata = input.metadata
    format_data = input.format_data

    current_speed_band_name = input.current_speed_band_name
    current_direction_band_name = input.current_direction_band_name

    temp_tiff_deg, time = convert_netcdf_to_temp_tiff(
        input.dataset_ncdf, current_direction_band_name, True)
    temp_tiff_mag = convert_netcdf_to_temp_tiff(
        input.dataset_ncdf, current_speed_band_name)

    dataset_deg = gdal.Open(temp_tiff_deg)
    dataset_mag = gdal.Open(temp_tiff_mag)

    deg_band_1 = dataset_deg.GetRasterBand(1)
    deg_grid_1 = deg_band_1.ReadAsArray()

    # calculate grid origin and res.
    # get six coefficients affine transformation
    ulx, dxx, dxy, uly, dyx, dyy = dataset_deg.GetGeoTransform()

    metadata["origin"] = [ulx + dxx/2, uly + dyy/2]
    metadata["res"] = [dxx, dyy]

    file_name = generate_random_filename(metadata['file_name'])
    res_x, res_y = metadata["res"]
    rows, cols = deg_grid_1.shape
    corner_x, corner_y = metadata['origin']

    # S-111 is node based, so distance to far corner is res * (n -1)
    opposite_corner_x = corner_x + res_x * (cols - 1)
    opposite_corner_y = corner_y + res_y * (rows - 1)

    minx = min((corner_x, opposite_corner_x))
    maxx = max((corner_x, opposite_corner_x))
    miny = min((corner_y, opposite_corner_y))
    maxy = max((corner_y, opposite_corner_y))

    upper_left_corner = (corner_x, corner_y)
    upper_right_corner = (opposite_corner_x, corner_y)
    bottom_left_corner = (corner_x, opposite_corner_y)
    bottom_right_corner = (opposite_corner_x, opposite_corner_y)

    # create hdf5 instance in memory
    bio = io.BytesIO()
    convert_tiff_to_hdf5_s111(bio, {
        'dataset_deg': dataset_deg,
        'dataset_mag': dataset_mag,
        'time': time,
        'maxx': maxx,
        'minx': minx,
        'maxy': maxy,
        'miny': miny,
        'metadata': metadata,
        'format_data': format_data,
        'res_x': res_x,
        'res_y': res_y,
        'rows': rows,
        'cols': cols
    })

    geojson_result = convert_tiff_to_geojson(
        upper_left_corner, upper_right_corner, bottom_right_corner, bottom_left_corner)

    hdf5File = bio.getvalue()

    # upload hdf5 file to firebase storage
    path = storage.child(f"/s111/hdf5/{file_name}.h5")
    path.put(hdf5File)
    url = storage.child(f"s111/hdf5/{file_name}.h5").get_url(None)

    # upload geojson file to firebase storage
    path_geojson = storage.child(f"/s111/geojson/{file_name}.geojson")
    path_geojson.put(geojson_result)
    url_geojson = storage.child(
        f"s111/geojson/{file_name}.geojson").get_url(None)

    input = jsonable_encoder(input)
    input["hdf5Uri"] = url
    input["geojsonUri"] = url_geojson

    # generate id(s)
    uid4 = uuid4()
    uuid_str = str(uid4)

    # insert new s111 to mongodb
    new_s111 = request.app.database["s111"].insert_one({
        "_id": uuid_str,
        "hdf5Uri": input["hdf5Uri"],
        "geojsonUri": input["geojsonUri"],
        "file_name": metadata["file_name"],
        "user_id": input["user_id"],
    })

    created_s111 = request.app.database["s111"].find_one(
        {"_id": new_s111.inserted_id}
    )

    return created_s111


@router.get("/{user_id}", response_description="Get S111 user data", response_model=List[S111ProductResponse])
def list_user_s111_data(user_id: str, request: Request):
    if (s111_data := list(request.app.database["s111"].find({"user_id": user_id}, limit=100))) is not None:
        return s111_data

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"user with ID {user_id} dont have any data")


@router.delete("/{_id}", response_description="Delete A S111 data")
def delete_s111_data(_id: str, request: Request, response: Response):
    # TODO: delete hdf5 and geojson file from firebase storage by Frontend

    delete_result = request.app.database["s111"].delete_one({"_id": _id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        response.message = "S111 data deleted"
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"S111 data with ID {_id} not found")
