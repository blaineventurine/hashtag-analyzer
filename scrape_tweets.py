import fileinput
import json
import re
import threading
import time
import csv
from geopy.geocoders import Nominatim
import tweepy
from api_keys import *

class Scrape():
  def __init__(self, num_of_tweets, keyword_list):
    self.auth = tweepy.OAuthHandler(key, secret_key)
    self.auth.set_access_token(token, secret_token)
    self.api = tweepy.API(self.auth)
    self.num_of_tweets = num_of_tweets
    self.keyword_list = keyword_list

  def get_data(self):
    stream = tweepy.Stream(self.auth, Listener(num_of_tweets=self.num_of_tweets))
    try:
      stream.filter(track=self.keyword_list, languages=['en'])
    except Exception as e:
      print(e.__doc__)

  def geocode_data(self):
    geocode = Geocoder()
    geocode.make_geojson()

class Listener(tweepy.StreamListener):

  def __init__(self, num_of_tweets):
    self.counter = 0
    self.num_of_tweets = num_of_tweets

  def on_data(self, data):
    if self.counter < self.num_of_tweets:
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


if __name__ == "__main__":
  num_of_tweets = 10
  keyword_list = ['trump', 'maga']
  scrape = Scrape(num_of_tweets, keyword_list)
  scrape.get_data()
  scrape.geocode_data()
