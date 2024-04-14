import json
from shapely.geometry import shape, Point
import numpy as np
from datetime import datetime
import os

def list_tiff_files(orthophoto_path):
    # List all .tif files from the given directory
    tiff_files = [f for f in os.listdir(orthophoto_path) if f.endswith('.tif')]
    return tiff_files

def calculate_polygon_center(polygon):
    # Calculate the center point of the polygon
    return Point(np.mean([p[0] for p in polygon.exterior.coords]), 
                 np.mean([p[1] for p in polygon.exterior.coords]))

def create_metadata(project_path):
    # Create metadata based on the project path
    # File paths
    images_path = f"{project_path}/images.json"
    cameras_path = f"{project_path}/cameras.json"
    bounds_path = f"{project_path}/odm_georeferencing/odm_georeferenced_model.bounds.geojson"
    orthophoto_path = f"{project_path}/odm_orthophoto"
    stats_data = f"{project_path}/odm_report/stats.json"
    
    # Read file contents
    with open(images_path, 'r') as f:
        images_data = json.load(f)
    with open(cameras_path, 'r') as f:
        cameras_data = json.load(f)
    with open(bounds_path, 'r') as f:
        bounds_data = json.load(f)
    with open(stats_data, 'r') as f:
        stats_data = json.load(f)

    # Camera details
    unique_camera_details = set((img["camera_make"], img["camera_model"], img["sun_sensor"], img["band_name"], img["band_index"], img["radiometric_calibration"], img["iso_speed"]) for img in images_data if "filename" in img)
    cameradetails = [{"make": make, "model": model, "sun_sensor": sun_sensor, "band_name": band_name, "band_index": band_index, "radiometric_calibration": radiometric_calibration, "iso_speed": iso_speed} for make, model, sun_sensor, band_name, band_index, radiometric_calibration, iso_speed in unique_camera_details]
    
    # Calculate the center point of the imaging area
    polygon = shape(bounds_data['features'][0]['geometry'])
    center_point = calculate_polygon_center(polygon)
 

    # List all .tif files from odm_orthophoto directory
    tiff_files = list_tiff_files(orthophoto_path)
    orthoimages = [{"filename": filename, "path": os.path.join(orthophoto_path, filename)} for filename in tiff_files]
    
       
    # Collect metadata
    metadata = {
        "cameras": list(cameras_data.keys()),
        "camera_and_image_info": cameradetails,
        "number_of_images": len(images_data),
        "imaging_area_center": [center_point.x, center_point.y],
        "imaging_time_utc": datetime.utcfromtimestamp(images_data[0]["utc_time"] / 1000.0).strftime('%Y-%m-%d %H:%M:%S'),
        "processed_ortho_images" : orthoimages,
        "has_gps": stats_data["reconstruction_statistics"]["has_gps"],
        "has_gcp": stats_data["reconstruction_statistics"]["has_gcp"],
        "boundary": stats_data["point_cloud_statistics"]["stats"]["bbox"]["EPSG:4326"]["boundary"],
        "processing_start_date": stats_data["processing_statistics"]["start_date"],
        "areaSize": stats_data["processing_statistics"]["area"]        
        
    }
    
    return metadata


def save_metadata(metadata, save_path):
    # Save metadata to a JSON file
    with open(save_path, 'w') as file:
        json.dump(metadata, file, indent=4)
    return save_path
    
    


# Define project path
# This is a case Mustiala. ODM produced zip folder, extracted locally.
project_path = "Mustiala"

# Create metadata
metadata = create_metadata(project_path)

# Print metadata
print(json.dumps(metadata, indent=4))

# Save metadata to file
metatieto_path = "metatieto.json"
save_metadata(metadata, metatieto_path)

print("Metadata saved")




