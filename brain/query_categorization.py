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
from nlp import *
from query_training_set import *

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
import cPickle


def train_predictor(set_to_train_on, classes, predictor):
	predictor.fit(set_to_train_on, classes)


def validate_predictor(set_to_validate_on, classes, predictor, probability_matrix, querylist, f):
	number_valid = 0
	probability_array = []
	for i in range (len(set_to_validate_on)):
		probability_predict = predictor.predict_proba(set_to_validate_on[i:i+1])
		probability_array.append(probability_predict)
		api_return = threshold_calculator(probability_array[i][0], querylist[i][0])

	## print "$$$$$$$$$$$$$$$ " + str(predictor.predict(set_to_validate_on[i:i+1])) + " " + str(classes[i:i+1])
		# print "api_return: ", api_return[0], " class_expect: ", classes[i:i+1][0]
		if int(api_return[0]) == int(classes[i]):
			number_valid += 1
		else:

			f.write("@@@@@    query: " + querylist[i][0] + "\n")
			f.write("@@@@@    expected: " + change_int_to_api_type(classes[i:i+1][0]) + "\n")
			f.write("@@@@@    predicted: " + change_int_to_api_type(predictor.predict(set_to_validate_on[i:i+1])[0]) + "\n")
			f.write("@@@@@    probabilities: " + "\n")
			f.write("@@@@@                   schedule suggest: " + str(probability_array[i][0][0]) + " %" + "\n")
			f.write("@@@@@                   calendar: " + str(probability_array[i][0][1]) + " %" + "\n")
			f.write("@@@@@                   calendar show: " + str(probability_array[i][0][2]) + " %" + "\n")
			f.write("@@@@@                   google docs: " + str(probability_array[i][0][3]) + " %" + "\n")
			f.write("@@@@@                   google drawings: " + str(probability_array[i][0][4]) + " %" + "\n")
			f.write("@@@@@                   wolfram: " + str(probability_array[i][0][5]) + " %" + "\n")
			f.write("@@@@@                   wikipedia: " + str(probability_array[i][0][6]) + " %" + "\n")
			f.write('\n');
	probability_matrix.append(probability_array)
	return number_valid


def threshold_calculator(probabilities, query):

	probabilities = probabilities.tolist()

	if probabilities[0] > .8 or probabilities[1] > .1:
		cal_parse = cal.parse(query)
		# print cal_parse
		if cal_parse[1] == 0 or cal_parse[1] == 1:
			return [1]
		else:
			return [2]
	elif probabilities[2] > .1 or probabilities[3] > .1 or probabilities[4] > .1:
		return [probabilities.index(max(probabilities[2:5])) + 1]
	elif probabilities[5] > .1 or probabilities[6]:
		return [probabilities.index(max(probabilities[5:7])) + 1]
	else:
		return [probabilities.index(max(probabilities)) + 1]


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
	if class_type == "schedule_suggest":
		return 1
	elif class_type == "calendar":
		return 2
	elif class_type == "calendar_show":
		return 3
	elif class_type == "google_docs":
		return 4
	elif class_type == "google_drawings":
		return 5
	elif class_type == "wolfram":
		return 6
	elif class_type == "wikipedia":
		return 7
	elif class_type == "google":# Defaults the google search if something messes up
		return 8
	else:
		return 9

def change_int_to_api_type(class_type):
	# this is a switch statement on the api type
	if class_type == 1:
		return "schedule_suggest"
	elif class_type == 2:
		return "calendar"
	elif class_type == 3:
		return "calendar_show"
	elif class_type == 4:
		return "google_docs"
	elif class_type == 5:
		return "google_drawings"
	elif class_type == 6:
		return "wolfram"
	elif class_type == 7:
		return "wikipedia"
	elif class_type == 8:
		return "google"
	else: #shit fucked up
		return "WHAT HAPPENED?!"

def percent_to_index(percentage, length_of_array):
	return int(percentage*length_of_array)

