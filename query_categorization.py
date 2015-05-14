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


#training set of strings
#it is a list of query, api_type

training_set = [("Let's meet up on Friday at 3 p.m.", "calendar"),
								("Can we have a meeting next week", "calendar"),
								("Benedict, schedule a meeting for next Tuesday", "calendar"),
								("Next Wednesday let's have a conference", "calendar"),
								("Can you schedule me a meeting for tomorrow", "calendar"),
								("Could you find a time that works for all of us", "calendar"),
								("Can we have a weekly meeting on Thursdays", "calendar"),
								("Would you be available after 2pm on Wednesday", "calendar"),
								("Lets meet tomorrow at 12", "calendar"),
								("Set up a meeting for tomorrow at 12", "calendar"),
								("Let's meet later", "calendar"),
								("Schedule a meeting tomorrow.", "calendar"),
								("What is the phase of the moon", "wolfram"),
								("Why are dogs", "google"),
								("What is the rate of expansion of the universe", "wolfram"),
								("When is my birthday", "google"),
								("Why do dogs have feet", "google"),
								("What are the biggest problems facing humanity", "google"),
								("When can I see my children again", "google"),
								("What are these spots on my genitals", "google"),
								("Why do birds suddenly appear", "google"),
								("Where is a good place to get Chinese food", "google")]


def train_predictor(set_to_train_on, classes, predictor):
	predictor.fit(set_to_train_on, classes)


def validate_predictor(set_to_validate_on, classes, predictor):

	number_valid = 0

	for i in range (len(set_to_validate_on)):

		if api_predictor.predict(set_to_validate_on[i]) == classes[i]:
			number_valid += 1

	# gross ass code by Brown Clow
	# num_valid = sum((api_predictor.predict(val) == j for val, j in zip(set_to_validate_on, classes)))
	# returns the rate
	return number_valid



def change_query_string_to_int_array(set_to_train_on):

	#Convert training set to binary feature arrays
	training_feature_arrays = []

	for i in range (len(set_to_train_on)):

		temp_query_array = query_to_array(set_to_train_on[i][0])

		# appends the integer features to the feature array
		training_feature_arrays.append(temp_query_array)

	return training_feature_arrays


def change_api_type_array_to_int_array(class_array):

	# this is used to hold the integer value of the api_type
	training_class_array = []

	for i in range (len(class_array)):

		temp_class = change_api_type_to_int(class_array[i][1])

		# changes class to the class array
		training_class_array.append(temp_class)

	return training_class_array


def change_api_type_to_int(class_type):

	# this is a switch statement on the api type

	if class_type == "calendar":
		return 1
	elif class_type == "calendar_show":
		return 2
	elif class_type == "schedule_suggest":
		return 3
	elif class_type == "google_doc":
		return 4
	elif class_type == "wolfram":
		return 5
	elif class_type == "wikipedia":
		return 6
	else: # Defaults the google search if something messes up
		return 7

def percent_to_index(percentage, length_of_array):

	return int(percentage*length_of_array)


def query_to_array(query):

	temp_array = np.array([0 for i in range(21)])

	#call list of functions to populate the array
	####

	return temp_array


def make_predictor(training_set, test_set_percentage):

	assert(len(training_set) > 1)
	# api predicting bernoulli naive bayesian classifier
	api_predictor = BernoulliNB()

	#random shuffles
	training_set_shuffle = random.shuffle(training_set)

	# convert training set to binary feature arrays
	training_feature_arrays = change_query_string_to_int_array(training_set_shuffle)

	# this is used to hold the integer value of the api_type
	training_class_array = change_api_type_array_to_int_array(training_set_shuffle)

	# returns the index
	index = percent_to_index(test_set_percentage, len(training_set))

	valid_num = 0

	if index == len(training_feature_arrays):
		train_predictor(training_feature_arrays, training_class_array, api_predictor)
		valid_num = -1
	else:
		train_predictor(training_feature_arrays[:index + 1], training_class_array[:index + 1], api_predictor)
		valid_num = validate_predictor(training_feature_arrays[index + 1:], training_class_array[index + 1:], api_predictor)
		print "The number of valid predictions is ratio is: " +
					str(valid_num) + "\nThe total number of predictions made is: " +
					str(len(training_feature_arrays[index + 1:])) + "\nThe validation ratio is: " +
					str(float(valid_num)/(len(training_feature_arrays[index + 1:])))

	return api_predictor




#EXAMPLE usage of BernoulliNB
# X = np.random.randint(2, size=(6, 100))
# Y = np.array([1, 2, 3, 4, 4, 5])
# clf = BernoulliNB()
# clf.fit(X, Y)
# print(clf.predict(X[2]))