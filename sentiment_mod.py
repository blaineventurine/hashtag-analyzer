import pickle
#import random
from statistics import mode

#import nltk
from nltk.classify import ClassifierI
#from nltk.corpus import movie_reviews
#from nltk.classify.scikitlearn import SklearnClassifier
from nltk.tokenize import word_tokenize
#from sklearn.linear_model import LogisticRegression, SGDClassifier
#from sklearn.naive_bayes import BernoulliNB, MultinomialNB
#from sklearn.svm import SVC, LinearSVC, NuSVC


class VoteClassifier(ClassifierI):
  def __init__(self, *classifiers):
    self._classifiers = classifiers

  def classify(self, features):
    votes = []
    for c in self._classifiers:
      v = c.classify(features)
      votes.append(v)
    return mode(votes)

  def confidence(self, features):
    votes = []
    for c in self._classifiers:
      v = c.classify(features)
      votes.append(v)
    choice_votes = votes.count(mode(votes))
    conf = choice_votes / len(votes)
    return conf

def find_features(document):
  words = word_tokenize(document)
  features = {}
  for w in word_features:
    features[w] = (w in words)
  return features

with open("pickles/documents.pickle", "rb") as documents_f:
  documents = pickle.load(documents_f)

with open("pickles/word_features5k.pickle", "rb") as word_features5k_f:
  word_features = pickle.load(word_features5k_f)

with open("pickles/featuresets.pickle", "rb") as featuresets_f:
  featuresets = pickle.load(featuresets_f)

with open("pickles/originalnaivebayes5k.pickle", "rb") as open_file:
  classifier = pickle.load(open_file)

with open("pickles/MNB_classifier5k.pickle", "rb") as open_file:
  MNB_classifier = pickle.load(open_file)

with open("pickles/BernoulliNB_classifier5k.pickle", "rb") as open_file:
  BernoulliNB_classifier = pickle.load(open_file)

with open("pickles/LogisticRegression_classifier5k.pickle", "rb") as open_file:
  LogisticRegression_classifier = pickle.load(open_file)

with open("pickles/LinearSVC_classifier5k.pickle", "rb") as open_file:
  LinearSVC_classifier = pickle.load(open_file)

with open("pickles/SGDC_classifier5k.pickle", "rb") as open_file:
  SGDC_classifier = pickle.load(open_file)

voted_classifier = VoteClassifier(
                                  classifier,
                                  LinearSVC_classifier,
                                  MNB_classifier,
                                  BernoulliNB_classifier,
                                  LogisticRegression_classifier)

def sentiment(text):
  feats = find_features(text)
  return voted_classifier.classify(feats), voted_classifier.confidence(feats)
