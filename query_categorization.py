import nltk
from parsedatetime import Calendar
from nltk.tag import pos_tag, map_tag
from stat_parser import Parser, display_tree
from time import mktime
from datetime import datetime , timedelta
from dateutil.relativedelta import *

#SciKit Learn Library Imports/Dependencies
import numpy as np
from sklearn.naive_bayes import BernoulliNB
from nltk_brain import *


#Features array is created here
#index 0: contains a schedule verb
#index 1: contains a schedule noun
#index 2: schedule verb modifies schedule noun
#index 3: time is in query
#index 4: what is in query
#index 5: when is in query
#index 6: why is in query
#index 7: how is in query
#index 8: where is in query
#index 9: who is in query
#index 10: is it a categorical question?
#index 11: document noun is in query
#index 12: document verb is in query
#index 13: document verb modifies document noun
#index 14: show verb is in query
#index 15: show verb along with calendar noun is in query
#index 16: has only 1 word
#index 17: has fewer than 5 words
#index 18: has fewer than 10 words
#index 19: has fewer than 20 words
#index 20: has more than 20 words



features_array = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

#training set of strings
#it is a list of query, api_type

training_set = [["Let's meet up on Friday at 3 p.m.", "calendar"],
								["Can we have a meeting next week", "calendar"],
								["Benedict, schedule a meeting for next Tuesday", "calendar"],
								["Next Wednesday let's have a conference", "calendar"],
								["Can you schedule me a meeting for tomorrow", "calendar"],
								["Could you find a time that works for all of us", "calendar"],
								["Can we have a weekly meeting on Thursdays", "calendar"],
								["Would you be available after 2pm on Wednesday", "calendar"],
								["Lets meet tomorrow at 12", "calendar"],
								["Set up a meeting for tomorrow at 12", "calendar"],
								["Let's meet later", "calendar"],
								["Schedule a meeting tomorrow.", "calendar"],
								["What is the phase of the moon", "wolfram"],
								["Why are dogs", "google"],
								["What is the rate of expansion of the universe", "wolfram"],
								["When is my birthday", "google"],
								["Why do dogs have feet", "google"],
								["What are the biggest problems facing humanity", "google"],
								["When can I see my children again", "google"],
								["What are these spots on my genitals", "google"],
								["Why do birds suddenly appear", "google"],
								["Where is a good place to get Chinese food", "google"]]


#api predicting bernoulli naive bayesian classifier

api_predictor = BernoulliNB()

def train(set_to_train_on):
	api_predictor.fit()

#Convert training set to binary feature arrays
training_feature_arrays = []

def put_training_set_through_query(set_to_train_on):

	for i in range 0 to len(set_to_train_on):
		temp_array = query_to_array(set_to_train_on[i][0], set_to_train_on[i][1])
		training_feature_arrays.append(temp_array)

def query_to_array(query, api_type):

	temp_array = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

	#call list of functions to populate the array
	####

	return temp_array

#EXAMPLE usage of BernoulliNB
# X = np.random.randint(2, size=(6, 100))
# Y = np.array([1, 2, 3, 4, 4, 5])
# clf = BernoulliNB()
# clf.fit(X, Y)
# BernoulliNB(alpha=1.0, binarize=0.0, class_prior=None, fit_prior=True)
# print(clf.predict(X[2]))