def interpret_for_scikit(sentences, temp_array):
	try:
		for sentence in sentences:
			if(len(sentence.split()) <= 1):
				words = sentences[0]
				text = '{"api_type": "google", \
			 		"query": "' + words + '"}'
			 	temp_array[7] = 1
				return


			sentence = oclock_remover(sentence)
			parser = Parser()
			tree = parser.parse(sentence)
			## print tree
			# first just check if its just a noun phrase, then go to wiki
			if 'NP' == tree.label() or \
			'NP+NP'== tree.label() or \
			'NX+NX'== tree.label() or \
			'NX+NP'== tree.label() or \
			'NP+NX'== tree.label() or \
			'FRAG'== tree.label() or \
			'NX' == tree.label():
				# print 'interpreting as just a noun phrase'
				words = sentence
				noun_phrase = []
				# this is code for finding the noun phrase
				for noun_subtree in tree.subtrees():
					if not "SBAR" in noun_subtree.label() \
					and not "W" in noun_subtree.label() \
					and "NP" in noun_subtree.label() \
					and len(noun_subtree.leaves()) > len(noun_phrase):

						noun_phrase = noun_subtree.leaves()

				# this code removes the article from the beginning
				if noun_phrase:
					if (noun_phrase[0] == 'a' or \
					 	noun_phrase[0] == 'an' or noun_phrase[0] == 'the'):
						del noun_phrase[0]

				## print noun_phrase
				noun_phrase = ' '.join(noun_phrase)

				text = '{"api_type": "wikipedia", \
					"noun_phrase": "' + noun_phrase + '", \
			 		"query": "' + words + '"}'
			 	temp_array[10] = 1
			 	return
				#return text

			# If the sentence starts with one of these parts of speech
			if 'VP' in tree.label():
				temp_array[11] = 1
			if 'RRC' in tree.label():
				temp_array[12] = 1
			if 'SQ' in tree.label():
				temp_array[13] = 1
			if 'ADJP' in tree.label():
				temp_array[14] = 1
			if 'ADVP' in tree.label():
				temp_array[15] = 1
			if 'INTJ' in tree.label():
				temp_array[16] = 1
			if 'SBAR' == tree.label():
				temp_array[17] = 1
			if 'SBARQ' in tree.label():
				temp_array[18] = 1
			if 'S' == tree.label():
				temp_array[19] = 1
			if 'SINV' in tree.label():
				temp_array[20] = 1


			for element in [tree] + [e for e in tree]: # Include the root element in the for loop

				if 'VP' in element.label() or 'SQ' in element.label() or 'RRC' in element.label():
					for verb_subtree in element.subtrees():

						if 'VB' in verb_subtree.label() or 'JJ' in verb_subtree.label() \
						and any(x in verb_subtree.leaves() for x in doc_verbs):
							for subtree in element.subtrees():
									if 'NP' in subtree.label() and any(x in subtree.leaves() for x in doc_nouns):
										# print 'Interpreting as doc request'
										temp_array[0] = 1
										return

									if 'NP' in subtree.label() and any(x in subtree.leaves() for x in drawing_nouns):
										# print 'Interpreting as drawing request'
										temp_array[9] = 1
										return

									if 'NP' in subtree.label() and any(x in subtree.leaves() for x in calendar_nouns):
										# print 'Interpreting as calendar request'
										temp_array[1] = 1
										return

						if 'VB' in verb_subtree.label() \
						and any(x in verb_subtree.leaves() for x in schedule_verbs):

							# print "Interpreting as schedule request"
							return schedule_for_scikit(element, tree, temp_array)


				if "SBAR" in element.label():
					for subtree in element.subtrees():
						if "W" in subtree.label():
							noun_phrase = []
							# this is code for finding the noun phrase
							for noun_subtree in element.subtrees():
								if not "SBAR" in noun_subtree.label() \
								and not "W" in noun_subtree.label() \
								and "NP" in noun_subtree.label() \
								and len(noun_subtree.leaves()) > len(noun_phrase):

									noun_phrase = noun_subtree.leaves()

							# this code removes the article from the beginning
							if noun_phrase:
								if (noun_phrase[0] == 'a' or \
								 	noun_phrase[0] == 'an' or noun_phrase[0] == 'the'):
									del noun_phrase[0]

							if len(noun_phrase) <= 2:
								temp_array[8] = 1
							# TODO: Implement logic here to catch "when"-questions related to scheduling.

							# print "Interpreting as Wolfram query"
							return wolfram_for_scikit(element,temp_array)

		# If we hit here and haven't returned, then the query didn't match any of our patterns,
		# so default to Google Search.

		temp_array[5] = 1
		return

	except Exception as e:
		# print "Error in NLTK Brain: ", e.message
		# print sentence
		return

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

	#cal = Calendar()
	cal_parse = cal.parse(words)
	## print cal_parse
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

