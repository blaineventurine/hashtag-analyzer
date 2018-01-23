from geopy.geocoders import Nominatim
import json

geolocator = Nominatim()
file = 'location.json'


with open(file, 'r') as f:
  geo_data = {
      "type": "FeatureCollection",
      "features": []
  }
  for line in f:
    loc = geolocator.geocode(line)
    if loc is not None and loc.latitude is not None and loc.longitude is not None:
      print(loc.latitude, loc.longitude)
      geo_json_feature = {
          "type": "Feature",
          "geometry": {
              "type": "Point",
              "coordinates": [loc.longitude, loc.latitude]
          },
          "properties" : {
            "text": ""
        }
      }
      geo_data['features'].append(geo_json_feature)
with open('geo_data.json', 'w') as fout:
  fout.write(json.dumps(geo_data, indent=4))
