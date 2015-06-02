import nltk
from parsedatetime import Calendar
from nltk.tag import pos_tag, map_tag
from stat_parser import Parser, display_tree
from time import mktime
from datetime import datetime , timedelta
from dateutil.relativedelta import *

parser = Parser()	# Build this outside the fn. so it doesn't rebuild each time
cal = Calendar()

schedule_verbs = ['add', 'set', 'make', 'create', 'get', 'schedule', 'appoint',
				 'slate', 'arrange', 'organize', 'construct', 'coordinate',
				 'establish', 'form', 'formulate', 'run', 'compose', 'have', 'meet',
				 'reschedule', 'find'] #'find' is for schedule-suggesting; be careful

schedule_suggest_verbs = ['suggest', 'recommend', 'propose', 'show']

schedule_nouns = ['appointment', 'meeting','meetup', 'reservation', 'session'
				 'talk', 'call', 'powwow', 'meet', 'rendezvous', 'event', 'conference', 'time']

doc_verbs = ['open', 'open up', 'view', 'launch', 'look','display', 'check', 'start',
				'begin','create', 'make', 'get', 'have', 'set', 'generate', 'show', 'pull']

avail_words = ['free', 'available', 'works', 'potential', 'options']

time_words = ['tomorrow', 'today', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
							'Friday', 'Saturday', 'Sunday','a.m.', 'am', 'p.m.', 'pm', 'week',
							'month', 'day', 'time', 'year', 'date']

doc_nouns = ['doc', 'dog', 'dock' , 'document', 'script', 'record', 'report', 'page', 'notepad']

drawing_nouns = ['drawing','picture','markerboard', 'board', 'whiteboard', 'painting',
				'sketch', 'layout', 'design', 'depiction', 'chalkboard']

calendar_nouns = ['calendar', 'agenda', 'schedule', 'itinerary']

group_prps  = ['we', 'us', 'our']
group_nouns = ['everyone', 'everybody']

def oclock_remover(sentence):
	if "o'clock" in sentence:
		potential_time = (sentence.split()).index("o'clock") - 1
		if int(sentence.split()[potential_time]) > 7 and int(sentence.split()[potential_time]) < 12:
			sentence = sentence.replace("o'clock", "a.m.")
		else:
			sentence = sentence.replace("o'clock", "p.m.")
	return sentence

def benedict_remover(sentence):

	if "benedict" in sentence:
		return sentence.replace("benedict", "")
	if "Benedict" in sentence:
		return sentence.replace("Benedict", "")
	else:
		return sentence


def am_pm_adder(words):
	for word in words.split():
		if word.isdigit() and not('pm' in words or 'p.m.' in words \
		or 'am' in words or 'a.m.' in words):
			if int(word) > 7 and int(word) < 12:
				words = words.replace(word, word + " a.m.")
			else:
				words = words.replace(word, word + " p.m.")

	return words

def time_converter(time_struct):
	starttime = datetime.fromtimestamp(mktime(time_struct))
	endtime = starttime + timedelta(hours = 1)
	return starttime.strftime('%Y-%m-%dT%H:%M:%S'), endtime.strftime('%Y-%m-%dT%H:%M:%S')

def interpret(sentences):
	try:
		for sentence in sentences:
			if(len(sentence.split()) <= 1):
				words = sentences[0]
				text = '{"api_type": "wikipedia", \
			 		"query": "' + words + '"}'
				return text

			sentence = oclock_remover(sentence)
			sentence = benedict_remover(sentence)

			tree = parser.parse(sentence)


			print tree

			print tree.leaves()
			# first just check if its just a noun phrase, then go to wiki
			if 'NP' == tree.label() or \
			'NP+NP'== tree.label() or \
			'NX+NX'== tree.label() or \
			'NX+NP'== tree.label() or \
			'NP+NX'== tree.label() or \
			'FRAG'== tree.label() or \
			'NX' == tree.label():
				print 'interpreting as just a noun phrase'
				words = sentence
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

				text = '{"api_type": "wikipedia", \
					"noun_phrase": "' + noun_phrase + '", \
			 		"query": "' + words + '"}'
				return text

			for element in [tree] + [e for e in tree]: # Include the root element in the for loop

				# RRC for case of "open a document" where open is interpeted as adjective
				if 'VP' in element.label() or 'SQ' in element.label() or 'RRC' in element.label():
					for verb_subtree in element.subtrees():

						if 'VB' in verb_subtree.label() or 'JJ' in verb_subtree.label() \
						and any(x in verb_subtree.leaves() for x in doc_verbs):
							for subtree in element.subtrees():
									if 'NP' in subtree.label() and any(x in subtree.leaves() for x in doc_nouns):
										print 'Interpreting as doc request'
										return '{"api_type": "google_docs"}'

									if 'NP' in subtree.label() and any(x in subtree.leaves() for x in drawing_nouns):
										print 'Interpreting as drawing request'
										return '{"api_type": "google_drawings"}'

									if 'NP' in subtree.label() and any(x in subtree.leaves() for x in calendar_nouns):
										print 'Interpreting as calendar request'
										return '{"api_type": "calendar_show"}'

						if 'VB' in verb_subtree.label() \
						and any(x in verb_subtree.leaves() for x in schedule_verbs):

							print "Interpreting as schedule request"
							return schedule(element, tree)


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


							# TODO: Implement logic here to catch "when"-questions related to scheduling.

							print "Interpreting as Wolfram or Wikipedia query"
							return wolfram(element, noun_phrase)



		# If we hit here and haven't returned, then the query didn't match any of our patterns,
		# so default to Google Search.
		words = sentences[0]
		text = '{"api_type": "google", \
			 "query": "' + words + '"}'
		return text

	except Exception as e:
		print "Error in NLTK Brain: ", e.message

	return '{"api_type": "blank_query"}'