def schedule_suggest(cal_parse, words):
	starttime = None
	endtime = None
	if cal_parse[1] == 0:		# No date or time
		if "this week" in words:
			starttime = datetime.today() + relativedelta(weekday=MO(-1), hour=8, minute=0, second=0)
			endtime = starttime + relativedelta(weekday=FR, hour=17)
		elif "this month" in words:
			starttime = datetime.today() + relativedelta(day=1, hour=8, minute=0, second=0)
			endtime = starttime + relativedelta(day=31, weekday=FR(-1), hour=17)	# Last Friday of the month.
		else:	# Default to finding a time today.
			starttime = datetime.today()
			endtime = starttime + relativedelta(hour=17, minute=0, second=0)

	elif cal_parse[1] == 1:		# Date without a time
		if cal_parse[0][6] == 0 and cal_parse[0][3] == 9 and cal_parse[0][4] == 0:
			if "next week" in words:
				starttime = datetime.fromtimestamp(mktime(cal_parse[0])) + relativedelta(hour=8)
				endtime = starttime + relativedelta(weekday=FR, hour=17)
		elif cal_parse[0][6] == 0 and cal_parse[0][3] == 9 and cal_parse[0][4] == 0:
			if "next month" in words:
				starttime = datetime.fromtimestamp(mktime(cal_parse[0]))	+ relativedelta(hour=8)
				endtime = starttime + relativedelta(day=31, weekday=FR(-1), hour=17)	# Last Friday of the month.
		else:
			starttime = datetime.fromtimestamp(mktime(cal_parse[0])) + relativedelta(hour=8, minute=0, second=0)
			endtime = starttime + relativedelta(hour=17)

	return starttime, endtime

def wolfram_for_scikit(element, temp_array):
	words = ' '.join(element.leaves())

	temp_array[2] = 1
	return

def query_to_array(query):
	temp_array = np.array([0 for i in range(50)])
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
	# # print query + "\n"
	# makes it into an array
	query_array = query.split(' ')

	interpret_for_scikit([query], temp_array)

	# if len(query) < 5:
	# 	temp_array[9] = 1
	#uses 10, till
	check_word_lists(query_array, temp_array, 28)

	#uses 6
	check_for_w_words(query, temp_array, 21)


	return temp_array


def check_word_lists(query_array, temp_array, index):
	for i in range(len(query_array)):
		if query_array[i] in schedule_nouns:
			temp_array[index] = 1
		if query_array[i] in schedule_verbs:
			temp_array[index + 1] = 1
		if query_array[i] in doc_nouns:
			temp_array[index + 2] = 1
		if query_array[i] in doc_verbs:
			temp_array[index + 3] = 1
		if query_array[i] in calendar_nouns:
			temp_array[index + 4] = 1
		if query_array[i] in group_prps:
			temp_array[index + 5] = 1
		if query_array[i] in group_nouns:
			temp_array[index + 6] = 1
		if query_array[i] in drawing_nouns:
			temp_array[index + 7] = 1
		if query_array[i] in avail_words:
			temp_array[index + 8] = 1
		if query_array[i] in time_words:
			temp_array[index + 9] = 1
		if query_array[i] in schedule_suggest_verbs:
			temp_array[index + 10] = 1

def check_for_w_words(query, temp_array, index):
	#checks substings and length
	#if "what" in query:
	#temp_array[9] = 1
	if "when" in query:
		temp_array[index] = 1
	if "why" in query:
		temp_array[index + 1] = 1
	if "how" in query:
		temp_array[index + 2] = 1
	if "where" in query:
		temp_array[index + 3] = 1
	if "who" in query:
		temp_array[index + 4] = 1
	if "which" in query:
		temp_array[index + 5] = 1

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
		# print "The number of valid predictions is: " + str(valid_num) + "\nThe total number of predictions made is: " + str(len(training_feature_arrays[index + 1:])) + "\nThe validation ratio is: " + str(float(valid_num)/(len(training_feature_arrays[index + 1:])))
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
		valid_num = validate_predictor(training_feature_arrays[index + 1:], training_class_array[index + 1:], api_predictor, probability_matrix,training_set[index+1:])
	return valid_num

