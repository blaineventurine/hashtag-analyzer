'''
  Blaine Venturine
'''
import csv
import json
import re

import tweepy
from geopy.geocoders import Nominatim

import api_keys

class Scrape():
  '''
  Set variables
  '''
  def __init__(self, num_of_tweets, keyword_list):
    self.auth = tweepy.OAuthHandler(api_keys.key, api_keys.secret_key)
    self.auth.set_access_token(api_keys.token, api_keys.secret_token)
    self.api = tweepy.API(self.auth)
    self.num_of_tweets = num_of_tweets
    self.keyword_list = keyword_list

  def get_data(self):
    '''
    Gather predetermined amount of tweets containing designated hashtags
    '''
    stream = tweepy.Stream(self.auth, Listener(num_of_tweets=self.num_of_tweets))
    try:
      stream.filter(track=self.keyword_list, languages=['en'])
    except ConnectionError as error:
      print(error.__doc__)

  @classmethod
  def geocode_data(cls):
    geocode = Geocoder()
    geocode.make_geojson()

class Listener(tweepy.StreamListener):

  def __init__(self, num_of_tweets):
    self.counter = 0
    self.num_of_tweets = num_of_tweets

  def on_data(self, data):
    '''
    Accept all tweet data as JSON, extract only only the necessary information,
    and write it into a CSV file.
    '''

    tweetcsv = 'output/tweets.csv'

    if self.counter < self.num_of_tweets:
      json_data = json.loads(data)
      try:
        location = json_data['user']['location']
        text = json_data['retweeted_status']['extended_tweet']['full_text']
        user = json_data['user']['name']
        necessary_tweet_data = [[location], [user], [text]]
        if location is not None:
          # only get locations ending with a comma and a space followed by two letters
          # filters out most locations not listed as "City, ST" so less queries are made
          # to OpenStreetMap
          expression = re.search(r'([,][\s][a-zA-z]{2}$)', location)

          if expression:
            with open(tweetcsv, 'a', newline='') as tweet_file:
              writer = csv.writer(tweet_file, quoting=csv.QUOTE_MINIMAL)
              writer.writerows([necessary_tweet_data])
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
  '''
    Class for turning tweet data into mappable data
    '''
  @classmethod
  def make_geojson(cls):
    '''
      Extracts tweet data from CSV and renders it into GeoJSON
      Uses OpenStreetMap API to guess coordinates from place names
      '''
    geolocator = Nominatim()
    tweet_file = 'output/tweets.csv'
    geo_json_file = 'output/geo_data.json'
    with open(tweet_file, 'r') as csvfile:
      reader = csv.reader(csvfile)
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
    with open(geo_json_file, 'w') as fout:
      fout.write(json.dumps(geo_data, indent=4, ensure_ascii=False))


if __name__ == "__main__":
  NUM_OF_TWEETS = 10
  KEYWORD_LIST = ['trump', 'maga']
  SCRAPE = Scrape(NUM_OF_TWEETS, KEYWORD_LIST)
  SCRAPE.get_data()
  SCRAPE.geocode_data()
