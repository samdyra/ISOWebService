from typing import Optional, Union
from pydantic import BaseModel, Field
from typing import Dict
from s100.utils.sample.dataset_1 import sample as dataset_1


class S104Product(BaseModel):
    user_id: str = Field(..., example="60a7b1b9d6b9a4a7f0a3b3a0")
    metadata: Dict[str, Union[str, bool, int]] = Field(..., example={
        'file_name': 'TESTING S104',
        'geographicIdentifier': 'Selat Alas',
        'epoch': 'G1762',
        'extent_type_code': True,
        'horizontalDatumReference': 'EPSG',
        'horizontalDatumValue': 4326,
        'issueTime': '1237',
        'issueDate': '20230409',
        'metadata': '102ID00_ITBS100PROJECT.xml'
    })
    format_data: Dict[str, int] = Field(..., example={
        'data_coding_format_dt_type': 2,
        'vertical_datum_dt_type': 3,
        'common_point_rule_dt_type': 1,
        'interpolation_type_dt_type': 1,
        'sequencing_rule_type_dt_type': 1,
    })
    netcdf: str = Field(..., example=dataset_1)
    netcdf_main_band: str = Field(..., example="wl_pred")

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
                "format_data": {
                    'data_coding_format_dt_type': 2,
                    'vertical_datum_dt_type': 3,
                    'common_point_rule_dt_type': 1,
                    'interpolation_type_dt_type': 1,
                    'sequencing_rule_type_dt_type': 1,
                },
                'netcdf': 'base64 text',
                'netcdf_main_band': 'wl_pred'

            }
        }


class S104ProductResponse(BaseModel):
    id: str = Field(alias="_id", example="60a7b1b9d6b9a4a7f0a3b3a0")
    hdf5Uri: str = Field(...,
                         example="https://s3.amazonaws.com/s100-hdf5/102ID00_ITBS100PROJECT.h5")
    geojsonUri: str = Field(
        ..., example="https://s3.amazonaws.com/s100-geojson/102ID00_ITBS100PROJECT.geojson")
    file_name: str = Field(..., example="102ID00_ITBS100PROJECT")
    user_id: str = Field(..., example="60a7b1b9d6b9a4a7f0a3b3a0")

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                'tiffFile': 'base64 text'
            }
        }