def multiple_predictors_for_testing_and_multiple_training_sets(ts_cal, ts_ss, ts_cs, ts_gd, ts_gdr, ts_wolf, ts_wiki, ts_gs, test_set_percentage, probability_matrix, f):
	# api predicting bernoulli naive bayesian classifier
	api_predictor = BernoulliNB()
	# random shuffles of training_sets
	random.shuffle(ts_cal) #calendar
	random.shuffle(ts_ss) #schedule suggest
	random.shuffle(ts_cs) #calendar show
	random.shuffle(ts_gd) #google docs
	random.shuffle(ts_gdr) #google drawings
	random.shuffle(ts_wolf) #wolram
	random.shuffle(ts_wiki) #wikipedia
	random.shuffle(ts_gs) #google search

	# returns the index of the percent of the test sets we want to test on
	index_cal = percent_to_index(test_set_percentage, len(ts_cal))
	index_ss = percent_to_index(test_set_percentage, len(ts_ss))
	index_cs = percent_to_index(test_set_percentage, len(ts_cs))
	index_gd = percent_to_index(test_set_percentage, len(ts_gd))
	index_gdr = percent_to_index(test_set_percentage, len(ts_gdr))
	index_wolf = percent_to_index(test_set_percentage, len(ts_wolf))
	index_wiki = percent_to_index(test_set_percentage, len(ts_wiki))
	index_gs = percent_to_index(test_set_percentage, len(ts_gs))

	# concatenate the test set list
	# TREVOR!!! THIS IS TO GET YOUR ATTENTION HERE.  JUST COMMENT THE FOLLOWING LINES OUT
	# AND TAKE WHATEVER SUBSET OF THE LISTS YOU WANT HERE. FOLLOW THE SYNTAX BELOW
	training_set = ts_cal[:index_cal + 1] + ts_ss[:index_ss + 1] + ts_cs[:index_cs + 1] + ts_gd[:index_gd + 1] + ts_gdr[:index_gdr + 1] + ts_wolf[:index_wolf + 1] +  ts_wiki[:index_wiki + 1]
	validation_set = ts_cal[index_cal + 1:] + ts_ss[index_ss + 1:] + ts_cs[:index_cs + 1] + ts_gd[index_gd + 1:] + ts_gdr[:index_gdr + 1] + ts_wolf[index_wolf + 1:] +  ts_wiki[index_wiki + 1:]

	# now we shuffle to mix up the list
	random.shuffle(training_set)
	random.shuffle(validation_set)

	# convert training set to binary feature arrays
	training_feature_arrays_train = change_query_string_to_int_array(training_set)
	training_feature_arrays_valid = change_query_string_to_int_array(validation_set)

	# this is used to hold the integer value of the api_type
	training_class_array_train = change_api_type_array_to_int_array(training_set)
	training_class_array_valid = change_api_type_array_to_int_array(validation_set)

	valid_num = -1

	train_predictor(training_feature_arrays_train, training_class_array_train, api_predictor)
	valid_num = validate_predictor(training_feature_arrays_valid, training_class_array_valid, api_predictor, probability_matrix, validation_set, f)
	return valid_num

def predictor_validation_list_to_plot_and_multiple_train_sets(num_tests, ts_cal, ts_ss, ts_cs, ts_gd, ts_gdr, ts_wolf, ts_wiki, ts_gs, test_set_percentage):
	f = open('failed_predictions', 'w')
	num_valid_list = []
	percentage_valid_list = []
	# this is the array of the probability confidence of picking a
	# particular class

	index_cal = percent_to_index(test_set_percentage, len(ts_cal))
	index_ss = percent_to_index(test_set_percentage, len(ts_ss))
	index_cs = percent_to_index(test_set_percentage, len(ts_cs))
	index_gd = percent_to_index(test_set_percentage, len(ts_gd))
	index_gdr = percent_to_index(test_set_percentage, len(ts_gdr))
	index_wolf = percent_to_index(test_set_percentage, len(ts_wolf))
	index_wiki = percent_to_index(test_set_percentage, len(ts_wiki))
	index_gs = percent_to_index(test_set_percentage, len(ts_gs))

	validation_set = ts_cal[index_cal + 1:] + ts_ss[index_ss + 1:] + ts_cs[index_cs + 1:] +  ts_gd[index_gd + 1:] + ts_gdr[index_gdr + 1:] + ts_wolf[index_wolf + 1:] +  ts_wiki[index_wiki + 1:] +  ts_gs[index_gs + 1:]

	probability_matrix = []


	total_validated_on = len(validation_set)
	for i in range(num_tests):
		num_valid_temp = multiple_predictors_for_testing_and_multiple_training_sets(ts_cal, ts_ss, ts_cs, ts_gd, ts_gdr, ts_wolf, ts_wiki, ts_gs, test_set_percentage, probability_matrix, f)
		num_valid_list.append(num_valid_temp)
		percentage_valid_list.append(float(num_valid_temp)/total_validated_on)
	# plots
	fig, ax = plt.subplots()
	# histogram our data with numpy
	data = percentage_valid_list
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

