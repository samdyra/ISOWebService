from fastapi import APIRouter, Body, Request, status
from s100.s104.models import S104Product, S104ProductResponse
import io
from osgeo import gdal, osr
from s100.utils.tiff_hdf5_s104 import tiff_hdf5_s104 as convert_tiff_to_hdf5_s104
from s100.utils.convert_base64_netcdf_tiff import save_raster_to_temp_file as convert_netcdf_to_temp_tiff
from uuid import uuid4
from fastapi.encoders import jsonable_encoder
from s100.utils.global_helper import generate_random_filename
from config.firebase import storage


router = APIRouter()


@router.post("/", response_description="Create a new s104 hdf5 file", status_code=status.HTTP_201_CREATED, response_model=S104ProductResponse)
def create_s104(request: Request, input: S104Product = Body(...)):
    # get input from request body
    metadata = input.metadata
    format_data = input.format_data

    temp_tiff, time = convert_netcdf_to_temp_tiff(
        input.dataset_ncdf, 'wl_pred', True)

    dataset = gdal.Open(temp_tiff)

    band_1 = dataset.GetRasterBand(1)
    grid_1 = band_1.ReadAsArray()

    # calculate grid origin and res.
    # get six coefficients affine transformation
    ulx, dxx, dxy, uly, dyx, dyy = dataset.GetGeoTransform()
    metadata["origin"] = [ulx + dxx/2, uly + dyy/2]
    metadata["res"] = [dxx, dyy]

    file_name = generate_random_filename(metadata['file_name'])
    res_x, res_y = metadata["res"]
    rows, cols = grid_1.shape
    corner_x, corner_y = metadata['origin']

    # S-111 is node based, so distance to far corner is res * (n -1)
    opposite_corner_x = corner_x + res_x * (cols - 1)
    opposite_corner_y = corner_y + res_y * (rows - 1)

    minx = min((corner_x, opposite_corner_x))
    maxx = max((corner_x, opposite_corner_x))
    miny = min((corner_y, opposite_corner_y))
    maxy = max((corner_y, opposite_corner_y))

    # create hdf5 instance in memory
    bio = io.BytesIO()
    convert_tiff_to_hdf5_s104(bio, {
        'dataset': dataset,
        'time': time,
        'maxx': maxx,
        'minx': minx,
        'maxy': maxy,
        'miny': miny,
        'metadata': metadata,

        'res_x': res_x,
        'res_y': res_y,
        'rows': rows,
        'cols': cols
    })

    hdf5File = bio.getvalue()

    # upload hdf5 file to firebase storage
    path = storage.child(f"/s104/hdf5/{file_name}.h5")
    path.put(hdf5File)
    url = storage.child(f"s104/hdf5/{file_name}.h5").get_url(None)

    input = jsonable_encoder(input)
    input["hdf5Uri"] = url

    # generate id(s)
    uid4 = uuid4()
    uuid_str = str(uid4)

    # insert new s104 to mongodb
    new_s104 = request.app.database["s104"].insert_one({
        "_id": uuid_str,
        "hdf5Uri": input["hdf5Uri"],
        "geojsonUri": "",
        "file_name": metadata["file_name"],
        "user_id": input["user_id"],
    })

    created_s104 = request.app.database["s104"].find_one(
        {"_id": new_s104.inserted_id}
    )

    return created_s104
