import nltk
import parsedatetime
from nltk.tag import pos_tag, map_tag
from stat_parser import Parser, display_tree
from time import mktime
from datetime import datetime , timedelta

parser = Parser()	# Build this outside the fn. so it doesn't rebuild each time
cal = parsedatetime.Calendar()

schedule_verbs = ['add', 'set', 'make', 'create', 'get', 'schedule', 'appoint',
				 'slate', 'arrange', 'organize', 'construct', 'coordinate',
				 'establish', 'form', 'formulate', 'run', 'compose', 'have', 'meet',
				 'reschedule']

schedule_nouns = ['appointment', 'meeting','meetup', 'reservation', 'session'
				 'talk', 'call', 'powwow', 'meet', 'rendezvous', 'event', 'conference']

doc_verbs = ['open', 'view', 'launch', 'look','display', 'check', 'start',
				'begin','create', 'make', 'get', 'have', 'set', 'generate']

doc_nouns = ['doc', 'dog', 'dock' , 'document', 'script', 'record', 'report', 'page']

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
	starttime = datetime.fromtimestamp(mktime(time_struct[0]))
	endtime = starttime + timedelta(hours = 1)
	return starttime.strftime('%Y-%m-%dT%H:%M:%S'), endtime.strftime('%Y-%m-%dT%H:%M:%S')

def interpret(sentences):
	try:
		for sentence in sentences:
			if(len(sentence.split()) <= 1):
				return None
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
										return '{"api_type": "google_docs"}'

						if 'VB' in verb_subtree.label() \
						and any(x in verb_subtree.leaves() for x in schedule_verbs):

							print "Interpreting as schedule request"
							return schedule(element, tree)



				if "SBAR" in element.label():
					for subtree in element.subtrees():
						if "W" in subtree.label():

							print "Interpreting as Wolfram query"
							return wolfram(element)



		# If we hit here and haven't returned, then the query didn't match any of our patterns,
		# so default to Google Search.
		words = sentences[0]
		text = '{"api_type": "google", \
			 "query": "' + words + '"}'
		return text

	except Exception as e:
		print "Error in NLTK Brain: ", e.message

	return None

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

	print group_flag

	if cal.parse(words)[1] == 0:
		return '{"api_type": "Blank Query"}'

	starttime, endtime = time_converter(cal.parse(words))

	text = '{"attendees": [{"email": "trevor.frese@gmail.com" }], \
    		"api_type": "calendar", \
    		"start": {"datetime": "' + str(starttime) + '", \
    		"timezone": "America/Los_Angeles"}, \
    		"end": {"datetime": "' + str(endtime) + '",\
    		"timezone": "America/Los_Angeles"}, \
    		"location": "", \
    		"summary": "' + str(schedule_word).capitalize() +' scheduled by Benedict"}'

	return text


def google_doc(element):

	for subtree in element.subtrees():
		if 'NP' in subtree.label() and any(x in subtree.leaves() for x in doc_nouns):
			return '{"api_type": "google_docs"}'

	

def wolfram(element):
	words = ' '.join(element.leaves())

	text = '{"api_type": "wolfram", \
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

if __name__ == "__main__":
	#run_tests('example_sentences.txt')
	#schedule_JJ("schedule meeting for tomorrow at 4 pm")
	#print schedule_meeting(["schedule a meeting for tomorrow at 3 pm"])
	#run_tests('example_sentences.txt')
	print interpret(["Can everybody meet on Thursday at 3 pm"])