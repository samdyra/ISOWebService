from typing import Optional, Union
from pydantic import BaseModel, Field
from typing import Dict
from s100.utils.sample.selatSundaS104 import sample as sample_ncdfs104


# from s100.utils.base64_tiff import sample_base64_text


class S104Product(BaseModel):
    user_id: str = Field(..., example="60a7b1b9d6b9a4a7f0a3b3a0")
    metadata: Dict[str, Union[str, bool, int, float]] = Field(..., example={
        'file_name': 'TESTING S104',
        'geographicIdentifier': 'Selat Alas',
        'epoch': 'G1762',
        'horizontalDatumReference': 'EPSG',
        'horizontalDatumValue': 4326,
        'issueTime': '1237',
        'issueDate': '20230409',
        'metadata': '102ID00_ITBS100PROJECT.xml',
        'waterLevelTrendThreshold': 0.2,
        'verticalCS': 6499,
        'verticalDatumReference': 2,
        'verticalDatum': 10,
        'horizontalPositionUncertainty': 10,
        'verticalUncertainty': 10,
        'timeUncertainty': 10,
        'methodCurrentsProduct': "ADCIRC_Hydrodynamic_Model_Forecasts",
    })
    format_data: Dict[str, int] = Field(..., example={
        'interpolation_type_dt_type': 1,
        'sequencing_rule_type_dt_type': 1,
        'data_dynamicity_dt_type': 1,
    })
    dataset_ncdf: str = Field(..., example=sample_ncdfs104)
    water_level_band_name: str = Field(..., example="wl_pred")


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
