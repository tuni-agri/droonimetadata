import json
from shapely.geometry import shape, Point
import numpy as np
from datetime import datetime
import os

def list_tiff_files(orthophoto_path):
    # Listaa kaikki .tif tiedostot annetusta kansiosta
    tiff_files = [f for f in os.listdir(orthophoto_path) if f.endswith('.tif')]
    return tiff_files

def calculate_polygon_center(polygon):
    #Laskee polygonin keskipisteen
    return Point(np.mean([p[0] for p in polygon.exterior.coords]), 
                 np.mean([p[1] for p in polygon.exterior.coords]))

def create_metadata(project_path):
    # Luo metatiedot projektipolun perusteella
    # Tiedostopolut
    images_path = f"{project_path}/images.json"
    cameras_path = f"{project_path}/cameras.json"
    bounds_path = f"{project_path}/odm_georeferencing/odm_georeferenced_model.bounds.geojson"
    orthophoto_path = f"{project_path}/odm_orthophoto"
    stats_data = f"{project_path}/odm_report/stats.json"
    
    # Lue tiedostojen sisällöt
    with open(images_path, 'r') as f:
        images_data = json.load(f)
    with open(cameras_path, 'r') as f:
        cameras_data = json.load(f)
    with open(bounds_path, 'r') as f:
        bounds_data = json.load(f)
    with open(stats_data, 'r') as f:
        stats_data = json.load(f)

    # Kameratiedot
    unique_camera_details = set((img["camera_make"], img["camera_model"], img["sun_sensor"], img["band_name"], img["band_index"], img["radiometric_calibration"], img["iso_speed"]) for img in images_data if "filename" in img)
    cameradetails = [{"make": make, "model": model, "sun_sensor": sun_sensor, "band_name": band_name, "band_index": band_index, "radiometric_calibration": radiometric_calibration, "iso_speed": iso_speed} for make, model, sun_sensor, band_name, band_index, radiometric_calibration, iso_speed in unique_camera_details]
    
    # Laske kuvausalueen keskipiste
    polygon = shape(bounds_data['features'][0]['geometry'])
    center_point = calculate_polygon_center(polygon)
 

    # Lista kaikista .tif tiedostoista odm_orthophoto kansiosta
    tiff_files = list_tiff_files(orthophoto_path)
    orthoimages = [{"filename": filename, "path": os.path.join(orthophoto_path, filename)} for filename in tiff_files]
    
       
    # Kerää metatiedot
    metatiedot = {
        "kamerat": list(cameras_data.keys()),
        "kameran ja kuvan tietoja":cameradetails,
        "kuvien_maara": len(images_data),
        "kuvausalueen_keskipiste": [center_point.x, center_point.y],
        "kuvausaika": datetime.utcfromtimestamp(images_data[0]["utc_time"] / 1000.0).strftime('%Y-%m-%d %H:%M:%S'),
        "kasitellyt_ortho_kuvat" : orthoimages,
        "has_gps": stats_data["reconstruction_statistics"]["has_gps"],
        "has_gcp": stats_data["reconstruction_statistics"]["has_gcp"],
        "boundary": stats_data["point_cloud_statistics"]["stats"]["bbox"]["EPSG:4326"]["boundary"],
        "processing_start_date": stats_data["processing_statistics"]["start_date"],
        "areaSize": stats_data["processing_statistics"]["area"]        
        
    }
    
    return metatiedot


def save_metatieto(metatiedot, save_path):
    #Tallentaa metatiedot JSON-tiedostoon
    with open(save_path, 'w') as file:
        json.dump(metatiedot, file, indent=4)
    return save_path
    
    
# Määritä projektin polku 
# Tämä on case tapaus. ODM:n tuottama zip-kansio, joka purettu paikallisesti.
project_path = "Mustiala"

# Luo metatiedot
metatiedot = create_metadata(project_path)

# Tulosta metatiedot
print(json.dumps(metatiedot, indent=4))

# Tallenna metatiedot tiedostoon
metatieto_path = "metatieto.json"
save_metatieto(metatiedot, metatieto_path)

print("Metatiedot tallennettu")




