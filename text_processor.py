import pickle
import random
from statistics import mode
import nltk
from nltk.classify import ClassifierI
from nltk.corpus import twitter_samples
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.tokenize import word_tokenize
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.svm import SVC, LinearSVC, NuSVC

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
  words_tokenized = word_tokenize(document)
  features = {}
  for word_f in word_features:
    features[word_f] = (word_f in words_tokenized)
  return features

SHORT_POS = open("training_data/positive.txt", "r", encoding="ISO-8859-1").read()
SHORT_NEG = open("training_data/negative.txt", "r", encoding="ISO-8859-1").read()

TWITTER_SAMPLES_NEGATIVE = twitter_samples.strings('negative_tweets.json')
TWITTER_SAMPLES_POSITIVE = twitter_samples.strings('positive_tweets.json')

all_words = []
documents = []

#  j is adject, r is adverb, and v is verb
#allowed_word_types = ["J","R","V"]
allowed_word_types = ["J"]

for p in SHORT_POS.split('\n'):
  documents.append((p, "pos"))
  words = word_tokenize(p)
  pos = nltk.pos_tag(words)
  for w in pos:
    if w[1][0] in allowed_word_types:
      all_words.append(w[0].lower())

for p in SHORT_NEG.split('\n'):
  documents.append((p, "neg"))
  words = word_tokenize(p)
  pos = nltk.pos_tag(words)
  for w in pos:
    if w[1][0] in allowed_word_types:
      all_words.append(w[0].lower())

for p in TWITTER_SAMPLES_POSITIVE:
  documents.append((p, "pos"))
  words = word_tokenize(p)
  pos = nltk.pos_tag(words)
  for w in pos:
    if w[1][0] in allowed_word_types:
      all_words.append(w[0].lower())

for p in TWITTER_SAMPLES_NEGATIVE:
  documents.append((p, "neg"))
  words = word_tokenize(p)
  pos = nltk.pos_tag(words)
  for w in pos:
    if w[1][0] in allowed_word_types:
      all_words.append(w[0].lower())

with open("pickles/documents.pickle", "wb") as save_documents:
  pickle.dump(documents, save_documents)

all_words = nltk.FreqDist(all_words)
word_features = list(all_words.keys())[:10000]
featuresets = [(find_features(rev), category) for (rev, category) in documents]

with open("pickles/word_features5k.pickle", "wb") as save_word_features:
  pickle.dump(word_features, save_word_features)
with open("pickles/featuresets.pickle", "wb") as save_featuresets:
  pickle.dump(featuresets, save_featuresets)

random.shuffle(featuresets)
print("Length of featuresets: ", len(featuresets))

TESTING_SET = featuresets[18000:]
TRAINING_SET = featuresets[:18000]

CLASSIFIER = nltk.NaiveBayesClassifier.train(TRAINING_SET)
print("Original Naive Bayes Algo accuracy percent:",
      (nltk.classify.accuracy(CLASSIFIER, TESTING_SET)) * 100)
#classifier.show_most_informative_features(15)
with open("pickles/originalnaivebayes5k.pickle", "wb") as save_classifier:
  pickle.dump(CLASSIFIER, save_classifier)

MNB_CLASSIFIER = SklearnClassifier(MultinomialNB())
MNB_CLASSIFIER.train(TRAINING_SET)
print("MNB_classifier accuracy percent:",
      (nltk.classify.accuracy(MNB_CLASSIFIER, TESTING_SET)) * 100)
with open("pickles/MNB_classifier5k.pickle", "wb") as save_classifier:
  pickle.dump(MNB_CLASSIFIER, save_classifier)

BERNOULLINB_CLASSIFIER = SklearnClassifier(BernoulliNB())
BERNOULLINB_CLASSIFIER.train(TRAINING_SET)
print("BernoulliNB_classifier accuracy percent:",
      (nltk.classify.accuracy(BERNOULLINB_CLASSIFIER, TESTING_SET)) * 100)
with open("pickles/BernoulliNB_classifier5k.pickle", "wb") as save_classifier:
  pickle.dump(BERNOULLINB_CLASSIFIER, save_classifier)

LOGISTICREGRESSION_CLASSIFIER = SklearnClassifier(LogisticRegression())
LOGISTICREGRESSION_CLASSIFIER.train(TRAINING_SET)
print("LogisticRegression_classifier accuracy percent:",
      (nltk.classify.accuracy(LOGISTICREGRESSION_CLASSIFIER, TESTING_SET)) * 100)
with open(
    "pickles/LogisticRegression_classifier5k.pickle", "wb") as save_classifier:
  pickle.dump(LOGISTICREGRESSION_CLASSIFIER, save_classifier)

LINEARSVC_CLASSIFIER = SklearnClassifier(LinearSVC())
LINEARSVC_CLASSIFIER.train(TRAINING_SET)
print("LinearSVC_classifier accuracy percent:",
      (nltk.classify.accuracy(LINEARSVC_CLASSIFIER, TESTING_SET)) * 100)
with open("pickles/LinearSVC_classifier5k.pickle", "wb") as save_classifier:
  pickle.dump(LINEARSVC_CLASSIFIER, save_classifier)

SGDC_CLASSIFIER = SklearnClassifier(SGDClassifier())
SGDC_CLASSIFIER.train(TRAINING_SET)
print("SGDClassifier accuracy percent:", nltk.classify.accuracy(
    SGDC_CLASSIFIER, TESTING_SET) * 100)
with open("pickles/SGDC_classifier5k.pickle", "wb") as save_classifier:
  pickle.dump(SGDC_CLASSIFIER, save_classifier)
