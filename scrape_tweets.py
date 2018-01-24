import tweepy
import re
import fileinput
from api_keys import *
import threading
import json
import time


auth = tweepy.OAuthHandler(key, secret_key)
auth.set_access_token(token, secret_token)
api = tweepy.API(auth)

keyword_list = ['trump', 'maga']
data_list = []
count = 0


@classmethod
def parse(cls, api, raw):
  status = cls.first_parse(api, raw)
  setattr(status, 'json', json.dumps(raw))
  return status

tweepy.models.Status.first_parse = tweepy.models.Status.parse
tweepy.models.Status.parse = parse

class Listener(tweepy.StreamListener):

  def on_data(self, data):
    global count
    if count < 1000:
      json_data = json.loads(data)
      try:
        location = json_data['user']['location']
        if location is not None:
          expression = re.search(r'([,][\s][a-zA-z]{2}$)', location)
          if expression:
            with open('location.json', 'a') as l:
              l.write(location + '\n')
            count += 1
      except KeyError:
        print("fail")
    return

  def on_error(self, status):
    print(status)
    return True


stream = tweepy.Stream(auth, Listener())
stream.filter(track=keyword_list, languages=['en'])
