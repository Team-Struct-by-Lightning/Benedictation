import nltk
import parsedatetime
from nltk.tag import pos_tag, map_tag
from stat_parser import Parser, display_tree
from time import mktime
from datetime import datetime , timedelta

parser = Parser()	# Build this outside the fn. so it doesn't rebuild each time
cal = parsedatetime.Calendar()

# A way to investigate how the test cases are parsed, for curiosity.
def test(sentence):
	print parser.parse(sentence)

def oclock_remover(sentence):
	if "o'clock" in sentence:
		potential_time = (sentence.split()).index("o'clock") - 1
		if int(sentence.split()[potential_time]) > 7 and int(sentence.split()[potential_time]) < 12: 
			sentence = sentence.replace("o'clock", "a.m.") 
		else:
			sentence = sentence.replace("o'clock", "p.m.")
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
# Input:  a sentence containing a request to schedule a meeting.
# Output: a date-time, or False if none was found.
def schedule_meeting(sentence):

	schedule_verbs = ['set', 'make', 'create', 'get', 'schedule', 'appoint',
					 'slate', 'arrange', 'organize', 'construct', 'coordinate',
					 'establish', 'form', 'formulate', 'run', 'compose', 'have', 'meet']
	schedule_nouns = ['appointment', 'meeting','meetup', 'reservation', 'session'
					 'talk', 'call', 'powwow', 'meet', 'rendezvous', 'event', 'conference']



	
	sentence = oclock_remover(sentence)

	tree = parser.parse(sentence)
	schedule_word = "Meeting"
	#print tree
	for element in [tree] + [e for e in tree]: # Include the root element in the for loop
		
		if 'VP' in element.label() or 'SQ' in element.label():
			#print element
			for verb_subtree in element.subtrees():
				# Check if the VP contains a VB that is in the schedule_verbs.
				# If it does, check if the VP contains a PP with a datetime,
				# or a NP with a datetime.
				if 'VB' in verb_subtree.label() \
				and any(x in verb_subtree.leaves() for x in schedule_verbs):
					for subtree in element.subtrees():
						#print subtree
						if 'NP' in subtree.label() and any(x in subtree.leaves() for x in schedule_nouns):
							# This section should ALWAYS return something. If it can't
							# figure out a time on its own, we should default to "right now"

							for x in subtree.leaves():
								if x in schedule_nouns:
									schedule_word = x
							
							words = ' '.join(subtree.leaves())
							words = am_pm_adder(words)

							#print words
							if cal.parse(words)[1] != 0:
								return time_converter(cal.parse(words), schedule_word)
						else:
							if subtree.label() == 'PP' or subtree.label() == 'QP':
								words = ' '.join(subtree.leaves())
								#print words
								if cal.parse(words)[1] != 0:
									#print cal.parse(words)[1]
									return time_converter(cal.parse(words), schedule_word)

	return None

def time_converter(time_struct, schedule_word):
	starttime = datetime.fromtimestamp(mktime(time_struct[0]))
	endtime = starttime + timedelta(hours = 1)
	return starttime.strftime('%Y-%m-%dT%H:%M:%S'), endtime.strftime('%Y-%m-%dT%H:%M:%S') , schedule_word


def run_tests(filename):
	testfile = open(filename, 'r')
	i = 0
	for line in testfile:
		print "Test ", i, ": ", line
		print schedule_meeting(line)
		print
		i += 1
	testfile.close()

if __name__ == "__main__":
	run_tests('example_sentences.txt')
	#print schedule_meeting("Set up a meeting at 8 for tomorrow ")
	#print cal.nlp("tomorrow at 5 pm ")
	#print schedule_meeting("Schedule a meeting tomorrow at 4 pm")