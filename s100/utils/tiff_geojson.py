import geojson
import json
from numpy import ndarray
import tempfile

def convert_tiff_to_geojson(depth_grid: ndarray, corner_x: str, corner_y: str, res_x: str, res_y: str):
    shape: tuple = depth_grid.shape

    # Create a list to store the polygon features
    polygons = []

    # Iterate over the depth grid
    for i in range(shape[0]):
        for j in range(shape[1]):
            # Get the depth value for the current grid cell
            depth_value = float(depth_grid[i, j])

            # Check if the depth value is 1000000
            if depth_value == 1000000:
                continue  # Skip creating the polygon

            # Calculate the corner coordinates for the current grid cell
            min_x = corner_x + j * res_x
            max_x = min_x + res_x
            max_y = corner_y + i * res_y
            min_y = max_y + res_y

            # Create a GeoJSON polygon feature for the current grid cell
            polygon = geojson.Polygon([[(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y), (min_x, min_y)]])
            
            # Set the depth value as a property of the polygon
            properties = {"depth": depth_value}
            feature = geojson.Feature(geometry=polygon, properties=properties)

            # Add the polygon feature to the list
            polygons.append(feature)

    # Create a GeoJSON feature collection from the list of polygons
    feature_collection = geojson.FeatureCollection(polygons)
    
   # Convert the feature collection to a GeoJSON string
    geojson_string = geojson.dumps(feature_collection)

    with tempfile.NamedTemporaryFile(suffix=".geojson", delete=False, mode="w") as temp_file:
        temp_file_path = temp_file.name

        with open(temp_file_path, "w") as file:
            file.write(geojson_string)

    return temp_file_path

