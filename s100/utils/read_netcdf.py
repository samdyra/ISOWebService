import xarray as xr
import rioxarray as rio

# Open the NetCDF
# Download the sample from https://www.unidata.ucar.edu/software/netcdf/examples/sresa1b_ncar_ccsm3-example.nc
ncfile = xr.open_dataset('SelatLombok.nc')

# Extract the variable
pr = ncfile['wl_pred']

# (Optional) convert longitude from (0-360) to (-180 to 180) (if required)
pr.coords['longitude'] = (pr.coords['longitude'] + 180) % 360 - 180
pr = pr.sortby(pr.longitude)

# Define lat/long
pr = pr.rio.set_spatial_dims('longitude', 'latitude')

# Check for the CRS
pr.rio.crs

# (Optional) If your CRS is not discovered, you should be able to add it like so:
pr.rio.set_crs("epsg:4326")


# Saving the file
pr.rio.to_raster(r"GeoTIFF.tif")
