from fastapi import APIRouter, Body, Request, status
from fastapi.encoders import jsonable_encoder
from s100.s102.models import S102Product
from config.firebase import storage
from h5py import File
from s100.utils.base64_tiff import convert_base64_to_temp_tiff 
import io
from osgeo import gdal, osr
import numpy



router = APIRouter()

@router.post("/", response_description="Create a new s102 hdf5 file", status_code=status.HTTP_201_CREATED, response_model=S102Product)
def create_s012(request: Request, input: S102Product = Body(...)):
    # tiffFile = input.tiffFile
    # metadata = input.metadata

    # temp_tiff = convert_base64_to_temp_tiff(tiffFile)

    # dataset = gdal.Open(temp_tiff)

    # # fetching depth and uncert. values from dataset
    # depth_band = dataset.GetRasterBand(1)
    # depth_grid = depth_band.ReadAsArray()

    # uncert_band = dataset.GetRasterBand(2)
    # uncert_grid = uncert_band.ReadAsArray()

    # depth_grid = numpy.flipud(depth_grid)
    # uncert_grid = numpy.flipud(uncert_grid)

    # nodata_value = 1000000
    # depth_nodata_value = 1000000

    # # calculate grid origin and res.
    # # get six coefficients affine transformation
    # ulx, dxx, _dxy, uly, _dyx, dyy = dataset.GetGeoTransform()

    # if "origin" not in metadata:
    #     # shift the gdal geotransform corner point to reference the node (pixel is center) rather than cell (pixel is area)
    #     metadata["origin"] = [ulx + dxx/2, uly + dyy/2]
    # if "res" not in metadata:
    #     metadata["res"] = [dxx, dyy]

    # if "horizontalDatumReference" not in metadata or "horizontalDatumValue" not in metadata:
    #     metadata["horizontalDatumReference"] = "EPSG"
    #     epsg = osr.SpatialReference(
    #         dataset.GetProjection()).GetAttrValue("AUTHORITY", 1)
    #     try:
    #         metadata["horizontalDatumValue"] = int(epsg)
    #     except TypeError:
    #         if osr.SpatialReference(dataset.GetProjection()).GetAttrValue("GEOGCS") == 'WGS 84':
    #             metadata["horizontalDatumValue"] = 4326

    # res_x, res_y = metadata["res"]

    # rows, cols = depth_grid.shape
    # corner_x, corner_y = metadata['origin']

    # # S-102 is node based, so distance to far corner is res * (n -1)
    # opposite_corner_x = corner_x + res_x * (cols - 1)
    # opposite_corner_y = corner_y + res_y * (rows - 1)

    # minx = min((corner_x, opposite_corner_x))
    # maxx = max((corner_x, opposite_corner_x))
    # miny = min((corner_y, opposite_corner_y))
    # maxy = max((corner_y, opposite_corner_y))

    # create hdf5 instance in memory
    bio = io.BytesIO()
    with File(bio, 'w') as f:
        f['array'] = [1, 2, 3]
        f['scalar'] = 42
        f['group1/dset1'] = [1, 2, 3]

    hdf5File = bio.getvalue()
    
    # upload hdf5 file to firebase storage
    path = storage.child("/s102/hdf5/file.hdf5")
    path.put(hdf5File)
    url = storage.child("s102/hdf5/file.hdf5").get_url(None)

    # use url from firebase storage as hdf5Uri in response
    input = jsonable_encoder(input)
    input["hdf5Uri"] = url

    # insert new s102 to mongodb
    new_s102 = request.app.database["s102"].insert_one(input)
    created_s102 = request.app.database["s102"].find_one(
        {"_id": new_s102.inserted_id}
    )

    return created_s102
