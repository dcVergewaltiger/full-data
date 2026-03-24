from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image_path):
    try:
        image = Image.open(image_path)
        info = image._getexif()
        if not info:
            return {"Fehler": "Keine Metadaten (EXIF) gefunden."}
        
        exif_data = {}
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                exif_data["GPS-Koordinaten"] = gps_data
            else:
                exif_data[decoded] = value
        return exif_data
    except Exception as e:
        return {"Fehler": f"Datei konnte nicht gelesen werden: {str(e)}"}
