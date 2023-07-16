import uuid
from typing import Optional
from pydantic import BaseModel, Field
from typing import Dict

class S102Product(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    metadata: Dict[str, str] = Field(..., example={
        "title": "Sample Title",
        "desc": "Sample Description",
        "author": "Sample Author"
    })
    hdf5Uri: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "metadata": {
                    "title": "Sample Title",
                    "desc": "Sample Description",
                    "author": "Sample Author"
                },
                "hdf5Uri": "https://s3.amazonaws.com/...",
            }
        }

class S102ProductUpdate(BaseModel):
    metadata: Optional[Dict[str, str]]
    hdf5Uri: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "metadata": {
                    "title": "Sample Title",
                    "desc": "Sample Description",
                    "author": "Sample Author"
                },
                "hdf5Uri": "https://s3.amazonaws.com/...",
            }
        }
