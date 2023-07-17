import uuid
from typing import Optional
from pydantic import BaseModel, Field
from typing import Dict
from s100.helpers.base64_tiff import sample_base64_text

class S102Product(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    metadata: Dict[str, str] = Field(..., example={
        'geographicIdentifier': 'Selat Alas',
        'epoch': 'G1762',
        'extent_type_code': True,
        'horizontalDatumReference': 'EPSG',
        'horizontalDatumValue': 4326,
        'issueTime': '1237',
        'issueDate': '20230409',
        'metadata': '102ID00_ITBS100PROJECT.xml'
    })
    format_data: Dict[str, str] = Field(..., example={
        'data_coding_format_dt': 2,
        'vertical_datum_dt': 3,
        'common_point_rule_dt': 1,
        'interpolation_type_dt': 1,
        'sequencing_rule_type_dt': 1,
    })
    tiffFile: str = Field(..., example=sample_base64_text)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "metadata": {
                    'geographicIdentifier': 'Selat Alas',
                    'epoch': 'G1762',
                    'extent_type_code': True,
                    'horizontalDatumReference': 'EPSG',
                    'horizontalDatumValue': 4326,
                    'issueTime': '1237',
                    'issueDate': '20230409',
                    'metadata': '102ID00_ITBS100PROJECT.xml'
                },
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
            }
        }