#predictor_validation_list_to_plot(150, training_set, .8)


def generate_questions_schedule_suggest():
	f = open('generated_questions_schedule_suggest', 'w')
	for i in range(len(schedule_verbs)):
		for j in range(len(schedule_nouns)):
			f.write("('" + schedule_verbs[i] + " " + schedule_nouns[j] + "', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + "', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + " for tomorrow', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + " for next week', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + " for next month', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + " for next year', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + " for us', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + " for all of us', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + " for all of us', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " " + schedule_nouns[j] + "', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + "', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + " for tomorrow', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + " for next week', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + " for next month', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + " for next year', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + " for us', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + " for all of us', 'schedule_suggest'),\n")
	for i in range(len(schedule_suggest_verbs)):
		for j in range(len(schedule_nouns)):
			f.write("('" + schedule_verbs[i] + " " + schedule_nouns[j] + "', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + "', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + " for tomorrow', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + " for next week', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + " for next month', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + " for next year', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + " for us', 'schedule_suggest'),\n")
			f.write("('" + schedule_verbs[i] + " a " + schedule_nouns[j] + " for all of us', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " " + schedule_nouns[j] + "', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + "', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + " for tomorrow', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + " for next week', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + " for next month', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + " for next year', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + " for us', 'schedule_suggest'),\n")
			f.write("('Benedict " + schedule_verbs[i] + " a " + schedule_nouns[j] + " for all of us', 'schedule_suggest'),\n")

def generate_questions_google_docs():
	f = open('generated_questions_google_docs', 'w')
	for i in range(len(doc_verbs)):
		for j in range(len(doc_nouns)):
			f.write("('" + doc_verbs[i] + " " + doc_nouns[j] + "', 'google_docs'),\n")
			f.write("('" + doc_verbs[i] + " a " + doc_nouns[j] + "', 'google_docs'),\n")
			f.write("('" + doc_verbs[i] + " a Google " + doc_nouns[j] + "', 'google_docs'),\n")
			f.write("('" + doc_verbs[i] + " Google " + doc_nouns[j] + "', 'google_docs'),\n")
			f.write("('" + doc_verbs[i] + " me " + doc_nouns[j] + "', 'google_docs'),\n")
			f.write("('" + doc_verbs[i] + " me a " + doc_nouns[j] + "', 'google_docs'),\n")
			f.write("('" + doc_verbs[i] + " us a " + doc_nouns[j] + "', 'google_docs'),\n")
			f.write("('" + doc_verbs[i] + " us " + doc_nouns[j] + "', 'google_docs'),\n")

def generate_questions_google_drawings():
	f = open('generated_questions_google_drawings', 'w')
	for i in range(len(doc_verbs)):
		for j in range(len(drawing_nouns)):
			f.write("('" + doc_verbs[i] + " " + drawing_nouns[j] + "', 'google_drawings'),\n")
			f.write("('" + doc_verbs[i] + " a " + drawing_nouns[j] + "', 'google_drawings'),\n")
			f.write("('" + doc_verbs[i] + " a Google " + drawing_nouns[j] + "', 'google_drawings'),\n")
			f.write("('" + doc_verbs[i] + " Google " + drawing_nouns[j] + "', 'google_drawings'),\n")
			f.write("('" + doc_verbs[i] + " me " + drawing_nouns[j] + "', 'google_drawings'),\n")
			f.write("('" + doc_verbs[i] + " me a " + drawing_nouns[j] + "', 'google_drawings'),\n")
			f.write("('" + doc_verbs[i] + " us a " + drawing_nouns[j] + "', 'google_drawings'),\n")
			f.write("('" + doc_verbs[i] + " us " + drawing_nouns[j] + "', 'google_drawings'),\n")

def generate_questions_google_calendar_show():
	f = open('generated_questions_google_calendar_show', 'w')
	for i in range(len(doc_verbs)):
		for j in range(len(calendar_nouns)):
			f.write("('" + doc_verbs[i] + " " + calendar_nouns[j] + "', 'calendar_show'),\n")
			f.write("('" + doc_verbs[i] + " a " + calendar_nouns[j] + "', 'calendar_show'),\n")
			f.write("('" + doc_verbs[i] + " a Google " + calendar_nouns[j] + "', 'calendar_show'),\n")
			f.write("('" + doc_verbs[i] + " Google " + calendar_nouns[j] + "', 'calendar_show'),\n")
			f.write("('" + doc_verbs[i] + " me " + calendar_nouns[j] + "', 'calendar_show'),\n")
			f.write("('" + doc_verbs[i] + " me a " + calendar_nouns[j] + "', 'calendar_show'),\n")
			f.write("('" + doc_verbs[i] + " us a " + calendar_nouns[j] + "', 'calendar_show'),\n")
			f.write("('" + doc_verbs[i] + " us " + calendar_nouns[j] + "', 'calendar_show'),\n")

# def generate_questions_wolfram():
# 	f = open('generated_questions_wolfram', 'w')
# 	for i in range(len(doc_verbs)):
# 		for j in range(len(doc_nouns)):
# 			f.write("('" + doc_verbs[i] + " " + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " a " + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " a Google " + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " Google " + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " me " + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " me a" + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " us a" + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " us " + doc_nouns[j] + "', 'google_docs'),\n")


# def generate_questions_wikipedia():
# 	f = open('generated_questions_wikipedia', 'w')
# 	for i in range(len(doc_verbs)):
# 		for j in range(len(doc_nouns)):
# 			f.write("('" + doc_verbs[i] + " " + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " a " + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " a Google " + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " Google " + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " me " + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " me a" + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " us a" + doc_nouns[j] + "', 'google_docs'),\n")
# 			f.write("('" + doc_verbs[i] + " us " + doc_nouns[j] + "', 'google_docs'),\n")






def pickle_predictor(predictor):
	print "starting to pickle predictor"
	train_predictor_for_brain(predictor, training_set_calendar, training_set_schedule_suggest, training_set_google_calendar_show, training_set_google_docs, training_set_google_drawings, training_set_wolfram, training_set_wikipedia, training_set_google)
	pickled_string = cPickle.dumps(predictor)
	f = open('brain/pickled_predictor.txt', 'w')
	f.write(pickled_string)
	f.close()
	print "finished pickling predictor"





def train_predictor_for_brain(predictor, ts_cal, ts_ss, ts_cs, ts_gd, ts_gdr, ts_wolf, ts_wiki, ts_goog):
	print "starting predictor training, please be patient, this will take a while"
	training_set = ts_cal + ts_ss + ts_cs + ts_gd + ts_gdr + ts_wolf + ts_wiki + ts_goog

	training_feature_arrays_train = change_query_string_to_int_array(training_set)
	training_class_array_train = change_api_type_array_to_int_array(training_set)
	train_predictor(training_feature_arrays_train, training_class_array_train, predictor)
	print "finished training predictor"



def check_word_lists_threshold(query_array, class_index):
	for i in range(len(query_array)):
		if class_index == 0 or class_index == 1 or class_index == 2:
			if query_array[i] in schedule_nouns:
				return 1
		if class_index == 3:
			if query_array[i] in doc_nouns:
				return 1
		if class_index == 4:
			if query_array[i] in drawing_nouns:
				return 1
	return 0

def threshold_calculator_for_predict(probabilities, query):

	probabilities = probabilities.tolist()[0]
	print probabilities
	if probabilities[0] > .7 or probabilities[1] > .1:
		cal_parse = cal.parse(query)
		if cal_parse[1] == 0 or cal_parse[1] == 1:
			if check_word_lists_threshold(query.split(' '), class_index):
				return 1
			else:
				if probabilities[2] > .1 or probabilities[3] > .1 or probabilities[4] > .1:
					class_index = probabilities.index(max(probabilities[2:5]))
					if check_word_lists_threshold(query.split(' '), class_index):
						return class_index + 1
					elif probabilities[5] > .1 or probabilities[6] > .1:
						return probabilities.index(max(probabilities[5:7])) + 1
					else:
						return probabilities.index(max(probabilities)) + 1
				elif probabilities[5] > .1 or probabilities[6] > .1:
					return probabilities.index(max(probabilities[5:7])) + 1
				else:
					return probabilities.index(max(probabilities)) + 1
		else:
			if check_word_lists_threshold(query.split(' '), class_index):
				return 2
			else:
				if probabilities[2] > .1 or probabilities[3] > .1 or probabilities[4] > .1:
					class_index = probabilities.index(max(probabilities[2:5]))
					if check_word_lists_threshold(query.split(' '), class_index):
						return class_index + 1
					elif probabilities[5] > .1 or probabilities[6] > .1:
						return probabilities.index(max(probabilities[5:7])) + 1
					else:
						return probabilities.index(max(probabilities)) + 1
				elif probabilities[5] > .1 or probabilities[6] > .1:
					return probabilities.index(max(probabilities[5:7])) + 1
				else:
					return probabilities.index(max(probabilities)) + 1

	elif probabilities[2] > .1 or probabilities[3] > .1 or probabilities[4] > .1:
		class_index = probabilities.index(max(probabilities[2:5]))
		if check_word_lists_threshold(query.split(' '), class_index):
			return class_index + 1
		elif probabilities[5] > .1 or probabilities[6] > .1:
			return probabilities.index(max(probabilities[5:7])) + 1
		else:
			return probabilities.index(max(probabilities)) + 1
	elif probabilities[5] > .1 or probabilities[6] > .1:
		return probabilities.index(max(probabilities[5:7])) + 1
	else:
		return probabilities.index(max(probabilities)) + 1

#Trevor fill this in!!!
def question_noun_phrase(query):
	if(len(query.split()) <= 1):
		return query

	query = oclock_remover(query)
	query = benedict_remover(query)
	parser = Parser()
	tree = parser.parse(query)

	if 'NP' == tree.label() or \
	'NP+NP'== tree.label() or \
	'NX+NX'== tree.label() or \
	'NX+NP'== tree.label() or \
	'NP+NX'== tree.label() or \
	'FRAG'== tree.label() or \
	'NX' == tree.label():
		words = query
		noun_phrase = []
		# this is code for finding the noun phrase
		noun_phrase = tree.leaves()

		# this code removes the article from the beginning
		if noun_phrase:
			if (noun_phrase[0] == 'a' or \
			 	noun_phrase[0] == 'an' or noun_phrase[0] == 'the'):
				del noun_phrase[0]

		#print noun_phrase
		noun_phrase = ' '.join(noun_phrase)

		return noun_phrase

	for element in [tree] + [e for e in tree]: # Include the root element in the for loop
		if "SBAR" in element.label():
			for subtree in element.subtrees():
				if "W" in subtree.label():
					noun_phrase = []
					print noun_phrase
					# this is code for finding the noun phrase
					for noun_subtree in element.subtrees():
						if not "SBAR" in noun_subtree.label() \
						and not "W" in noun_subtree.label() \
						and "NP" in noun_subtree.label() \
						and len(noun_subtree.leaves()) > len(noun_phrase):

							noun_phrase = noun_subtree.leaves()

					# this code removes the article from the beginning
					if noun_phrase:
						if (noun_phrase[0] == 'a' or \
						 	noun_phrase[0] == 'an' or noun_phrase[0] == 'the'):
							del noun_phrase[0]

					noun_phrase = ' '.join(noun_phrase)

					return noun_phrase

	return ""

def get_datetime(query):
	cal_parse = cal.parse(query)
	## print cal_parse
	if cal_parse[1] == 0 or cal_parse[1] == 1:
		starttime, endtime = schedule_suggest(cal_parse, query)
		starttime = starttime.strftime('%Y-%m-%dT%H:%M:%S')
		endtime   = endtime.strftime('%Y-%m-%dT%H:%M:%S')
	else:
		starttime, endtime = time_converter(cal_parse[0])

	return starttime, endtime

# EVAN THIS IS WHERE WE MAKE THE JSON I NEED TO SOMEHOW PUT THE DATETIME STUFF IN IT
def make_json(query, api_type, api_number):
	if api_type == "wolfram" or api_type == "wikipedia" or api_type == "google":
		if query != "":
			noun_phrase = question_noun_phrase(query)
			return '{"api_number": "' + str(api_number) + '", "api_type": "' + api_type + '", "query": "' + query + '", "noun_phrase": "' + noun_phrase +'"}'
		else:
			return '{"api_number": "' + str(api_number) + '", "api_type": "' + api_type + '", "query": "blank", "noun_phrase": ""}'

	#THIS IS THE SPECIFIC SPOT WE NEED TO ADD DATETIME STUFF AND THE ATTENDEES ARRAY
	if api_type == "calendar" or api_type == "schedule_suggest":
		starttime, endtime = get_datetime(query)
		print "starttime: ", starttime, "     ", "endtime: ", endtime
		return '{"api_number": "' + str(api_number) +'", "api_type": "' + api_type + '", "query": "' + query + '", "noun_phrase": "", "start": "' + starttime + '", "end": "' + endtime + '" }'

	# EVAN WE NEED THE ATTENDEES ARRAY IN THIS ONE
	if api_type == "calendar_show" or api_type == "google_docs" or api_type == "google_drawings":
		return '{"api_number": "' + str(api_number) +'", "api_type": "' + api_type + '", "query": "' + query + '", "noun_phrase": ""}'



def predict_api_type(predictor, query):

	query_array = query_to_array(query)

	probability_predict = predictor.predict_proba(query_array)

	api_return = threshold_calculator_for_predict(probability_predict, query)

	api_type = change_int_to_api_type(api_return)

	return make_json(query, api_type, api_return)




#predictor_to_be_pickled = BernoulliNB()

#90pickle_predictor(predictor_to_be_pickled)






#print question_noun_phrase("big dogs eating cabbage")
#generate_questions_google_calendar_show()
#generate_questions_google_drawings()

#predictor_validation_list_to_plot_and_multiple_train_sets(1, training_set_calendar, training_set_schedule_suggest, training_set_google_calendar_show, training_set_google_docs, training_set_google_drawings, training_set_wolfram, training_set_wikipedia, training_set_google, .8)



def schedule_suggest(cal_parse, words):
	starttime = None
	endtime = None
	if cal_parse[1] == 0:		# No date or time
		if "this week" in words:
			starttime = datetime.today() + relativedelta(weekday=MO(-1), hour=8, minute=0, second=0)
			endtime = starttime + relativedelta(weekday=FR, hour=17)
		elif "this month" in words:
			starttime = datetime.today() + relativedelta(day=1, hour=8, minute=0, second=0)
			endtime = starttime + relativedelta(day=31, weekday=FR(-1), hour=17)	# Last Friday of the month.
		else:	# Default to finding a time today.
			starttime = datetime.today()
			endtime = starttime + relativedelta(hour=17, minute=0, second=0)

	elif cal_parse[1] == 1:		# Date without a time
		if cal_parse[0][6] == 0 and cal_parse[0][3] == 9 and cal_parse[0][4] == 0:
			if "next week" in words:
				starttime = datetime.fromtimestamp(mktime(cal_parse[0])) + relativedelta(hour=8)
				endtime = starttime + relativedelta(weekday=FR, hour=17)
		elif cal_parse[0][6] == 0 and cal_parse[0][3] == 9 and cal_parse[0][4] == 0:
			if "next month" in words:
				starttime = datetime.fromtimestamp(mktime(cal_parse[0]))	+ relativedelta(hour=8)
				endtime = starttime + relativedelta(day=31, weekday=FR(-1), hour=17)	# Last Friday of the month.
		else:
			starttime = datetime.fromtimestamp(mktime(cal_parse[0])) + relativedelta(hour=8, minute=0, second=0)
			endtime = starttime + relativedelta(hour=17)

	return starttime, endtime