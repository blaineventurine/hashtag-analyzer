import pickle
import random
from statistics import mode

import nltk
from nltk.classify import ClassifierI
#from nltk.corpus import movie_reviews
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


short_pos = open("training_data/positive.txt", "r", encoding="ISO-8859-1").read()
short_neg = open("training_data/negative.txt", "r", encoding="ISO-8859-1").read()


all_words = []
documents = []


#  j is adject, r is adverb, and v is verb
#allowed_word_types = ["J","R","V"]
allowed_word_types = ["J"]

for p in short_pos.split('\n'):
  documents.append((p, "pos"))
  words = word_tokenize(p)
  pos = nltk.pos_tag(words)
  for w in pos:
    if w[1][0] in allowed_word_types:
      all_words.append(w[0].lower())


for p in short_neg.split('\n'):
  documents.append((p, "neg"))
  words = word_tokenize(p)
  pos = nltk.pos_tag(words)
  for w in pos:
    if w[1][0] in allowed_word_types:
      all_words.append(w[0].lower())


with open("pickles/documents.pickle", "wb") as save_documents:
  pickle.dump(documents, save_documents)


all_words = nltk.FreqDist(all_words)
word_features = list(all_words.keys())[:5000]
featuresets = [(find_features(rev), category) for (rev, category) in documents]

with open("pickles/word_features5k.pickle", "wb") as save_word_features:
  pickle.dump(word_features, save_word_features)

def find_features(document):
  words = word_tokenize(document)
  features = {}
  for w in word_features:
    features[w] = (w in words)
  return features

with open("pickles/featuresets.pickle", "wb") as save_featuresets:
  pickle.dump(featuresets, save_featuresets)

random.shuffle(featuresets)
print(len("Length of featuresets: ", featuresets))

testing_set = featuresets[10000:]
training_set = featuresets[:10000]

classifier = nltk.NaiveBayesClassifier.train(training_set)
print("Original Naive Bayes Algo accuracy percent:",
      (nltk.classify.accuracy(classifier, testing_set)) * 100)
#classifier.show_most_informative_features(15)


with open("pickles/originalnaivebayes5k.pickle", "wb") as save_classifier:
  pickle.dump(classifier, save_classifier)

MNB_classifier = SklearnClassifier(MultinomialNB())
MNB_classifier.train(training_set)
print("MNB_classifier accuracy percent:",
      (nltk.classify.accuracy(MNB_classifier, testing_set)) * 100)

with open("pickles/MNB_classifier5k.pickle", "wb") as save_classifier:
  pickle.dump(MNB_classifier, save_classifier)


BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
BernoulliNB_classifier.train(training_set)
print("BernoulliNB_classifier accuracy percent:",
      (nltk.classify.accuracy(BernoulliNB_classifier, testing_set)) * 100)

with open("pickles/BernoulliNB_classifier5k.pickle", "wb") as save_classifier:
  pickle.dump(BernoulliNB_classifier, save_classifier)


LogisticRegression_classifier = SklearnClassifier(LogisticRegression())
LogisticRegression_classifier.train(training_set)
print("LogisticRegression_classifier accuracy percent:",
      (nltk.classify.accuracy(LogisticRegression_classifier, testing_set)) * 100)

with open(
    "pickles/LogisticRegression_classifier5k.pickle", "wb") as save_classifier:
  pickle.dump(LogisticRegression_classifier, save_classifier)



LinearSVC_classifier = SklearnClassifier(LinearSVC())
LinearSVC_classifier.train(training_set)
print("LinearSVC_classifier accuracy percent:",
      (nltk.classify.accuracy(LinearSVC_classifier, testing_set)) * 100)

with open("pickles/LinearSVC_classifier5k.pickle", "wb") as save_classifier:
  pickle.dump(LinearSVC_classifier, save_classifier)

SGDC_classifier = SklearnClassifier(SGDClassifier())
SGDC_classifier.train(training_set)
print("SGDClassifier accuracy percent:", nltk.classify.accuracy(
    SGDC_classifier, testing_set) * 100)

with open("pickles/SGDC_classifier5k.pickle", "wb") as save_classifier:
  pickle.dump(SGDC_classifier, save_classifier)
