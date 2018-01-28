'''
  Blaine Venturine
'''
import csv
import json
import re
import tweepy
from geopy.geocoders import Nominatim
from textblob import TextBlob
import api_keys
import sentiment_mod as sentiment_mod

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
    encode = TextEncoder()
    encode.make_geojson()
    #encode.do_blob()

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
            return True
      except KeyError:
        print("fail")
    else:
      return False

  def on_error(self, status):
    print(status)
    return True

class TextEncoder():
  '''Class for turning tweet data into mappable data'''
  tweet_file = 'output/tweets.csv'
  geo_json_file = 'output/geo_data.json'


  def clean_text(self, string):
    ''' Returns the string without non-ASCII characters'''

    # strip out URLs
    string = re.sub(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        '',
        string)
    string = string.replace('[\'', '').replace('\']', '').replace('\\n', ' ').replace('[', '').replace('\\', '').replace(']', '')
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

  def make_geojson(self):
    '''
      Extracts tweet data from CSV and renders it into GeoJSON
      Uses OpenStreetMap API to guess coordinates from place names
      '''
    geolocator = Nominatim()

    with open(self.tweet_file, 'r') as csvfile:
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
            # if re.match(r'^RT.*', text):
            #   continue
          text = self.clean_text(text)
          user = self.clean_text(user)

          sentiment_value, confidence = sentiment_mod.sentiment(text)

          print(loc.latitude, loc.longitude)
          geo_json_feature = {
              "type": "Feature",
              "geometry": {
                  "type": "Point",
                  "coordinates": [loc.longitude, loc.latitude]
              },
              "properties": {
                  "text": text,
                  "user": user,
                  "sentiment_value": sentiment_value,
                  "confidence": confidence
              }
          }
          geo_data['features'].append(geo_json_feature)
    with open(self.geo_json_file, 'w') as fout:
      fout.write(json.dumps(geo_data, indent=4, ensure_ascii=False))


if __name__ == "__main__":
  NUM_OF_TWEETS = 10
  KEYWORD_LIST = ['trump', 'maga']
  SCRAPE = Scrape(NUM_OF_TWEETS, KEYWORD_LIST)
  SCRAPE.get_data()
  SCRAPE.geocode_data()
