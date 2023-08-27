import geojson
import tempfile


def convert_tiff_to_geojson(top_left, top_right, bottom_right, bottom_left):

    coordinates = [top_left, top_right, bottom_right, bottom_left, top_left]

    # Create a list to store the polygon features
    polygon_geojson = {
        "type": "Feature",
        "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates]
        },
        "properties": {}
    }

   # Convert the feature collection to a GeoJSON string
    geojson_string = geojson.dumps(polygon_geojson)

    with tempfile.NamedTemporaryFile(suffix=".geojson", delete=False, mode="w") as temp_file:
        temp_file_path = temp_file.name

        with open(temp_file_path, "w") as file:
            file.write(geojson_string)

    return temp_file_path
