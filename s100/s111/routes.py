from fastapi import APIRouter, Body, Request, status, HTTPException, Response

router = APIRouter()



@router.get("/", response_description="Get S111")
def list_user_s102_data( request: Request):
    print("s111")
    return "s111"
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"error")

@router.post("/", response_description="Get S111")
def list_user_s102_data( request: Request):
    print("s111 post")
    return "s111 post"

@router.patch("/", response_description="Get S111")
def list_user_s102_data( request: Request):
    print("s111 patch")
    return "s111 patch"

@router.delete("/{id}", response_description="Get S111")
def list_user_s102_data( id: str, request: Request):
    print("s111 delete ")
    return Response(content=f"s111 delete {id}")