# Pass a top-level element to this once we've determined that it likely contains a scheduling request.
# Input:  an NLTK Tree element
# Return: a tuple containing (start_time, end_time, description)
def schedule(element, tree):
	# Find the "schedule word" in a NP, if one exists
	schedule_word = "Meeting"
	for subtree in element.subtrees():
		if 'NP' in subtree.label() and any(x in subtree.leaves() for x in schedule_nouns):
			for x in subtree.leaves():
				if x in schedule_nouns:
					schedule_word = x

	group_flag = False
	for elem in tree.subtrees():
		if 'PRP' in elem.label() and any(x in elem.leaves() for x in group_prps):
			group_flag = True
		if any (x in elem.leaves() for x in group_nouns):
			group_flag = True

	words = ' '.join(element.leaves())
	words = am_pm_adder(words)

	cal_parse = cal.parse(words)
	print cal_parse
	if cal_parse[1] == 0 or cal_parse[1] == 1:
		starttime, endtime = schedule_suggest(cal_parse, words)
		starttime = starttime.strftime('%Y-%m-%dT%H:%M:%S')
		endtime   = endtime.strftime('%Y-%m-%dT%H:%M:%S')
		print("@@@@@@@@@@@@@@@@@SCHEDULE SUGGEST")
		api_type  = "schedule_suggest"
	else:
		starttime, endtime = time_converter(cal_parse[0])
		api_type = "calendar"

	text = '{"attendees": [{"email": "trevor.frese@gmail.com" }], \
    		"api_type": "' + api_type + '", \
    		"start": {"datetime": "' + str(starttime) + '", \
    		"timezone": "America/Los_Angeles"}, \
    		"end": {"datetime": "' + str(endtime) + '",\
    		"timezone": "America/Los_Angeles"}, \
    		"location": "", \
    		"summary": "' + str(schedule_word).capitalize() +' scheduled by Benedict",\
    		"group_flag": "' + str(group_flag) + '"}'

	print text

	return text

# Currently supports: "this week", "next week", "this month", "next month",
# specific days e.g. "[this] Thursday", "next Tuesday"
# Eventually: even more precision ("the first week in April"?)
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

def wolfram(element, nouns):
	words = ' '.join(element.leaves())
	noun_phrase = ' '.join(nouns)
	text = '{"api_type": "wolfram", \
			 "noun_phrase": "' + noun_phrase + '", \
			 "query": "' + words + '"}'

	return text

def run_tests(filename):
	testfile = open(filename, 'r')
	i = 0
	for line in testfile:
		print "Test ", i, ": ", line
		print interpret([line])
		print
		i += 1
	testfile.close()


def check_apis(filename):
	testfile = open(filename, 'r')
	i = 0
	for line in testfile:

		result = interpret([line])
		word_list = result.split(' ')
		index = word_list.index('{"api_type":')
		line = line.replace('\n', ' ')
		print
		print "Test ", i, ": ", line , word_list[index + 1]
		print
		i += 1
	testfile.close()

if __name__ == "__main__":
	#run_tests('example_sentences.txt')
	#schedule_JJ("schedule meeting for tomorrow at 4 pm")
	#print schedule_meeting(["schedule a meeting for tomorrow at 3 pm"])
	#run_tests('example_sentences.txt')
	print interpret(['the eiffel tower'])

	#check_apis("example_sentences.txt")
