import nltk
import parsedatetime
from nltk.tag import pos_tag, map_tag
from stat_parser import Parser, display_tree
from time import mktime
from datetime import datetime , timedelta

parser = Parser()	# Build this outside the fn. so it doesn't rebuild each time
cal = parsedatetime.Calendar()

schedule_verbs = ['set', 'make', 'create', 'get', 'schedule', 'appoint',
				 'slate', 'arrange', 'organize', 'construct', 'coordinate',
				 'establish', 'form', 'formulate', 'run', 'compose', 'have', 'meet',
				 'reschedule']
schedule_nouns = ['appointment', 'meeting','meetup', 'reservation', 'session'
				 'talk', 'call', 'powwow', 'meet', 'rendezvous', 'event', 'conference']

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

def time_converter(time_struct, schedule_word):
	starttime = datetime.fromtimestamp(mktime(time_struct[0]))
	endtime = starttime + timedelta(hours = 1)
	return starttime.strftime('%Y-%m-%dT%H:%M:%S'), endtime.strftime('%Y-%m-%dT%H:%M:%S') , schedule_word

# Input:  a list of sentences, each possibly containing a request to schedule a meeting.
# Output: a tuple of (start_time, end_time, description) for the first successful sentence.
def schedule_meeting(sentences):
	for sentence in sentences:
		try:
			if(len(sentence.split()) <= 1):
				return None
			sentence = oclock_remover(sentence)

			tree = parser.parse(sentence)
			schedule_word = "Meeting"
			print tree

			for element in [tree] + [e for e in tree]: # Include the root element in the for loop

				if 'VP' in element.label() or 'SQ' in element.label():
					for verb_subtree in element.subtrees():
						# Check if the VP contains a VB that is in the schedule_verbs.
						if 'VB' in verb_subtree.label() \
						and any(x in verb_subtree.leaves() for x in schedule_verbs):
						
							return accept(element)

		except Exception as e:
			print "Error in NLTK Brain: ", e.message
			return None

	return None

# Pass a top-level element to this once we've determined that it likely contains a scheduling request.
# Input:  an NLTK Tree element
# Return: a tuple containing (start_time, end_time, description)
def accept(element):
	# Find the "schedule word" in a NP, if one exists
	for subtree in element.subtrees():
		if 'NP' in subtree.label() and any(x in subtree.leaves() for x in schedule_nouns):
			for x in subtree.leaves():
				if x in schedule_nouns:
					schedule_word = x

	# Run the datetime parser on the entire sentence
	words = ' '.join(element.leaves())	# Operate on the whole VP
	words = am_pm_adder(words)
	if cal.parse(words)[1] != 0:
		return time_converter(cal.parse(words), schedule_word)

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
	#run_tests('example_sentences.txt')
	#schedule_JJ("schedule meeting for tomorrow at 4 pm")
	print schedule_meeting(["schedule a meeting for tomorrow at 3 pm"])