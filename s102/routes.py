from fastapi import APIRouter, Body, Request, status
from fastapi.encoders import jsonable_encoder
from s102.models import S102Product

router = APIRouter()

@router.post("/", response_description="Create a new s102 hdf5 file", status_code=status.HTTP_201_CREATED, response_model=S102Product)
def create_s012(request: Request, input: S102Product = Body(...)):
    input = jsonable_encoder(input)
    new_s102 = request.app.database["s102"].insert_one(input)
    created_s102 = request.app.database["s102"].find_one(
        {"_id": new_s102.inserted_id}
    )

    return created_s102
