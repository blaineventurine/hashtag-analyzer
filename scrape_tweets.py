import fileinput
import json
import re
import threading
import time
import csv
from geopy.geocoders import Nominatim
import tweepy
from api_keys import *

auth = tweepy.OAuthHandler(key, secret_key)
auth.set_access_token(token, secret_token)
api = tweepy.API(auth)

keyword_list = ['trump', 'maga']
data_list = []
count = 0

class Listener(tweepy.StreamListener):

  def __init__(self):
    self.counter = 0

  def on_data(self, data):
    #global count
    if self.counter < 10:
      json_data = json.loads(data)
      try:
        location = json_data['user']['location']
        text = json_data['retweeted_status']['extended_tweet']['full_text']
        user = json_data['user']['name']
        d = [[location], [user], [text]]
        if location is not None:
          # only get locations ending with a comma and a space followed by two letters
          expression = re.search(r'([,][\s][a-zA-z]{2}$)', location)
          if expression:
            with open('tweets.csv', 'a', newline='') as t:
              w = csv.writer(t, quoting=csv.QUOTE_MINIMAL)
              w.writerows([d])
              self.counter += 1
            return
          return
      except KeyError:
        print("fail")
    else:
      return False
  def on_error(self, status):
    print(status)
    return True

class Geocoder():
  def make_geojson(self):
    geolocator = Nominatim()
    file = 'tweets.csv'
    with open(file, 'r') as f:
      reader = csv.reader(f)
      geo_data = {
          "type": "FeatureCollection",
          "features": []
      }
      for line in reader:
        loc = geolocator.geocode(line[0])
        user = line[1]
        text = line[2]
        if loc is not None and loc.latitude is not None and loc.longitude is not None:
          print(loc.latitude, loc.longitude)
          geo_json_feature = {
              "type": "Feature",
              "geometry": {
                  "type": "Point",
                  "coordinates": [loc.longitude, loc.latitude]
              },
              "properties": {
                  "text": text,
                  "user": user
              }
          }
          geo_data['features'].append(geo_json_feature)
    with open('geo_data.json', 'w') as fout:
      fout.write(json.dumps(geo_data, indent=4, ensure_ascii=False))

stream = tweepy.Stream(auth, Listener())
geocode = Geocoder()
stream.filter(track=keyword_list, languages=['en'])
geocode.make_geojson()
