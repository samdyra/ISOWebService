import xarray as xr
import rioxarray as rio
import tempfile
import base64


def convert_base64_to_temp_ncdf(base64_string):
    tiff_bytes = base64.b64decode(base64_string)

    with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as temp_file:
        temp_file_path = temp_file.name

        with open(temp_file_path, "wb") as file:
            file.write(tiff_bytes)

    return temp_file_path


def save_raster_to_temp_file(nc_file_base64, path, is_return_time=False):
    ncdf_file_path = convert_base64_to_temp_ncdf(nc_file_base64)

    # Open the NetCDF
    ncfile = xr.open_dataset(ncdf_file_path)

    # Extract the variable
    pr = ncfile[path]

    # (Optional) convert longitude from (0-360) to (-180 to 180) (if required)
    pr.coords['longitude'] = (pr.coords['longitude'] + 180) % 360 - 180
    pr = pr.sortby(pr.longitude)

    # Define lat/long
    pr = pr.rio.set_spatial_dims('longitude', 'latitude')

    # Check for the CRS
    pr.rio.crs

    # (Optional) If your CRS is not discovered, you should be able to add it like so:
    pr.rio.set_crs("epsg:4326")

    # Uncomment this if you want to test the output file (copy paste sample file from ncdfs111.py)
    # pr.rio.to_raster(r"GeoTIFF.tif")

    # Create a temporary file to save the raster
    with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as temp_file:
        temp_filepath = temp_file.name
        pr.rio.to_raster(temp_filepath)

    if is_return_time:
        return temp_filepath, ncfile.time.values

    return temp_filepath


# Provide the NetCDF file path as an argument
# save_raster_to_temp_file(sample, "Surface Current Speed")
