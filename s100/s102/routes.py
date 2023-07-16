from fastapi import APIRouter, Body, Request, status
from fastapi.encoders import jsonable_encoder
from s100.s102.models import S102Product
from config.firebase import storage
from h5py import File
from s100.helpers.base64_tiff import sample_base64_text
import io

router = APIRouter()

@router.post("/", response_description="Create a new s102 hdf5 file", status_code=status.HTTP_201_CREATED, response_model=S102Product)
def create_s012(request: Request, input: S102Product = Body(...)):
    bio = io.BytesIO()
    with File(bio, 'w') as f:
        f['array'] = [1, 2, 3]
        f['scalar'] = 42
        f['group1/dset1'] = [1, 2, 3]

    hdf5File = bio.getvalue()
    
    path = storage.child("/s102/hdf5/file.hdf5")
    path.put(hdf5File)
    url = storage.child("s102/hdf5/file.hdf5").get_url(None)

    input = jsonable_encoder(input)
    input["hdf5Uri"] = url
    input["tiffFile"] = sample_base64_text

    new_s102 = request.app.database["s102"].insert_one(input)
    created_s102 = request.app.database["s102"].find_one(
        {"_id": new_s102.inserted_id}
    )

    return created_s102
