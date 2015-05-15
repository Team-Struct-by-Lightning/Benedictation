import nltk
from parsedatetime import Calendar
from nltk.tag import pos_tag, map_tag
from stat_parser import Parser, display_tree
from time import mktime
from datetime import datetime , timedelta
from dateutil.relativedelta import *

#SciKit Learn Library Imports/Dependencies
import numpy as np
import random
from sklearn.naive_bayes import BernoulliNB
from nltk_brain import *

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path


#OLD!!!!!
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

#NEW
#index 0: what is in query
#index 1: when is in query
#index 2: why is in query
#index 3: how is in query
#index 4: where is in query
#index 5: who is in query
#index 6: has fewer than 5 words
#index 7: FILL THESE IN BECAUSE WE USE THEM
#index 8:
#index 9:
#index 10:
#index 11:
#index 12:
#index 13:



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


def validate_predictor(set_to_validate_on, classes, predictor, probability_matrix):
	number_valid = 0
	probability_array = []
	for i in range (len(set_to_validate_on)):
		probability_array.append(predictor.predict_proba(set_to_validate_on[i:i+1]))
		if predictor.predict(set_to_validate_on[i:i+1]) == classes[i:i+1]:
			number_valid += 1
	probability_matrix.append(probability_array)
	return number_valid



def change_query_string_to_int_array(set_to_train_on):
# Convert training set to binary feature arrays
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
	else:# Defaults the google search if something messes up
		return 7

def percent_to_index(percentage, length_of_array):
	return int(percentage*length_of_array)

def interpret_for_scikit(sentences, temp_array):
	try:
		for sentence in sentences:
			if(len(sentence.split()) <= 1):
				words = sentences[0]
				text = '{"api_type": "google", \
			 		"query": "' + words + '"}'
				return text

			sentence = oclock_remover(sentence)

			tree = parser.parse(sentence)
			print tree

			for element in [tree] + [e for e in tree]: # Include the root element in the for loop

				if 'VP' in element.label() or 'SQ' in element.label():
					for verb_subtree in element.subtrees():

						if 'VB' in verb_subtree.label() \
						and any(x in verb_subtree.leaves() for x in doc_verbs):
							for subtree in element.subtrees():
									if 'NP' in subtree.label() and any(x in subtree.leaves() for x in doc_nouns):
										print 'Interpreting as doc request'
										temp_array[0] = 1
										return

									if 'NP' in subtree.label() and any(x in subtree.leaves() for x in calendar_nouns):
										print 'Interpreting as calendar request'
										temp_array[1] = 1
										return

						if 'VB' in verb_subtree.label() \
						and any(x in verb_subtree.leaves() for x in schedule_verbs):

							print "Interpreting as schedule request"
							return schedule_for_scikit(element, tree)


				if "SBAR" in element.label():
					for subtree in element.subtrees():
						if "W" in subtree.label():

							# TODO: Implement logic here to catch "when"-questions related to scheduling.

							print "Interpreting as Wolfram query"
							return wolfram_for_scikit(element,temp_array)

def schedule_for_scikit(element, tree, temp_array):
# Find the "schedule word" in a NP, if one exists
	schedule_word = "Meeting"
	for subtree in element.subtrees():
		if 'NP' in subtree.label() and any(x in subtree.leaves() for x in schedule_nouns):
			for x in subtree.leaves():
				if x in schedule_nouns:
					schedule_word = x



	words = ' '.join(element.leaves())
	words = am_pm_adder(words)

	cal_parse = cal.parse(words)
	print cal_parse
	if cal_parse[1] == 0 or cal_parse[1] == 1:
		starttime, endtime = schedule_suggest(cal_parse, words)
		starttime = starttime.strftime('%Y-%m-%dT%H:%M:%S')
		endtime   = endtime.strftime('%Y-%m-%dT%H:%M:%S')
		api_type  = "schedule_suggest"
		temp_array[3] = 1
	else:
		starttime, endtime = time_converter(cal_parse[0])
		api_type = "calendar"
		temp_array[4] = 1

	return

def wolfram_for_scikit(element, temp_array):
	words = ' '.join(element.leaves())

	temp_array[2] = 1
	return

def query_to_array(query):
	temp_array = np.array([0 for i in range(14)])
