import nltk
import parsedatetime
from nltk.tag import pos_tag, map_tag
from stat_parser import Parser, display_tree
from timex import time_tag


parser = Parser()	# Build this outside the fn. so it doesn't rebuild each time
cal = parsedatetime.Calendar()

# A way to investigate how the test cases are parsed, for curiosity.
def test(sentence):
	print parser.parse(sentence)

# Input:  a sentence containing a request to schedule a meeting.
# Output: a date-time, or False if none was found.
def schedule_meeting(sentence):


	schedule_verbs = ['set', 'make', 'create', 'get', 'schedule', 'appoint', 
					 'slate', 'arrange', 'organize', 'construct', 'coordinate',
					 'establish', 'form', 'formulate', 'run', 'compose', 'have', 'meet']
	schedule_nouns = ['appointment', 'meeting','meetup', 'reservation', 'session'
					 'talk', 'call', 'powwow', 'meet', 'rendezvous', 'event', 'conference']


	tree = parser.parse(sentence)
	
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
						print subtree
						if 'NP' in subtree.label() and any(x in subtree.leaves() for x in schedule_nouns):
							words = ' '.join(subtree.leaves())
							print words
							if cal.parse(words)[1] != 0:
								return cal.parse(words)
						else:
							if subtree.label() == 'PP':
								words = ' '.join(subtree.leaves())
								print words
								if cal.parse(words)[1] != 0:
									return cal.parse(words)


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
	test("Schedule a meeting tomorrow.")
	print schedule_meeting("Schedule a meeting tomorrow.")

