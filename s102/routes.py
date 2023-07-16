from fastapi import APIRouter, Body, Request, status
from fastapi.encoders import jsonable_encoder
from s102.models import S102Product
from config.firebase import storage

router = APIRouter()

@router.post("/", response_description="Create a new s102 hdf5 file", status_code=status.HTTP_201_CREATED, response_model=S102Product)
def create_s012(request: Request, input: S102Product = Body(...)):
    path = storage.child("/s102/hdf5/test.json")
    path.put("./s102/test.json")
    url = storage.child("s102/hdf5/test.json").get_url(None)

    input = jsonable_encoder(input)
    input["hdf5Uri"] = url

    new_s102 = request.app.database["s102"].insert_one(input)
    created_s102 = request.app.database["s102"].find_one(
        {"_id": new_s102.inserted_id}
    )

    return created_s102