# call list of functions to populate the array
####
# NEW
# index 0: what is in query
# index 1: when is in query
# index 2: why is in query
# index 3: how is in query
# index 4: where is in query
# index 5: who is in query
# index 6: has fewer than 5 words
# print query + "\n"
# makes it into an array
	query_array = query.split(' ')

	interpret_for_scikit([query])
	'''
	for i in range(len(query_array)):
		if query_array[i] in schedule_nouns:
			temp_array[7] = 1
		if query_array[i] in schedule_verbs:
			temp_array[8] = 1
		if query_array[i] in doc_nouns:
			temp_array[9] = 1
		if query_array[i] in doc_verbs:
			temp_array[10] = 1
		if query_array[i] in calendar_nouns:
			temp_array[11] = 1
		if query_array[i] in group_prps:
			temp_array[12] = 1
		if query_array[i] in group_nouns:
			temp_array[13] = 1
#checks substings and length
	if "what" in query:
		temp_array[0] = 1
	if "what" in query:
		temp_array[1] = 1
	if "why" in query:
		temp_array[2] = 1
	if "how" in query:
		temp_array[3] = 1
	if "where" in query:
		temp_array[4] = 1
	if "who" in query:
		temp_array[5] = 1
	if len(query) < 5:
		temp_array[6] = 1
		'''
	return temp_array


def make_single_predictor(training_set, test_set_percentage):
	assert(len(training_set) > 1)
# api predicting bernoulli naive bayesian classifier
	api_predictor = BernoulliNB()
# random shuffles of training_set
	random.shuffle(training_set)
# convert training set to binary feature arrays
	training_feature_arrays = change_query_string_to_int_array(training_set)
# this is used to hold the integer value of the api_type
	training_class_array = change_api_type_array_to_int_array(training_set)
# this is the array of the probability confidence of picking a
# particular class
	probabilities_array = []
# returns the index of the percent of the test set we want to test on
	index = percent_to_index(test_set_percentage, len(training_set))
	valid_num = 0
	if index == len(training_feature_arrays):
		train_predictor(training_feature_arrays, training_class_array, api_predictor)
		valid_num = -1
	else:
		train_predictor(training_feature_arrays[:index + 1], training_class_array[:index + 1], api_predictor)
		valid_num = validate_predictor(training_feature_arrays[index + 1:], training_class_array[index + 1:], api_predictor, probabilities_array)
		print "The number of valid predictions is: " + str(valid_num) + "\nThe total number of predictions made is: " + str(len(training_feature_arrays[index + 1:])) + "\nThe validation ratio is: " + str(float(valid_num)/(len(training_feature_arrays[index + 1:])))
	return api_predictor



def multiple_predictors_for_testing(training_set, test_set_percentage, probability_matrix):
	assert(len(training_set) > 1)
# api predicting bernoulli naive bayesian classifier
	api_predictor = BernoulliNB()
# random shuffles of training_set
	random.shuffle(training_set)
# convert training set to binary feature arrays
	training_feature_arrays = change_query_string_to_int_array(training_set)
# this is used to hold the integer value of the api_type
	training_class_array = change_api_type_array_to_int_array(training_set)
# returns the index of the percent of the test set we want to test on
	index = percent_to_index(test_set_percentage, len(training_set))
	valid_num = 0
	if index == len(training_feature_arrays):
		train_predictor(training_feature_arrays, training_class_array, api_predictor)
		valid_num = -1
	else:
		train_predictor(training_feature_arrays[:index + 1], training_class_array[:index + 1], api_predictor)
		valid_num = validate_predictor(training_feature_arrays[index + 1:], training_class_array[index + 1:], api_predictor, probability_matrix)
	return valid_num


def predictor_validation_list_to_plot(num_tests, training_set, test_set_percentage):
	num_valid_list = []
	percentage_valid_list = []
# this is the array of the probability confidence of picking a
# particular class
	probability_matrix = []
	index = percent_to_index(test_set_percentage, len(training_set))
	total_validated_on = len(training_set[index + 1:])
	for i in range(num_tests):
		num_valid_temp = multiple_predictors_for_testing(training_set, test_set_percentage, probability_matrix)
		num_valid_list.append(num_valid_temp)
		percentage_valid_list.append(float(num_valid_temp)/total_validated_on)
# plots
	fig, ax = plt.subplots()
# histogram our data with numpy
	data = num_valid_list
	n, bins = np.histogram(data, 10)
# get the corners of the rectangles for the histogram
	left = np.array(bins[:-1])
	right = np.array(bins[1:])
	bottom = np.zeros(len(left))
	top = bottom + n
# we need a (numrects x numsides x 2) numpy array for the path helper
# function to build a compound path
	XY = np.array([[left,left,right,right], [bottom,top,top,bottom]]).T
# get the Path object
	barpath = path.Path.make_compound_path_from_polys(XY)
# make a patch out of it
	patch = patches.PathPatch(barpath, facecolor='blue', edgecolor='gray', alpha=0.8)
	ax.add_patch(patch)
# update the view limits
	ax.set_xlim(left[0], right[-1])
	ax.set_ylim(bottom.min(), top.max())
	plt.show()


predictor_validation_list_to_plot(1000, training_set, .7)


#make_single_predictor(training_set, .8)

#EXAMPLE usage of BernoulliNB
# X = np.random.randint(2, size=(6, 100))
# Y = np.array([1, 2, 3, 4, 4, 5])
# clf = BernoulliNB()
# clf.fit(X, Y)
# print(clf.predict(X[2]))