from h5py import File
from json import dump

def convert_hdf5_to_json(hdf5):
    with File(hdf5, 'r') as f:
    # Extract relevant attributes and datasets
        long_location = f['/BathymetryCoverage/BathymetryCoverage.01']
        west_bound_longitude = long_location.attrs['westBoundLongitude']
        south_bound_latitude = long_location.attrs['southBoundLatitude']
        depth_grid = f['/BathymetryCoverage/BathymetryCoverage.01/Group_001/values']['depth']
        uncertainty_grid = f['/BathymetryCoverage/BathymetryCoverage.01/Group_001/values']['uncertainty']

    # Create a dictionary for the GeoJSON structure
    geojson_data = {
        "type": "FeatureCollection",
        "features": []
    }

    # Iterate over the depth and uncertainty grids and create features
    for row in range(depth_grid.shape[0]):
        for col in range(depth_grid.shape[1]):
            depth = float(depth_grid[row, col])
            uncertainty = float(uncertainty_grid[row, col])

            # Create a feature for each grid point
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [west_bound_longitude + col, south_bound_latitude + row]
                },
                "properties": {
                    "depth": depth,
                    "uncertainty": uncertainty
                }
            }

            # Add the feature to the feature collection
            geojson_data["features"].append(feature)

    # Save the GeoJSON data to a file
    with open("output.geojson", 'w') as f:
        dump(geojson_data, f)
